"""
Build Specs for Modular Sessions
"""

from setuptools import setup

import modular_sessions.__meta__ as application

setup(
    name=application.__name__,
    version=application.__version__,
    description=application.__description__,
    long_description=open("README.md").read(),
    url=application.__url__,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        "Operating System :: OS Independent"
    ],
    license=application.__license__,
    author=application.__author__,
    author_email=application.__email__,
    install_requires=["fastapi", "itsdangerous", "pydantic", "starlette"]
)

