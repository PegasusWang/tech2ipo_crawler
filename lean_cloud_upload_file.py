#!/usr/bin/env python
# -*- coding:utf-8 -*-

import leancloud
from leancloud import Object
from leancloud import ACL
import json
import os
import time

CRAWL_APP_ID = 'p7brywvt5xr7prmh5kpta5ez2yc5zlza18w5za9opiex8693'
CRAWL_APP_KEY = 'itdu6xgjcigj7x4qphf8ksdvka7f4u1tt39mcpv95s9gaqls'

XPURE_APP_ID = 'ky522fknrn8mu6gxalshtr6amh7uun96lw4i9io5weti8067'
XPURE_APP_KEY = 'xjenlt7tz8kkm6f3g7o5xw7utaqcvzyz0hanxj2pajcwzkxd'

#leancloud.init(CRAWL_APP_ID, CRAWL_APP_KEY)
leancloud.init(XPURE_APP_ID, XPURE_APP_KEY)

Site = Object.extend('Site')
CRAWL_SITE_ID = '55587250e4b066d5620c901d'
XPURE_SITE_ID = '5559a0a7e4b0f937a0db18b0'

site_obj = Site.create_without_data(XPURE_SITE_ID)


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
            self.__dict__[key]=value


class Post(Db):
    _field = (
        'author',
        'title',
        'kind',
        'createdAt',
        'updatedAt',
        'html',
        'brief',
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
    post_obj.brief = json_obj.get('brief')
    print post_obj.author
    post_obj.createdAt = from_stamp_to_createdAt(json_obj.get('time'))
    print from_stamp_to_createdAt(json_obj.get('time'))
    post_obj.html = json_obj.get('content')
    return post_obj


def init_SiteTagPost_obj(json_obj, post_obj):
    """Init SiteTagPost object."""
    siteTagPost_obj = SiteTagPost()
    siteTagPost_obj.tag_list = json_obj.get('tag')
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
        filename = os.path.basename(eachfile)
        local_file = open(eachfile, 'r')
        json_obj = json.load(local_file)
        post_obj = init_Post_obj(json_obj)
        siteTagPost_obj = init_SiteTagPost_obj(json_obj, post_obj)

        try:
            time.sleep(1)
            post_obj.save()
            siteTagPost_obj.save()
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

    #new_file_set = all_file_set - old_file_set
    new_file_set = get_new_file_set()
    print new_file_set

    upload_file(new_file_set)


if __name__ == '__main__':
    main()
