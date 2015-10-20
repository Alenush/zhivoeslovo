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


def diff_strings2(sent1, sent2):
    #word_punct_tokenizer = WordPunctTokenizer()
    #s1 = word_punct_tokenizer.tokenize(sent1)
    #s2 = word_punct_tokenizer.tokenize(sent2)
    s1 = sent1.split(" ")
    s2 = sent2.split(" ")
    print sent1, sent2
    d = difflib.Differ()
    diff_arr = []
    for i in zip(s1,s2):
        diff = d.compare(i[1], i[0])
        diff_arr.append((''.join(diff)).replace("  ",""))
    return diff_arr


def diff_strings(sent1, sent2):
    """
    Function aligns two strings.
    :param sent1: sentence user
    :param sent2: sentence origin
    :return: sentence with + -. - delete, + add right
    """
    d = difflib.Differ()
    diff = d.compare(sent1, sent2)
    result = (''.join(diff)).replace(u"  ", u"")
    return result


def normalize_string(word_with_error):
    """
    Collect the user errors.
    :param string_with_error:
    :return:
    """
    word = word_with_error.replace("+ ", "+"). replace("- ","-")
    print word, "replace"
    #words = string_with_error.split(" ")
    #errors = []
    #user_string = ""
    #for word in words:
    if "-" in word:
            word = word[:word.index("-")]+word[word.index("-")+2:]
            user_error_word = word.replace(u"+", u"").replace(u" ", u"")
            #errors.append(user_error_word)
            print user_error_word, "my_word"
            return user_error_word
            #user_string += user_error_word + " "
    else:
            if "+" in word:
                error = word.replace("-", "")
                #errors.append(error)
                return error

                #print error, "without -"
                #user_string += error + " "
            #else:
                #user_string += word + ' '
   # return errors #, user_string


def check_error_base(errors):
    """
    Function check if such errors are in error database.
    If yes - show type,comments and etc.
    :param errors: array with words with errors
    :return: array with dictionaries from database table. keys: error, type, comment
    """
    ar_error_infos = []
    for error in errors:
        print error, "ERROR"
        accept_error = Errors_table.objects.filter(error_variant = error.lower())
        ar_error_infos.append(accept_error.values('error_variant','type_of_error','comments_to_error'))
    return ar_error_infos


def send_error_to_db(error):
    return ( "OR", "comment about error", 5)


def check_string(result):
    """
    If too many + - then write user to rewrite a diktant.
    :param:result: sentence with +-
    :return:
    """
    result_words = [] # word or word_with_error:("OR", "com", place in sent)
    errors = []
    for word in result:
        str_dif = re.findall(u"[+-]", word)
        if len(str_dif) == 0: result_words.append(word)
        else:
            print word, "with error"
            error = normalize_string(word)[0] #send to normilize error
            errors_info = send_error_to_db(error)
            type_of_error = errors_info[0]
            result_words.append({error:errors_info})
            errors.append(type_of_error)
    grade = return_user_grade(errors)
    return result_words, grade


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
    return render(request,'write_dict.html', {"video":link})


def count_results(request):
    if request.method == 'GET':
        user_text = request.GET.get("dict_text") #what user wrote
        user_hash = add_hash_number()
        #Save user info
        #user_info = User_text(user_id = user_hash, user_text = user_text)
        #user_info.save()

        original_text = Dict_text.objects.get() #first text. Check if None!!
        result = diff_strings2(user_text, original_text.dic_origin_text) #array with текст с + и -
        answer, grade = check_string(result)
        #print answer, grade
        word_id, comment, error_type = 1, u"Чк,Чн пишется без мягкого знака!", "OR"

        results = {"grade": grade, "mistakes": [{ "word_id": word_id,"comment": comment, "error_type": error_type}],
                   "user_text":user_text, "confirmation": user_hash}
        json = simplejson.dumps(results)
        return HttpResponse(json, content_type='application/json')


def send_good_result(request):
    pass