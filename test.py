from multi_model.mt import (
        rw, mt_rw, mp_rw, mt_web_rw, mp_web_rw, web_rw,
        co_rw, co_web_rw, gevent_web_rw)
if __name__ == '__main__':
    web_rw()
    mt_web_rw()
    mp_web_rw()
    co_web_rw()
    gevent_web_rw()
    rw()
    co_rw()
    mt_rw()
    mp_rw()
