from setuptools import setup
import sys


if sys.version_info.major < 3:
    sys.exit('Python <3 is unsupported.')
    

#def readfile(filename):
#    with open(filename, 'r+') as f:
#        return f.read()


setup(
    name="hexapterygon",
    version="1.1.1",
    description="A user-friendly all-in-one cross-platform, (uni-curses compatible component, module and uitility) software for orchestrating and debloating your Android devices from unwanted pre-installed crap.",
    #long_description=readfile('README.md'),
    author="George Chousos",
    author_email="gxousos@gmail.com",
    url="https://github.com/GiorgosXou/hexapterygon",
    packages=['hexapterygon'],
    install_requires=['uni-curses', 'pure-python-adb', 'PyGithub'],
    entry_points={
        'console_scripts': [
            'hexapterygon = hexapterygon.__main__:main'
        ]
    },
)

# pip3 install .
# python setup.py sdist
# twine upload dist/*
