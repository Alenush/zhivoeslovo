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
    заводим список из кучи []; проходим по найденным диапазонам в координатах user,
    и дописываем в каждый [] по этим координатам описания ошибок, соответствующие этому диапазону
    :return:
    """
    array = [[]]*10



#- проходим по zip(от этого списка и текста user), и собираем словари { text, errors }
# из каждой цепочки идущих подряд букв, имеющих одинаковые ошибки

#- проходим по словарям, и считаем, сколько итоговых словарей содержат хотя бы одну орфографическую ошибку,
# сколько хотя бы одну пунктуационную; эти числа и называем числом ошибок


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
    fill_user_arrays(user_borders, errors)
    return result


def return_user_grade(errors):
    """
    Function takes an array of types of errors and returns mark
    :param errors: errors = ["PU", "OR", "OR", "OR", "PU", "OR"]
    :return: string with user grade or См.
    """
    count = Counter(errors)
    p = count["PU"]
    o = count["OR"]
    five = [(0,0)]
    four = [(0,1), (0,2),(0,3),(0,4),(1,0),(1,1), (1,2), (1,3), (2,0), (2,1), (2,2)]
    three = [(0,5),(0,6),(0,7),(0,8),(1,4),(1,5), (1,6), (1,7), (2,3), (2,4), (2,5),(2,6),
        (3,0),(3,1),(3,2),(3,3),(3,4),(3,5),(4,0),(4,1),(4,2),(4,3),(4,4)]
    if (o,p) in five:
        return u"5"
    elif (o,p) in four:
        return u"4"
    elif (o,p) in three:
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
        result = diff_strings(user_text, original_text.dic_origin_text)

        user_hash = add_hash_number()
        #Save user info
        #user_info = User_text(user_id = user_hash, user_text = user_text)
        #user_info.save()

        markup = []
        next_date = "10.11.15"
        next_time = "20:00"
        p_er = 1
        or_er = 1
        grade = 5
        results = {"grade": grade, "confirmation": user_hash,  "next_date": next_date, "next_time": next_time,
                   "markup": markup, "punct_errors": p_er, "ortho_errors":or_er}
        json = simplejson.dumps(results)
        return HttpResponse(json, content_type='application/json')


def send_good_result(request):
    pass

