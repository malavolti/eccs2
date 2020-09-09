#!/usr/bin/env python3

import argparse
import datetime
import json
import re
import requests
import sys

from eccs2properties import DAY, ECCS2HTMLDIR, ECCS2OUTPUTDIR, ECCS2RESULTSLOG, ECCS2SPS, ECCS2SELENIUMDEBUG,ROBOTS_USER_AGENT,ECCS2REQUESTSTIMEOUT, FEDS_DISABLED_DICT, IDPS_DISABLED_DICT
from pathlib import Path
from selenium.common.exceptions import TimeoutException
from urllib3.util import parse_url
from utils import getLogger, getIdPContacts, getDriver


"""
The check works with the wayfless url of two SP and successed if the IdP Login Page appears and contains the fields "username" and "password" for each of them.
It is possible to disable the check by eccs2properties with *denylist or by "robots.txt" put on the SAMLRequest endpoint root web dir.
"""

# Returns the FQDN to use on the HTML page_source files
def getIDPlabel(url_or_urn):
    if url_or_urn.startswith('http'):
       return parse_url(url_or_urn)[2]
    else:
       return url_or_urn.split(":")[-1] 

def getIDPfqdn(samlrequest_url):
    return getIDPlabel(samlrequest_url)

# This function checks if an IdP recognized the SP by presenting its Login page with "username" and "password" fields.
# It is possible to disable the check on eccs2properties with the *denylist or by "robots.txt" file into the SAMLRequest endpoint root web dir.
# If the IdP Login page contains "username" and "password" fields, than the test is passed.
def checkIdP(sp,idp,test):

   # Disable SSL requests warning messages
   requests.packages.urllib3.disable_warnings()

   debug_selenium = ECCS2SELENIUMDEBUG
   label_idp = getIDPlabel(idp['entityID'])
   # WebDriver MUST be instanced here to avoid problems with SESSION
   driver = getDriver(label_idp,debug_selenium)

   # Exception of WebDriver raises
   if (driver == None):
      return None

   # Configure Blacklists
   #federations_disabled_list = FEDS_DISABLED_LIST
   #idps_disabled_list = IDPS_DISABLED_LIST
   federations_disabled_dict = FEDS_DISABLED_DICT
   idps_disabled_dict = IDPS_DISABLED_DICT

   fqdn_sp = parse_url(sp)[2]
   wayfless_url = sp + idp['entityID']

   robots = ""

   if (idp['registrationAuthority'] in federations_disabled_dict.keys()):
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

      if (test is not True):
         with open("%s/%s/%s---%s.html" % (ECCS2HTMLDIR,DAY,label_idp,fqdn_sp),"w") as html:
              html.write("%s" % federations_disabled_dict[idp['registrationAuthority']])
      else:
         print("%s" % federations_disabled_dict[idp['registrationAuthority']])

      return (idp['entityID'],wayfless_url,check_time,"NULL","DISABLED")

   if (idp['entityID'] in idps_disabled_dict.keys()):
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

      if (test is not True):
         with open("%s/%s/%s---%s.html" % (ECCS2HTMLDIR,DAY,label_idp,fqdn_sp),"w") as html:
              html.write("%s" % idps_disabled_dict[idp['entityID']])
      else:
         print("%s" % idps_disabled_dict[idp['entityID']])

      return (idp['entityID'],wayfless_url,check_time,"NULL","DISABLED")

   # Open SP, select the IDP from the EDS and press 'Enter' to reach the IdP login page to check
   try:
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'
      driver.get(wayfless_url)
      page_source = driver.page_source
      samlrequest_url = driver.current_url

      if (test is not True):
         # Put the page_source into an appropriate HTML file
         with open("%s/%s/%s---%s.html" % (ECCS2HTMLDIR,DAY,label_idp,fqdn_sp),"w") as html:
              html.write(page_source)
      else:
         print("\n[page_source of '%s' for sp '%s']\n%s" % (label_idp,fqdn_sp,page_source))

   except TimeoutException as e:
     if (test is not True):
        # Put an empty string into the page_source file
        with open("%s/%s/%s---%s.html" % (ECCS2HTMLDIR,DAY,label_idp,fqdn_sp),"w") as html:
             html.write("")
     else:
        print("\n[page_source of '%s' for sp '%s']\nNo source code" % (label_idp,fqdn_sp))
     return (idp['entityID'],wayfless_url,check_time,"(failed)","Timeout")

   except Exception as e:
     print ("!!! EXCEPTION DRIVER !!!")
     print (e.__str__())
     print ("IdP: %s\nSP: %s" % (idp['entityID'],sp))
     return None

   finally:
     driver.quit()

   try:
      headers = {
         'User-Agent': '%s' % ROBOTS_USER_AGENT
      }

      fqdn_idp = getIDPfqdn(samlrequest_url)

      robots = requests.get("https://%s/robots.txt" % fqdn_idp, headers=headers, verify=True, timeout=ECCS2REQUESTSTIMEOUT)

      if (robots == ""):
         robots  = requests.get("http://%s/robots.txt" % fqdn_idp, headers=headers, verify=True, timeout=ECCS2REQUESTSTIMEOUT)

   # Catch only SSL Exception. Don't block the ECCS check if other exceptions occurred
   except (requests.exceptions.SSLError) as e:
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

      if (test is not True):
         with open("%s/%s/%s---%s.html" % (ECCS2HTMLDIR,DAY,label_idp,fqdn_sp),"w") as html:
             html.write("<p>IdP excluded from check due the following SSL Error:<br/><br/>%s</p><p>Check it on SSL Labs: <a href='https://www.ssllabs.com/ssltest/analyze.html?d=%s'>Click Here</a></p>" % (e.__str__(),fqdn_idp))
      else:
          print("IdP excluded from check due the following SSL Error:\n\n%s\n\nCheck it on SSL Labs: https://www.ssllabs.com/ssltest/analyze.html?d=%s" % (e.__str__(),fqdn_idp))

      return (idp['entityID'],wayfless_url,check_time,"(failed)","SSL-Error")

   # Pass every other exceptions on /robots.txt file. I consider only SSLError.
   except Exception as e:
      #print("IdP '%s' HAD HAD A REQUEST ERROR: %s" % (fqdn_idp,e.__str__()))
      robots = ""

   if (robots):
      check_time = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S') + 'Z'

      p = re.compile('^User-agent:\sECCS\sDisallow:\s\/\s*$', re.MULTILINE)
      m = p.search(robots.text)

      if (m):
         if (test is not True):
            with open("%s/%s/%s---%s.html" % (ECCS2HTMLDIR,DAY,label_idp,fqdn_sp),"w") as html:
                 html.write("IdP excluded from check by robots.txt")
         else:
            print("IdP excluded from check by robots.txt")

         return (idp['entityID'],wayfless_url,check_time,"NULL","DISABLED")


   pattern_metadata = "Unable.to.locate(\sissuer.in|).metadata(\sfor|)|no.metadata.found|profile.is.not.configured.for.relying.party|Cannot.locate.entity|fail.to.load.unknown.provider|does.not.recognise.the.service|unable.to.load.provider|Nous.n'avons.pas.pu.(charg|charger).le.fournisseur.de service|Metadata.not.found|application.you.have.accessed.is.not.registered.for.use.with.this.service|Message.did.not.meet.security.requirements"

   pattern_username = '<input[\s]+[^>]*((type=\s*[\'"](text|email)[\'"]|user)|(name=\s*[\'"](name)[\'"]))[^>]*>';
   pattern_password = '<input[\s]+[^>]*(type=\s*[\'"]password[\'"]|password)[^>]*>';

   metadata_not_found = re.search(pattern_metadata,page_source, re.I)
   username_found = re.search(pattern_username,page_source, re.I)
   password_found = re.search(pattern_password,page_source, re.I)

   try:
      headers = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
      status_code = str(requests.get(samlrequest_url, headers=headers, verify=False, timeout=ECCS2REQUESTSTIMEOUT).status_code)

   except requests.exceptions.ConnectionError as e:
     print ("status-code: (failed) - ConnectionError for IdP '%s' with SP '%s'" % (idp['entityID'],sp))
     #print("!!! REQUESTS STATUS CODE CONNECTION ERROR EXCEPTION !!!")
     #print (e.__str__())
     status_code = "(failed)"

   except requests.exceptions.Timeout as e:
     print ("status-code: 111 - TimeoutError for IdP '%s' with SP '%s'" % (idp['entityID'],sp))
     #print("!!! REQUESTS STATUS CODE TIMEOUT EXCEPTION !!!")
     #print (e.__str__())
     status_code = "111"

   except requests.exceptions.TooManyRedirects as e:
     print ("status-code: 222 - TooManyRedirectsError for IdP '%s' with SP '%s'" % (idp['entityID'],sp))
     #print("!!! REQUESTS TOO MANY REDIRECTS EXCEPTION !!!")
     #print (e.__str__())
     status_code = "222"

   except requests.exceptions.RequestException as e:
     print ("status-code: 333 - RequestException for IdP '%s' with SP '%s'" % (idp['entityID'],sp))
     #print ("!!! REQUESTS EXCEPTION !!!")
     print (e.__str__())
     status_code = "333"

   except Exception as e:
     print ("status-code: 555 - OtherException for IdP '%s' with SP '%s'" % (idp['entityID'],sp))
     #print ("!!! EXCEPTION REQUESTS !!!")
     print (e.__str__())
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
           if "&#039;" in elem:
              elem = elem.replace("&#039;","'")
           if '"' in elem:
              elem = elem.replace('"','\\"')
           return elem.split(';', 1)[1]


# Append the result of the check on a file
def storeECCS2result(idp,check_results,idp_status,test):

    # Build the contacts lists: technical/support
    list_technical_contacts = getIdPContacts(idp,'technical')
    list_support_contacts = getIdPContacts(idp,'support')

    str_technical_contacts = ','.join(list_technical_contacts)
    str_support_contacts = ','.join(list_support_contacts)

    if (test is not True):
       # IdP-DisplayName;IdP-entityID;IdP-RegAuth;IdP-tech-ctc-1,IdP-tech-ctc-2;IdP-supp-ctc-1,IdP-supp-ctc-2;IdP-ECCS-Status;SP-wayfless-url-1;SP-check-time-1;SP-status-code-1;SP-result-1;SP-wayfless-url-2;SP-check-time-2;SP-status-code-2;SP-result-2
       with open("%s/%s" % (ECCS2OUTPUTDIR,ECCS2RESULTSLOG), 'a') as f:
           f.write('{"displayName":"%s","entityID":"%s","registrationAuthority":"%s","contacts":{"technical":"%s","support":"%s"},"status":"%s","sp1":{"wayflessUrl":"%s","checkTime":"%s","statusCode":"%s","status":"%s"},"sp2":{"wayflessUrl":"%s","checkTime":"%s","statusCode":"%s","status":"%s"}}\n' % (
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
    else:
       print("\nECCS2:")
       print('{"displayName":"%s","entityID":"%s","registrationAuthority":"%s","contacts":{"technical":"%s","support":"%s"},"status":"%s","sp1":{"wayflessUrl":"%s","checkTime":"%s","statusCode":"%s","status":"%s"},"sp2":{"wayflessUrl":"%s","checkTime":"%s","statusCode":"%s","status":"%s"}}\n' % (
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
def check(idp,sps,test):
    check_results = []
    for sp in sps:
        result = checkIdP(sp,idp,test)
        if result is not None:
           check_results.append(result)

    if len(check_results) == 2:
       check_result_sp1 = check_results[0][4]
       check_result_sp2 = check_results[1][4]

       # If all checks are 'OK', than the IdP consuming correctly eduGAIN Metadata.
       if (check_result_sp1 == check_result_sp2 == "OK"):
          storeECCS2result(idp,check_results,'OK',test)

       elif (check_result_sp1 == check_result_sp2 == "DISABLED"):
            storeECCS2result(idp,check_results,'DISABLED',test)

       else:
            storeECCS2result(idp,check_results,'ERROR',test)


# MAIN
if __name__=="__main__":

   sps = ECCS2SPS

   parser = argparse.ArgumentParser(description='Checks if the input IdP consumed correctly eduGAIN metadata by accessing two different SPs')
   parser.add_argument("idpJson", metavar="idpJson", nargs=1, help="An IdP in Json format")
   parser.add_argument("--test", action='store_true', help="Test the IdP without effects")

   args = parser.parse_args()

   idp = json.loads(args.idpJson[0])

   Path("%s/%s" % (ECCS2HTMLDIR,DAY)).mkdir(parents=True, exist_ok=True)   # Create dir needed to page_source content

   check(idp,sps,args.test)
