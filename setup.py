from setuptools import setup
from setuptools import find_packages
from instagram_scraper.version import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

requires = [
    'colorama>=0.4.3',
    'requests>=2.23.0',
    'selenium>=3.141.0',
    'urllib3>=1.25.9',
    'wget>=3.2',
    'simplejson>=3.17.0'
]

setup(
    name='igscraper',
    version=__version__,
    author='Zairon Jacobs',
    author_email='zaijacobs@gmail.com',
    description=('A command line application that uses Selenium to download all posts '
                 'and stories from an Instagram profile.'),
    long_description=long_description,
    url='https://github.com/zaijacobs/instagram-scraper',
    download_url='https://github.com/zaijacobs/instagram-scraper/archive/v' + __version__ + '.tar.gz',
    keywords=['instagram', 'scraper', 'download', 'photos', 'pictures', 'videos', 'selenium'],
    packages=find_packages(),
    entry_points={
        'console_scripts': ['igscraper=instagram_scraper.app:main'],
    },
    install_requires=requires,
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Natural Language :: English'
    ],
    python_requires='>=3.8',
)
