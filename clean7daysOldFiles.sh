#!/bin/bash

BASEDIR=/var/www/html/eccs2

# Remove ECCS2 result older than 7 days
find $BASEDIR/output/* -mtime +6 -type f -delete

# Remove ECCS2 logs older than 7 days
find $BASEDIR/logs/* -mtime +6 -type f -delete

# Remove ECCS2 HTML code older than 7 days
find $BASEDIR/html/* -mtime +6 -type f -delete
find $BASEDIR/html -type d -empty -delete
