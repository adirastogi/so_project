#!/usr/bin/env python
import sys
import csv
from bs4 import BeautifulSoup,NavigableString

#Removes HTML tags. HTML taglist contains tags to remove. code tag is removed automatically"

def cleanup_html(text):
    taglist2 = ['p','a','pre','strong','blockquote']
    taglist1 = ['code']
    t1 = remove_html_tag_content(text,taglist1);
    t2 = strip_tags(text,taglist2);
    t2 = t2[12:]
    t2 = t2[:-14]
    return t2;

def filter_common_words(text, stop_words):
    if isinstance(text, unicode):
        text = text.encode('utf8')
    # the following symbols will be replaced with white space
    symbols = [',','.',':',';','+','=','"','/']
    for symbol in symbols:
        text = text.replace(symbol,' ')
    output = ""
    for word in text.split():
        if not word.lower() in stop_words:
            output += word + ' '
    return output

def remove_html_tag_content(text,tags_to_filter):
    # the following tags and their content will be removed, for example <a> tag will remove any html links
    if isinstance(text, unicode):
        text = text.encode('utf8')
    soup = BeautifulSoup(text)
    for tag_to_filter in tags_to_filter:
        text_to_remove = soup.findAll(tag_to_filter)
        [tag.extract() for tag in text_to_remove]
    return soup.get_text()


def strip_tags(html, invalid_tags):
    soup = BeautifulSoup(html)
    for tag in soup.findAll(True):
        if tag.name in invalid_tags:
            s = ""
            for c in tag.contents:
                if not isinstance(c, NavigableString):
                    c = strip_tags(unicode(c), invalid_tags)
                s += unicode(c)
            tag.replaceWith(s)
    return soup

