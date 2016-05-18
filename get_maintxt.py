#-*- coding: utf-8 -*-
__author__ = 'sohyeon'

import xml.etree.ElementTree as ET
from lxml import html
import json
import re

# file path to read, write
INFILE_PATH = "./blog_data/test_fire_blog.json"
OUTFILE_PATH = "./blog_data/get_maintxt.json"
TEST_PATH = "./blog_data/test.json"

# write a blog dictionaly to file
def write_blog(blog, file_path):
    with open(file_path, 'a') as outfile:
        json.dump(blog, outfile)
        outfile.write("/n")

# extract maintext to html
def extract_maintxt(blog,xpath):
    re
    tree= html.fromstring(blog["content"])
    a = tree.xpath(xpath)


# open json file
# put html main text as maintxt and save as json_data
with open(INFILE_PATH) as infile:
    # read file line by line
    for line in infile:
        # convert line' type to dictionaly
        blog = eval(line)

        # read blog's link and find host name
        if re.search('blog.naver|blog.me', blog["link"]):
            # set blog's host to naver and write the blog to outfile
            blog["host"] = "naver"
            extract_maintxt(blog, '//*[@id="postViewArea"]')
            write_blog(blog, OUTFILE_PATH)
        elif re.search('tistory', blog["link"]):
            # set blog's host to tistory and write the blog to outfile
            blog["host"] = "tistory"
            write_blog(blog, OUTFILE_PATH)
        else:
            # write a blog that is neither naver and tistory to testfile
            write_blog(blog, TEST_PATH)


