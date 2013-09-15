import logging

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

from baseconsumer import DirqConsumerBase