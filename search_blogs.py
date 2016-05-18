#-*- coding: utf-8 -*-
__author__ = 'sohyeon'

import requests
import bs4
import re
import json
import urllib
import urllib.request
from datetime import datetime, timedelta, date

# search date option
start_date = date(2015, 9, 16)
end_date = date(2016, 1, 31)

# query
QUERY_WORDS = '화재 -삼성화재 -동부화재 -메리츠화재'

# the number of articles
count = 0

# date range function
def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

# make url with date, query option
def make_url(date):
    target_date = date.strftime("%Y%m%d")
    next_date = (date + timedelta(1)).strftime("%Y%m%d")
    query = urllib.parse.quote_plus(QUERY_WORDS)
    url = 'http://search.daum.net/search?w=blog&nil_search=btn&DA=NTB&enc=utf8'+ '&sd='+target_date+ '&ed='+next_date+ '&q=' + query
    return url

#
for single_date in daterange(start_date, end_date + timedelta(1)):
    base_url = make_url(single_date)

    # Requests
    data = requests.get(base_url)

    # Parsing ( totalCount )
    data = bs4.BeautifulSoup(data.text)

    # total_count
    total_count = data.find("span", attrs={'id': 'resultCntArea'})
    total_count = [int(s) for s in re.findall('\d+', total_count.text)][2]


    # Calc Pages
    # 1 페이지당 10개의 블로그가 보여진다.
    # 예, 23개의 기사일 경우 3페이지까지 있다.
    pages = total_count / 10 + 1

    # Parsing Articles per Page
    for page in range(1, int(pages)+1):
        TARGET_URL = base_url + "&page=" + str(page)

        try:
            data = requests.get(TARGET_URL)
        except Exception as e:
            print (e)
        data = bs4.BeautifulSoup(data.text)

        try:
            blogs = data.findAll("div", attrs={'id': 'blogColl'})[0]
            blogs = blogs.findAll("div", attrs={'class': 'cont_inner'})
        except Exception as e:
            print(e)
            print(TARGET_URL)

        for blog in blogs:
            #타이틀, 링크 가져오기
            title_and_link = blog.findAll("a")[0]
            title = title_and_link.text
            link = title_and_link["href"]

            #날짜 가져오기
            date = blog.findAll("span", attrs={'class': 'date'})[0].text

            # ~시간전, ~분전, ~초전  시간 고치기
            if re.search('전', date):
                if re.search('시간',date):
                    date = datetime.now() - timedelta(hours=int(date.split("시간")[0]))
                    date = date.strftime("%Y-%m-%d")
                elif re.search('분',date):
                    date = datetime.now() - timedelta(minutes=int(date.split("분")[0]))
                    date = date.strftime("%Y-%m-%d")
                elif re.search('초',date):
                    date = datetime.now() - timedelta(seconds=int(date.split("초")[0]))
                    date = date.strftime("%Y-%m-%d")
            else:
                date = datetime.strptime(date, "%Y.%m.%d")
                date = date.strftime("%Y-%m-%d")

            # 해당 blog의 html 가져오기
            if re.search('blog.daum.net', link):
                continue
            else:
                try:
                    blog_content = requests.get(link.encode('utf-8'))
                except Exception as e:
                    print(e)
                    print(link)
                    continue

            # file에 입력할 하나의 blog data
            blog_data = {"query": QUERY_WORDS, "title": title, "link": link, "date": date, "content": blog_content.text.strip()}

            count += 1

            # ensure_ascii 옵션으로 UTF-8 ( 한글로 보이도록 ) 출력한다.
            try:
                with open("fire_blog.json", 'a') as outfile:
                    json.dump(blog_data, outfile, ensure_ascii=False)
                    outfile.write("\n")
            except Exception as e:
                print(e)
                print("link: " + link)
                continue

            print("date : " + target_date + " / count : " + str(count))
