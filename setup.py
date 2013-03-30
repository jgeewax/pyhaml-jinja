#!/usr/bin/env python
"""
This extension to jinja make it possible to use a
`haml <http://haml-lang.com/>`_-style syntax for your Jinja2 templates.

Example::

    -extends "base.haml"

    -block title: Page title

    -block content
      %ul.list#users
        -for user in users
          %li
            %a(href="#{user.url}") #{user.username}

For more information read the
`documentation <http://github.com/jgeewax/pyhaml-jinja>`_
"""


from setuptools import setup

setup(
  name='pyhaml-jinja',
  version='0.1-dev',
  description='Haml-style syntax for Jinja2 templates',
  long_description=__doc__,
  author='JJ Geewax',
  author_email='jj@geewax.org',
  url='http://github.com/jgeewax/pyhaml-jinja',
  packages=['pyhaml_jinja'],
  install_requires=['Jinja2'],
  zip_safe=True,
  keywords="jinja2 templates haml html",
  platforms='any',
  classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Web Environment',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: BSD License',
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      'Topic :: Software Development :: Libraries :: Python Modules',
      'Topic :: Text Processing :: Markup :: HTML'
  ],
)

