#!/bin/bash

# Remove ECCS2 result older than 7 days
find $HOME/eccs2/output/* -mtime +6 -type f -delete

# Remove ECCS2 logs older than 7 days
find $HOME/eccs2/logs/* -mtime +6 -type f -delete

# Remove ECCS2 HTML code older than 7 days
find $HOME/eccs2/html/* -mtime +6 -type f -delete
