#!/usr/bin/env python3

from datetime import date
import logging


"""
  Apre un SP con Discovery Service, seleziona l'IdP di cui fare il test e lo raggiunge iniziando una vera sessione via browser.
  A noi serve fare un test di accesso e presentazione della pagina di Login su 2 SP dislocati geograficamente in punti diversi.
  Per questo sono stati scelti SP24(IDEM) e l'Attribute Viewer (SWITCH). Se il test fallisce su entrambi, allora non va bene.
  Questo script funziona SOLO con SP aventi Embedded Discovery Service come DS.
"""

def getIdpListFromUrl():
   import certifi
   import urllib3
   import json

   manager = urllib3.PoolManager(
               cert_reqs='CERT_REQUIRED',
               ca_certs=certifi.where()
             )

   url = "https://technical.edugain.org/api.php?action=list_eccs_idps"
   json_data = manager.request('GET', url)
   data = json.loads(json_data.data.decode('utf-8'))

   return data


def getIdpListFromFile():
   import json

   with open('list_eccs_idps-idem.txt','r',encoding='utf-8') as f:
      json_data = json.loads(f.read())
      return json_data


def checkIdP(sp,idp,logger):
   from selenium import webdriver
   from selenium.webdriver.common.by import By
   from selenium.webdriver.support.ui import Select
   from selenium.webdriver.common.keys import Keys
   from selenium.common.exceptions import NoSuchElementException
   from selenium.common.exceptions import TimeoutException
   import re

   # Configure Web-driver
   chrome_options = webdriver.ChromeOptions()
   chrome_options.add_argument('--headless')
   chrome_options.add_argument('--no-sandbox')

#   driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options,  service_args=['--verbose', '--log-path=./selenium_chromedriver.log'])
   driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)

   # Configure timeouts: 45 sec
   driver.set_page_load_timeout(45)
   driver.set_script_timeout(45)

   # Configure Blacklists
   federation_blacklist = ['http://www.surfconext.nl/','https://www.wayf.dk','http://feide.no/']
   entities_blacklist = ['https://idp.eie.gr/idp/shibboleth','https://gn-vho.grnet.gr/idp/shibboleth','https://wtc.tu-chemnitz.de/shibboleth','https://wtc.tu-chemnitz.de/shibboleth','https://idp.fraunhofer.de/idp/shibboleth','https://login.hs-owl.de/nidp/saml2/metadata','https://idp.dfn-cert.de/idp/shibboleth']

   if (idp['entityID'] in entities_blacklist):
      logger.info("%s;%s;IdP excluded from checks" % (idp['entityID'],sp))
      driver.close()
      driver.quit()
      return "DISABLED"
   if (idp['registrationAuthority'] in federation_blacklist):
      logger.info("%s;%s;Federation excluded from checks" % (idp['entityID'],sp))
      driver.close()
      driver.quit()
      return "DISABLED"

   # Open SP, select the IDP from the EDS and press 'Enter' to reach the IdP login page to check
   try:
      driver.get(sp)
      driver.find_element_by_id("idpSelectInput").send_keys(idp['entityID'] + Keys.ENTER)

      driver.find_element_by_id("username")
      driver.find_element_by_id("password")

   except NoSuchElementException as e:
     pass
   except TimeoutException as e:
     logger.info("%s;%s;TIMEOUT" % (idp['entityID'],sp))
     driver.close()
     driver.quit()
     return "TIMEOUT"

   pattern_metadata = "Unable.to.locate(\sissuer.in|).metadata(\sfor|)|no.metadata.found|profile.is.not.configured.for.relying.party|Cannot.locate.entity|fail.to.load.unknown.provider|does.not.recognise.the.service|unable.to.load.provider|Nous.n'avons.pas.pu.(charg|charger).le.fournisseur.de service|Metadata.not.found|application.you.have.accessed.is.not.registered.for.use.with.this.service|Message.did.not.meet.security.requirements"

   pattern_username = '<input[\s]+[^>]*((type=\s*[\'"](text|email)[\'"]|user)|(name=\s*[\'"](name)[\'"]))[^>]*>';
   pattern_password = '<input[\s]+[^>]*(type=\s*[\'"]password[\'"]|password)[^>]*>';

   metadata_not_found = re.search(pattern_metadata,driver.page_source, re.I)
   username_found = re.search(pattern_username,driver.page_source, re.I)
   password_found = re.search(pattern_password,driver.page_source, re.I)

   if(metadata_not_found):
      logger.info("%s;%s;No-eduGAIN-Metadata" % (idp['entityID'],sp))
      driver.close()
      driver.quit()
      return "No-eduGAIN-Metadata"
   elif not username_found and not password_found:
      logger.info("%s;%s;Invalid-Form" % (idp['entityID'],sp))
      driver.close()
      driver.quit()
      return "Invalid Form"
   else:
      logger.info("%s;%s;OK" % (idp['entityID'],sp))
      driver.close()
      driver.quit()
      return "OK"


# Use logger to produce files consumed by ECCS-2 API
def getLogger(filename,log_level="DEBUG",path="./"):

    logger = logging.getLogger(filename)
    ch = logging.FileHandler(path+filename,'w','utf-8')

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
            ctcList.append(ctc['emailOrPhone']['EmailAddress'][0])

   return ctcList

# MAIN
if __name__=="__main__":

   day = date.today().isoformat() 

   eccs2log = getLogger("logs/eccs2_"+day+".log","INFO")
   eccs2checksLog = getLogger("logs/eccs2checks_"+day+".log","INFO")

   sps = ["https://sp24-test.garr.it/secure", "https://attribute-viewer.aai.switch.ch/eds/"]

   #listIdPs = getIdpListFromUrl()
   listIdPs = getIdpListFromFile()

   for idp in listIdPs:
      result = []
      for sp in sps:
         result.append(checkIdP(sp,idp,eccs2checksLog))

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
