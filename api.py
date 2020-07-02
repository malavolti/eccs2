#!/usr/bin/env python3.8

import json
import logging
import re

from eccs2properties import DAY,ECCS2LOGSDIR,ECCS2OUTPUTDIR
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from utils import getLogger

app = Flask(__name__)
api = Api(app)


# /eccs2/test
class Test(Resource):
    def get(self):
        app.logger.info("Test Passed!")
        return {'test':'It Works!'}

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
       date = DAY
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
          # Strip the line feed and carriage return characters
          line = line.rstrip("\n\r")

          # Loads the json line into aux
          aux = json.loads(line)

          aux['date'] = date
          aux['contacts']['technical'] = buildEmailAddress(aux['contacts']['technical'])
          aux['contacts']['support'] = buildEmailAddress(aux['contacts']['support'])

          if (idp and status):
              app.logger.info("eccsresults: check for 'idp':'%s' with 'status':'%s'" % (idp, status))
              if (idp == aux['entityID'] and status == aux['status']):
                 result.append( aux )
          elif (idp):
              app.logger.info("eccsresults: results for IdP:'%s'." % idp)
              if (re.search(".*."+idp+".*.", aux['entityID'], re.IGNORECASE)):
                 result.append( aux )
          elif (status):
              if (status == aux['status']):
                 result.append( aux )
          else:
             result.append(aux) 

       if (pretty):
          pp_json = json.dumps(result, indent=4, sort_keys=True)
          return jsonify(pp_json)
       else:
          return jsonify(result)

api.add_resource(Test, '/eccs/test') # Route_1
api.add_resource(EccsResults, '/eccs/eccsresults') # Route_2

if __name__ == '__main__':
   
   app.config['JSON_AS_ASCII'] = False
   app.logger = getLogger("eccs2api.log", ECCS2LOGSDIR, "w", "INFO")
   app.run(port='5002')
