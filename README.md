# ESHC Intranet
[ESHC Homepage](http://edinburghcoop.wordpress.com/)

## Goal
Make usable intranet.

## Testing Instructions
**Virtualenv recommended!**
Install Python3
1. Make venv for this project
2. Install Django in venv
3. Install waliki in venv
4. Clone repo into venv directory
5. Activate venv
6. run eshcIntranet/manage.py runserver
7. Go to 127.0.0.1:8000

## Features implemented
* Basic user login
* Basic new user registration
* User information displayed on profile page
* Store ESHC member specific information
* Allow user to edit profile information
* Basic Wiki - based on [waliki](https://github.com/mgaitan/waliki)

## Features wanted
* User management (available through 'admin')

## Stretch features wanted
* Lease management
* Extend wiki functionality
  * Side bars, no-link page list,
* Email verification/authentication?
* Automatically assign reference numbers to new users?
  * QBO integration? Maybe better to keep manual
* Proposal voting
* Polling
* Flat map
* Browse bylaws
* £££ Overview
* Style everything nicely

## Notes
* Uses the [waliki](https://github.com/mgaitan/waliki) app for wiki functionality. 
  * Had to modify the page creation views to use page.raw = " " instead of page.raw = "".
