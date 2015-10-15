# -*- coding: utf-8 -*-
#__author__ = 'alenush'
from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from .models import Dict_text, Errors_in_text, Annotate_text
import difflib, re
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
    for i in zip(s1,s2):
        diff =  d.compare(i[1], i[0])
        print (''.join(diff)).replace("  ","")


def diff_strings(sent1, sent2):
    """
    Function aligns two strings.
    :param sent1: sentence original
    :param sent2: sentence from user
    :return: sentence with + -. - delete, + add right
    """
    d = difflib.Differ()
    diff = d.compare(sent1, sent2)
    result = (''.join(diff)).replace(u"  ", u"")
    return result


def normalize_string(string_with_error):
    """
    Collect the user errors.
    :param string_with_error:
    :return:
    """
    string_with_error = string_with_error.replace("+ ", "+"). replace("- ","-")
    print string_with_error
    words = string_with_error.split(" ")
    errors = []
    user_string = ""
    for word in words:
        if "+" in word:
            word = word[:word.index("+")]+word[word.index("+")+2:]
            user_error_word = word.replace(u"-", u"").replace(u" ", u"")
            errors.append(user_error_word)
            print user_error_word
            user_string += user_error_word + " "
        else:
            if "-" in word:
                error = word.replace("-", "")
                errors.append(error)
                user_string += error + " "
            else:
                user_string += word + ' '
    return errors, user_string


def check_error_base(errors):
    """
    Function check if such errors are in error database.
    If yes - show type,commetns and etc.
    :param errors: array with words with errors
    :return: array with dictionaries from database table. keys: error, type, comment
    """
    ar_error_infos = []
    for error in errors:
        print error, "ERROR"
        accept_error = Errors_in_text.objects.filter(error_variant = error.lower())
        ar_error_infos.append(accept_error.values('error_variant','type_of_error','comments_to_error'))
    return ar_error_infos


def check_string(result):
    """
    If too many + - then write user to rewrite a dictant.
    :param:result: sentence with +-
    :return:
    """
    str_dif = re.findall("[+-]", result)
    if len(str_dif) >= len(result)/4:
        return "User wrote smth strange!"
    elif len(str_dif) == 0:
        return "Everything is ok!"
    else:
        errors, user_string = normalize_string(result)
        dic_with_error_info = check_error_base(errors)
        return (user_string, errors, dic_with_error_info)


def take_mark(errors):
    """
    Function takes an array of types of errors and returns mark
    :param errors: errors = ["PU", "OR", "OR", "OR", "PU", "OR"]
    :return:mark = 5
    """
    mark = 2
    count = Counter(errors)
    p = count["PU"]
    o = count["OR"]
    five = [(0,0), (0,1)]
    four = [(0,2),(0,3),(0,4),(1,0),(1,1), (1,2), (1,3), (2,0), (2,1), (2,2)]
    three = [(0,5),(0,6),(0,7),(0,8),(1,4),(1,5), (1,6), (1,7), (2,3), (2,4), (2,5),(2,6),
        (3,0),(3,1),(3,2),(3,3),(3,4),(3,5),(4,0),(4,1),(4,2),(4,3),(4,4)]
    if (o,p) in five:
        mark = 5
    elif (o,p) in four:
        mark = 4
    elif (o,p) in three:
        mark = 3
    return mark


# ========SEND TO TEMPlATE ===============================

def choose_dict(request):
    return render(request,'zhivoeslovo.html')

def begin_dict(request):
    return render(request,'write_dict.html')


def count_results(request):
    if request.method == 'POST':
        #diff_strings2(sent1=u"Речка бежала в великих молчаливых необозримых лесах, и от их однообразия казалось, что путь будет длиться вечно.", sent2=u"Речка бижала в великих, молчаливых, необозримых лесах, и от их однообразия казалось что путь будет длиться вечно.")
        user_text = request.POST.get("dict_text") #what user wrote
        original_text = Dict_text.objects.get() #first text. Check if None!!
        result = diff_strings(user_text, original_text.dic_origin_text)
        answer = check_string(result)
        if isinstance(answer, tuple):
            send_user, errors, error_dic = answer[0], answer[1], answer[2]
            return render(request,'dic_results.html', {"answer": send_user, "errors": errors, "error_info":error_dic})
        else:
            return render(request,'dic_results.html', {"answer": answer})