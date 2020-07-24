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
ECCS2REQUESTSTIMEOUT = 15   #seconds

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

# { 'reg_auth':'reason' }
FEDS_DISABLED_DICT = {
   'http://www.surfconext.nl/':'Federation excluded from check',
   'https://www.wayf.dk':'Federation excluded from check',
   'http://feide.no/':'Federation excluded from check'
}

# { 'entityid_idp':'reason' }
IDPS_DISABLED_DICT = {
   'https://idp.eie.gr/idp/shibboleth':'Disabled on 2019-04-24 because ECCS cannot check non-standard login page',
#   'https://edugain-proxy.igtf.net/simplesaml/saml2/idp/metadata.php':'Disabled on 2017-03-17 on request of federation operator',
   'https://gn-vho.grnet.gr/idp/shibboleth':'Disabled on 2019-04-24 because basic authentication is not supported by ECCS check',
   'https://wtc.tu-chemnitz.de/shibboleth':'Disabled on 2019-02-26 because ECCS cannot check non-standard login page',
#   'https://idp.utorauth.utoronto.ca/shibboleth':'Disabled on 2015-08-17 because login on this IdP requires JavaScript, which is not supported by the check',
   'https://login.lstonline.ac.uk/idp/pingfederate':'Disabled on 2017-02-08 on request of federation operator',
   'https://idp.cambria.ac.uk/openathens':'Disabled on 2017-10-27 on request of federation operator',
   'https://indiid.net/idp/shibboleth':'Disabled on 2017-10-27 on request of federation operator',
   'https://idp.nulc.ac.uk/openathens':'Disabled on 2017-10-27 on request of federation operator',
#   'https://lc-idp.lincolncollege.ac.uk/shibboleth':'Disabled on 2015-08-17 because uses HTTP Basic authentication, which cannot be checked reliably',
#   'https://boleth.chi.ac.uk/idp/shibboleth':'Disabled on 2015-08-17 because uses HTTP Basic authentication, which cannot be checked reliably',
   'https://idp.wnsc.ac.uk/idp/shibboleth':'Disabled on 2017-10-27 on request of federation operator',
#   'https://idp.strodes.ac.uk/shibboleth':'Disabled on 2015-08-17 because uses HTTP Basic authentication, which cannot be checked reliably',
   'https://idp.ucreative.ac.uk/shibboleth':'Disabled on 2017-10-27 on request of federation operator',
   'https://idp.llandrillo.ac.uk/shibboleth':'Disabled on 2017-10-27 on request of federation operator',
   'https://idp.uel.ac.uk/shibboleth':'Disabled on 2017-10-27 on request of federation operator',
   'https://idp-dev.cardiff.ac.uk/idp/shibboleth':'Disabled on 2017-02-08 on request of federation operator',
   'https://sso.vu.lt/SSO/saml2/idp/metadata.php':'Disabled on 2018-11-02 because ECCS cannot check non-standard login page',
   #'https://ssl.education.lu/saml/saml2/idp/metadata.php':'Disabled on 2018-11-06 ECCS cannot check non-standard login page',
   'https://iif.iucc.ac.il/idp/saml2/idp/metadata.php':'Disabled on 2018-11-06 ECCS cannot check non-standard login page'
}
