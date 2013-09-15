try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    f = open('README.md')
    return f.read()

setup(
    name = "dirqconsumer",
    version = "0.1",
    description = "Generic library to consume messages from a directory queue using messaging.dirq",
    long_description=readme(),
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.4"
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7'
        # 'Programming Language :: Python :: 3.0'
        # 'Programming Language :: Python :: 3.1'
    ],
    author = 'Omar Pera Mira',
    author_email = 'campbell.sx@gmail.com',
    url = 'https://github.com/ompemi/dirq-consumer',
    packages=['dirqconsumer'],
    license = 'GPL',
    zip_safe = False,
)