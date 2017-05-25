# ESHC Intranet
[ESHC Homepage](http://edinburghcoop.wordpress.com/)

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

## Features implemented
* Basic user login
* Basic new user registration
* User information displayed on profile page
* Store ESHC member specific information
* Allow user to edit relevant profile information
* Basic Wiki - based on [waliki](https://github.com/mgaitan/waliki)
* User management available through admin app
* Lease management - admin and user sides

## Features wanted
  * ~~App called 'leases'~~
  * ~~Display all leases to admins - allow add, edit, etc.~~
  * ~~Display all leases connected to a user to the user~~
    * ~~Start date, end date, room~~
* Mark Users as deactivated when they have moved out

## Stretch features wanted
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
* 'Share received' indicator in profile
* Option to change password

## Notes
* Uses the [waliki](https://github.com/mgaitan/waliki) app for wiki functionality. 
  * Had to modify the page creation views to use page.raw = " " instead of page.raw = "".
