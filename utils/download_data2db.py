#!/usr/bin/env python
# -*- coding: utf-8 -*-
#__author__ = 'alenush'
#from django.db import connection
#from models import Errors_table
import sqlite3
import os, codecs
from nltk.tokenize import WordPunctTokenizer

db_path = "../db.sqlite3"
path = '/home/alenush/Рабочий стол/texts/'

origin_dict = "."

def write_in_db(id, place_in_sent, token_begin, token_end, type, comment, right):
    #print id, place_in_sent, token_begin, token_end, type, comment, right
    #er_string = Errors_table.objects.create(id_dict=id, symbol_place_in_sent=place_in_sent,
    #                             token_border_begin=token_begin, token_border_end=token_end,
    #                             comments_to_error=comment, type_of_error=type,
    #                             right_answer=right)
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(
        'INSERT INTO zh_slovo_errors_table (id_dict, symbol_place_in_sent, token_border_begin,'
        'token_border_end, comments_to_error, type_of_error, right_answer)'
        'VALUES (?, ?, ?, ?, ?, ?, ?)',
        (id, place_in_sent, token_begin, token_end, comment, type, right)
    )
    connection.commit()


def convert_coord_2dbformat(markup, token_origin, id):
    word_number = int(markup[0])
    er_begin, er_end = markup[1], markup[2]
    token = token_origin[word_number]
    print token[0]+int(er_begin), token[0], token[1]-1, markup[3], markup[5], markup[4]
    write_in_db(id, token[0]+int(er_begin), token[0], token[1]-1, markup[3], markup[5], markup[4])


def change_db2(text, origin_dict, id):
    print origin_dict
    tokens_ar = []
    word_punct_tokenizer = WordPunctTokenizer()
    for token in word_punct_tokenizer.span_tokenize(origin_dict):
        tokens_ar.append(token)
    for line in text.split("\n"):
        markup_error_line = line.split(';')
        print "MARKUP", markup_error_line
        convert_coord_2dbformat(markup_error_line, tokens_ar, id)


for filename in os.listdir(path):
    print filename
    txt = codecs.open(path+filename, 'r', 'utf8')
    text = txt.read()
    id = 1
    change_db2(text, origin_dict, id)
