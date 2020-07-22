#!/usr/bin/env python3.8

from datetime import date

DAY = date.today().isoformat()

ECCS2DIR = "/opt/eccs2"

# Input
ECCS2INPUTDIR = "%s/input" % ECCS2DIR
ECCS2LISTIDPSURL = 'https://technical.edugain.org/api.php?action=list_eccs_idps&format=json'
ECCS2LISTIDPSFILE = "%s/list_eccs_idps.json" % ECCS2INPUTDIR
ECCS2LISTFEDSURL = 'https://technical.edugain.org/api.php?action=list_feds&opt=1&format=json' 
ECCS2LISTFEDSFILE = "%s/list_fed.json" % ECCS2INPUTDIR

# Output
ECCS2OUTPUTDIR = "%s/output" % ECCS2DIR
ECCS2RESULTSLOG = "eccs2_%s.log" % DAY
ECCS2HTMLDIR = "%s/html" % ECCS2DIR

# Selenium
ECCS2SELENIUMDEBUG = False
ECCS2SELENIUMLOGDIR = "%s/selenium-logs" % ECCS2DIR
ECCS2SELENIUMPAGELOADTIMEOUT = 30 #seconds
ECCS2SELENIUMSCRIPTTIMEOUT = 30   #seconds

# Logs
ECCS2LOGSDIR = "%s/logs" % ECCS2DIR
ECCS2STDOUT = "%s/stdout_%s.log" % (ECCS2LOGSDIR,DAY)
ECCS2STDERR = "%s/stderr_%s.log" % (ECCS2LOGSDIR,DAY)
ECCS2FAILEDCMD = "%s/failed-cmd.sh" % ECCS2LOGSDIR
ECCS2STDOUTIDP = "%s/stdout_idp_%s.log" % (ECCS2LOGSDIR,DAY)
ECCS2STDERRIDP = "%s/stderr_idp_%s.log" % (ECCS2LOGSDIR,DAY)
ECCS2FAILEDCMDIDP = "%s/failed-cmd-idp.sh" % ECCS2LOGSDIR

# Number of processes to run in parallel
ECCS2NUMPROCESSES = 25

# The 2 SPs that will be used to test each IdP
ECCS2SPS = ["https://sp24-test.garr.it/Shibboleth.sso/Login?entityID=", "https://attribute-viewer.aai.switch.ch/Shibboleth.sso/Login?entityID="]

# ROBOTS.TXT
ROBOTS_USER_AGENT = "ECCS/2.0 (+https://dev-mm.aai-test.garr.it/eccs2)"

# Registration Authority of Federations to exclude from the check
FEDS_BLACKLIST = [
   'http://www.surfconext.nl/',
   'https://www.wayf.dk',
   'http://feide.no/'
]

# EntityID of IDPs to exclude from the check
IDPS_BLACKLIST = [
   'https://idp.eie.gr/idp/shibboleth',
   'https://edugain-proxy.igtf.net/simplesaml/saml2/idp/metadata.php',
   'https://gn-vho.grnet.gr/idp/shibboleth',
   'https://wtc.tu-chemnitz.de/shibboleth',
   'https://idp.utorauth.utoronto.ca/shibboleth',
   'https://login.lstonline.ac.uk/idp/pingfederate',
   'https://idp.cambria.ac.uk/openathens',
   'https://indiid.net/idp/shibboleth',
   'https://idp.nulc.ac.uk/openathens',
   'https://lc-idp.lincolncollege.ac.uk/shibboleth',
   'https://boleth.chi.ac.uk/idp/shibboleth',
   'https://idp.wnsc.ac.uk/idp/shibboleth',
   'https://idp.strodes.ac.uk/shibboleth',
   'https://idp.ucreative.ac.uk/shibboleth',
   'https://idp.llandrillo.ac.uk/shibboleth',
   'https://idp.uel.ac.uk/shibboleth',
   'https://idp-dev.cardiff.ac.uk/idp/shibboleth',
   'https://sso.vu.lt/SSO/saml2/idp/metadata.php',
   #'https://ssl.education.lu/saml/saml2/idp/metadata.php',
   'https://iif.iucc.ac.il/idp/saml2/idp/metadata.php'
]
