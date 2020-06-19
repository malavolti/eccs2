#!/usr/bin/env python3.8

import argparse
import datetime
import json
import re
import requests
import time

from eccs2properties import ECCS2LOGSDIR, ECCS2RESULTSLOG, ECCS2CHECKSLOG, FEDS_BLACKLIST, IDPS_BLACKLIST, ECCS2SPS, ECCS2SELENIUMDEBUG
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException, UnexpectedAlertPresentException
from urllib3.exceptions import MaxRetryError
from urllib3.util import parse_url
from utils import getLogger, getIdPContacts, getDriver

"""
  This script use Selenium and Chromium to select the IdP to check from a Shibboleth SP with the Shibboleth Embedded Discovery Service installed and configured to answer to all eduGAIN IdPs.
  The SPs used to check an IdP will be SP24(IDEM) and Attribute Viewer (SWITCH). 
  The check will be passed when both SPs will return the authentication page of the IdP checked.
"""

def checkIdP(sp,idp,logger):
   # Chromedriver MUST be instanced here to avoid problems with SESSION

   # Disable SSL requests warning messages
   requests.packages.urllib3.disable_warnings()

   debugSelenium = ECCS2SELENIUMDEBUG
   fqdn_idp = parse_url(idp['entityID'])[2]
   driver = getDriver(fqdn_idp,debugSelenium)

   # Configure Blacklists
   federation_blacklist = FEDS_BLACKLIST
   entities_blacklist = IDPS_BLACKLIST 

   if (idp['registrationAuthority'] in federation_blacklist):
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
      logger.info("%s;%s;%s;NULL;Federation excluded from checks" % (idp['entityID'],sp,check_time))
      return (sp,check_time,"NULL","DISABLED")

   if (idp['entityID'] in entities_blacklist):
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
      logger.info("%s;%s;%s;NULL;IdP excluded from checks" % (idp['entityID'],sp,check_time))
      return (sp,check_time,"NULL","DISABLED")

   # Open SP, select the IDP from the EDS and press 'Enter' to reach the IdP login page to check
   try:
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
      driver.get(sp)
      element = WebDriverWait(driver, 50).until(EC.presence_of_element_located((By.ID,"idpSelectInput"))) 
      element.send_keys(idp['entityID'] + Keys.ENTER)
      page_source = driver.page_source
      samlrequest_url = driver.current_url

   except TimeoutException as e:
     logger.info("%s;%s;%s;999;Timeout" % (idp['entityID'],sp,check_time))
     return (sp,check_time,"999","Timeout")

   except NoSuchElementException as e:
     # The input of the bootstrap tables are provided by "eccs2" and "eccs2checks" log.
     # If I don't return anything and I don't put anything in the logger
     # I'll not write on the input files for the table
     # and I can re-run the command that caused the exception from the "stdout.log" file.
     print("!!! NO SUCH ELEMENT EXCEPTION - RUN AGAIN THE COMMAND !!!")
     return None

   except UnexpectedAlertPresentException as e:
     logger.info("%s;%s;%s;888;UnexpectedAlertPresent" % (idp['entityID'],sp,check_time))
     return (sp,check_time,"888","ERROR")

   except WebDriverException as e:
     print("!!! WEB DRIVER EXCEPTION - RUN AGAIN THE COMMAND!!!")
     print (e.__str__())
     print ("IdP: %s\nSP: %s" % (idp['entityID'],sp))
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
      status_code = requests.get(samlrequest_url, headers=headers, verify=False, timeout=30).status_code

   except requests.exceptions.ConnectionError as e:
     #print("!!! REQUESTS STATUS CODE CONNECTION ERROR EXCEPTION !!!")
     #print (e.__str__())
     #print ("IdP: %s\nSP: %s" % (idp['entityID'],sp))
     status_code = "000"

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
      logger.info("%s;%s;%s;%s;No-eduGAIN-Metadata" % (idp['entityID'],sp,status_code,check_time))
      return (sp,check_time,status_code,"No-eduGAIN-Metadata")
   elif not username_found or not password_found:
      logger.info("%s;%s;%s;%s;Invalid-Form" % (idp['entityID'],sp,status_code,check_time))
      return (sp,check_time,status_code,"Invalid-Form")
   else:
      logger.info("%s;%s;%s;%s;OK" % (idp['entityID'],sp,status_code,check_time))
      return (sp,check_time,status_code,"OK")


def check(idp,sps,eccs2log,eccs2checksLog):
      result = []
      for sp in sps:
         resultCheck = checkIdP(sp,idp,eccs2checksLog)
         result.append(resultCheck)

      listTechContacts = getIdPContacts(idp,'technical')
      listSuppContacts = getIdPContacts(idp,'support')

      strTechContacts = ','.join(listTechContacts)
      strSuppContacts = ','.join(listSuppContacts)

      # If all checks are 'OK', than the IdP consuming correctly eduGAIN Metadata.
      if (result[0][3] == result[1][3] == "OK"):
         # IdP-DisplayName;IdP-entityID;IdP-RegAuth;IdP-tech-ctc-1,IdP-tech-ctc-2;IdP-supp-ctc-1,IdP-supp-ctc-2;Status;SP-entityID-1;SP-check-time-1;SP-status-code-1;SP-result-1;SP-entityID-2;SP-check-time-2;SP-status-code-2;SP-result-2
         eccs2log.info("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
             idp['displayname'].replace("&apos;","'").split(';')[1].split('==')[0],
             idp['entityID'],
             idp['registrationAuthority'],
             strTechContacts,
             strSuppContacts,
             'OK',
             result[0][0],
             result[0][1],
             result[0][2],
             result[0][3],
             result[1][0],
             result[1][1],
             result[1][2],
             result[1][3]))
      elif (result[0][3] == result[1][3] == "DISABLED"):
         eccs2log.info("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
             idp['displayname'].replace("&apos;","'").split(';')[1].split('==')[0],
             idp['entityID'],
             idp['registrationAuthority'],
             strTechContacts,
             strSuppContacts,
             'DISABLE',
             result[0][0],
             result[0][1],
             result[0][2],
             result[0][3],
             result[1][0],
             result[1][1],
             result[1][2],
             result[1][3]))
      elif (result[0][3] == None or result[1][3] == None):
          # Do nothing
          return
      else:
         eccs2log.info("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
             idp['displayname'].replace("&apos;","'").split(';')[1].split('==')[0],
             idp['entityID'],
             idp['registrationAuthority'],
             strTechContacts,
             strSuppContacts,
             'ERROR',
             result[0][0],
             result[0][1],
             result[0][2],
             result[0][3],
             result[1][0],
             result[1][1],
             result[1][2],
             result[1][3]))


# MAIN
if __name__=="__main__":

   eccs2log = getLogger(ECCS2RESULTSLOG, ECCS2LOGSDIR, 'a', "INFO")
   eccs2checksLog = getLogger(ECCS2CHECKSLOG, ECCS2LOGSDIR, 'a', "INFO")

   sps = ECCS2SPS

   parser = argparse.ArgumentParser(description='Checks if the input IdP consumed correctly eduGAIN metadata by accessing two different SPs')
   parser.add_argument("idpJson", metavar="idpJson", nargs=1, help="An IdP in Json format")

   args = parser.parse_args()

   idp = json.loads(args.idpJson[0])

   check(idp,sps,eccs2log,eccs2checksLog)
