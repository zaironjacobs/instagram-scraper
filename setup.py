from setuptools import setup
from setuptools import find_packages
from instagram_scraper.console_name import __console_name__
from instagram_scraper.version import __version__

with open('README.md', 'r') as fh:
    long_description = fh.read()

requires = [
    'colorama>=0.4.3',
    'requests>=2.24.0',
    'selenium>=3.141.0',
    'urllib3>=1.25.10',
    'wget>=3.2',
    'simplejson>=3.17.2',
    'get-chromedriver>=1.1.0',
    'pytest>=6.1.0'
]

setup(
    name=__console_name__,
    version=__version__,
    author='Zairon Jacobs',
    author_email='zaironjacobs@gmail.com',
    description=('A command line application that uses Selenium to download all posts '
                 'and stories from an Instagram profile.'),
    long_description=long_description,
    url='https://github.com/zaironjacobs/instagram-scraper',
    download_url='https://github.com/zaironjacobs/instagram-scraper/archive/v' + __version__ + '.tar.gz',
    keywords=['instagram', 'scraper', 'download', 'photos', 'pictures', 'videos', 'selenium'],
    packages=find_packages(),
    entry_points={
        'console_scripts': [__console_name__ + '=instagram_scraper.app:main'],
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
