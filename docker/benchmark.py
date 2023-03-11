#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import timeit
import time
import string
import argparse
import csv


# Dead abandoned lib (broken) http://urlgrabber.baseurl.org
requests_setups = """
import requests
session = requests.Session()
r = requests.Request('GET', '$url').prepare()"""

pycurl_setups = """
from pycurl import Curl
mycurl = Curl()
mycurl.setopt(mycurl.URL, '$url')
mycurl.setopt(mycurl.WRITEFUNCTION, lambda x: None)"""

pycurl_setups_nossl = """
from pycurl import Curl
mycurl = Curl()
mycurl.setopt(mycurl.SSL_VERIFYPEER, 0)
mycurl.setopt(mycurl.SSL_VERIFYHOST, 0)
mycurl.setopt(mycurl.URL, '$url')
mycurl.setopt(mycurl.WRITEFUNCTION, lambda x: None)"""


def run_test(library, url, repetitions, setup_test, run_test, timer=None):
    TIMER = timeit.default_timer
    if timer and timer.lower() == 'cpu':
        TIMER = time.clock
    run_cmd = string.Template(run_test).substitute(url=url)
    setup_cmd = string.Template(setup_test).substitute(url=url)
    mytime = timeit.timeit(stmt=run_cmd, setup=setup_cmd, number=repetitions, timer=TIMER)
    print(f"{library.upper()} =\t{round(mytime, 4)}\n")
    return [library, repetitions, mytime]


def run_all_benchmarks(url='', repetitions=10_000, output_file="results.csv", **kwargs):
    results = []
    timer_type = kwargs.get('timer')

    tests = [
        ('pywget', "import wget", "wget.download('$url', bar=None)"),
        ('requests', 'import requests', "requests.get('$url', verify=False)"),
        ('requests_session', requests_setups, "session.send(r, verify=False)"),
        (
            'urllib',
            "from urllib.request import urlopen",
            "urlopen('$url').read()",
        ),
        (
            'urllib3',
            "import urllib3; http_pool = urllib3.PoolManager()",
            "http_pool.urlopen('GET', '$url').read()",
        ),
        ('pycurl', pycurl_setups, "mycurl.perform()"),
        ('pycurl_nossl', pycurl_setups_nossl, "mycurl.perform()"),
        (
            'faster_than_requests',
            "import faster_than_requests",
            "faster_than_requests.get2str('$url')",
        ),
    ]
    for test in tests:
        my_result = run_test(test[0], url, repetitions, test[1], test[2], timer=timer_type)
        results.append((test[0], my_result[-1]))

    if output_file:
        with open(output_file, 'w') as csvfile:
            outwriter = csv.writer(csvfile, dialect=csv.excel)
            outwriter.writerow(('library', 'time'))
            for result in results:
                outwriter.writerow(result)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Benchmarks for HTTP Client libs")
    parser.add_argument('--url', metavar='u', type=str, default='http://localhost:5000/', help="URL")
    parser.add_argument('--repetitions', metavar='c', type=int, default=10_000, help="Repetitions")
    parser.add_argument('--timer', type=str, default="real", choices=('real','cpu'), help="Timer type: real [default] or cpu")
    args = vars(parser.parse_args())
    assert args.get('url') is not None, "URL must not be an empty string."
    assert args.get('repetitions') > 100, "Repetitions must be > 100."
    print(args)
    run_all_benchmarks(**args)
