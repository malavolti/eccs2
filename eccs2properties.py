#!/usr/bin/env python3.8

from datetime import date

day = date.today().isoformat()

ECCS2PATH = "/opt/eccs2"
ECCS2LOGSPATH = "%s/logs" % ECCS2PATH
ECCS2INPUTPATH = "%s/input" % ECCS2PATH

# Input
ECCS2LISTIDPSURL = 'https://technical.edugain.org/api.php?action=list_eccs_idps&format=json'
ECCS2LISTIDPSFILE = "%s/list_eccs_idps.json" % ECCS2INPUTPATH
ECCS2LISTFEDSURL = 'https://technical.edugain.org/api.php?action=list_feds&opt=1&format=json' 
ECCS2LISTFEDSFILE = "%s/list_fed.json" % ECCS2INPUTPATH

# Output
ECCS2RESULTSLOG = "eccs2_%s.log" % day
ECCS2CHECKSLOG = "eccs2checks_%s.log" % day
ECCS2SELENIUMLOG = "%s/selenium_chromedriver.log" % ECCS2LOGSPATH
ECCS2STDOUT = "%s/stdout.log" % ECCS2LOGSPATH
ECCS2STDERR = "%s/stderr.log" % ECCS2LOGSPATH

# Selenium Log Levels
# 0: All     (Show all log messages)
# 1: Debug   (Show messages with information useful for debugging)
# 2: Info    (Show informational messages)
# 3: Warning (Show messages corresponding to non-critical issues)
# 4: Severe  (Show messages corresponding to critical issues)
# 5: Off     (Show no log messages)
ECCS2SELENIUMLOGLEVEL = 4 

# Number of processes to run in parallel
ECCS2NUMPROCESSES = 15

# Registration Authority of Federations to exclude from the check
FEDS_BLACKLIST = [
   'http://www.surfconext.nl/',
   'https://www.wayf.dk',
   'http://feide.no/'
]

# EntityID of IDPs to exclude from the check
IDPS_BLACKLIST = [
]
