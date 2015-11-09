def consumer():
    r = ''
    while 1:
        n = yield r
        if not n:
            print ('exit!')
            return
        print('consumer: %d' % n)
        r = 'ok!'

def producer(c):
    c.send(None)
    n = 0
    for n in range(1, 5):
        print('produce %d' % n)
        r = c.send(n)
        print('producer consume return %s' % r)
    c.close()

c = consumer()

p = producer(c)


