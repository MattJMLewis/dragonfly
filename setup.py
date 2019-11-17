import setuptools

setuptools.setup(
    name="dragonfly-web",
    version="0.0.3a",
    author="Matthew Lewis",
    description="A web framework.",
    long_description="A web framework that is loosely based on the syntax of Django and Laravel. It is inteded to be "
                       "used as a rapid development tool.",
    url="https://github.com/MattJMLewis/dragonfly",
    packages=setuptools.find_packages(),
    classifiers=["Programming Language :: Python :: 3.7"]
)