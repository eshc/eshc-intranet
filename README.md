# ESHC Intranet

[ESHC Homepage](http://eshc.coop/)

[Deployment](https://intranet.eshc.coop/)

## Goal
Make usable intranet.

## Local Development Instructions
1. Install a relatively modern version of Python 3 (3.12 is recommended but other versions might also work)
2. Install [uv](https://docs.astral.sh/uv/getting-started/installation/), a Python package and project manager
3. `git clone <repo_url>` and `cd` into the directory  
5. Run `uv sync` (if you do not have postgres installed on your local machine, you might have to edit the `pyproject.toml` file to replace `psycopg` with `psycopg-binary`
6. Run `uv venv`
7. Copy env file `cp .env.dev .env`
    - This will use a local sqlite database and setup logging.
8. Run `python manage.py makemigrations`, `python manage.py migrate`, `python manage.py collectstatic`, `python manage.py createcachetable`. In order, these set up the required changes to the database, appy the changes, and collect static files into the `/staticfiles/` folder for serving.
9. Run `python manage.py runserver`.
10. Go to `localhost:8000` to access the site or `localhost:8000/admin/` to view the admin panel.
11. To use the admin panel run `python manage.py createsuperuser` and follow the instructions to create an admin user.

## Deployment Setup
- Production environment variables are stored in vaultwarden.
- These are loaded from `.env` file on the host.
- Currently deployed using docker compose

## Updating
1. Upon push to `main`, a github action builds and pushes to `ghcr.io/eshc/eshc-intranet:main`. Its also tagged with its commit hash.
2. Connect to the host running the container (via proxmox) and redeploy. Currently, just using docker compose.
  > docker compose pull
  > docker compose up -d
3. Check that its working.
    - If it's not working, you may wish to revert to an older commit by modifying the `docker-compose.yml` on the host.


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
