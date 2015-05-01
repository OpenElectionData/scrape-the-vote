try:
    from setuptools import setup
except ImportError :
    raise ImportError("setuptools module required, please go to https://pypi.python.org/pypi/setuptools and follow the instructions for installing setuptools")

reqs = [
    'scrapelib',
    'beautifulsoup4',
    'lxml',
]

setup(
    name='stv',
    version='0.1',
    packages=['stv'],
    install_requires=reqs,
    entry_points={
        'console_scripts': [
            'stv = stv.main:dispatch',
        ]
    }
)