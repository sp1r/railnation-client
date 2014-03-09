__author__ = 'Slava'

import sys
import time


class Engine:
    def __init__(self,
                 log_file_name=None,
                 log_file_mode='w',
                 time_format="%H:%M:%S"):
        self.time_format = time_format
        try:
            self.log_file = open(log_file_name,
                                 log_file_mode)
        except IOError:
            print 'ERROR! Log file not found!'
            sys.exit(1)

    def write_to_log(self,
                     message,
                     message_time,
                     level):
        log_line = "%s: %s\n" % (time.strftime(self.time_format,
                                               message_time),
                                 message)
        if level == 0:
            self.log_file.write(log_line)
            self.log_file.flush()
        elif level == 1:
            print log_line


class Interface:
    def __init__(self, engine):
        assert isinstance(engine, Engine)
        self.srv = engine

    def write_to_file(self,
                      message="",
                      message_time=time.localtime()):
        self.srv.write_to_log(message, message_time, 0)

    def write_to_screen(self,
                        message="",
                        message_time=time.localtime()):
        self.srv.write_to_log(message, message_time, 1)