#!/usr/bin/env python3.8

import argparse
import json
import logging
import os
import signal
import re
import requests

from datetime import date
from eccs2properties import ECCS2LOGSPATH, ECCS2RESULTSLOG, ECCS2CHECKSLOG, ECCS2SELENIUMLOG, FEDS_BLACKLIST, IDPS_BLACKLIST
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from urllib3.exceptions import MaxRetryError


"""
  This script use Selenium and Chromium to select the IdP to check from a Shibboleth SP with the Shibboleth Embedded Discovery Service installed and configured to answer to all eduGAIN IdPs.
  The SPs used to check an IdP will be SP24(IDEM) and Attribute Viewer (SWITCH). 
  The check will be passed when both SPs will return the authentication page of the IdP checked.
"""

def checkIdP(sp,idp,logger,driver):

   # Configure Blacklists
   federation_blacklist = FEDS_BLACKLIST
   entities_blacklist = IDPS_BLACKLIST 

   if (idp['registrationAuthority'] in federation_blacklist):
      logger.info("%s;%s;NULL;Federation excluded from checks" % (idp['entityID'],sp))
      return "DISABLED"

   if (idp['entityID'] in entities_blacklist):
      logger.info("%s;%s;NULL;IdP excluded from checks" % (idp['entityID'],sp))
      return "DISABLED"

   # Open SP, select the IDP from the EDS and press 'Enter' to reach the IdP login page to check
   try:
      driver.get(sp)
      driver.find_element_by_id("idpSelectInput").send_keys(idp['entityID'] + Keys.ENTER)

   except TimeoutException as e:
     logger.info("%s;%s;999;TIMEOUT" % (idp['entityID'],sp))
     return "TIMEOUT"

   except WebDriverException as e:
     print("!!! WEB DRIVER EXCEPTION !!!")
     raise e

   except Exception as e:
     print ("!!! EXCEPTION !!!")
     raise e


   """
   except MaxRetryError as e:
     logger.info("%s;%s;111;MaxRetryError" % (idp['entityID'],sp))
     return "MaxRetryError"

   except ConnectionRefusedError as e:
     logger.info("%s;%s;222;ConnectionRefusedError" % (idp['entityID'],sp))
     return "ConnectionRefusedError"

   except ConnectionError as e:
     logger.info("%s;%s;333;ConnectionError" % (idp['entityID'],sp))
     return "ConnectionError"

   except NoSuchElementException as e:
     print("!!! NO SUCH ELEMENT EXCEPTION !!!")
     print(e.__str__())
     pass
   """

   """
     if "ConnectionRefusedError" in e.__str__():
        logger.info("%s;%s;000;ConnectionError" % (idp['entityID'],sp))
        return "ConnectionRefusedError"
     elif "Connection Refused" in e.__str__():
        logger.info("%s;%s;000;ConnectionRefused" % (idp['entityID'],sp))
        return "Connection-Refused"
     else:
        print("!!! UN-HANDLE WEB DRIVER EXCEPTION !!!")
        raise e
   """

   pattern_metadata = "Unable.to.locate(\sissuer.in|).metadata(\sfor|)|no.metadata.found|profile.is.not.configured.for.relying.party|Cannot.locate.entity|fail.to.load.unknown.provider|does.not.recognise.the.service|unable.to.load.provider|Nous.n'avons.pas.pu.(charg|charger).le.fournisseur.de service|Metadata.not.found|application.you.have.accessed.is.not.registered.for.use.with.this.service|Message.did.not.meet.security.requirements"

   pattern_username = '<input[\s]+[^>]*((type=\s*[\'"](text|email)[\'"]|user)|(name=\s*[\'"](name)[\'"]))[^>]*>';
   pattern_password = '<input[\s]+[^>]*(type=\s*[\'"]password[\'"]|password)[^>]*>';

   metadata_not_found = re.search(pattern_metadata,driver.page_source, re.I)
   username_found = re.search(pattern_username,driver.page_source, re.I)
   password_found = re.search(pattern_password,driver.page_source, re.I)

   try:
      r = requests.get(driver.current_url, verify=False)
      status_code = r.status_code

   except requests.exceptions.ConnectionError as e:
      logger.info("%s;%s;000;ConnectionError" % (idp['entityID'],sp))
      return "Connection-Error"
   except requests.exceptions.RequestException as e:
      print("!!! UN-HANDLE REQUEST EXCEPTION !!!")
      raise SystemExit(e)

   if(metadata_not_found):
      #print("MD-NOT-FOUND - driver.current_url: %s" % (driver.current_url))
      logger.info("%s;%s;%s;No-eduGAIN-Metadata" % (idp['entityID'],sp,status_code))
      return "No-eduGAIN-Metadata"
   elif not username_found or not password_found:
      #print("INVALID-FORM - entityID: %s, sp: %s, driver.current_url: %s" % (idp['entityID'],sp,driver.current_url))
      logger.info("%s;%s;%s;Invalid-Form" % (idp['entityID'],sp,status_code))
      return "Invalid-Form"
   else:
      #print("MD-FOUND - driver.current_url: %s" % (driver.current_url))
      logger.info("%s;%s;%s;OK" % (idp['entityID'],sp,status_code))
      return "OK"


# Use logger to produce files consumed by ECCS-2 API
def getLogger(filename, path=".", log_level="DEBUG"):

    logger = logging.getLogger(filename)
    ch = logging.FileHandler(path + '/' + filename,'a','utf-8')

    if (log_level == "DEBUG"):
       logger.setLevel(logging.DEBUG)
       ch.setLevel(logging.DEBUG)
    elif (log_level == "INFO"):
       logger.setLevel(logging.INFO)
       ch.setLevel(logging.INFO)
    elif (log_level == "WARN"):
       logger.setLevel(logging.WARN)
       ch.setLevel(logging.WARN)
    elif (log_level == "ERROR"):
       logger.setLevel(logging.ERROR)
       ch.setLevel(logging.ERROR)
    elif (log_level == "CRITICAL"):
       logger.setLevel(logging.CRITICAL)
       ch.setLevel(logging.CRITICAL)

    formatter = logging.Formatter('%(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger


# Return a list of email address for a specific type of contact
def getIdPContacts(idp,contactType):

   ctcList = []
   for ctcType in idp['contacts']:
      if (ctcType == contactType):
         for ctc in idp['contacts'][contactType]:
            if (ctc['emailOrPhone'].get('EmailAddress')):
               ctcList.append(ctc['emailOrPhone']['EmailAddress'][0])
            else:
               ctcList.append('missing')

   return ctcList

def checkIdp(idp,sps,eccs2log,eccs2checksLog,driver):
      result = []
      for sp in sps:
         resultCheck = checkIdP(sp,idp,eccs2checksLog,driver)
         result.append(resultCheck)

      listTechContacts = getIdPContacts(idp,'technical')
      listSuppContacts = getIdPContacts(idp,'support')

      strTechContacts = ','.join(listTechContacts)
      strSuppContacts = ','.join(listSuppContacts)

      # If all checks are 'OK', than the IdP consuming correctly eduGAIN Metadata.
      if (result[0] == result[1] == "OK"):
         # IdP-DisplayName;IdP-entityID;IdP-RegAuth;IdP-tech-ctc-1,IdP-tech-ctc-2;IdP-supp-ctc-1,IdP-supp-ctc-2;Status;SP-entityID-1;SP-status-1;SP-entityID-2;SP-status-2
         eccs2log.info("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
             idp['displayname'].split(';')[1].split('==')[0],
             idp['entityID'],
             idp['registrationAuthority'],
             strTechContacts,
             strSuppContacts,
             'OK',
             sps[0],
             result[0],
             sps[1],
             result[1]))
      elif (result[0] == result[1] == "DISABLED"):
         eccs2log.info("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
             idp['displayname'].split(';')[1].split('==')[0],
             idp['entityID'],
             idp['registrationAuthority'],
             strTechContacts,
             strSuppContacts,
             'DISABLE',
             sps[0],
             result[0],
             sps[1],
             result[1]))
      else:
         eccs2log.info("%s;%s;%s;%s;%s;%s;%s;%s;%s;%s" % (
             idp['displayname'].split(';')[1].split('==')[0],
             idp['entityID'],
             idp['registrationAuthority'],
             strTechContacts,
             strSuppContacts,
             'ERROR',
             sps[0],
             result[0],
             sps[1],
             result[1]))

# MAIN
if __name__=="__main__":

   eccs2log = getLogger(ECCS2RESULTSLOG, ECCS2LOGSPATH, "INFO")
   eccs2checksLog = getLogger(ECCS2CHECKSLOG, ECCS2LOGSPATH, "INFO")

   sps = ["https://sp24-test.garr.it/secure", "https://attribute-viewer.aai.switch.ch/eds/"]

   parser = argparse.ArgumentParser(description='Checks if the input IdP consumed correctly eduGAIN metadata by accessing two different SPs')
   parser.add_argument("idpJson", metavar="idpJson", nargs=1, help="An IdP in Json format")

   args = parser.parse_args()

   idp = json.loads(args.idpJson[0])

   # Disable SSL requests warning messages
   requests.packages.urllib3.disable_warnings()

   # Configure Web-driver
   chrome_options = webdriver.ChromeOptions()
   chrome_options.add_argument('--headless')
   chrome_options.add_argument('--no-sandbox')
   chrome_options.add_argument('--disable-dev-shm-usage')
   chrome_options.add_argument('--ignore-certificate-errors')
   chrome_options.add_argument('--start-maximized')
   chrome_options.add_argument('--disable-extensions')

   driver = webdriver.Chrome('chromedriver', options=chrome_options,  service_args=['--log-path=%s' % ECCS2SELENIUMLOG])
   #driver = webdriver.Chrome('chromedriver', options=chrome_options,  service_args=['--verbose', '--log-path=./selenium_chromedriver.log'])
   #driver = webdriver.Chrome('chromedriver', options=chrome_options)

   # Configure timeouts: 30 sec
   driver.set_page_load_timeout(30)
   driver.set_script_timeout(30)

   checkIdp(idp,sps,eccs2log,eccs2checksLog,driver)

   driver.delete_all_cookies()
   driver.close()
   driver.quit()

   # Kill process to release resources and to avoid zombies
#   pid = os.getpid()
#   os.kill(pid, signal.SIGTERM)
