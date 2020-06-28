#!/usr/bin/env python3.8

import logging
import re

from eccs2properties import DAY,ECCS2LOGSDIR,ECCS2OUTPUTDIR
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from json import dumps, loads
from logging.handlers import RotatingFileHandler
from pathlib import PurePath
from utils import getLogger, getDriver

app = Flask(__name__)
api = Api(app)


# /eccs2/test
class Test(Resource):
    def get(self):
        app.logger.info("Test Passed!")
        return {'test':'It Works!'}


class Checks(Resource):
    def get(self):
       app.logger.info("Request 'Checks'")

       file_path = "%s/eccs2checks_%s.log" % (ECCS2OUTPUTDIR,DAY) 
       date = PurePath(file_path).parts[-1].split('_')[1].split('.')[0]
       pretty = 0
       status = None 
       idp = None

       if 'date' in request.args:
          app.logger.info("'date' parameter inserted")
          date = request.args['date']
          file_path = "%s/eccs2checks_%s.log" % (ECCS2OUTPUTDIR,date)
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
          status_code = check[2]
          check_time = check[3]
          check_status = check[4].rstrip("\n\r")

          if (idp and status):
              app.logger.info("Search for 'idp':'%s' and 'status':'%s'." % (idp,status))
              if (idp == check_idp and status == check_status):
                 result.append( { 'sp' : check_sp,
                                  'idp' : check_idp,
                                  'check_time': check_time,
                                  'status_code': status_code,
                                  'status' : check_status,
                                  'date': date
                                } )
          elif (idp):
              app.logger.info("Search for 'idp':'%s'" % idp)
              if (re.search(".*."+idp+".*.", check_idp, re.IGNORECASE)):
                 result.append( { 'sp' : check_sp,
                                  'idp' : check_idp,
                                  'check_time': check_time,
                                  'status_code': status_code,
                                  'status' : check_status,
                                  'date': date
                                } )
          elif (status):
              app.logger.info("Search for 'status':'%s'." % status)
              if (status == check_status):
                  result.append( { 'sp' : check_sp,
                                   'idp' : check_idp,
                                   'check_time': check_time,
                                   'status_code': status_code,
                                   'status' : check_status,
                                   'date': date
                                 } )
          else:
                 app.logger.info("All checks.")
                 result.append( { 'sp' : check_sp,
                                  'idp' : check_idp,
                                  'check_time': check_time,
                                  'status_code': status_code,
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

       file_path = "%s/eccs2_%s.log" % (ECCS2OUTPUTDIR,DAY)
       date = PurePath(file_path).parts[-1].split('_')[1].split('.')[0]
       pretty = 0
       status = None
       idp = None

       if 'date' in request.args:
          app.logger.info("'date' parameter inserted")
          date = request.args['date']
          file_path = "%s/eccs2_%s.log" % (ECCS2OUTPUTDIR,date)
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
          # ECCS Status;                     check[5]
          # SP-wayfless-url-1;               check[6]
          # SP-check-time-1;                 check[7]
          # SP-status-code-1;                check[8]
          # SP-status-1;                     check[9]
          # SP-wayfless-url-2;               check[10]
          # SP-check-time-2;                 check[11]
          # SP-status-code-2                 check[12]
          # SP-status-2                      check[13]
          check = line.split(";")

          idp_displayname = check[0]
          idp_entity_id = check[1]
          idp_reg_auth = check[2]
          idp_tech_ctcs = check[3]
          idp_supp_ctcs = check[4]
          idp_eccs_status = check[5]
          sp1_wayfless_url = check[6]
          sp1_check_time = check[7]
          sp1_status_code = check[8]
          sp1_check_status = check[9]
          sp2_wayfless_url = check[10]
          sp2_check_time = check[11]
          sp2_status_code = check[12]
          sp2_check_status = check[13].rstrip("\n\r")

          if (idp and status):
              app.logger.info("eccsresults: check for 'idp':'%s' with 'status':'%s'" % (idp, status))
              if (idp == idp_entity_id and status == idp_eccs_status):
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
                            'wayfless_url' : sp1_wayfless_url,
                            'checkTime' : sp1_check_time,
                            'statusCode' : sp1_status_code,
                            'status' : sp1_check_status
                        },
                        'sp2' : {
                            'wayflessUrl' : sp2_wayfless_url,
                            'checkTime' : sp2_check_time,
                            'statusCode' : sp2_status_code,
                            'status' : sp2_check_status
                        },
                        'status' : idp_eccs_status
                    } )
          elif (idp):
              #app.logger.info(re.search(".*."+idp+".*.", idp_entity_id, re.IGNORECASE))
              #app.logger.info(idp_entity_id))
              app.logger.info("eccsresults: results for IdP:'%s'." % idp)
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
                            'wayflessUrl' : sp1_wayfless_url,
                            'checkTime' : sp1_check_time,
                            'statusCode' : sp1_status_code,
                            'status' : sp1_check_status
                        },
                        'sp2' : {
                            'wayflessUrl' : sp2_wayfless_url,
                            'checkTime' : sp2_check_time,
                            'statusCode' : sp2_status_code,
                            'status' : sp2_check_status
                        },
                        'status' : idp_eccs_status
                    } )
          elif (status):
              app.logger.info("eccsresults: Search for 'status':'%s'." % status)
              if (status == idp_eccs_status):
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
                           'wayflessUrl' : sp1_wayfless_url,
                           'checkTime' : sp1_check_time,
                           'statusCode' : sp1_status_code,
                           'status' : sp1_check_status
                        },
                        'sp2' : {
                           'wayflessUrl' : sp2_wayfless_url,
                           'checkTime' : sp2_check_time,
                           'statusCode' : sp2_status_code,
                           'status' : sp2_check_status
                        },
                        'status' : idp_eccs_status
                    } )
          else:
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
                    'wayflessUrl' : sp1_wayfless_url,
                    'checkTime' : sp1_check_time,
                    'statusCode' : sp1_status_code,
                    'status' : sp1_check_status
                 },
                 'sp2' : {
                    'wayflessUrl' : sp2_wayfless_url,
                    'checkTime' : sp2_check_time,
                    'statusCode' : sp2_status_code,
                    'status' : sp2_check_status
                 },
                 'status' : idp_eccs_status
             } )

       if (pretty):
          pp_json = dumps(result, indent=4, sort_keys=True)
          return jsonify(pp_json)
       else:
          return jsonify(result)

# Run check for a specific IDP
# <idpdisc:DiscoveryResponse Location>?entityID=<IDP_ENITIYID>&target=<DESTINATION_RESOURCE_URL> (tutto url encoded)
#class RunCheck(Resource):
#    def get(self):

api.add_resource(Test, '/eccs/test') # Route_1
api.add_resource(Checks, '/eccs/checks') # Route_2
api.add_resource(EccsResults, '/eccs/eccsresults') # Route_3
#api.add_resource(RunCheck, '/eccs/runcheck') # Route_4

if __name__ == '__main__':
   
   app.config['JSON_AS_ASCII'] = False
   app.logger = getLogger("eccs2api.log", ECCS2LOGSDIR, "w", "INFO")
   app.run(port='5002')
