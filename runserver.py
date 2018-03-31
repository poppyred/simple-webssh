#!/usr/bin/env python3
# coding=utf-8

"""
@author: guoyanfeng
@software: PyCharm
@time: 17-11-15 下午6:24
"""
import uuid

import aelog
import tornado.web
from path import Path
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line

from simple_webssh.routers import handlers

define('address', default='0.0.0.0', help='listen address')
define('port', default=8888, help='listen port', type=int)


def main():
    aelog.init_aelog("access.log", True)
    settings = {
        'template_path': Path(__file__).dirname().joinpath('simple_webssh/templates').abspath(),
        'static_path': Path(__file__).dirname().joinpath('simple_webssh/static').abspath(),
        'cookie_secret': uuid.uuid4().hex,
        'xsrf_cookies': False,
        'debug': True
    }

    parse_command_line()
    app = tornado.web.Application(handlers, **settings)
    app.listen(options.port, options.address)
    aelog.info('Listening on {}:{}'.format(options.address, options.port))
    IOLoop.current().start()


if __name__ == '__main__':
    main()
