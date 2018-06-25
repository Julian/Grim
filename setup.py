import os

from setuptools import find_packages, setup


with open(os.path.join(os.path.dirname(__file__), "README.rst")) as readme:
    long_description = readme.read()

classifiers = [
    "Development Status :: 3 - Alpha",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3.6",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: Implementation :: CPython",
    "Programming Language :: Python :: Implementation :: PyPy"
]

setup(
    name="grim",
    url="https://github.com/Julian/Grim",

    description="",
    long_description=long_description,

    author="Julian Berman",
    author_email="Julian@GrayVines.com",

    packages=find_packages(),

    install_requires=["attrs", "pyrsistent"],
    setup_requires=["setuptools_scm"],
    use_scm_version=True,

    classifiers=classifiers,
)
