#!/usr/bin/python
import sys, os
import logging
import optparse

try:
    import simplejson as json 
except ImportError:
    import json # from 2.6+

# Just adding dirqconsumer pythonpath for developement
sys.path.append(os.path.abspath("../"))

from dirqconsumer import DirqConsumerBase
import utils

class SimpleMonitoringConsumer(DirqConsumerBase):
    
    NUM_RETRIES_ERROR_MSG = 5
    
    def __init__(self, dq_path, step_sec=0.5):
        DirqConsumerBase.__init__(self, dq_path, step_sec)
        self.logger = logging.getLogger("browserconsumer")
        
        self.ename_msg_with_errors = {}
        
    def _setup(self):
        self.logger.info("Waiting for new messages from monitoring topics")
        
        return True

    def _process(self, msg):
        self.logger.info("New message read from the directory queue")
        self.logger.debug("Received raw message to process: '%s'" % msg)
        
        header, body = msg.header, json.loads(msg.body)

        self.logger.info("Message info: type=%s host=%s hostgroup=%s " % (header["m_source-type"], header["m_host"],
                                                                           header["m_hostgroup"]))
        
        return True # consumed message, it will remove it
    
    def _handle_process_error(self, ename, msg, exception):
        self.__handle_error_retries(ename, msg)
    
    def _handle_msg_error(self, ename, exception):
        self.__handle_error_retries(ename)

    def _handle_error(self, ename, exception):
        self.__handle_error_retries(ename)
        
    def __handle_error_retries(self, ename, msg=None):
        if self.ename_msg_with_errors.get(ename):
            self.ename_msg_with_errors[ename] += 1
        else:
            self.ename_msg_with_errors[ename] = 1
            
        if self.ename_msg_with_errors[ename] >= SimpleMonitoringConsumer.NUM_RETRIES_ERROR_MSG:
            self.logger.exception("More than 5 errors for the processing of one message, we discard it")
            if msg:
                self.logger.debug("Skipping this message: %s" % msg)

            self.dirq.remove(ename)
        else:
            self.logger.exception("There was an error during the processing of the message, we will try later")
            self.dirq.unlock(ename, permissive=True)
            
if __name__ == '__main__':
    desc = """Example of a full working example of a simple consumer."""
    
    parser = optparse.OptionParser(version='%prog version 1.0', description=desc)
    parser.add_option('-d', '--dirq', help='Directory queue path', dest='dirq_path')
    parser.add_option('-L', '--loglevel', help='Log level (INFO, WARNING, ERROR, DEBUG, LOWDEBUG)', 
                      dest='log_level', default='INFO')
    parser.add_option('-l', '--logfile', help='Log file path', dest='log_file', 
                      default='/var/log/browser-monitoring-consumer.log')
    
    (opts, args) = parser.parse_args()
    
    # Making sure all mandatory options appeared.
    mandatories = ['dirq_path']
    for m in mandatories:
        if not opts.__dict__[m]:
            print "Mandatory option is missing: %s\n" % m
            parser.print_help()
            sys.exit(-1)
            
    utils.setup_app_logger("browserconsumer", opts.log_level, opts.log_file, show_stdout=True)
    utils.setup_app_logger("dirqconsumer", opts.log_level, opts.log_file, show_stdout=True)

    consumer = SimpleMonitoringConsumer(opts.dirq_path)
    consumer.init_queue()
    consumer.purge(maxtemp=600, maxlock=600)
    consumer.consume_forever()    

