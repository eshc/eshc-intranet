# ESHC Intranet
[ESHC Homepage](http://edinburghcoop.wordpress.com/)

## Goal
Make usable intranet.

## Features implemented
* Basic user login
* Basic new user registration
* User information displayed on profile page
* Allow user to edit name and email address
* Basic Wiki

## Basic features wanted
* User management (available through 'admin')
* Store ESHC member specific information (eg. ref no.)
  * Will need ot extend th estandard User model to include more fields

## Stretch features wanted
* Email verification/authentication?
* Lease management
* Proposal voting
* Flat map
* Browse bylaws
* Polling
* £££ Overview

## Notes
* Uses the [waliki](https://github.com/mgaitan/waliki) app for wiki functionality. 
  * Had to modify the page creation views to use page.raw = " " instead of page.raw = "".
