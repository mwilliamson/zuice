from distutils.core import setup

setup(
    name='Zuice',
    version='0.1',
    description='A dependency injection framework for Python',
    author='Michael Williamson',
    author_email='mike@zwobble.org',
    url='http://gitorious.org/zuice',
    packages=['zuice'],
    data_files={'doc': ['doc/index.rst']},
)
