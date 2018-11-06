#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Create by Meibenjin.
#
# Last updated: 2013-04-02
#
# google search results crawler

import sys
# reload(sys)
# sys.setdefaultencoding('utf-8')

import urllib.request, urllib.error, socket, time
import gzip
import re, random, types
from io import StringIO
from bs4 import BeautifulSoup
import zlib

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
def extractDomain( url):
    pattern = r'http[s]?://[^&]+' + keyword
    domain = re.compile(pattern.rstrip(), re.U | re.M).search(url).group()
    return domain

# results from the search engine
# basically include url, title,content
class SearchResult:
    def __init__(self):
        self.url = ''
        self.title = ''
        self.content = ''

    def getURL(self):
        return self.url

    def setURL(self, url):
        self.url = url

    def getTitle(self):
        return self.title

    def setTitle(self, title):
        self.title = title

    def getContent(self):
        return self.content

    def setContent(self, content):
        self.content = content

    def printIt(self, prefix=''):
        # print('url\t->', self.url
        # print('title\t->', self.title
        # print('content\t->', self.content
        print(self.url)

    def writeFile(self, filename):
        file = open(filename, 'a')
        url =  extractDomain(self.url)
        try:
            file.write(str(url) + '/\n')
            # file.write('title:' + self.title + '\n')
            # file.write('content:' + self.content + '\n\n')

        except IOError as e:
            print('file error:', e)
        finally:
            file.close()


class GoogleAPI:
    def __init__(self):
        timeout = 40
        socket.setdefaulttimeout(timeout)

    def randomSleep(self):
        sleeptime = random.randint(60, 120)
        time.sleep(sleeptime)

    # extract a url from a link
    def extractUrl(self, href):
        url = ''
        pattern = re.compile(r'(http[s]?://[^&]''+)&', re.U | re.M)
        url_match = pattern.search(href)
        if (url_match and url_match.lastindex > 0):
            url = url_match.group(1)

        return url

        # extract serach results list from downloaded html file

    def extractSearchResults(self, html):
        results = list()
        soup = BeautifulSoup(html, 'html.parser')
        div = soup.find('div', id='search')
        if (type(div) is not None):
            lis = div.findAll('', {'class': 'g'})
            if (len(lis) > 0):
                for li in lis:
                    result = SearchResult()
                    h3 = li.find('h3', {'class': 'r'})
                    if (type(h3) is None):
                        continue

                    # extract domain and title from h3 object
                    link = h3.find('a')
                    if (type(link) is None):
                        continue

                    url = link['href']
                    url = self.extractUrl(url)
                    if (cmp(url, '') == 0):
                        continue
                    title = link.renderContents()
                    result.setURL(url)
                    result.setTitle(title)

                    span = li.find('span', {'class': 'st'})
                    if (type(span) is not None):
                        content = span.renderContents()
                        result.setContent(content)
                    results.append(result)
        return results

    # search web
    # @param query -> query key words
    # @param lang -> language of search results
    # @param num -> number of search results to return
    def search(self, query, lang='en', num=results_per_page):
        search_results = list()
        query = urllib.request.quote(query)
        if (num % results_per_page == 0):
            pages = num / results_per_page
        else:
            pages = num / results_per_page + 1

        for p in range(0, int(pages)):
            start = p * results_per_page
            url = '%s/search?hl=%s&num=%d&start=%s&q=%s' % (base_url, lang, results_per_page, start, query)
            retry = 3
            while (retry > 0):
                try:
                    request = urllib.request.Request(url)
                    length = len(user_agents)
                    index = random.randint(0, length - 1)
                    user_agent = user_agents[index]
                    request.add_header('User-agent', user_agent)
                    request.add_header('connection', 'keep-alive')
                    request.add_header('Accept-Encoding', 'gzip')
                    request.add_header('referer', base_url)
                    response = urllib.request.urlopen(request)
                    html = response.read()
                    if (response.headers.get('content-encoding') == 'gzip'):
                        html = zlib.decompress(html, 16 + zlib.MAX_WBITS)

                    results = self.extractSearchResults(html)
                    search_results.extend(results)
                    break;
                except urllib.error.URLError as e:
                    print('url error:', e)
                    self.randomSleep()
                    retry = retry - 1
                    continue

                except Exception as e:
                    print('error:', e)
                    retry = retry - 1
                    self.randomSleep()
                    continue
        return search_results


def load_user_agent():
    fp = open('./user_agents', 'r')

    line = fp.readline().strip('\n')
    while (line):
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
    expect_num = 10
    # if no parameters, read query keywords from file
    if (len(sys.argv) < 2):
        keywords = open('./keywords', 'r')
        keyword = keywords.readline()
        while (keyword):
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
