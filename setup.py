#!/usr/bin/env python

import uuid
from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session=uuid.uuid1())

setup(name="lightsaber",
        version="0.1",
        license="MIT",
        description="Utility scripts for machine learning research",
        url="https://github.com/imai-laboratory/lightsaber",
        packages=find_packages(),
        scripts=[
            'lightsaber/tools/plot-json',
            'lightsaber/tools/echo-timestamp'
        ])
