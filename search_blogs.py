# -*- coding: utf-8 -*-
__author__ = 'sohyeon'

import requests
import bs4
import re
import json
import urllib
import urllib.request
from lxml import html
from datetime import datetime, timedelta, date

# search date option
START_DATE = date(2015, 9, 16)
END_DATE = date(2016, 1, 31)

# query
QUERY_WORDS = '화재 -삼성화재 -동부화재 -메리츠화재'


# date range function
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days)):
        yield start_date + timedelta(n)


# make url with date, query option
def make_url(date):
    target_date = date.strftime("%Y%m%d")
    next_date = (date + timedelta(1)).strftime("%Y%m%d")
    query = urllib.parse.quote_plus(QUERY_WORDS)
    url = 'http://search.daum.net/search?w=blog&nil_search=btn&DA=NTB&enc=utf8' + '&sd=' + target_date + '&ed=' + next_date + '&q=' + query
    return url


# get page html
def get_html(url):
    # requests
    data = requests.get(url)
    # get html
    html = bs4.BeautifulSoup(data.text)
    return html


# calculate the number of pages
# one page contains 10 blogs
# (ex)13 blogs need 2 pages
def page_count(html):
    total_count = html.find("span", attrs={'id': 'resultCntArea'})
    total_count = [int(s) for s in re.findall('\d+', total_count.text)][2]
    pages = total_count / 10 + 1
    return pages


# get blog list
def get_blog_list(html):
    blogs = html.findAll("div", attrs={'id': 'blogColl'})[0]
    blogs = blogs.findAll("div", attrs={'class': 'cont_inner'})
    return blogs


# read blog's link a
def get_host(link):
    # blog's host is naver
    if re.search('blog.naver|blog.me', link):
        return "naver"
    # blog's host is tistory
    elif re.search('tistory', link):
        return "tistory"
    # blog's host is neither naver no
    else:
        return "other"


# reshape date to "%Y-%m-%d" format
def reshape_date(date):
    # ~시간전, ~분전, ~초전 시간 고치기
    if re.search('전', date):
        if re.search('시간', date):
            date = datetime.now() - timedelta(hours=int(date.split("시간")[0]))
            date = date.strftime("%Y-%m-%d")
        elif re.search('분', date):
            date = datetime.now() - timedelta(minutes=int(date.split("분")[0]))
            date = date.strftime("%Y-%m-%d")
        elif re.search('초', date):
            date = datetime.now() - timedelta(seconds=int(date.split("초")[0]))
            date = date.strftime("%Y-%m-%d")
    else:
        date = datetime.strptime(date, "%Y.%m.%d")
        date = date.strftime("%Y-%m-%d")
    return date


# write data to UTF-8 by ensure_ascii option
def write_data(data):
    with open("test.json", 'a') as outfile:
        json.dump(data, outfile, ensure_ascii=False)
        outfile.write("\n")


def get_maintxt(page):
    tree = html.fromstring(page.content)
    pass


def main():
    # the number of articles
    count = 0

    # get search result page per day
    for single_date in daterange(START_DATE, END_DATE + timedelta(1)):

        # get result page's url of one target day
        base_url = make_url(single_date)

        # get the number of pages
        try:
            result_html = get_html(base_url)
            pages = page_count(result_html)
        except Exception as e:
            print(e)
            print(base_url)
            continue

        # parsing blogs per page
        for page in range(1, int(pages) + 1):

            # get one page's url
            target_url = base_url + "&page=" + str(page)

            # get blog list
            try:
                page_html = get_html(target_url)
                blogs = get_blog_list(page_html)
            except Exception as e:
                print(e)
                print(target_url)
                continue

            for blog in blogs:
                # get blog's title and link
                title_and_link = blog.findAll("a")[0]
                title = title_and_link.text
                link = title_and_link["href"].encode('utf-8')

                # get blog's host
                host = get_host(link)

                # get blog's date
                date = blog.findAll("span", attrs={'class': 'date'})[0].text
                # reshape date to "%Y-%m-%d" format
                date = reshape_date(date)

                # get blog's html except host is daum
                # daum blog's html is not readable because of frame tag
                if re.search('blog.daum.net', link):
                    continue
                else:
                    try:
                        # requests
                        blog_page = requests.get(link)
                        # get blog's original html
                        blog_html = bs4.BeautifulSoup(blog_page.text)
                        # get blog's maintext

                        # one blog data to write
                        blog_data = {"query": QUERY_WORDS, "title": title, "host": host, "link": link, "date": date,
                                     "content": blog_html.text.strip()}
                        # write data to UTF-8 by ensure_ascii option
                        write_data(blog_data)
                    except Exception as e:
                        print(e)
                        print(link.encode('utf-8'))
                        continue

                # count number of blogs that wrote to file
                count += 1
                print("date : " + single_date.strftime("%Y%m%d") + " / count : " + str(count))


if __name__ == '__main__':
    main()
