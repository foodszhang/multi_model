import time
from functools import wraps

def time_over(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print('In function {}'.format(func.__name__))
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        print('耗时 {}'.format(end-start))
    return wrapper

def run_mul(times):
    def decorate(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print('in function {} run {} times'.format(func.__name__, times))
            for i in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorate


if __name__ == '__main__':
    @time_over
    def test_caculate():
        from math import log
        a = 0
        for i in range(100):
            a +=  123456789 ** 987654
        print(log(a))
        return 0
    @time_over
    def test_sleep():
        time.sleep(3)

    test_caculate()
    test_sleep()


