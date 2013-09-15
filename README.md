dirq-consumer
=======

Overview
-------

Python module that provides an easy way to create consumers of "messages" from STOMP-compatible messaging brokers (such as ActiveMQ/Apollo).

It relays on top of [python-messaging](https://github.com/cern-mig/python-messaging) and [messaging.dirq](https://github.com/cern-mig/python-dirq) (which uses [stompclt](http://mig.web.cern.ch/mig/doc/stompclt.html)). These libraries includes a transport independent message abstraction and several message queues/spools to locally store messages, using the underlying filesystem.

Install
-----

To install this module, run the following command::

    python setup.py install

Or create the rpm with::

    make rpm

Documentation
--------

[How to use it](http://androidsx.com/projects/dirq-consumer-docs/)
