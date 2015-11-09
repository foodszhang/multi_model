from multi_model.mt import TestCase
if __name__ == '__main__':
    #co_web_unlimit_rw()
    test = TestCase(times=1)
    test.co_web_rw()
    test.web_rw()
    test.mp_web_rw()
    test.mt_web_rw()
