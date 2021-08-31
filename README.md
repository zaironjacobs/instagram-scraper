Instagram Scraper - DEPRECATED
=================

A command-line application that uses Selenium to download all posts from an Instagram profile.

## Install

To install:

```console
$ python setup.py install
```

## Usage

Create a new directory and cd into the directory.

*Use --max to specify a maximum amount of posts to scrape*

Scrape a profile:

```console
$ igscraper username1 username2 username3 --max 5
```

To scrape stories you have to be logged in first:

```console
$ igscraper username1 username2 username3 --max 5 --stories --login-username username
```

Scrape a tag:

```console
$ igscraper --recent-tags tag1 tag2 --max 10
```

```console
$ igscraper --top-tags tag1 tag2 --max 3
```

List all scraped users or tags:

```console
$ igscraper --list-users
```

```console
$ igscraper --list-tags
```

Remove users or tags:

```console
$ igscraper --remove-users username1 username2
```

```console
$ igscraper --remove-tags tag1 tag2
```

Remove users or tags by list number:

```console
$ igscraper --remove-users-n 1 2
```

```console
$ igscraper --remove-tags-n 1 2
```

#### Downloads can be found at:

*`<current directory>/<users>/<username>/<display_photo>`*

*`<current directory>/<users>/<username>/<posts>`*

*`<current directory>/<users>/<username>/<stories>`*

*`<current directory>/<tags>/<tag>/<top>`*

*`<current directory>/<tags>/<tag>/<recent>`*

*Scraping the same profile again will only download new posts, provided that you are inside the same directory when you
run the program again.*

## Options

```
--help                  Show help message and exit.

--login-username        Instagram login username.

--update-users          Check all previously scraped users for new posts.

--top-tags              Top tags to scrape.

--recent-tags           Recent tags to scrape (also provide a maximum amount of posts to download with --max).

--max                   Maximum number of posts to scrape.

--stories               Scrape stories also.

--headful               Display the browser UI.

--list-users            List all scraped users.

--list-tags             List all scraped tags.

--remove-users          Remove user(s).

--remove-users-n        Remove user(s) by number.

--remove-all-users      Remove all users.

--remove-tags           Remove tag(s).

--remove-tags-n         Remove tag(s) by number.

--remove-all-tags       Remove all tags.

--log                   Create log file.

--version               Program version.
```