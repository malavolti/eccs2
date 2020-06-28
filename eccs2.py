#!/usr/bin/env python3.8

import argparse
import datetime
import json
import re
import requests
import time

from eccs2properties import DAY, ECCS2HTMLDIR, ECCS2OUTPUTDIR, ECCS2RESULTSLOG, ECCS2CHECKSLOG, FEDS_BLACKLIST, IDPS_BLACKLIST, ECCS2SPS, ECCS2SELENIUMDEBUG
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, UnexpectedAlertPresentException
from urllib3.exceptions import MaxRetryError
from urllib3.util import parse_url
from utils import getLogger, getIdPContacts, getDriver


"""
The script works with 2 SPs that using Shibboleth Embedded Discovery Service to allow IdP selection on their login page.
The script has been written to simulate an user that inserts the IdP's entityID into the EDS search box and press "Enter" to load its Login Page. The Login Page MUST presents the fields "username" and "password" to pass the check on each SP involved into the test.
If the IdP Login page presente the fields for both selected SP the test is passed, otherwise it is failed.
"""

# Returns the FQDN to use on the HTML page_source files
def getIDPfqdn(entityIDidp):
    if entityIDidp.startswith('http'):
       return parse_url(entityIDidp)[2]
    else:
       return entityIDidp.split(":")[-1] 


# The function check that the IdP recognized the SP by presenting its Login page.
# If the IdP Login page contains "username" and "password" fields, than the test is passed.
def checkIdP(sp,idp):
   # Chromedriver MUST be instanced here to avoid problems with SESSION

   # Disable SSL requests warning messages
   requests.packages.urllib3.disable_warnings()

   debug_selenium = ECCS2SELENIUMDEBUG
   fqdn_idp = parse_url(idp['entityID'])[2]
   driver = getDriver(fqdn_idp,debug_selenium)

   # Exception of WebDriver raises
   if (driver == None):
      return None

   # Configure Blacklists
   federation_blacklist = FEDS_BLACKLIST
   entities_blacklist = IDPS_BLACKLIST 

   fqdn_idp = getIDPfqdn(idp['entityID'])
   fqdn_sp = parse_url(sp)[2]
   wayfless_url = sp + idp['entityID']

   if (idp['registrationAuthority'] in federation_blacklist):
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

      with open("%s/%s/%s---%s.html" % (ECCS2HTMLDIR,DAY,fqdn_idp,fqdn_sp),"w") as html:
           html.write("Federation excluded from check")
      return (idp['entityID'],wayfless_url,check_time,"NULL","DISABLED")

   if (idp['entityID'] in entities_blacklist):
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

      with open("%s/%s/%s---%s.html" % (ECCS2HTMLDIR,DAY,fqdn_idp,fqdn_sp),"w") as html:
           html.write("Identity Provider excluded from check")
      return (idp['entityID'],wayfless_url,check_time,"NULL","DISABLED")

   # Open SP, select the IDP from the EDS and press 'Enter' to reach the IdP login page to check
   try:
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
      driver.get(wayfless_url)
      page_source = driver.page_source
      samlrequest_url = driver.current_url

      # Put the page_source into an appropriate HTML file
      with open("%s/%s/%s---%s.html" % (ECCS2HTMLDIR,DAY,fqdn_idp,fqdn_sp),"w") as html:
           html.write(page_source)

   except TimeoutException as e:
     # Put an empty string into the page_source file
     with open("%s/%s/%s---%s.html" % (ECCS2HTMLDIR,DAY,fqdn_idp,fqdn_sp),"w") as html:
          html.write("")
     return (idp['entityID'],wayfless_url,check_time,"(failed)","Timeout")

   except NoSuchElementException as e:
     # The input of the bootstrap tables are provided by "eccs2" and "eccs2checks" log.
     # If I don't return anything and I don't put anything in the logger
     # I'll not write on the input files for the table
     # and I can re-run the command that caused the exception from the "stdout.log" file.
     print("!!! NO SUCH ELEMENT EXCEPTION - RUN AGAIN THE COMMAND !!!")
     return None

   except Exception as e:
     print ("!!! EXCEPTION !!!")
     print (e.__str__())
     print ("IdP: %s\nSP: %s" % (idp['entityID'],sp))
     return None

   finally:
     driver.quit()

   pattern_metadata = "Unable.to.locate(\sissuer.in|).metadata(\sfor|)|no.metadata.found|profile.is.not.configured.for.relying.party|Cannot.locate.entity|fail.to.load.unknown.provider|does.not.recognise.the.service|unable.to.load.provider|Nous.n'avons.pas.pu.(charg|charger).le.fournisseur.de service|Metadata.not.found|application.you.have.accessed.is.not.registered.for.use.with.this.service|Message.did.not.meet.security.requirements"

   pattern_username = '<input[\s]+[^>]*((type=\s*[\'"](text|email)[\'"]|user)|(name=\s*[\'"](name)[\'"]))[^>]*>';
   pattern_password = '<input[\s]+[^>]*(type=\s*[\'"]password[\'"]|password)[^>]*>';

   metadata_not_found = re.search(pattern_metadata,page_source, re.I)
   username_found = re.search(pattern_username,page_source, re.I)
   password_found = re.search(pattern_password,page_source, re.I)

   try:
      headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
      status_code = str(requests.get(samlrequest_url, headers=headers, verify=False, timeout=30).status_code)

   except requests.exceptions.ConnectionError as e:
     #print("!!! REQUESTS STATUS CODE CONNECTION ERROR EXCEPTION !!!")
     #print (e.__str__())
     #print ("IdP: %s\nSP: %s" % (idp['entityID'],sp))
     status_code = "(failed)"

   except requests.exceptions.Timeout as e:
     #print("!!! REQUESTS STATUS CODE TIMEOUT EXCEPTION !!!")
     #print (e.__str__())
     #print ("IdP: %s\nSP: %s" % (idp['entityID'],sp))
     status_code = "111"

   except requests.exceptions.TooManyRedirects as e:
     #print("!!! REQUESTS TOO MANY REDIRECTS EXCEPTION !!!")
     #print (e.__str__())
     #print ("IdP: %s\nSP: %s" % (idp['entityID'],sp))
     status_code = "222"

   except requests.exceptions.RequestException as e:
     print ("!!! REQUESTS EXCEPTION !!!")
     print (e.__str__())
     print ("IdP: %s\nSP: %s" % (idp['entityID'],sp))
     status_code = "333"

   except Exception as e:
     print ("!!! EXCEPTION !!!")
     print (e.__str__())
     print ("IdP: %s\nSP: %s" % (idp['entityID'],sp))
     status_code = "555"

   if(metadata_not_found):
      return (idp['entityID'],wayfless_url,check_time,status_code,"No-eduGAIN-Metadata")
   elif not username_found or not password_found:
      return (idp['entityID'],wayfless_url,check_time,status_code,"Invalid-Form")
   else:
      return (idp['entityID'],wayfless_url,check_time,status_code,"OK")


# Extract IdP DisplayName by fixing input string
def getDisplayName(display_name):
    display_name_equal_splitted = display_name.split('==')
    for elem in display_name_equal_splitted:
        if "en" in elem:
           if "&apos;" in elem:
               elem = elem.replace("&apos;","'")
           if "&#039;" in elem:
               elem = elem.replace("&#039;","'")
           return elem.split(';')[1]


# Append the result of the check on a file
def storeECCS2result(idp,check_results,idp_status):

    # Build the contacts lists: technical/support
    list_technical_contacts = getIdPContacts(idp,'technical')
    list_support_contacts = getIdPContacts(idp,'support')

    str_technical_contacts = ','.join(list_technical_contacts)
    str_support_contacts = ','.join(list_support_contacts)

    # IdP-DisplayName;IdP-entityID;IdP-RegAuth;IdP-tech-ctc-1,IdP-tech-ctc-2;IdP-supp-ctc-1,IdP-supp-ctc-2;IdP-ECCS-Status;SP-wayfless-url-1;SP-check-time-1;SP-status-code-1;SP-result-1;SP-wayfless-url-2;SP-check-time-2;SP-status-code-2;SP-result-2
    with open("%s/%s" % (ECCS2OUTPUTDIR,ECCS2RESULTSLOG), 'a') as f:
         f.write("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s\n" % (
                getDisplayName(idp['displayname']),  # IdP-DisplayName
                idp['entityID'],                     # IdP-entityID
                idp['registrationAuthority'],        # IdP-RegAuth
                str_technical_contacts,              # IdP-TechCtcsList
                str_support_contacts,                # IdP-SuppCtcsList
                idp_status,                          # IdP-ECCS-Status
                check_results[0][1],                 # SP-wayfless-url-1
                check_results[0][2],                 # SP-check-time-1
                check_results[0][3],                 # SP-status-code-1
                check_results[0][4],                 # SP-result-1
                check_results[1][1],                 # SP-wayfless-url-2
                check_results[1][2],                 # SP-check-time-2
                check_results[1][3],                 # SP-status-code-2
                check_results[1][4]))                # SP-result-2


# Check an IdP with 2 SPs.
def check(idp,sps):
    check_results = []
    for sp in sps:
        result = checkIdP(sp,idp)
        if result is not None:
           check_results.append(result)

    if len(check_results) == 2:
       with open("%s/%s" % (ECCS2OUTPUTDIR,ECCS2CHECKSLOG), 'a') as f:
            for elem in check_results:
                f.write(";".join(elem))
                f.write("\n")

       # If all checks are 'OK', than the IdP consuming correctly eduGAIN Metadata.
       if (check_results[0][4] == check_results[1][4] == "OK"):
          storeECCS2result(idp,check_results,'OK')

       elif (check_results[0][4] == check_results[1][4] == "DISABLED"):
            storeECCS2result(idp,check_results,'DISABLED')

       else:
            storeECCS2result(idp,check_results,'ERROR')


# MAIN
if __name__=="__main__":

   sps = ECCS2SPS

   parser = argparse.ArgumentParser(description='Checks if the input IdP consumed correctly eduGAIN metadata by accessing two different SPs')
   parser.add_argument("idpJson", metavar="idpJson", nargs=1, help="An IdP in Json format")

   args = parser.parse_args()

   idp = json.loads(args.idpJson[0])

   Path("%s/%s" % (ECCS2HTMLDIR,DAY)).mkdir(parents=True, exist_ok=True)   # Create dir needed to page_source content

   check(idp,sps)
