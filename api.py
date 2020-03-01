#!/usr/bin/env python3

from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps, loads
from flask import jsonify
from pathlib import PurePath
import logging
from logging.handlers import RotatingFileHandler
import re


app = Flask(__name__)
api = Api(app)

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


# Setup Chromium Webdriver
def setup():

   chrome_options = webdriver.ChromeOptions()
   chrome_options.add_argument('--headless')
   chrome_options.add_argument('--no-sandbox')

   driver = webdriver.Chrome('chromedriver', chrome_options=chrome_options)

   # Configure timeouts
   driver.set_page_load_timeout(45)
   driver.set_script_timeout(45)

   return driver

# /eccs2/test
class Test(Resource):
    def get(self):
        app.logger.info("Test Passed!")
        return {'test':'It Works!'}


class Checks(Resource):
    def get(self):
       app.logger.info("Request 'Checks'")

       file_path = "logs/eccs2checks_2020-02-22.log"
       date = PurePath(file_path).parts[-1].split('_')[1].split('.')[0]
       pretty = 0
       status = None 
       idp = None

       if 'date' in request.args:
          app.logger.info("'date' parameter inserted")
          file_path = "logs/eccs2checks_"+request.args['date']+".log"
          date = request.args['date']
       if 'pretty' in request.args:
          app.logger.info("'pretty' parameter inserted")
          pretty = request.args['pretty']
       if 'status' in request.args:
          app.logger.info("'status' parameter inserted")
          status = request.args['status']
       if 'idp' in request.args:
          app.logger.info("'idp' parameter inserted")
          idp = request.args['idp']
          app.logger.info(idp)

       fo = open(file_path,"r",encoding="utf-8")
       result = []
       lines = fo.readlines()

       for line in lines:
          check = line.split(";")

          check_idp = check[0]
          check_sp = check[1]
          check_status = check[2].rstrip("\n\r")

          if (idp and status):
              app.logger.info("Checks for 'idp' and 'status'.")
              if (idp == check_idp and status == check_status):
                 result.append( { 'sp' : check_sp,
                                  'idp' : check_idp,
                                  'status' : check_status,
                                  'date': date
                                } )
          elif (idp):
              #app.logger.info(re.search(".*."+idp+".*.", check_idp, re.IGNORECASE))
              #app.logger.info(check_idp))
              app.logger.info("Checks for Idp '%s'." % idp)
              if (re.search(".*."+idp+".*.", check_idp, re.IGNORECASE)):
                 result.append( { 'sp' : check_sp,
                                  'idp' : check_idp,
                                  'status' : check_status,
                                  'date': date
                                } )
          elif (status):
              app.logger.info("Check for the status '%s'." % status)
              if (status == check_status):
                 result.append( { 'sp' : check_sp,
                                  'idp' : check_idp,
                                  'status' : check_status,
                                  'date': date
                                } )
          else:
             app.logger.info("All checks.")
             result.append( { 'sp' : check_sp,
                              'idp' : check_idp,
                              'status' : check_status,
                              'date': date
                            } )

       if (pretty):
          pp_json = dumps(result, indent=4, sort_keys=True)
          return jsonify(pp_json)
       else:
          return jsonify(result)


# Build Email Addresses Link for ECCS2 Web Gui
def buildEmailAddress(listContacts):

    listCtcs = listContacts.split(",")
    hrefList = []

    for email in listCtcs:
       hrefList.append("<a href='%s'>%s</a>" % (email,email.replace('mailto:', '')))
 
    return hrefList

class EccsResults(Resource):
    def get(self):
       app.logger.info("Request 'EccsResults'")

       file_path = "logs/eccs2_2020-03-01.log"
       date = PurePath(file_path).parts[-1].split('_')[1].split('.')[0]
       pretty = 0
       status = None
       idp = None

       if 'date' in request.args:
          app.logger.info("'date' parameter inserted")
          file_path = "logs/eccs2_"+request.args['date']+".log"
          date = request.args['date']
       if 'pretty' in request.args:
          app.logger.info("'pretty' parameter inserted")
          pretty = request.args['pretty']
       if 'status' in request.args:
          app.logger.info("'status' parameter inserted")
          status = request.args['status']
       if 'idp' in request.args:
          app.logger.info("'idp' parameter inserted")
          idp = request.args['idp']
          app.logger.info(idp)

       fo = open(file_path,"r",encoding="utf-8")
       result = []
       lines = fo.readlines()

       for line in lines:
          # Line: 
          # IdP-DisplayName;                 check[0]
          # IdP-entityID;                    check[1]
          # IdP-RegAuth;                     check[2]
          # IdP-tech-ctc-1,IdP-tech-ctc-2;   check[3]
          # IdP-supp-ctc-1,IdP-supp-ctc-2;   check[4]
          # Status;                          check[5]
          # SP-entityID-1;                   check[6]
          # SP-status-1;                     check[7]
          # SP-entityID-2;                   check[8]
          # SP-status-2                      check[9]
          check = line.split(";")

          idp_displayname = check[0].rstrip("\n\r")
          idp_entity_id = check[1].rstrip("\n\r")
          idp_reg_auth = check[2].rstrip("\n\r")
          idp_tech_ctcs = check[3].rstrip("\n\r")
          idp_supp_ctcs = check[4].rstrip("\n\r")
          idp_checks_status = check[5].rstrip("\n\r")
          sp1_entity_id = check[6].rstrip("\n\r")
          sp1_check_status = check[7].rstrip("\n\r")
          sp2_entity_id = check[8].rstrip("\n\r")
          sp2_check_status = check[9].rstrip("\n\r")

          if (idp and status):
              app.logger.info("Results for the idp '%s' with status '%s'" % (idp, status))
              if (idp == idp_entity_id and status == idp_checks_status):
                 result.append( 
                    { 
                        'displayName' : idp_displayname,
                        'entityID' : idp_entity_id,
                        'registrationAuthority' : idp_reg_auth,
                        'contacts' : { 
                            'technical' : buildEmailAddress(idp_tech_ctcs),
                            'support' : buildEmailAddress(idp_supp_ctcs),
                        },
                        'date' : date,
                        'sp1' : {
                            'entityID' : sp1_entity_id,
                            'status' : sp1_check_status
                        },
                        'sp2' : {
                            'entityID' : sp2_entity_id,
                            'status' : sp2_check_status
                        },
                        'status' : idp_checks_status
                    } )
          elif (idp):
              #app.logger.info(re.search(".*."+idp+".*.", idp_entity_id, re.IGNORECASE))
              #app.logger.info(idp_entity_id))
              app.logger.info("Results for IdP '%s'." % idp)
              if (re.search(".*."+idp+".*.", idp_entity_id, re.IGNORECASE)):
                 result.append( 
                    { 
                        'displayName' : idp_displayname,
                        'entityID' : idp_entity_id,
                        'registrationAuthority' : idp_reg_auth,
                        'contacts' : { 
                            'technical' : buildEmailAddress(idp_tech_ctcs),
                            'support' : buildEmailAddress(idp_supp_ctcs),
                        },
                        'date' : date,
                        'sp1' : {
                            'entityID' : sp1_entity_id,
                            'status' : sp1_check_status
                        },
                        'sp2' : {
                            'entityID' : sp2_entity_id,
                            'status' : sp2_check_status
                        },
                        'status' : idp_checks_status
                    } )
          elif (status):
              app.logger.info("Results for status '%s'." % status)
              if (status == idp_checks_status):
                 result.append( 
                    { 
                        'displayName' : idp_displayname,
                        'entityID' : idp_entity_id,
                        'registrationAuthority' : idp_reg_auth,
                        'contacts' : { 
                            'technical' : buildEmailAddress(idp_tech_ctcs),
                            'support' : buildEmailAddress(idp_supp_ctcs),
                        },
                        'date' : date,
                        'sp1' : {
                           'entityID' : sp1_entity_id,
                           'status' : sp1_check_status
                        },
                        'sp2' : {
                           'entityID' : sp2_entity_id,
                           'status' : sp2_check_status
                        },
                        'status' : idp_checks_status
                    } )
          else:
             app.logger.info("All checks.")
             result.append( 
             { 
                 'displayName' : idp_displayname,
                 'entityID' : idp_entity_id,
                 'registrationAuthority' : idp_reg_auth,
                 'contacts' : { 
                    'technical' : buildEmailAddress(idp_tech_ctcs),
                    'support' : buildEmailAddress(idp_supp_ctcs),
                 },
                 'date' : date,
                 'sp1' : {
                    'entityID' : sp1_entity_id,
                    'status' : sp1_check_status
                 },
                 'sp2' : {
                    'entityID' : sp2_entity_id,
                    'status' : sp2_check_status
                 },
                 'status' : idp_checks_status
             } )

       if (pretty):
          pp_json = dumps(result, indent=4, sort_keys=True)
          return jsonify(pp_json)
       else:
          return jsonify(result)


api.add_resource(Test, '/eccs/test') # Route_1
api.add_resource(Checks, '/eccs/checks') # Route_2
api.add_resource(EccsResults, '/eccs/eccsresults') # Route_3

if __name__ == '__main__':
   
   app.config['JSON_AS_ASCII'] = False
   app.logger = getLogger("logs/eccs2api.log","INFO")
   app.run(port='5002')
