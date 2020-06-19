#!/usr/bin/env python3.8

from datetime import date

DAY = date.today().isoformat()

ECCS2DIR = "/opt/eccs2"
ECCS2LOGSDIR = "%s/logs" % ECCS2DIR
ECCS2INPUTDIR = "%s/input" % ECCS2DIR

# Input
ECCS2LISTIDPSURL = 'https://technical.edugain.org/api.php?action=list_eccs_idps&format=json'
ECCS2LISTIDPSFILE = "%s/list_eccs_idps.json" % ECCS2INPUTDIR
ECCS2LISTFEDSURL = 'https://technical.edugain.org/api.php?action=list_feds&opt=1&format=json' 
ECCS2LISTFEDSFILE = "%s/list_fed.json" % ECCS2INPUTDIR

# Output
ECCS2RESULTSLOG = "eccs2_%s.log" % DAY
ECCS2CHECKSLOG = "eccs2checks_%s.log" % DAY
ECCS2SELENIUMLOGDIR = "%s/selenium-logs" % ECCS2DIR
ECCS2STDOUT = "%s/stdout.log" % ECCS2LOGSDIR
ECCS2STDERR = "%s/stderr.log" % ECCS2LOGSDIR

# Selenium Timeouts (in seconds)
ECCS2SELENIUMPAGELOADTIMEOUT = 30
ECCS2SELENIUMSCRIPTTIMEOUT = 30

# Selenium Debug Enable/Disable
ECCS2SELENIUMDEBUG = True

# Number of processes to run in parallel
ECCS2NUMPROCESSES = 20

# The 2 SPs that will be used to test each IdP
ECCS2SPS = ["https://sp24-test.garr.it/secure", "https://attribute-viewer.aai.switch.ch/eds/"]

# Registration Authority of Federations to exclude from the check
FEDS_BLACKLIST = [
   'http://www.surfconext.nl/',
   'https://www.wayf.dk',
   'http://feide.no/'
]

# EntityID of IDPs to exclude from the check
IDPS_BLACKLIST = [
   'https://iif.iucc.ac.il/idp/saml2/idp/metadata.php',
   'https://login.lstonline.ac.uk/idp/pingfederate',
   'https://idp.pearsoncollege.com/openathens',
   'https://idp.cambria.ac.uk/openathens',
   'https://idp.wnsc.ac.uk/idp/shibboleth',
   'https://indiid.net/idp/shibboleth',
   'https://idp.nulc.ac.uk/openathens',
   'https://lc-idp.lincolncollege.ac.uk/shibboleth',
   'https://oa-idp.wlv.ac.uk/oala/metadata',
   'https://idp.uel.ac.uk/shibboleth',
   'https://idp.ucreative.ac.uk/shibboleth',
   'https://idp.llandrillo.ac.uk/shibboleth',
   'https://idp-dev.cardiff.ac.uk/idp/shibboleth',
   'https://idp.kingston.ac.uk/shibboleth',   # iframe to load
   'https://shibboleth.aber.ac.uk/shibboleth',
   'https://sso.vu.lt/SSO/saml2/idp/metadata.php', # no standard login page
   'urn:mace:federation.org.au:testfed:uq.edu.au'
]
