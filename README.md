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
* Mark Users as deactivated when they have moved out 
* 'Share received' checkbox for admins, display on user profile

## Features wanted

### Leases app
* Prompt if no valid lease registered
* Notify that lease will run out some months before end (via email?)
* Add 'date_signed' field
* Fill out inventory information - time limited editing, +7 days from date_signed
* Generate customised PDF ready for signing - user can print on their own
* TESTS

## Stretch features wanted
* Extend wiki functionality
  * Side bars, no-link page list,
  * Per page comments section?
* Email verification/authentication?
* Email sending
* Automatically assign reference numbers to new users?
  * QBO integration? Maybe better to keep manual
* Proposal voting
* Calendar?
* Polling
* Flat map
* Browse bylaws - subset of wiki
* £££ Overview
* Style everything nicely
* 'Share received' indicator in profile
* Option to change password
* mySQL? Deploy and see
* Deploy to web?

## Notes
* Uses the [waliki](https://github.com/mgaitan/waliki) app for wiki functionality. 
  * Had to modify the page creation views to use page.raw = " " instead of page.raw = "".
