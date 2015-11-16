#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = 'alenush'
import difflib
import re
import random
import json
import math
import datetime
from uuid import uuid4
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
            array[x] += error
    return array


def error2json(error):
    """Convert error object to dictionary suitable for JSON.
    """
    return {
        "type": error.type_of_error,
        "comment": error.comments_to_error,
        "right_answer": error.right_answer,
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
    dif = difflib.SequenceMatcher(unicode.isspace, origin, user, autojunk=False)
    print u'\n'.join(u"{}: {}~{} {} / {}~{} {}".format(op, a1, a2, origin[a1:a2], b1, b2, user[b1:b2]) for op, a1, a2, b1, b2 in dif.get_opcodes())
    result = dif.get_opcodes()
    origin2user = orig_to_user(result) # dictionary of orig to user match
    errors = check_errors_in_db(result, dict_id) # array with (er_object, tok_begin, tok_end))
    print "errors", errors
    user_borders = token_borders2user(origin2user, errors) # user tokens with errors
    print "borders", user_borders
    array_with_parts = fill_user_arrays(user_borders, errors, user) #array with [[][][][Error][][Error][Error]]
    print "parts", map(len, array_with_parts)
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


def active_future_dictation(all_dictations):
    now = datetime.datetime.now()
    duration = datetime.timedelta(minutes=settings.DICT_DURATION)
    active = future = None
    for dictation in all_dictations:
        date = dictation.data.replace(tzinfo=None)
        if date < now < date + duration:
            active = dictation
        if now < date:
            if not future or future.data > dictation.data:
                future = dictation
    return active, future


def dict_schedule(all_dictations):
    return [
        [d.data.day, d.data.month, d.data.isoweekday(),
        d.data.hour, d.data.minute, d.id]
        for d in all_dictations
    ]

dash_re = re.compile(r'[—––—‒–—―‒–—―⁓⸺⸻‐_~¯ˉˍ˗˜‐‑‾⁃⁻₋−∼⎯⏤─➖𐆑]+')
space_re = re.compile(r'\s+(\s+)?')
sentence_re = re.compile(r'(?:[.][.][.]|[.]|[?]|[?][!]|[!])$')
def normalize_user_text(user_text):
    r"""
    Example:

    >>> print normalize_user_text('\r\nЯ   нёс — домой - кулёк\tконфет , вдруг навстречу мне сосед?')
    Я нёс домой кулёк конфет, вдруг навстречу мне сосед.
    """
    user_text = user_text.strip()
    #user_text = dash_re.sub('-', user_text)# 8 dikt
    #user_text = user_text.replace(' -',':') for 8 dikt it is bad
    user_text = user_text.replace(',-',', -')# for 8 dikt
    user_text = user_text.replace(';',',')
    #user_text = user_text.replace(u'ё',u'е')
    user_text = space_re.sub(' ', user_text)
    user_text = sentence_re.sub('.', user_text)
    user_text = user_text.replace(" ,", ",")
    return user_text


def append_to_storage(filename, values, keys=None):
    now = str(datetime.datetime.now())
    with open(filename, 'a', encoding='utf-8') as fd:
        if keys:
            values = [values.get(key) for key in keys]
        parts = (value.replace('\t', ' ').replace('\n', '\\n') for value in values)
        fd.write(now + '\t' + '\t'.join(parts) + '\n')

# ========SEND TO TEMPlATE ===============================

@cache_page(15)
def begin_dict(request, dict_id=None):
    request.session.setdefault('uid', str(uuid4()))
    all_dictations = Dict_text.objects.all()
    active, future = active_future_dictation(all_dictations)
    if future == None: #if no future diktation!
        return render(request,'the_end.html')
    if dict_id:
        active = Dict_text.objects.get(id=int(dict_id))
    return write_dict(request, active, future, all_dictations)


def write_dict(request, active, future, all_dictations):
    return render(request, 'write_dict.html', dict(
        next_date=future and future.data.day,
        next_month=future and future.data.month,
        next_time=future and '{:%H:%M}'.format(future.data),
        next_id=future and future.id,
        video=active.video_link,
        dict_name=active.dict_name,
        dict_id=active.id,
        list_of_dict=dict_schedule(all_dictations),
    ))


def count_results(request):
    if request.method == 'GET':
        user_text = request.GET.get("dict_text")
        dict_id = request.GET.get("dict_id")
        user_text = normalize_user_text(user_text)
        original_text = Dict_text.objects.get(id=dict_id)
        result, grade, or_er, p_er, markup = diff_strings(user_text, original_text.dic_origin_text, dict_id)
        user_hash = str(uuid4())

        append_to_storage(settings.ALL_RESULTS, (user_hash, user_text, str(int(grade)), request.session.get('uid', '')))

        results = {"grade": grade, "confirmation": user_hash,
                   "markup": markup, "punct_errors": p_er, "ortho_errors":or_er}
        return HttpResponse(json.dumps(results), content_type='application/json')


def send_good_result(request):
    if request.method == 'GET':
        data = dict(request.GET.items())
        data['uid'] = request.session.get('uid', '')
        append_to_storage(
            settings.GOOD_RESULTS,
            data,
            ("username", "age", "sex", "city", "email",
             "prof", "edu", "confirmation", "dict_id", "uid"))
        return redirect('/zhivoeslovo/success/')
        

def custom_404(request):
        return redirect('http://totaldict.ru/404')


def test(request):
    return render(request,'test_json.html')


@cache_page(15)
def anons(request):
    request.session.setdefault('uid', str(uuid4()))
    all_dictations = Dict_text.objects.all()
    active, future = active_future_dictation(all_dictations)
    print "WTF", active, future
    if active:
        return write_dict(request, active, future, all_dictations)
    else:
        return render(request,'anons.html', dict(link=future and future.otschet))


def success(request):
    return render(request,'success.html')    


def selftest(request):
    import doctest
    from zh_slovo import views
    return HttpResponse(str(doctest.testmod(views)), content_type='text/plain')
