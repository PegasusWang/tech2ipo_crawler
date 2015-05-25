#!/usr/bin/env python
# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
import StringIO
import leancloud
from leancloud import Object
from leancloud import Query
from PIL import Image
import requests

CRAWL_APP_ID = 'p7brywvt5xr7prmh5kpta5ez2yc5zlza18w5za9opiex8693'
CRAWL_APP_KEY = 'itdu6xgjcigj7x4qphf8ksdvka7f4u1tt39mcpv95s9gaqls'
CRAWL_APP_MASTER_KEY = '7d2za2s63xlxjmccta5wcuufwc3se4bxcc7sjq690yn6gatv'

XPURE_APP_ID = 'ky522fknrn8mu6gxalshtr6amh7uun96lw4i9io5weti8067'
XPURE_APP_KEY = 'xjenlt7tz8kkm6f3g7o5xw7utaqcvzyz0hanxj2pajcwzkxd'
XPURE_APP_MASTER_KEY = 'kxwg6khxsoec5aox023xarizh7ex332r2hhzmevpy5xbfh1o'

CRAWL_SITE_ID = '55587250e4b066d5620c901d'
XPURE_SITE_ID = '555d759fe4b06ef0d72ce8e7'

Site = Object.extend('Site')

'''
# for crawl
leancloud.init(CRAWL_APP_ID, master_key=CRAWL_APP_MASTER_KEY)    # use master key
site_obj = Site.create_without_data(CRAWL_SITE_ID)
'''


#for xpure
leancloud.init(XPURE_APP_ID, master_key=XPURE_APP_MASTER_KEY)
site_obj = Site.create_without_data(XPURE_SITE_ID)


def get_first_image_url(html):
    """Get first image url we need."""
    soup = BeautifulSoup(html)
    img_url_all = soup.find_all('img')
    for each in img_url_all:
        url = each['src']
        try:
            img_raw = requests.get(url, stream=True, timeout=3).content    # use raw insteadof text
        except:
            continue

        img_buf = StringIO.StringIO(img_raw)    # use content don't use text for img

        try:
            im = Image.open(img_buf)
        except:
            continue
        else:
            if im.size[0] >= 600 and im.size[1] >= 300:
                print url
                img_buf.close()
                im.close()
                return url

    print 'no image to return'
    return u''


def get_Post_obj_list():
    """Get all Post obj from leancloud."""
    Post = Object.extend('Post')

    query = Query(Post)
    query.limit(1000)    # max is 1000
    length = query.count()
    cnt = length / 1000 + 1
    all_cnt = 0
    all_post_obj_list = []

    for i in range(cnt):
        query.skip(all_cnt)    # skip
        query_list = query.find()

        for each in query_list:
            all_post_obj_list.append(each)

        all_cnt += 1000

    return all_post_obj_list


def get_img_post_obj_set():
    """Get post_obj id that already have an image field from post_obj.txt"""
    img_post_obj_set = set()
    with open('post_obj.txt', 'r') as f:
        for each_line in f:
            img_post_obj_set.add(each_line.strip())
    return img_post_obj_set


def write_image_field(post_obj):
    """Write image field to leancloud."""
    html = post_obj.get('html')
    img_url = get_first_image_url(html)
    post_obj.set('image', img_url)
    post_obj.save()

    with open('post_obj.txt', 'a+') as f:
        f.write(post_obj.id + '\n')


def main():
    """Write image url to Post image field. Remember to use master_key.
       each post_obj that have image field will write to post_obj.txt.
    """
    all_post_obj_list = get_Post_obj_list()
    print 'all post_obj_list length', len(all_post_obj_list)
    image_post_obj_set = get_img_post_obj_set()
    print 'image_post_obj_set length', len(image_post_obj_set)
    for each_post_obj in all_post_obj_list:
        if each_post_obj.id in image_post_obj_set:
            print 'skip obj', each_post_obj.id
        else:
            print 'processing', each_post_obj
            write_image_field(each_post_obj)


if __name__ == '__main__':
    main()
    print 'finish'
