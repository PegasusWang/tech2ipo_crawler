#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import codecs
import HTMLParser
import leancloud
from leancloud import Object
from leancloud import ACL
import json
import os
import re
import time

CRAWL_APP_ID = 'p7brywvt5xr7prmh5kpta5ez2yc5zlza18w5za9opiex8693'
CRAWL_APP_KEY = 'itdu6xgjcigj7x4qphf8ksdvka7f4u1tt39mcpv95s9gaqls'
CRAWL_APP_MASTER_KEY = '7d2za2s63xlxjmccta5wcuufwc3se4bxcc7sjq690yn6gatv'

XPURE_APP_ID = 'ky522fknrn8mu6gxalshtr6amh7uun96lw4i9io5weti8067'
XPURE_APP_KEY = 'xjenlt7tz8kkm6f3g7o5xw7utaqcvzyz0hanxj2pajcwzkxd'
XPURE_APP_MASTER_KEY = 'kxwg6khxsoec5aox023xarizh7ex332r2hhzmevpy5xbfh1o'

CRAWL_SITE_ID = '55587250e4b066d5620c901d'
XPURE_SITE_ID = '555d759fe4b06ef0d72ce8e7'

Site = Object.extend('Site')

"""
# for crawl
leancloud.init(CRAWL_APP_ID, master_key=CRAWL_APP_MASTER_KEY)    # use master key
site_obj = Site.create_without_data(CRAWL_SITE_ID)
"""

#for xpure
leancloud.init(XPURE_APP_ID, master_key=XPURE_APP_MASTER_KEY)
site_obj = Site.create_without_data(XPURE_SITE_ID)


tag_dict = {u'新闻': u'每日资讯', u'观点': u'深度观点',  u'人物': u'人物特写',
            u'公司': u'公司行业', u'产品': u'产品快报', u'TechReview': u'产品评测'}


class Db(Object):
    def __getattr__(self, name):
        if name in self._field:
            return self.get(name)
        else:
            return getattr(self._field, name)

    def __setattr__(self, key, value):
        if key in self._field:
            self.set(key, value)
        else:
            self.__dict__[key] = value


class Post(Db):
    _field = (
        'author',
        'title',
        'kind',
        'createdAt',
        'updatedAt',
        'html',
        'brief',
        'ID',
    )


class SiteTagPost(Db):
    _field = (
        'tag_list',
        'site',
        'post',
    )


def get_all_file_set(root_dir):
    """Get all file from root_dir ./article"""
    article_set = set()
    list_dirs = os.walk(unicode(root_dir, 'utf-8'))
    for root, dirs, files in list_dirs:
        for eachfile in files:
            if u'.txt' in eachfile:
                article_set.add(os.path.join(root, eachfile))
    return article_set


def get_uploaded_file_set():
    """Get uploaded file stored in uploaded.txt in this folder."""
    old_file_set = set()
    with open('uploaded.txt', 'r+') as f:
        for eachfile in f:
            old_file_set.add(eachfile.strip())
    return old_file_set


def get_new_file_set():
    """Get file name set need to upload to leancloud."""
    new_file_set = get_all_file_set('./article') - get_uploaded_file_set()
    new_file_set = sorted(new_file_set, key=lambda s: int(s[10:].split('.')[0]))
    return new_file_set


def from_stamp_to_createdAt(time_stamp):
    """Change time stamp to date."""
    time_array = time.localtime(time_stamp)
    return time.strftime('%Y-%m-%d %H:%M:%S', time_array)


def get_remove_ad(html_text):
    """Remove advertisement of content."""
    soup = BeautifulSoup(html_text)
    all_tag = soup.find_all('p')
    length = len(all_tag)
    if u'本文' in all_tag[length-3].text or u'来源' in all_tag[length-3].text:
        all_tag[length-3].decompose()    # delete article source
    all_tag[length-2].decompose()    # delete advertisement
    return unicode(soup.section)


def get_tag_and_removed_tag(html_text):
    """Remove tag."""
    html_text = get_remove_ad(html_text)
    soup = BeautifulSoup(html_text)
    # delete span font style
    span_tag_all = soup.find_all('span')
    for each in span_tag_all:
        del each['style']

    try:
        articleTag_tag = soup.find(class_='articleTag')
        articleTag_tag.extract()
    except:
        pass

    re_comment = re.compile('<!--[^>]*-->')
    s = unicode(soup.section)
    s = re_comment.sub(u'', s)
    return s.replace(u'\n\n', u'')


def get_need_tag_set():
    """Get tag from"""
    all_tag_set = set()
    with codecs.open('tag.txt', 'r', encoding='utf-8') as f:
        for each_line in f:
            all_tag_set.add(each_line.split()[0])
    return all_tag_set


def get_tag_list(html_text):
    """Return tag list of each article."""
    html_text = get_remove_ad(html_text)
    soup = BeautifulSoup(html_text)
    articleTag_tag = soup.find(class_='articleTag')
    articleTag_list = []
    try:
        for each_tag in articleTag_tag.find_next('p').find_all('a'):
            articleTag_list.append(each_tag.text)
    except:
        return []
    return articleTag_list


def init_Post_obj(json_obj):
    """Init Post() object."""
    post_obj = Post()

    post_acl = ACL()
    post_acl.set_public_write_access(False)
    post_acl.set_public_read_access(True)
    post_obj.set_acl(post_acl)

    post_obj.kind = 10
    post_obj.title = json_obj.get('title')
    post_obj.author = json_obj.get('author')
    post_obj.ID = long(json_obj.get('id'))    # use number not string

    brief_text = json_obj.get('brief')
    if brief_text is None:
        post_obj.brief = u''

    else:
        post_obj.brief = HTMLParser.HTMLParser().unescape(brief_text)

    print post_obj.author
    post_obj.createdAt = from_stamp_to_createdAt(json_obj.get('time'))
    print from_stamp_to_createdAt(json_obj.get('time'))
    #post_obj.html = get_remove_ad(json_obj.get('content'))  # remove advertisement
    post_obj.html = get_tag_and_removed_tag(json_obj.get('content'))  # remove advertisement
    return post_obj

all_need_tag = get_need_tag_set()

def init_SiteTagPost_obj(json_obj, post_obj):
    """Init SiteTagPost object."""
    siteTagPost_obj = SiteTagPost()
    article_tag_list = get_tag_list(json_obj.get('content'))
    tmp_tag_list = []
    tmp_tag_list.append(tag_dict[json_obj.get('tag')])    # add tag_dict
    tmp_tag_list += article_tag_list
    siteTagPost_obj.tag_list = []
    for each_tag in tmp_tag_list:
        if each_tag in all_need_tag:
            siteTagPost_obj.tag_list.append(each_tag)
    print json_obj.get('tag')
    siteTagPost_obj.site = site_obj
    siteTagPost_obj.post = post_obj
    return siteTagPost_obj


def upload_file(file_set):
    """Upload files to leancloud and write uploaded file's name
    to uploaded.txt
    """
    print len(file_set)
    for eachfile in file_set:
        #raw_input()
        filename = os.path.basename(eachfile)
        print 'processing file', filename
        local_file = open(eachfile, 'r')
        json_obj = json.load(local_file)
        post_obj = init_Post_obj(json_obj)
        siteTagPost_obj = init_SiteTagPost_obj(json_obj, post_obj)

        try:
            post_obj.save()
            siteTagPost_obj.save()
            time.sleep(0.7)
        except:
            time.sleep(1)
            continue
        finally:
            print '%s is uploaded' % filename
            local_file.close()
            with open('uploaded.txt', 'a+') as f:
                f.write(eachfile+'\n')
            local_file.close()


def main():
    all_file_set = get_all_file_set('./article')
    print len(all_file_set)

    old_file_set = get_uploaded_file_set()
    print len(old_file_set)

    new_file_set = get_new_file_set()
    print new_file_set

    upload_file(new_file_set)


if __name__ == '__main__':
    main()
