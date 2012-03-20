#!/usr/bin/env python

from setuptools import setup

setup(name='treecompare',
      packages=['treecompare'],
      version='1.0',
      description="""
      	Compare complex trees of objects with useful 
      	diff output and fuzzy matching options.""",
      author='Ruy Asan',
      author_email='ruyasan@gmail.com',
      url='https://github.com/rubyruy/treecompare',
      install_requires=['distribute'],
      classifiers=[
      	"Programming Language :: Python",
      	"License :: OSI Approved :: BSD License",
      	"Operating System :: OS Independent",
      	"Development Status :: 5 - Production/Stable",
      	"Intended Audience :: Developers",
      	"Topic :: Software Development :: Testing",
      	"Topic :: Software Development :: Libraries :: Python Modules"

      ],
      long_description="""A library for comparing trees of various objects
            in a way that yields useful "paths" to each difference. Simply
            knowing that two object blobs differ is hardly useful without
            knowing where exactly the differences are located. For text
            blobs, text-diff utilities can solve this problem, but they are
            ill suited for dealing with arbitrary data structures such as
            dictionaries where key order doesn't matter."""
     )