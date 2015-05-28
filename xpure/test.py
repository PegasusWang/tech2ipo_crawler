#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import os
import io
import HTMLParser
from lean_cloud_upload_file import *


def get_all_files_list(root_dir):
    list_all = os.walk(unicode(root_dir, 'utf-8'))
    files_list = []
    for root, dirs, files in list_all:
        for each_file in files:
            if '.txt' in each_file:
                files_list.append(os.path.join(root, each_file))
    return files_list


def escape_brief(each_file):
        print 'processing...', each_file
        f = open(each_file, 'r')
        try:
            article = json.load(f)
        except:
            f.close()
            return
        html_text = article['content']
        get_tag_and_removed_tag(html_text)


        f.close()
        """
        with io.open(each_file, 'w+', encoding='utf-8') as outfile:
            data = json.dumps(article, ensure_ascii=False, encoding='utf-8', indent=4)
            outfile.write(unicode(data))
        """


def main():
    files_list = get_all_files_list('./article')
    print len(files_list)
    for each_file in files_list:
       # raw_input()
        if '61520' in each_file:
            escape_brief(each_file)
            break
    print 'finish'


main()