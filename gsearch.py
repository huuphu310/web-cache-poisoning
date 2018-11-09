#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Create by Meibenjin.
#
# Last updated: 2018-11-06 by huuphu310
#
# google search results crawler

import random
import re
import socket
import sys
import time
import requests
from bs4 import BeautifulSoup

base_url = 'https://www.google.com.vn'
results_per_page = 10

user_agents = list()


def cmp(x, y):
    if x < y:
        return -1
    elif x > y:
        return 1
    else:
        return 0


# extract the domain of a url
def extractDomain(url):
    pattern = r'http[s]?://[^&]+' + keyword
    domain = re.compile(pattern.rstrip(), re.U | re.M).search(url).group()
    return domain


# results from the search engine
# basically include url, title,content
class SearchResult:
    def __init__(self):
        self.url = ''

    def getURL(self):
        return self.url

    def setURL(self, url):
        self.url = url

    def writeFile(self, filename):
        file = open(filename, 'a')
        url = extractDomain(self.url)
        try:
            file.write(str(url) + '/\n')
        except IOError as e:
            print('file error:', e)
        finally:
            file.close()


def extractUrl(href):
    url = ''
    pattern = re.compile(r'(http[s]?://[^&]''+)&', re.U | re.M)
    url_match = pattern.search(href)
    if url_match and url_match.lastindex > 0:
        url = url_match.group(1)

    return url


def randomSleep():
    sleeptime = random.randint(60, 120)
    time.sleep(sleeptime)


class GoogleAPI:
    def __init__(self):
        timeout = 40
        socket.setdefaulttimeout(timeout)

    @staticmethod
    def extractSearchResults(html):
        results = list()
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', id='search')
        if type(div) is not None:
            lis = div.findAll('', {'class': 'g'})
            if len(lis) > 0:
                for li in lis:
                    result = SearchResult()
                    h3 = li.find('h3', {'class': 'r'})
                    if type(h3) is None:
                        continue
                    link = h3.find('a')
                    if type(link) is None:
                        continue
                    url = link['href']
                    url = extractUrl(url)
                    if cmp(url, '') == 0:
                        continue
                    result.setURL(url)
                    results.append(result)
        return results

    def search(self, query, lang='en', num=results_per_page):
        search_results = list()
        if num % results_per_page == 0:
            pages = num / results_per_page
        else:
            pages = num / results_per_page + 1

        for p in range(0, int(pages)):
            start = p * results_per_page
            url = '%s/search?hl=%s&num=%d&start=%s&q=%s' % (base_url, lang, results_per_page, start, query)
            retry = 3
            while retry > 0:
                try:
                    length = len(user_agents)
                    index = random.randint(0, length - 1)
                    user_agent = user_agents[index]
                    headers = {
                        'User-agent': user_agent,
                        'connection': 'keep-alive',
                        'Accept-Encoding': 'gzip',
                        'referer': base_url
                    }
                    request = requests.get(url, headers=headers)
                    html = request.text

                    results = self.extractSearchResults(html)
                    search_results.extend(results)
                    break
                except requests.HTTPError as e:
                    print('url error:', e)
                    randomSleep()
                    retry = retry - 1
                    continue

                except Exception as e:
                    print('error:', e)
                    retry = retry - 1
                    randomSleep()
                    continue
        return search_results


def load_user_agent():
    fp = open('./user_agents', 'r')

    line = fp.readline().strip('\n')
    while line:
        user_agents.append(line)
        line = fp.readline().strip('\n')
    fp.close()


def crawler():
    # Load use agent string from file
    load_user_agent()
    global keyword
    # Create a GoogleAPI instance
    api = GoogleAPI()

    # set expect search results to be crawled
    expect_num = 25
    # if no parameters, read query keywords from file
    if len(sys.argv) < 2:
        keywords = open('./keywords', 'r')
        keyword = keywords.readline()
        while keyword:
            results = api.search(keyword, num=expect_num)
            for r in results:
                r.writeFile('domain.txt')
            keyword = keywords.readline()
        keywords.close()
    else:
        keyword = sys.argv[1]
        results = api.search(keyword, num=expect_num)
        for r in results:
            r.writeFile('domain.txt')


if __name__ == '__main__':
    crawler()
