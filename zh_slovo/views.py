#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = 'alenush'
from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from .models import Dict_text, Errors_table, Answer_user
import difflib, re, random, simplejson
from collections import Counter

from nltk.tokenize import WordPunctTokenizer


def tokenize_sentence(sent1, sent2):
    #word_punct_tokenizer = WordPunctTokenizer()
    #s1 = word_punct_tokenizer.tokenize(sent1)
    #s2 = word_punct_tokenizer.tokenize(sent2)
    pass


def check_errors_in_db(result):
    """
    Find, where !=equal
    Function takes from diff resuls (array with ("equal, a1,a2, b1,b2") )
    :param result:
    :return: array from (error-object, tok_begin for error tok_end)
    """
    dictation = Dict_text.objects.get()
    origin, dic_id = dictation.dic_origin_text, dictation.id
    errors = []
    for op, a1, a2, b1, b2 in result:
        if op != "equal":
            er_object = Errors_table.objects.filter(id_dict=dic_id,symbol_place_in_sent=a1)
            if len(er_object) != 0:
                object_dic = er_object.values()[0]
                tok_begin, tok_end = object_dic["token_border_begin"], object_dic["token_border_end"]
                errors.append((er_object, tok_begin, tok_end))
    #if more than ? return СМ,
    return errors


def orig_to_user(result):
    #строим словарь orig2user, координатами в user для каждого символа orig;
    # для диапазонов в user берём крайнюю левую координату
    #переводит координату одного символа из ориг в юсер
    orig2user = {}
    for tup in result:
        for i, j in zip(range(tup[1], tup[2]+1), range(tup[3], tup[4]+1)):
            orig2user[i] = j
    print orig2user
    return orig2user


def token_borders2user(origin2user, errors):
    """перевести границы токена в координаты user
    :return:user_er_tokens: массив. границы токенов с ошибкой у пользователя
    """
    user_er_tokens = []
    for error in errors:
        user_er_tokens.append((origin2user[error[1]], origin2user[error[2]]))
    print user_er_tokens
    return user_er_tokens


def fill_user_arrays(user_borders, errors):
    """
    :param:user_borders: [token begin, token end]
    :param:errors: array with (er_object, tok_begin, tok_end))
    заводим список из кучи []; проходим по найденным диапазонам в координатах user,
    и дописываем в каждый [] по этим координатам описания ошибок, соответствующие этому диапазону
    :return:
    """
    array = [[]]*50
    for i in range(0, len(array)):
        for teil in user_borders:
            if i in range(teil[0],teil[1]+1):
                array[i] = errors[user_borders.index(teil)][0]
    print array
    return array


def collect_markup(parts_array, user_text):
    """- проходим по zip(от этого списка и текста user), и собираем словари { text, errors }
    из каждой цепочки идущих подряд букв, имеющих одинаковые ошибки
    :param:parts_array:
    """
    markup = {} #should be {"part_text":[errors],} errors -> (type_of_error, comments_to_error, right_answer)
    text_part = ""
    last_error = []
    for user, error in zip(user_text, parts_array):
        if error == last_error:
            text_part += user
        else:
            if last_error != []:
                error_info = [{"type":last_error[0].type_of_error, "comment":last_error[0].comments_to_error, "right_answer":last_error[0].right_answer}]
                markup[text_part] = error_info
            else:
                markup[text_part] = last_error
            text_part = user
            last_error = error
    markup[text_part] = last_error
    print "MARK_UP", markup
    return markup

def count_errors(markup):
    #- проходим по словарям, и считаем, сколько итоговых словарей содержат хотя бы одну орфографическую ошибку,
    # сколько хотя бы одну пунктуационную; эти числа и называем числом ошибок
    OR = 0
    PU = 0
    for key in markup.keys():
        for ar in markup[key]:
            if "OR" in ar.values():
                OR +=1
            elif "PU" in ar.values():
                PU += 1
    return OR, PU


def diff_strings(user, origin):
    """
    Function aligns two strings.
    :param sent1: sentence user
    :param sent2: sentence origin
    :return: sentence with + -. - delete, + add right
    """
    dif = difflib.SequenceMatcher(unicode.isspace, origin, user)
    print u'\n'.join(u"{}: {}~{} {} / {}~{} {}".format(op, a1, a2, origin[a1:a2], b1, b2, user[b1:b2]) for op, a1, a2, b1, b2 in dif.get_opcodes())
    result = dif.get_opcodes()
    origin2user = orig_to_user(result) # dictionary of orig to user match
    errors = check_errors_in_db(result) # array with (er_object, tok_begin, tok_end))
    user_borders = token_borders2user(origin2user, errors) # user tokens with errors
    array_with_parts = fill_user_arrays(user_borders, errors) #array with [[][][][Error][][Error][Error]]
    markup = collect_markup(array_with_parts, user)
    or_er, p_er = count_errors(markup)
    grade = return_user_grade(or_er, p_er)
    return result, grade, or_er, p_er, markup


def return_user_grade(orph,punct):
    """
    Function takes an array of types of errors and returns mark
    :return: string with user grade or См.
    """
    five = [(0,0)]
    four = [(0,1), (0,2),(0,3),(0,4),(1,0),(1,1), (1,2), (1,3), (2,0), (2,1), (2,2)]
    three = [(0,5),(0,6),(0,7),(0,8),(1,4),(1,5), (1,6), (1,7), (2,3), (2,4), (2,5),(2,6),
        (3,0),(3,1),(3,2),(3,3),(3,4),(3,5),(4,0),(4,1),(4,2),(4,3),(4,4)]
    if (orph,punct) in five:
        return u"5"
    elif (orph,punct) in four:
        return u"4"
    elif (orph,punct) in three:
        return u"3"
    else:
        return u"См."


def add_hash_number():
    """
    Add hash to user answer.
    :return:
    """
    hash = random.getrandbits(128)
    print "%032x" % hash
    return "%032x"%hash


# ========SEND TO TEMPlATE ===============================


def begin_dict(request):
    dictation = Dict_text.objects.get()
    link = dictation.video_link
    data = dictation.data
    print data, "Data_time"
    return render(request,'write_dict.html', {"video":link, "dictations":data})


def count_results(request):
    if request.method == 'GET':
        user_text = request.GET.get("dict_text") #what user wrote
        original_text = Dict_text.objects.get()
        result, grade, or_er, p_er, markup = diff_strings(user_text, original_text.dic_origin_text)

        user_hash = add_hash_number()
        #Save user info
        #user_info = User_text(user_id = user_hash, user_text = user_text)
        #user_info.save()

        next_date = "10.11.15"
        next_time = "20:00"
        results = {"grade": grade, "confirmation": user_hash,  "next_date": next_date, "next_time": next_time,
                   "markup": markup, "punct_errors": p_er, "ortho_errors":or_er}
        json = simplejson.dumps(results)
        return HttpResponse(json, content_type='application/json')


def send_good_result(request):
    pass

