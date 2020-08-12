Instagram Scraper
=================
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/igscraper?color=blue)](https://pypi.python.org/pypi/igscraper)
[![PyPI](https://img.shields.io/pypi/v/igscraper?color=blue)](https://pypi.python.org/pypi/igscraper)
[![PyPI - Status](https://img.shields.io/pypi/status/igscraper)](https://pypi.python.org/pypi/igscraper)
[![PyPI - License](https://img.shields.io/pypi/l/igscraper)](https://pypi.python.org/pypi/igscraper)

A command-line application that uses Selenium to download all posts and stories from an Instagram profile.

How to install
-----
To install:
```bash
$ pip install igscraper
```

To upgrade:
```bash
$ pip install igscraper --upgrade
```

How to use
-----

Create a new directory for the downloads, then cd into the directory and run the program.

Scrape a profile:
```bash
$ igscraper username1 username2 username3
```

*With --max you can provide a maximum amount of posts to download*

To scrape stories you have to be logged in first. Login and scrape a profile:
```bash
$ igscraper username1 username2 username3 --login-username username
```

Scrape a tag:
```bash
$ igscraper --recent-tags tag1 tag2 --max 10
```

```bash
$ igscraper --top-tags tag1 tag2
```

List all scraped users or tags:
```bash
$ igscraper --list-users
```

```bash
$ igscraper --list-tags
```

Remove users or tags:
```bash
$ igscraper --remove-users username1 username2
```

```bash
$ igscraper --remove-tags tag1 tag2
```

Alternative method to remove users or tags by list number:
```bash
$ igscraper --remove-users-n 1 2
```

```bash
$ igscraper --remove-tags-n 1 2
```

Downloads can be found at:

*`<current directory>/<users>/<username>/<display_photo>`*

*`<current directory>/<users>/<username>/<posts>`*

*`<current directory>/<users>/<username>/<stories>`*

*`<current directory>/<tags>/<tag>/<top>`*

*`<current directory>/<tags>/<tag>/<recent>`*

*Scraping the same profile again will only download new posts, provided that you are inside the same directory 
when you run the program again.*

*Scraping too much will get your IP address temporarily restricted by Instagram, this means that you can not
view any posts without being logged in.*

Options
-------

```
--help                  Show help message and exit.

--login-username        Instagram login username.

--update-users          Check all scraped users for new posts.

--top-tags              Top tags to scrape.

--recent-tags           Recent tags to scrape (also provide a maximum amount to download with --max).

--max                   Maximum number of posts to scrape.

--set-driver            Choose a webdriver.

--headful               Display the browser UI.

--list-users            List all scraped users.

--list-tags             List all scraped tags.

--remove-users          Remove user(s).

--remove-users-n        Remove user(s) by number.

--remove-all-users      Remove all users.

--remove-tags           Remove tag(s).

--remove-tags-n         Remove tag(s) by number.

--remove-all-tags       Remove all tags.

--version               Program version.
```