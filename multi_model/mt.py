import re
import os
import threading
import queue
import multiprocessing as mp
import asyncio
from hashlib import md5

import requests

from .test import time_over, run_mul

@time_over
@run_mul(5)
def download_pic():
    t = requests.get('http://www.kexuelife.com').text
    r = re.compile(r'<img src="([a-zA-z]+://[^\s<>\"\']*)')
    urls = r.findall(t)
    for u in urls:
        content = requests.get(u).text
        path = '{}/pic/{}.jpg'.format(os.path.abspath(os.path.dirname(__file__)), md5(u.encode('utf-8')).hexdigest())
        with open(path, 'w') as fp:
            fp.write(content)


async def async_insert_data(dir_queue):
    dirs = os.scandir('{}/pic/'.format(os.path.abspath(os.path.dirname(__file__))))
    for d in dirs:
        await dir_queue.put(d.path)

async def async_read_write(dir_queue):
    while True:
        d = await dir_queue.get()
        if d is None:
            break
        with open(d, 'r') as fp:
            content = fp.read()
        with open(d, 'w') as fp:
            fp.write(content)
        dir_queue.task_done()


class IOTest():
    def __init__(self, queue):
        self.queue = queue
    def run(self):
        while True:
            d = self.queue.get()
            if d is None:
                break
            with open(d, 'r') as fp:
                content = fp.read()
            with open(d, 'w') as fp:
                fp.write(content)
            self.queue.task_done()


class IOWebTest():
    def __init__(self, queue):
        self.queue = queue
    def run(self):
        while True:
            d = self.queue.get()
            if d is None:
                break
            content = requests.get(d).text
            path = '{}/pic/{}.jpg'.format(os.path.abspath(os.path.dirname(__file__)), md5(d.encode('utf-8')).hexdigest())
            with open(path, 'w') as fp:
                fp.write(content)
            self.queue.task_done()


class ThreadIOTest(threading.Thread, IOTest):
    def __init__(self, queue):
        self.queue = queue
        threading.Thread.__init__(self)

class ThreadWebIOTest(threading.Thread, IOWebTest):
    def __init__(self, queue):
        self.queue = queue
        threading.Thread.__init__(self)

class ProcessIOTest(mp.Process, IOTest):
    def __init__(self, queue):
        self.queue = queue
        mp.Process.__init__(self)

class ProcessWebIOTest(mp.Process, IOWebTest):
    def __init__(self, queue):
        self.queue = queue
        mp.Process.__init__(self)


@run_mul(5)
def insert_data(dir_queue):
    dirs = os.scandir('{}/pic/'.format(os.path.abspath(os.path.dirname(__file__))))
    for d in dirs:
        dir_queue.put(d.path)


@run_mul(5)
def insert_web_data(dir_queue):
    t = requests.get('http://www.kexuelife.com').text
    r = re.compile(r'<img src="([a-zA-z]+://[^\s<>\"\']*)')
    urls = r.findall(t)
    for u in urls:
        dir_queue.put(u)

def multi_test(dir_queue, insert_func, test_case):
    insert_func(dir_queue)
    subs = []
    for i in range(8):
        s = test_case(dir_queue)
        s.start()
        subs.append(s)
    for i in range(8):
        dir_queue.put(None)
    for s in subs:
        s.join()

def normal_test(dir_queue, insert_func, test_case):
    insert_func(dir_queue)
    dir_queue.put(None)
    s = test_case(dir_queue)
    s.run()


@time_over
def rw():
    dir_queue = queue.Queue(0)
    normal_test(dir_queue, insert_data, IOTest)

@time_over
def mt_rw():
    dir_queue = queue.Queue(0)
    multi_test(dir_queue, insert_data, ThreadIOTest)

@time_over
def mp_rw():
    dir_queue = mp.JoinableQueue(0)
    multi_test(dir_queue, insert_data, ProcessIOTest)

@time_over
def co_rw():
    loop = asyncio.get_event_loop()
    dir_queue = asyncio.Queue(0)
    loop.run_until_complete(async_read_write(dir_queue))

@time_over
def web_rw():
    dir_queue = queue.Queue()
    normal_test(dir_queue, insert_web_data, IOWebTest)

@time_over
def mt_web_rw():
    dir_queue = queue.Queue(0)
    multi_test(dir_queue, insert_web_data, ThreadWebIOTest)

@time_over
def mp_web_rw():
    dir_queue = mp.JoinableQueue(0)
    multi_test(dir_queue, insert_web_data, ProcessWebIOTest)


