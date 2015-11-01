#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = 'alenush'
import difflib
import re
import random
import json
import math
import datetime
from codecs import open
from itertools import izip

from django.shortcuts import render, render_to_response
from django.shortcuts import redirect
from django.http import Http404
from django.http import HttpResponse, HttpResponseRedirect
from django.template import RequestContext, loader
from django.conf import settings

from .models import Dict_text, Errors_table, Answer_user

try:
    import memcache
    from django.views.decorators.cache import cache_page
except ImportError:
    cache_page = lambda t: (lambda f: f)


def check_errors_in_db(result, dict_id): #add id_dict and text_user
    """
    Find, where !=equal
    Function takes from diff results (array with ("equal, a1,a2, b1,b2") )
    :param result:
    :return: array from (error-object, tok_begin for error tok_end)
    NOTE: ? если у пользователя , или др. пунктуация, то
    b1-b2 кусок беру - это \запятая\, проверяю, что это пунктуация и не равно тире. ?
    Добавляем ошибку и пишем - ЗДЕСЬ ОШИБКА ПУНКТАЦИОННАЯ
    """
    dictation = Dict_text.objects.get(id=dict_id)
    origin = dictation.dic_origin_text
    errors = []
    for op, a1, a2, b1, b2 in result:
        if op != "equal":
            if a2 == a1: # при вставке мы хотим иметь непустой диапазон букв со стороны orig
                a2 += 1
            for pos in xrange(a1, a2):
                er_object = Errors_table.objects.filter(id_dict=dict_id, symbol_place_in_sent=pos)
                if len(er_object) != 0:
                    object_dic = er_object.values()[0]
                    tok_begin, tok_end = object_dic["token_border_begin"], object_dic["token_border_end"]
                    errors.append((er_object, tok_begin, tok_end))
    return errors


def orig_to_user(result):
    #строим словарь orig2user, координатами в user для каждого символа orig;
    # для диапазонов в user берём крайнюю левую координату
    #переводит координату одного символа из ориг в юсер
    orig2user = {}
    for operation, a1, a2, b1, b2 in result:
        a2, b2 = a2 + 1, b2 + 1 # грязный хак: хотя difflib выдаёт диапазоны уже пригодными
        # для range, мы добавляем в каждый из них по пустой букве, чтобы каждый край delete
        # и insert получил по соответствующему символу в пару;
        # это не должно испортить отображение ощутимо, т.к. лишняя буква будет переписана более
        # точным соответствием на следующей итерации цикла
        stretch = int(math.ceil(float(a2 - a1)/(b2 - b1)))
        user_range = [pos for pos in xrange(b1, b2) for repeat in xrange(stretch)]
        print operation, a1, a2, b1, b2, "stretch", stretch, "user", user_range
        for i, j in izip(xrange(a1, a2), user_range):
            orig2user[i] = j
    return orig2user


def token_borders2user(origin2user, errors):
    """перевести границы токена в координаты user
    :return:user_er_tokens: массив. границы токенов с ошибкой у пользователя
    """
    user_er_tokens = []
    for error in errors:
        user_er_tokens.append((origin2user[error[1]], origin2user[error[2]]))
    return user_er_tokens


def fill_user_arrays(user_borders, errors, dict_text):
    """
    :param:user_borders: [token begin, token end]
    :param:errors: array with (er_object, tok_begin, tok_end))
    заводим список из кучи []; проходим по найденным диапазонам в координатах user,
    и дописываем в каждый [] по этим координатам описания ошибок, соответствующие этому диапазону
    :return:
    """
    array = [[] for n in xrange(len(dict_text) + 1)]
    for (begin, end), (error, ebegin, eend) in izip(user_borders, errors):
        for x in range(begin, end+1):
            array[x].append(error)
    return array


def error2json(error):
    """Convert error object to dictionary suitable for JSON.
    """
    return {
        "type": error[0].type_of_error,
        "comment": error[0].comments_to_error,
        "right_answer": error[0].right_answer,
    }


def collect_markup(parts_array, user_text):
    """- проходим по zip(от этого списка и текста user), и собираем словари { text, errors }
    из каждой цепочки идущих подряд букв, имеющих одинаковые ошибки
    """
    markup = []
    text_part = ""
    last_error = []
    print "Array_wth_parts", parts_array, user_text,  len(parts_array), len(user_text)
    if len(parts_array) > len(user_text): user_text += " "
    for user, error in izip(user_text, parts_array):
        if error == last_error:
            text_part += user
        else:
            print "LAST_ERROR", last_error, error
            errors = map(error2json, last_error)
            print "ANSWER", errors
            print "TEXT", text_part, user
            markup.append(dict(text=text_part, errors=errors))
            text_part = user
            last_error = error
    errors = map(error2json, last_error)
    markup.append(dict(text=text_part, errors=errors))
    print "MARK UP: ", markup
    return markup


def count_errors(markup):
    #- проходим по словарям, и считаем, сколько итоговых словарей содержат хотя бы одну орфографическую ошибку,
    # сколько хотя бы одну пунктуационную; эти числа и называем числом ошибок
    OR = 0
    PU = 0
    for dict_string_part in markup:
        for er_dic in dict_string_part["errors"]:
            if "OR" in er_dic.values():
                OR +=1
            elif "PU" in er_dic.values():
                PU += 1
    return OR, PU


def diff_strings(user, origin, dict_id):
    """
    Function aligns two strings. and make everything
    :param sent1: sentence user
    :param sent2: sentence origin
    :return: sentence with + -. - delete, + add right
    """
    dif = difflib.SequenceMatcher(unicode.isspace, origin, user)
    print u'\n'.join(u"{}: {}~{} {} / {}~{} {}".format(op, a1, a2, origin[a1:a2], b1, b2, user[b1:b2]) for op, a1, a2, b1, b2 in dif.get_opcodes())
    result = dif.get_opcodes()
    origin2user = orig_to_user(result) # dictionary of orig to user match
    errors = check_errors_in_db(result, dict_id) # array with (er_object, tok_begin, tok_end))
    print "errors", errors
    user_borders = token_borders2user(origin2user, errors) # user tokens with errors
    print "borders", user_borders
    array_with_parts = fill_user_arrays(user_borders, errors, user) #array with [[][][][Error][][Error][Error]]
    print "parts", array_with_parts
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
        return u"2"


def add_hash_number():
    """
    Add hash to user answer.
    :return:
    """
    hash = random.getrandbits(128)
    print "%032x" % hash
    return "%032x"%hash


def find_date_now():
    time_now = str(datetime.datetime.now())
    date, time =  time_now.split(" ")[0], time_now.split(" ")[1][0:5]
    year, month, day = date.split("-")[0], date.split("-")[1], date.split("-")[2]
    return time, day, month, year

def count_week_day(day, month, year):
    days = [1,2,3,4,5,6,7]
    an = (14 - month) // 12
    y = year - an
    m = month + (12*an) - 2
    result = ((7000 + (day + y + y//4 - y//100 + y//400 + (31*m) // 12)) % 7) - 1
    return days[result]


def compare_date(now_day, now_month, day, month):
    if now_month ==  month:
            day_left = int(day) - int(now_day)
            if day_left < 0: return 0
            elif day_left == 0: return 0
            else: return day_left


def find_days_left(day, month, year):
    factor = 365*year + day+ 31*(month-1)+((year-1)/4)-(3/4*((year-1)/100+1))
    return factor


def select_date_time(object_dictionary):
    print "DICTIONARY", object_dictionary
    now_time, now_day, now_month, now_year = find_date_now()
    days_left_now = find_days_left(int(now_day), int(now_month), int(now_year))
    dict_with_obj_dayleft = {}
    min_daysleft = 0
    for date_object in object_dictionary:
        print "OBJECT", date_object
        date = (object_dictionary[date_object])[0]
        year, month, day = date.split("-")[0], date.split("-")[1], date.split("-")[2]
        days_left = find_days_left(int(day), int(month), int(year))
        print "DAYS DIFFERENCE", days_left - days_left_now
        difference = days_left-days_left_now
        if min_daysleft == 0:
            if difference > 0: min_daysleft = difference
        else:
            if difference > 0:
                if difference < min_daysleft: min_daysleft = difference
        print "MIN!", min_daysleft
        dict_with_obj_dayleft[difference] = date_object
    next_date_ar = dict_with_obj_dayleft[min_daysleft]
    return next_date_ar.data, next_date_ar.id


dash_re = re.compile(r'[—––—‒–—―‒–—―⁓⸺⸻‐_~¯ˉˍ˗˜‐‑‾⁃⁻₋−∼⎯⏤─➖𐆑]')
space_re = re.compile(r'\s+(-+\s+)?')
sentence_re = re.compile(r'(?:[.][.][.]|[.]|[?]|[?][!]|[!])$')
def normalize_user_text(user_text):
    r"""
    Example:

    >>> print normalize_user_text('\r\nЯ   нёс — домой - кулёк\tконфет , вдруг навстречу мне сосед?')
    Я нёс домой кулёк конфет, вдруг навстречу мне сосед.
    """
    user_text = user_text.strip()
    user_text = dash_re.sub('-', user_text)
    user_text = space_re.sub(' ', user_text)
    user_text = sentence_re.sub('.', user_text)
    user_text = user_text.replace(" ,", ",")
    return user_text


def append_to_storage(filename, values, keys=None):
    with open(filename, 'a', encoding='utf-8') as fd:
        if keys:
            values = [values.get(key) for key in keys]
        parts = (value.replace('\t', ' ').replace('\n', '\\n') for value in values)
        fd.write('\t'.join(parts) + '\n')

# ========SEND TO TEMPlATE ===============================

@cache_page(15)
def begin_dict(request, dict_id=None):
        all_dict = Dict_text.objects.all()
        list_of_all_dict = []
        date_dictionary = {}
        for date_info in all_dict:
            string_of_date = str(date_info.data)
            date = string_of_date.split(" ")[0]
            time = string_of_date.split(" ")[1]
            date_dictionary[date_info] = [date, time]
            t1, t2 = time[0:2], time[3:5]
            week_day =  count_week_day(int(date.split("-")[2]), int(date.split("-")[1]), 2015)
            print "WEEK", week_day
            list_of_all_dict.append([int(date.split("-")[2]), int(date.split("-")[1]), week_day, int(t1), int(t2), date_info.id])
        next_date_time, next_id = select_date_time(date_dictionary)
        if dict_id: next_id = int(dict_id)
        next_date = str(next_date_time).split(" ")[0]
        next_time = str(next_date_time).split(" ")[1]
        next_day, next_month = next_date.split("-")[2], next_date.split("-")[1]
        dictation = Dict_text.objects.get(id=next_id)
        link = dictation.video_link
        dict_name = dictation.dict_name
        print "DICTATIONS", list_of_all_dict
        return render(request,'write_dict.html', {"video":link, "next_date":next_day, "next_month":next_month,
                                                  "next_time":next_time[0:5], "next_id":next_id,
                                                  "dict_name":dict_name, "dict_id":next_id,
                                                  "list_of_dict":list_of_all_dict})

def count_results(request):
    if request.method == 'GET':
        user_text = request.GET.get("dict_text")
        dict_id = request.GET.get("dict_id")
        user_text = normalize_user_text(user_text)
        original_text = Dict_text.objects.get(id=dict_id)
        result, grade, or_er, p_er, markup = diff_strings(user_text, original_text.dic_origin_text, dict_id)
        user_hash = add_hash_number()

        append_to_storage(settings.ALL_RESULTS, (user_hash, user_text, str(int(grade))))

        results = {"grade": grade, "confirmation": user_hash,
                   "markup": markup, "punct_errors": p_er, "ortho_errors":or_er}
        return HttpResponse(json.dumps(results), content_type='application/json')


def send_good_result(request):
    if request.method == 'GET':
        append_to_storage(
            settings.GOOD_RESULTS,
            request.GET,
            ("username", "age", "sex", "city", "email",
             "prof", "edu", "confirmation", "dict_id"))
        return redirect('/zhivoeslovo/success/')
        

def custom_404(request):
        return redirect('http://totaldict.ru/404')

def test(request):
    return render(request,'test_json.html')
    
    
def anons(request):
    return render(request,'anons.html')
    
def success(request):
    return render(request,'success.html')    

def selftest(request):
    import doctest
    from zh_slovo import views
    return HttpResponse(str(doctest.testmod(views)), content_type='text/plain')
