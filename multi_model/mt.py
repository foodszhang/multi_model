import re
import os
import threading
import queue
import time
import multiprocessing as mp
import asyncio
from hashlib import md5
import logging

import aiohttp
import aiofiles

import requests

from .test import time_over, run_mul
from .config import Config


class WebIOTest():
    def __init__(self, queue_class, multi_class=object, times = 1, core_num = 8):
        self.queue = queue_class(0)
        self.multi_class = multi_class
        self.times = times
        self.core_num = core_num
        self.producer = type('%s' % multi_class.__name__, (multi_class, ), {'run': self._producer})
        self.consumer = type('%s' % multi_class.__name__, (multi_class, ), {'run': self._consumer})

    def _producer(self):
        @run_mul(self.times)
        def _run(self):
            url = Config.CRAWL_URL
            t = requests.get(url).text
            r = re.compile(r'<img src="([a-zA-z]+://[^\s<>\"\']*)')
            urls = r.findall(t)
            for u in urls:
                self.queue.put(u)
                logging.debug('up %d', self.queue.qsize())
        _run(self)

    def _consumer(self):
        while True:
            logging.debug('limit %d', self.queue.qsize())
            d = self.queue.get()
            logging.debug('%s', d)
            if d is None:
                logging.debug('is break')
                break
            time.sleep(0.01)
            content = requests.get(d).content

            path = '{}/pic/{}.jpg'.format(os.path.abspath(os.path.dirname(__file__)), md5(d.encode('utf-8')).hexdigest())
            with open(path, 'wb') as fp:
                fp.write(content)

    def multi_test(self):
        producers = []
        for i in range(self.core_num):
            producer = self.producer()
            producer.start()
            producers.append(producer)
        consumers = []
        for i in range(self.core_num):
            consumer = self.consumer()
            consumer.start()
            consumers.append(consumer)
        for s in producers:
            s.join()
        for i in range(self.core_num):
            self.queue.put(None)
        for s in consumers:
            s.join()

    def normal_test(self):
        for i in range(self.core_num):
            s = self.producer()
            s.run()
        self.queue.put(None)
        s = self.consumer()
        s.run()


class AsyncWebIoTest():
    def __init__(self, times=1, core_num=8):
        self.queue = asyncio.Queue(0)
        self.times = times
        self.core_num = core_num
    async def consumer(self):
        while True:
            logging.debug('limit %d', self.queue.qsize())
            d = await self.queue.get()
            logging.debug('%s', d)
            if d is None:
                break
            async with aiohttp.get(d) as resp:
                content = await resp.read()
                path = '{}/pic/{}.jpg'.format(os.path.abspath(os.path.dirname(__file__)), md5(d.encode('utf-8')).hexdigest())
                fp = await aiofiles.open(path, 'wb')
                await fp.write(content)
                await fp.close()

    async def producer(self):
        @run_mul(self.times)
        async def _run(self):
            url = Config.CRAWL_URL
            async with aiohttp.get(url) as resp:
                content = await resp.read()
            r = re.compile(r'<img src="([a-zA-z]+://[^\s<>\"\']*)')
            urls = r.findall(content.decode('utf-8'))
            for u in urls:
                await self.queue.put(u)
                logging.debug('up %d', self.queue.qsize())
        await _run(self)

    async def delay(self):
        for i in range(self.core_num):
            await self.queue.put(None)

    def async_test(self, core_num = 0):
        producers = []
        consumers = []
        if not core_num:
            core_num = self.core_num
        for i in range(core_num):
            producers.append(asyncio.ensure_future(self.producer()))
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(producers))
        loop.run_until_complete(self.delay())
        for i in range(core_num):
            consumers.append(asyncio.ensure_future(self.consumer()))
        loop.run_until_complete(asyncio.wait(consumers))



class TestCase:
    def __init__(self, times = 1, core_num = 8):
        self.times = times
        self.core_num = core_num
    @time_over
    def web_rw(self):
        case = WebIOTest(queue.Queue,times=self.times, core_num=self.core_num)
        case.normal_test()

    @time_over
    def mt_web_rw(self):
        case = WebIOTest(queue.Queue, threading.Thread, times=self.times, core_num=self.core_num)
        case.multi_test()

    @time_over
    def mp_web_rw(self):
        case = WebIOTest(mp.Queue, mp.Process, times=self.times, core_num=self.core_num)
        case.multi_test()


    @time_over
    def co_web_rw(self):
        case = AsyncWebIoTest(times=self.times, core_num=self.core_num)
        case.async_test()



