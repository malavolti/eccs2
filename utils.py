#!/usr/bin/env python3.8

import json
import logging
import pathlib
import requests
import sys

from eccs2properties import ECCS2SELENIUMLOGDIR, ECCS2SELENIUMPAGELOADTIMEOUT, ECCS2SELENIUMSCRIPTTIMEOUT
from selenium import webdriver
from selenium.common.exceptions import WebDriverException


# Returns a Dict of "{ nameFed:reg_auth }"
def getRegAuthDict(list_feds):
    regAuth_dict = {}

    for key,value in list_feds.items():
       name = value['name']
       reg_auth = value['reg_auth']

       regAuth_dict[name] = reg_auth

    return regAuth_dict


# Returns a list of IdP for a single federation
def getIdpList(list_eccs_idps,reg_auth=None,idp_entityid=None):
    fed_idp_list = []
    for idp in list_eccs_idps:
       if (idp_entityid):
          if (idp['entityID'] == idp_entityid):
             fed_idp_list.append(idp)
       elif (reg_auth):
          if (idp['registrationAuthority'] == reg_auth):
             fed_idp_list.append(idp)
       else:
          fed_idp_list.append(idp)

    return fed_idp_list


# Returns a Python Dictionary
def getListFeds(url, dest_file):
    # If file does not exists... download it into the dest_file
    path = pathlib.Path(dest_file)
    if(path.exists() == False):
       with open("%s" % (dest_file), mode="w+", encoding='utf-8') as f:
            f.write(requests.get(url).text)

    # then open it and work with local file
    with open("%s" % (dest_file), mode="r", encoding='utf-8') as f:
         return json.loads(f.read().replace("'","&#039;"))


# Download all eduGAIN IdPs from URL, store them on a local file and returns a Python List
def getListEccsIdps(url, dest_file):
    # If file does not exists... download it into the dest_file
    path = pathlib.Path(dest_file)
    if(path.exists() == False):
       with open("%s" % (dest_file), mode="w+", encoding='utf-8') as f:
            f.write(requests.get(url).text)

    # then open it and work with local file
    with open("%s" % (dest_file), mode="r", encoding='utf-8') as f:
         return json.loads(f.read().replace("'","&#039;"))


# Use logger to produce files consumed by ECCS-2 API
def getLogger(filename, path, mode, log_level="DEBUG"):

    logger = logging.getLogger(filename)
    ch = logging.FileHandler("%s/%s" % (path,filename), mode,'utf-8')

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
               if (ctc.get('emailOrPhone')):
                  if (ctc['emailOrPhone'].get('EmailAddress')):
                     ctcList.append(ctc['emailOrPhone']['EmailAddress'][0])
                  else:
                     ctcList.append('missing email')
               else:
                  ctcList.append('missing email')
    return ctcList


def getDriver(fqdn_idp=None,debugSelenium=False):
    # Disable SSL requests warning messages
    requests.packages.urllib3.disable_warnings()

    # Configure Web-driver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    #chrome_options.add_argument('--start-maximized')

    # For DEBUG only (By default ChromeDriver logs only warnings/errors to stderr.
    # When debugging issues, it is helpful to enable more verbose logging.)
    try:
       if (debugSelenium and fqdn_idp):
          driver = webdriver.Chrome('chromedriver', options=chrome_options,  service_args=['--verbose', '--log-path=%s/%s.log' % (ECCS2SELENIUMLOGDIR, fqdn_idp)])
       else:
          driver = webdriver.Chrome('chromedriver', options=chrome_options)
    except WebDriverException as e:
       sys.stderr.write("!!! WEB DRIVER EXCEPTION - RUN AGAIN THE COMMAND!!!")
       sys.stderr.write(e.__str__())
       return None

    # Configure timeouts
    driver.set_page_load_timeout("%d" % ECCS2SELENIUMPAGELOADTIMEOUT)
    driver.set_script_timeout("%d" % ECCS2SELENIUMSCRIPTTIMEOUT)

    return driver
