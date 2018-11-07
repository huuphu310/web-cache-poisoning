import random
import string
from pip._vendor import requests

def _random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def _load_domains():
    fp = open('./domain.txt', 'r')
    domain = []
    line = fp.readline().strip('\n')
    while line:
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
        print(rand_host)
        for i in range(10):
            r = requests.get(url, headers={'X-Forwarded-Host': rand_host})
            if rand_host in str(r.content):
                if _check_without_header(rand_host, url):
                    break
        return True
    except Exception as e:
        print(str(e))
        return False


def _check_without_header(rand_host, url):
    try:
        r = requests.get(url)
        if rand_host in str(r.content):
            print("Domain %s ăn được đó" % str(url))
            return True
        else:
            return False
    except Exception as e:
        print(str(e))
        return False


if __name__ == '__main__':
    _domain = _load_domains()
    for domain in _domain:
        _check(domain)
