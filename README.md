# happy-rabbit
Happy Rabbit is a service that inspires kids to perform activities on a regular basis by earning carrots.
Happy Rabbit experience is powered by gamification and behavioural psychology. We are confindent that your children
will have lots of fun making boring math, learning chess, jogging or helping parents with household.  

# Tech-Stack
* Admin and API: API and Admin
* telegram bot: python-telegram-bot + dramatiq+periodiq + redis 
* storage: 
  * Admin powered by Postgres
  * Google Spreadsheet for activity records 
* CI/CD: deployment Dokku + GitHub Actions template

[![Sparkline](https://stars.medv.io/Rustem/kz-geekabitz-happy-rabbit.svg)](https://stars.medv.io/Rustem/kz-geekabitz-happy-rabbit)


### Check the example bot that uses the code from Main branch: [t.me/happy-rabbit](https://t.me/happy-rabbit)

## Features

Design of the project is wrapped in [google-doc](https://docs.google.com/document/d/1epWaq-Y69iot4fWCFkCu6dX0CYvjH--mz87mK1H7yeU/edit?usp=sharing).

## Documentation

* Admin panel (thanks to [Django](https://docs.djangoproject.com/en/3.1/intro/tutorial01/))
* Background jobs using [Dramatiq](https://dramatiq.io/motivation.html) and crontab scheduling with [Periodiq](https://pypi.org/project/periodiq/). 
* [Production-ready](https://github.com/Rustem/kz-geekabitz-happy-rabbit/wiki/Production-Deployment-using-Dokku) deployment using [Dokku](https://dokku.com)
* Telegram API usage in pooling or [webhook mode](https://core.telegram.org/bots/api#setwebhook)


# How to run

## Quickstart: Pooling & SQLite

The fastest way to run the bot is to run it in pooling mode using SQLite database without Periodiq workers for background tasks. This should be enough for quickstart:

``` bash
git clone https://github.com/Rustem/kz-geekabitz-happy-rabbit
cd django-telegram-bot
```

Create virtual environment (optional)
``` bash
python3 -m venv happy-rabbit-venv
source happy-rabbit-venv/bin/activate
```

Install all requirements:
```
pip3 install -r requirements.txt
```

Create `.env` file in root directory and copy-paste this:
``` bash 
DJANGO_DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
TELEGRAM_TOKEN=<ENTER YOUR TELEGRAM TOKEN HERE>
```

Run migrations to setup SQLite database:
``` bash
python manage.py migrate
```

Create superuser to get access to admin panel:
``` bash
python manage.py createsuperuser
```

Run bot in pooling mode:
``` bash
python manage-bot.py 
```

If you want to open Django admin panel which will be located on http://localhost:8000/admin/:
``` bash
python manage.py runserver
```

## Run locally using docker-compose

If you like docker-compose you can check [full instructions in our Wiki](TBD).

## Deploy to Production 

Read Wiki page on how to [deploy production-ready](TBD).

----
