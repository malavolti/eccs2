#!/usr/bin/env python3.8

import json
import logging
import re

from eccs2properties import DAY,ECCS2LOGSDIR,ECCS2OUTPUTDIR
from flask.logging import default_handler
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from utils import getLogger

app = Flask(__name__)
api = Api(app)


### Functions

# Build Email Addresses Link for ECCS2 Web Gui
def buildEmailAddress(listContacts):
    listCtcs = listContacts.split(",")
    hrefList = []

    for email in listCtcs:
       hrefList.append("<a href='%s'>%s</a>" % (email,email.replace('mailto:', '')))
 
    return hrefList


### Classes

# Test
class Test(Resource):
    def get(self):
        return {'test':'It Works!'}


# /eccs2/api/eccsresults
class EccsResults(Resource):
    def get(self):

       file_path = "%s/eccs2_%s.log" % (ECCS2OUTPUTDIR,DAY)
       date = DAY
       pretty = 0
       status = None
       idp = None
       reg_auth = None
       eccsDataTable = False

       if 'eccsdt' in request.args:
          eccsDataTable = True
       if 'date' in request.args:
          date = request.args['date']
          file_path = "%s/eccs2_%s.log" % (ECCS2OUTPUTDIR,date)
       if 'status' in request.args:
          status = request.args['status'].upper()
          if (status not in ['OK','DISABLED','ERROR']):
             return "Incorrect status format, should be 'ok','disabled','error'"
       if 'idp' in request.args:
          idp = request.args['idp']
          with open(file_path,"r",encoding="utf-8") as fo:
               lines = fo.readlines()
               found = False
               for line in lines:
                   aux = json.loads(line)
                   if (idp == aux['entityID']):
                      found = True
               if (found == False):
                   return "Identity Provider not found with the entityID: %s" % idp
       if 'reg_auth' in request.args:
          reg_auth = request.args['reg_auth']
          with open(file_path,"r",encoding="utf-8") as fo:
               lines = fo.readlines()
               found = False
               for line in lines:
                   aux = json.loads(line)
                   if (reg_auth == aux['registrationAuthority']):
                      found = True
               if (found == False):
                   return "Identity Providers not found with the Registration Authority: %s" % reg_auth

       lines = []
       results = []
       with open(file_path,"r",encoding="utf-8") as fo:
            lines = fo.readlines()

       for line in lines:
          # Strip the line feed and carriage return characters
          line = line.rstrip("\n\r")

          # Loads the json line into aux
          aux = json.loads(line)
    
          aux['date'] = date

          # If the results are for ECCS2 DataTable, otherwise... remove only "mailto:" prefix
          if (eccsDataTable):
             aux['contacts']['technical'] = buildEmailAddress(aux['contacts']['technical'])
             aux['contacts']['support'] = buildEmailAddress(aux['contacts']['support'])
          else:
             aux['contacts']['technical'] = aux['contacts']['technical'].replace("mailto:","")
             aux['contacts']['support'] = aux['contacts']['support'].replace("mailto:","")

          if (idp and status):
              if (idp == aux['entityID'] and status == aux['status']):
                 results.append(aux)
          elif (reg_auth and status):
              if (reg_auth == aux['registrationAuthority'] and status == aux['status']):
                 results.append(aux)
          elif (idp):
              if (idp == aux['entityID']):
                 results.append(aux)
          elif (reg_auth):
              if (reg_auth == aux['registrationAuthority']):
                 results.append(aux)
          elif (status):
              if (status == aux['status']):
                 results.append(aux)
          else:
             results.append(aux)

       return jsonify(results)


# /eccs2/api/fedstats
class FedStats(Resource):
   def get(self):
       return {'fedstats':'It Works!'}

# Routes
api.add_resource(Test, '/test') # Route_1
api.add_resource(EccsResults, '/eccsresults') # Route_2
api.add_resource(FedStats, '/fedstats') # Route_3

if __name__ == '__main__':

   #app.config['JSON_AS_ASCII'] = True
   #app.logger.removeHandler(default_handler)
   #app.logger = getLogger("eccs2api.log", ECCS2LOGSDIR, "w", "INFO")
   app.run(port='5002')
