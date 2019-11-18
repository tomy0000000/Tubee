# Tubee

![Python Version](https://img.shields.io/badge/python-3.4+-blue.svg)
[![Build Status](https://travis-ci.com/tomy0000000/Tubee.svg?token=pcX4zcaLzopbPNP4Hs2J&branch=master)](https://travis-ci.com/tomy0000000/Tubee)
[![codecov](https://codecov.io/gh/tomy0000000/Tubee/branch/master/graph/badge.svg?token=j6pUVAg2Wf)](https://codecov.io/gh/tomy0000000/Tubee)
[![liscense](https://img.shields.io/github/license/tomy0000000/Tubee.svg)](https://github.com/tomy0000000/Tubee/blob/master/LICENSE)

<p align="center">
    <img src="tubee/static/favicon.png" align="center">
    <br>
    <img width="150" src="tubee/static/img/tubee_text.png" align="center">
</p>

# Overview

Tubee is a web application, provides dozens of handful features related to YouTube.

The core functions is completly working, yet this application is still in development stage right now, please pm or leave issues if you run into any problems😘

# Installation

*Full guide will be released when stable version published, only important notice will be provided at the moment*

* Database (**Be aware that migration scripts will constantly modified during the whole dev stage**)
  * `MySQL`
    * The only fully-compatible-well-tested option...at least for now.
    * Please set encoding to `utf8mb4_unicode_ci` as video description can really be anything you couldn't expected.
  * `SQLite`
    * Might worked initially
    * Even though `render_as_batch=True` is set on Flask-Migrate, but upgrade scripts doesn't always works as expected.
  * `PostgreSQL`  
    * Doesn't compatible with hashed `user.password` field, might be fix in future patched.

# Features

* Channel Subscribing
  * New Video Push Notification (via [Pushover](https://pushover.net/), [LINE Notify](https://notify-bot.line.me))
  * New Video to Playlist
  * New Video Download (Save to Dropbox)

## More on the Way

* Channel Inspection
* Audio Streaming

# Config

* Environment Variables
  * `SERVER_NAME`
  * `APPLICATION_ROOT`
  * `SECRET_KEY`
  * `DATABASE_URL`
  * `REDIS_PASSWORD`, `REDIS_HOST`, `REDIS_PORT`, `REDIS_DB`
* `YOUTUBE_API_DEVELOPER_KEY`
  * `PUSHOVER_TOKEN`
* Files
  * `instance/client_secret`

### Testing/Deployment

* Travis CI
  * `.travis.yml`

* Heroku
  * `Procfile`
