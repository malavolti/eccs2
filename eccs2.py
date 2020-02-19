#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import logging


"""
  Apre un SP con Discovery Service, seleziona l'IdP di cui fare il test e lo raggiunge iniziando una vera sessione via browser.
  A noi serve fare un test di accesso e presentazione della pagina di Login su 2 SP dislocati geograficamente in punti diversi.
  Per questo sono stati scelti SP24(IDEM) e l'Attribute Viewer (SWITCH). Se il test fallisce su entrambi, allora non va bene.
  Questo script funziona SOLO con SP aventi Embedded Discovery Service come DS.
"""

def logFile(idp,content):
   path = idp+".txt"

   f = open(path,'w')
   f.write(content)

   f.close()

def getIdPs():
   import certifi
   import urllib3
   import json

   manager = urllib3.PoolManager(
               cert_reqs='CERT_REQUIRED',
               ca_certs=certifi.where()
             )

   url = "https://technical.edugain.org/api.php?action=list_eccs_idps"
   idp_json = manager.request('GET', url)

   idp_dict = json.loads(idp_json.data.decode('utf-8'))

   idp_list = []

   for idp in idp_dict:
      idp_list.append(idp['entityID'])

   return idp_list


def checkIdP(driver,sp,idp,logger):
   import re

   # Apro la URL contenente il Discovery Service, inserisco l'idp e vado alla pagina di login
   try:
      driver.get(sp)
      driver.find_element_by_id("idpSelectInput").send_keys(idp + Keys.ENTER)

      driver.find_element_by_id("username")
      driver.find_element_by_id("password")

   except NoSuchElementException as e:
     pass
   except TimeoutException as e:
     logger.info("%s;%s;TIMEOUT" % (idp,sp))
     return "TIMEOUT"

   pattern_metadata = "Unable.to.locate(\sissuer.in|).metadata(\sfor|)|no.metadata.found|profile.is.not.configured.for.relying.party|Cannot.locate.entity|fail.to.load.unknown.provider|does.not.recognise.the.service|unable.to.load.provider|Nous.n'avons.pas.pu.(charg|charger).le.fournisseur.de service|Metadata.not.found|application.you.have.accessed.is.not.registered.for.use.with.this.service|Message.did.not.meet.security.requirements"

   pattern_username = '<input[\s]+[^>]*((type=\s*[\'"](text|email)[\'"]|user)|(name=\s*[\'"](name)[\'"]))[^>]*>';
   pattern_password = '<input[\s]+[^>]*(type=\s*[\'"]password[\'"]|password)[^>]*>';

   metadata_not_found = re.search(pattern_metadata,driver.page_source, re.I)
   username_found = re.search(pattern_username,driver.page_source, re.I)
   password_found = re.search(pattern_password,driver.page_source, re.I)

   if(metadata_not_found):
      logger.info("%s;%s;No-eduGAIN-Metadata" % (idp,sp))
      return "No-eduGAIN-Metadata"
   elif not username_found and not password_found:
      logger.info("%s;%s;Invalid-Form" % (idp,sp))
      return "Invalid Form"
   else:
      logger.info("%s;%s;OK" % (idp,sp))
      return "OK"

def setup():

   chrome_options = webdriver.ChromeOptions()
   chrome_options.add_argument('--headless')
   chrome_options.add_argument('--no-sandbox')

   driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options,  service_args=['--verbose', '--log-path=./selenium_chromedriver.log'])

   # Configuro i timeout
   driver.set_page_load_timeout(45)
   driver.set_script_timeout(45)

   return driver

# Use logger to produce files consumed by ECCS-2
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


if __name__=="__main__":

   eccs2log = getLogger("logs/eccs2.log","INFO")
   eccs2checks = getLogger("logs/eccs2checks.log","INFO")

   driver = setup()

   sps = ["https://sp24-test.garr.it/secure", "https://attribute-viewer.aai.switch.ch/eds/"]

   listIdPs = [
      'https://garr-idp-prod.irccs.garr.it',
      'https://idp.hec.gov.pk/idp/shibboleth',
      'https://login.itsak.gr/idp/shibboleth',
      'https://idp.eastdurham.ac.uk/openathens',
      'https://idp-lib.nwafu.edu.cn/idp/shibboleth',
   ]

   #listIdPs = getIdPs()

   for idp in listIdPs:
      result = []
      for sp in sps:
         result.append(checkIdP(driver,sp,idp,eccs2checks))

      # se tutti e 2 i check sono andati bene, allora l'IdP è OK, altrimenti no.
      if (result[0] == result[1] == "OK"):
         eccs2log.info("IdP '%s' results into: OK" % (idp))
      else:
         eccs2log.info("IdP '%s' results into: NOT OK" % (idp))

   driver.close()
