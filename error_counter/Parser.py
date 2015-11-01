#-*- coding: utf-8 -*-
__author__ = 'rover'

import codecs
import locale
import sys
import re

# Wrap sys.stdout into a StreamWriter to allow writing unicode.
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


PUNCT = ['.', ',', ';', '!', '?']
SEP = [" ", "\t"]
MARK_START = ["[", "{"]
MARK_END = ["]", "}"]
MARK_TYPE = {"}": "PU", "]": "OR"}
FIELD_SEP = "|"

class Error:
    def __init__(self, start = 0):
        self.errors = []
        self.start = start
        self.end = 0
        self.rules = []
        self.text = ""
        self.type = ""

    def parse(self, raw):
        position = self.start
        mark_count = 0
        error = None
        content = ""
        error_raw = ""
        for char in raw:
            if error:
                error_raw += char
            if char in MARK_START:
                if mark_count == 0:
                    error = Error()
                    error.start = position
                mark_count += 1
            elif char in MARK_END:
                mark_count -= 1
                if mark_count == 0:
                    error.type = MARK_TYPE[char]
                    error.end = position - 1
                    error.parse(error_raw[:-1])
                    self.errors.append(error)
                    error = None
                    error_raw = ""
            elif char.isalpha() or char in SEP or char in PUNCT:
                # self.text += char
                position += 1

            if mark_count == 0 and not char in MARK_START and not char in MARK_END:
                content += char

        self.rules = content.split("/")
        self.text = self.rules.pop(0)

    def get_list(self):
        list = []
        for error in self.errors:
            list.extend(error.get_list())
        list.append(self)
        return list


class Token:
    def __init__(self, raw = ""):
        self.errors = []
        self.text = ""
        self.raw = raw
        if raw != "":
            self.parse(raw)

    def parse(self, raw):
        for char in raw:
            if char.isalpha() or char in SEP or char in PUNCT:
                self.text += char
        error = Error()
        error.parse(raw)
        self.errors = error.errors

    def get_errors(self):
        list = []
        for error in self.errors:
            list.extend(error.get_list())
        return  list

class Parser:
    word_regex = u"([А-я]+|\[(\[[А-я]+(/\d+)+\]|[А-я]*(/\d+)*)+\])+"
    sep_regex = u"(?P<sep>\s+|\[\s+(?P<sep_rules>/\d+)+\])+"
    punct_regex = u"(\s*([.,!?]|\{[.,!?](/\d+)+\})\s*)"
    regex = re.compile("|".join([word_regex, punct_regex, sep_regex]), re.UNICODE)

    def __init__(self):
        self.tokens = []

    def parse(self, text):
        iter = Parser.regex.finditer(text)
        prev = ""
        try:
            while True:
                mo = iter.next()
                if not mo.group("sep") is None and prev != "":
                    if not mo.group("sep_rules") is None:
                        self.tokens.append(Token(prev + mo.group().strip()))
                    else:
                        self.tokens.append(Token(prev + "{ /0}"))
                    prev = ""
                elif prev != "":
                    self.tokens.append(Token(prev))
                    prev = mo.group().strip()
                else:
                    prev = mo.group().strip()
        except StopIteration:
            pass
        if prev != "":
            self.tokens.append(Token(prev))


if __name__ == "__main__":

    file_in = codecs.open("input.txt", "rb", "utf-8")

    if not file_in:
        exit(0)

    parts = []
    lines = []
    for line in file_in:
        if line.startswith('#'):
            continue
        if line.strip() == "":
            if len(lines) > 0:
                parts.append(lines)
            lines = []
            continue
        lines.append(line.strip())
    if len(lines) > 0:
        parts.append(lines)

    file_in.close()

    text = parts[0][0]
    rules_or = parts[1]
    rules_pu = parts[2]
    rules_pu.insert(0, u"На этом месте не может быть знаков препинания")

    parser = Parser()
    parser.parse(text)

    for num, tok in enumerate(parser.tokens):
        # print num, tok.raw
        for error in tok.get_errors():
            for rule in error.rules:
                rule_txt = ""
                if error.type == "OR":
                    rule_txt = rules_or[int(rule) - 1]
                else:
                    rule_txt = rules_pu[int(rule)]
                print FIELD_SEP.join([str(num), str(error.start), str(error.end), error.type, tok.text.strip(), rule_txt])
