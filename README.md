# ESHC Intranet
[ESHC Homepage](http://edinburghcoop.wordpress.com/)

## Goal
Make usable intranet.

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
