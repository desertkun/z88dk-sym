try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


setup(
    name='z88dk-sym',
    version='0.1.1',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    packages=[
        'z88dk',
        'z88dk.sym',
    ],
)
