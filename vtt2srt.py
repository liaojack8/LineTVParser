#!/usr/bin/python
# Reference: Jansen A. Simanullang / Jeison Cardoso
# MOD by liaojack8

import os
import re
import sys
from stat import *

def convert_content(file_contents):
    replacement = re.sub(r"(\d\d:\d\d:\d\d).(\d\d\d) --> (\d\d:\d\d:\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n", r"\1,\2 --> \3,\4\n", file_contents)
    replacement = re.sub(r"(\d\d:\d\d).(\d\d\d) --> (\d\d:\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n", r"\1,\2 --> \3,\4\n", replacement)
    replacement = re.sub(r"(\d\d).(\d\d\d) --> (\d\d).(\d\d\d)(?:[ \-\w]+:[\w\%\d:]+)*\n", r"\1,\2 --> \3,\4\n", replacement)
    replacement = re.sub(r"WEBVTT\n", "", replacement)
    replacement = re.sub(r"Kind:[ \-\w]+\n", "", replacement)
    replacement = re.sub(r"Language:[ \-\w]+\n", "", replacement)
    replacement = re.sub(r"<c[.\w\d]*>", "", replacement)
    replacement = re.sub(r"</c>", "", replacement)
    replacement = re.sub(r"<\d\d:\d\d:\d\d.\d\d\d>", "", replacement)
    replacement = re.sub(r"::[\-\w]+\([\-.\w\d]+\)[ ]*{[.,:;\(\) \-\w\d]+\n }\n", "", replacement)
    replacement = re.sub(r"Style:\n##\n", "", replacement)
    return replacement

def file_create(str_name_file, str_data):
    try:
        f = open(str_name_file, "w", encoding='UTF-8')
        f.writelines(str(str_data))
        f.close()
    except IOError:
        str_name_file = str_name_file.split(os.sep)[-1]
        f = open(str_name_file, "w")
        f.writelines(str(str_data))
        f.close()

def read_text_file(str_name_file):
    f = open(str_name_file, mode="r", encoding='UTF-8')
    return f.read()

def vtt_to_srt(str_name_file):
    file_contents: str = read_text_file(str_name_file)
    str_data: str = ""
    str_data = str_data + convert_content(file_contents)
    str_name_file: str = str_name_file.replace(".vtt", ".srt")
    file_create(str_name_file, str_data)