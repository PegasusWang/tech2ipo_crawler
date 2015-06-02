#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""zaker crawler.
"""

import io
import json
import os
import shutil
import requests
from bs4 import BeautifulSoup

ZAKER_URL = 'http://iphone.myzaker.com/zaker/apps_v3.php?_appid=AndroidPhone&_version=5.14&m=1431488395'


def get_content_library_list(library_url):
    """Return list of content_library, each element is a dict, dict['sons']
       is list of channel dict.
    """
    library_json_str = requests.get(library_url).text
    library_obj = json.loads(library_json_str)
    return library_obj.get('data').get('datas')


def get_channel_list_from_library(library_dict):
    """Return all channels of a library, each channel is a dict."""
    channel_dict_list = library_dict.get('sons', None)
    return channel_dict_list


def get_articles_dict_list_from_channel(channel_dict):
    """Each channel dict has some articles, return a list of all articles'
       full_url.
    """
    api_url = channel_dict.get('api_url')
    print api_url
    try:
        json_str = requests.get(api_url, timeout=2).text
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.MissingSchema):
        return None
    try:
        obj = json.loads(json_str)
        articles_dict_list = obj.get('data').get('articles')
    except ValueError:
        return None
    return articles_dict_list


def is_non_aggregated_channel(channel_dict):
    """If author of all articles is the same, it's a non aggregated channel"""
    article_dict_list = get_articles_dict_list_from_channel(channel_dict)
    try:    # "ahtuer_name" is zaker's spell mistake
        author_list = [article_dict.get('auther_name') for article_dict in article_dict_list]
    except TypeError:
        return False
    return len(set(author_list)) == 1


def parse_full_url_page(full_url):
    """Parse page and return a article dict contains article['pk'] and article['content'].

    :param full_url: article full_url from article json list.
    :return: article dict.
    """
    try:
        json_str = requests.get(full_url, timeout=2).text
        obj = json.loads(json_str)

        json_content = obj.get('data').get('content')
        soup = BeautifulSoup(json_content)
        content = ''.join([eachp.text for eachp in soup.find_all('p')])
        article = {'pk': obj.get('data').get('pk'), 'content': content}
    except:    # skip no response page
        return None

    else:
        return article


def create_directory(dir_name):
    """Create directory of each channel."""
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def write_article_to_file(article_dict, dir_name):
    """Write article to txt file use json store in channel directory. """
    filename = article_dict.get('pk') + '.txt'
    with io.open(filename, 'w+', encoding='utf-8') as outfile:
        data = json.dumps(article_dict, ensure_ascii=False, encoding='utf-8',
                          indent=4)
        outfile.write(unicode(data))
    try:
        shutil.move(filename, dir_name)
    except shutil.Error:
        os.remove(filename)


def get_downloaded_channel_set(root_dir):
    """Get the set of channels already downloaded."""
    list_all = os.walk(unicode(root_dir, 'utf-8'))
    channel_set = set()
    for root, dirs, files in list_all:
        for each_dir in dirs:
            channel_set.add(each_dir)
    return channel_set


def main():
    cur_handle_num = 0
    downloaded_channel_set = get_downloaded_channel_set('.')
    library_dict_list = get_content_library_list(ZAKER_URL)

    for each_library_dict in library_dict_list:
        print '*****************library: %s*****************' % each_library_dict.get('title')
        channel_dict_list = get_channel_list_from_library(each_library_dict)
        if channel_dict_list is None:
            continue

        for each_channel_dict in channel_dict_list:
            print '=========%s:channel: %s===============%d' % (each_library_dict.get('title'),
                                                                each_channel_dict.get('title'),
                                                                cur_handle_num)
            cur_handle_num += 1

            print is_non_aggregated_channel(each_channel_dict)
            if not is_non_aggregated_channel(each_channel_dict):
                continue
            if each_channel_dict.get('title') in downloaded_channel_set:
                print '%s already exists' % each_channel_dict.get('title')
                continue

            article_dict_list = get_articles_dict_list_from_channel(each_channel_dict)
            channel_name = each_channel_dict.get('title')
            create_directory(channel_name)

            if article_dict_list is not None:

                for each_article_dict in article_dict_list:

                    article = parse_full_url_page(each_article_dict.get('full_url'))
                    if article is None:
                        continue
                    article['channel_name'] = channel_name
                    article['date'] = each_article_dict.get('date')
                    article['title'] = each_article_dict.get('title')
                    article['author_name'] = each_article_dict.get('auther_name')
                    article['full_url'] = each_article_dict.get('full_url')
                    article['weburl'] = each_article_dict.get('weburl')

                    print channel_name
                    print each_article_dict.get('title')

                    print each_article_dict.get('auther_name')
                    print each_article_dict.get('full_url')
                    print each_article_dict.get('date')

                    write_article_to_file(article, channel_name)


if __name__ == '__main__':
    main()
