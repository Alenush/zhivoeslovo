#-*- coding: utf-8 -*-
import codecs
import re

word_cnt = 0
letter_cnt = 0
err_cnt = 0
rules = []


def parse_word(word):
    global err_cnt
    global letter_cnt
    global word_cnt
    global rules_or
    global rules_pu
    types = {"}": "PU", "]": "OR"}
    letter_cnt = 0
    ed = ""
    err_start = 0
    for ch in word:
        if ch == "[" or ch == "{":
            if err_cnt == 0:
                err_start = letter_cnt
            err_cnt += 1
        elif ch == "]" or ch == "}":
            err_cnt -= 1
            edp = ed.split("/")
            for p in edp[1:]:
                rule = ""
                if ch == "]":
                    rule = rules_or[int(p) - 1]
                else:
                    rule = rules_pu[int(p) - 1]
                rule = rule.rstrip()
                if err_cnt == 0:
                    print "|".join([str(word_cnt), str(err_start), str(letter_cnt + len(edp[0]) - 1), types[ch], rule, p, ed, word])
                else:
                    print "|".join([str(word_cnt), str(letter_cnt), str(letter_cnt + len(edp[0]) - 1), types[ch], rule, p, ed, word])
            letter_cnt += len(edp[0])
            ed = ""

        elif err_cnt == 0:
            letter_cnt += 1
        else:
            ed += ch
    if err_cnt == 0:
        word_cnt += 1

text = codecs.open("text.txt", "rb", "utf-8")
file_or = codecs.open("rules_or.txt", "rb", "utf-8")
file_pu = codecs.open("rules_pu.txt", "rb", "utf-8")

if not text or not file_or or not file_pu:
    exit(0)

rules_or = file_or.readlines()
file_or.close()
rules_pu = file_pu.readlines()
file_pu.close()

for line in text:
    for word in line.split():
        parse_word(word)

text.close()
