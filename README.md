# ESHC Intranet
[ESHC Homepage](http://edinburghcoop.wordpress.com/)

[Heroku deployment](https://eshc.herokuapp.com/)

## Goal
Make usable intranet.

## Testing Instructions
**Virtualenv recommended!**
Install Python3
1. Make venv for this project
2. Activate venv
3. Install Django in venv
4. Install waliki in venv
5. Clone repo into venv directory
6. run eshcIntranet/manage.py runserver
7. Go to 127.0.0.1:8000

### New Testing Instructions
create folder

clone repo to folder

virtualenv venv

pip install -r eshcIntranet/requirements.txt in venv

uses postgresql on heroku so to mimic the heroku setup completely install postgress locally

[postgres database creation tutorial](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04)

can also develop using SQLite (will need a different setting.py file setup to use SQLite locally and keep postgreql on heroku)

with either setup before running server migrate databse and collectstatic 

## Features implemented
* Allauth based user management 
* User information displayed on profile page
* Basic Wiki - based on [waliki](https://github.com/mgaitan/waliki) - modified
* User management available through admin app
* Lease management - admin and user sides
* Mark Users as deactivated when they have moved out 
* 'Share received' checkbox for admins, display on user profile
* Style everything nicely (Bootstrap 3.3.0)
* Navbar
* Waliki app copied to main directory 
* Wiki change history button appears in navbar again
* Email sending - uses finance acc
* Email verification/authentication - allauth
* Store ESHC member specific information - check if properly compatible with allauth

## Features wanted
* Allow user to edit relevant profile information
* List created wiki pages
* Polling - can probably be later adapted to proposal voting
* Admin approval of users

### Leases app
* ~~Prompt if no valid lease registered~~
* Notify that lease will run out some months before end (via email?)
* ~~Add 'date_signed' field~~
* ~~Fill out inventory information - only allowed once~~
* Generate customised PDF ready for signing - user can print on their own
* TESTS

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

## Stretch features wanted
* GM help?  
  * Agenda forming?
* Extend wiki functionality
  * Side bars, no-link page list,
  * Per page comments section?
* Automatically assign reference numbers to new users?
  * QBO integration? Maybe better to keep manual
* Proposal voting
* Calendar?
* Flat map
* Browse bylaws - subset of wiki
* £££ Overview

## Implementation Questions
* mySQL? Heroku uses PostgreSQL, so maybe stick with that?
* Deploy to web? Heroku dynos? How many would we need? It'd be nice if they don't sleep
* Static files for wiki etc. S3 AWS recommended, requires credit card. Should cost micropennies

## Notes
* Uses the [waliki](https://github.com/mgaitan/waliki) app for wiki functionality. 
  * Had to modify the page creation views to use page.raw = " " instead of page.raw = "".
* Uses bootstrap v3.3.0
* If we decide to continue with Heroku, then to actually host the wiki (and any other files) we'll need S3 AWS
