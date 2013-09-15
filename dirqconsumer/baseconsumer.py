#!/usr/bin/python
""" 
:py:class:`DirqConsumerBase` - Base class for consuming *messages* of a Message Queue

Description
===========

This module provides a class that abstracts the logic to consume messages from a Messaging Queue. It relies on the *messaging.queue* module that provides a generic directory-based queue, and the *messaging.message* for the abstraction of the *message*.

It will consume *messages* forever from the given *Message Queue* (abstraction of a directory queue in the filesystem). The *Message Queue* needs to be filled in independently by the STOMP client stompclt (http://tomdoc.web.cern.ch/tomdoc/mig/stompclt.html).

The two required modules are python-dirq and python-messaging and are provided by the Messaging team: http://mpaladin.web.cern.ch/mpaladin/python/messaging/message.html. The latest stable libraries can be found in https://twiki.cern.ch/twiki/bin/view/EMI/MessagingLibraries.

Synopsis
===========

This module is designed so that you subclass :py:class:`DirqConsumerBase`, and you provide as a minimum the logic of
:py:meth:`DirqConsumerBase._process`. This method will be called when there are messages to process in the Directory
Queue.

Example of use extending the base class, providing the processing logic:
::
    from dirqconsumer import DirqConsumerBase

    logger = logging.getLogger(__name__)

    class ExampleConsumer(DirqConsumerBase):
        def __init__(self, dq_path, step_sec=0.1):
            DirqConsumerBase.__init__(self, dq_path, step_sec)

        def _process(self, msg):
            # parses the messaging.message
            header, body = msg.header, json.loads(msg.body)
            metadata, data = body.get("metadata", {}), body.get("data", {})
            
            # process your message
            logger.debug("Processing message: %s" % metadata.get('key2'))
            success = do_something(metadata, data)

             # consumes the message, if false leave it in the queue for later processing
            return success

    consumer = ExampleConsumer('/var/spool/example-consumer/')
    consumer.init_queue()
    consumer.purge(maxtemp=600, maxlock=600)
    consumer.consume_forever()

This example is consuming *messages* in the following format:
::
    {
        "body": "{
            "data": {
                "key1": "value1"
            },
            "metadata": {
                "key2": "value2"
            }
        }",
        "header": {
            "key3": "value3"
        },
        "encoding": {}
    }

If you want to enable logging, setup a handler and the level to "dirqconsumer" logging identifier.

It checks every *step_sec* seconds if there are new messages to consume, being a pull mechanism. There is no way to
implement an event-based mechanism using the current libraries.

Installation
===========

Grab the code from and run:
::
    $ python setup.py install

Or use the rpm *dirq-consumer* in the lemon6 tag of Koji.

Example
===========

Under the directory example/ of the root directory of the package, you have a full working python program with a simple
consumer which browses the directory queue.
::
    $ cd example
    $ python simple_consumer.py -d /var/spool/some-directory-queue/ -L DEBUG

Contact
===========================================

Maintainer: Omar Pera <campbell.sx@gmail.com>

Class documentation
===========================================

"""

import logging
import time
import threading

import messaging.queue
import messaging.message
from messaging.message import MessageError
from dirq.Exceptions import QueueError, QueueLockError

from dirqconsumer import NullHandler

logger = logging.getLogger("dirqconsumer")
logger.addHandler(NullHandler())

class DirqConsumerBase(object):
    """Base class that provides an abstraction of a Message Queue consumer."""
    
    def __init__(self, dq_path, step_sec=0.5, dq_type="DQS"):
        """
        Initialize the Message Queue class
        
            :param dq_path: File system path of the Message Queue
            :type step_sec: Interval in seconds to check if new messages to consume
            :type type: type the type of the Message Queue
        """
        self.dirq = None
        self.shutdown = threading.Event()

        self.dq_path = dq_path
        self.__step_sec = step_sec
        self.__dirq_option = {"type" : dq_type,
                  "path" : dq_path }
        
        
    def init_queue(self):
        """
        Create the message queue from where we will consume messages
        """
        logger.info("Initializing directory queue in %s" % self.dq_path)
        self.dirq = messaging.queue.new(self.__dirq_option)

    def consume_forever(self):
        """
        Consume messaging.message.Message's forever for the given messaging.queue, removing them from 
        the queue if succesfully consumed.
        
        For each message to be processed it will call the method :py:meth:`DirqConsumerBase._process`, consuming 
        the message or not from the Message Queue, depending on the result of the processing.
        
            :note: before calling this method, the client should initialize the Queue with :py:meth:`init_queue`
        """
        # Setup the consumer, if error we do not do nothing with the queue.
        if self._setup():
            while not self.shutdown.is_set():
                for ename in self.dirq:
                    if self.shutdown.is_set():
                        break

                    try:
                        if self.dirq.lock(ename):
                            message = self.dirq.get_message(ename)
                            
                            try:
                                success = self._process(message)
                            except Exception, e:
                                self._handle_process_error(ename, message, e)
                            else:
                                if success:
                                    self.dirq.remove(ename)
                                else:
                                    self.dirq.unlock(ename) # TODO: use finally when moving to python2.6+
                        else:
                            self._handle_file_locked(ename)
                    except (MessageError), e:
                        self._handle_msg_error(ename, e)
                    except (QueueError, QueueLockError, OSError), e:
                        self._handle_error(ename, e)
                    except (KeyboardInterrupt, SystemExit):
                        self.dirq.unlock(ename, permissive=True)
                        self.stop()
                        break

                try:
                    time.sleep(self.__step_sec)
                except (KeyboardInterrupt, SystemExit):
                    self.stop()
                    break
    
            self._teardown()
                
    def purge(self, **kwargs):
        """
        Remove unused intermediate directories,too old temporary elements and unlock too old locked elements from
        the Message Queue

            :param kwargs: keyword arguments passed to :py:meth:`dirq.purge` method, most common are maxtemp and
            maxlock
        
            :raises: OSError
        """
        logger.debug("Purging the directory queue (unlock too old locks, temp dirs, etc.)")
        self.dirq.purge(**kwargs)

    def stop(self):
        """Stop the processing of new messages on the next step interval"""
        self.shutdown.set()
    
    def _setup(self):
        """
        Callback before the Message Queue starts to consume messages in :py:meth:`consume_forever`
        
            :returns: True if success. If False, we do not consume any messages in 
                :py:meth:`consume_forever`, up to the client to decide what to do next.
        """
        return True

    def _process(self, msg):
        """
        Callback to process a messaging.message.Message coming from the Message Queue in :py:meth:`consume_forever`
    
            :param msg: messaging.message.Message ready to be consumed
            
            :returns: True if we want to indicate that the Message has been succesfully consumed, and can be removed from the
                Queue. If False, it will unlock the element, for later processing.
        """
        raise NotImplementedError # for python 2.6+, refactor with @abstractmethod decorator

    def _teardown(self):
        """
        Callback after the Message Queue has finished consumed messages in :py:meth:`consume_forever`, the reason could be
        an error or the user stopped the consumer
        """
        pass

    def _handle_file_locked(self, ename):
        """Callback when the element to be processed is locked, usually by another process"""
        logger.debug("The file %s is locked" % ename)

    def _handle_process_error(self, ename, msg, exception):
        """Callback when :py:meth:`_process` method raises an exception, by default we unlock it for later processing"""
        logger.exception("There was an error during the processing of the message: %s" % msg)
        self.dirq.unlock(ename, permissive=True)

    def _handle_msg_error(self, ename, exception):
        """Callback when there has been an error during the retrieval of the message, by default we unlock it for later processing"""
        logger.exception("There was an error during the retrieval of a message")
        self.dirq.unlock(ename, permissive=True)

    def _handle_error(self, ename, exception):
        """Callback when there has been an error looking for new elements in the Message Queue, by default we unlock it for later processing"""
        logger.exception("There was an error during the retrieval of a message")
        self.dirq.unlock(ename, permissive=True)
        
