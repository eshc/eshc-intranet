# ESHC Intranet

[ESHC Homepage](http://eshc.coop/)

[Deployment](https://intranet.eshc.coop/)

## Goal
Make usable intranet.

## Setup Instructions
1. Install Python 3. Developed using version 3.5.2.
2. Install poetry
3. `git clone <repo_url>` and `cd` into the directory  
5. Run `poetry install` 
6. Run `poetry shell`

Follow the instructions on setting up a [postgres database](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04) if you want to set up the database in the same way it is set up on Heroku. Set it up using the settings in `settings.py`.

If not, you can probably just use SQLite locally, but you'll have to use the commented out database setup in `settings.py`.

## Testing Instructions
1. Create a local_settings.py file in the eshcIntranet directory with the following contents:
 ```python
import os

DEBUG = True
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DEFAULT_FILE_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
MEDIA_FILE_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
SECRET_KEY = 'none'
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
 ```
2. Run `python manage.py makemigrations`, `python manage.py migrate`, `python manage.py collectstatic`, `python manage.py createcachetable`. In order, these set up the required changes to the database, appy the changes, and collect static files into the `/staticfiles/` folder for serving.
3. Run `python manage.py runserver`.
4. Go to 127.0.0.1:8000 to access the site or 127.0.0.1:8000/admin/ to view the admin panel.
5. To use the admin panel run `python manage.py createsuperuser` and follow the instructions to create an admin user.

## Features implemented
* Allauth based user management 
* User information displayed on profile page
* ~~Basic Wiki - based on [waliki](https://github.com/mgaitan/waliki) - modified~~ uses django-wiki
* User management available through admin app
* Lease management - admin and user sides
* Mark Users as deactivated when they have moved out 
* 'Share received' checkbox for admins, display on user profile
* Style everything nicely (Bootstrap 3.3.0)
* Navbar
* ~~Waliki app copied to main directory~~
* ~~Wiki change history button appears in navbar again~~
* ~~Email sending - uses finance acc~~ uses Sendgrid now
* Email verification/authentication - allauth
* Store ESHC member specific information 
* Polling - can probably be later adapted to proposal voting
* Allow user to edit relevant profile information
* Allows users to sign up to / become members of specific working grops
* Flat info / map
* GM Agenda making

### Leases app
* ~~Prompt if no valid lease registered~~
* ~~Add 'date_signed' field~~
* ~~Fill out inventory information - only allowed once~~

### Proposals app
* ~~add who added it~~
* ~~add some proposal text~~
  * ~~Formatting? Upload markdown? Paste markdown and render on detail page?~~
  * ~~Preview of markdown before submission~~
* ~~add form for adding proposal~~
* ~~add option to remove proposal~~
* ~~List proposals currently open for voting~~
* ~~Add result to model~~
* ~~Vote counting and single vote per user~~
  * ~~Display number of votes~~
* Option to edit a proposal

## Stretch features wanted
* Browse bylaws - subset of wiki / or its own, non-editable section
* User directory:
  * Shows convenors
* ~~Cash overview~~
  * Open budgets
  * Open proposals with money status
* Moving refunds and liaisons to the intranet? Make public list of refunds?

## Implementation Questions
* mySQL? Heroku uses PostgreSQL, so maybe stick with that?
* Deploy to web? Heroku dynos? How many would we need? It'd be nice if they don't sleep
* Static files for wiki etc. S3 AWS recommended, requires credit card. Should cost micropennies

## Notes
* Uses bootstrap v3.3.0
* AWS S3 for static files in production
* Uses django-wiki
