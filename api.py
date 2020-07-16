#!/usr/bin/env python3.8

import json
import logging
import re

from eccs2properties import DAY, ECCS2LOGSDIR, ECCS2OUTPUTDIR, ECCS2LISTFEDSURL, ECCS2LISTFEDSFILE
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from utils import getLogger, getListFeds, getRegAuthDict

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

# Research the value of the research_item into ECCS2 output files
def existsInFile(file_path, value, research_item, eccsDataTable, date):
    try:
       with open(file_path,"r",encoding="utf-8") as fo:
            lines = fo.readlines()
    except FileNotFoundError as e:
        if (eccsDataTable):
           return ''
        else:
           return jsonify(error='FileNotFound: ECCS2 script has not been executed on %s yet' % date)

    for line in lines:
        aux = json.loads(line)
        if (research_item == "entityID"):
           if (value == aux['entityID']):
              return True
        if (research_item == "registrationAuthority"):
           if (value == aux['registrationAuthority']):
              return True
    return False


### Classes

# /api/test
class Test(Resource):
    def get(self):
        return {'test':'It Works!'}


# /api/eccsresults
class EccsResults(Resource):
    def get(self):

       file_path = "%s/eccs2_%s.log" % (ECCS2OUTPUTDIR,DAY)
       date = DAY
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
              return jsonify(error="Incorrect status provided. It can be 'ok','disabled','error'")
       if 'idp' in request.args:
          idp = request.args['idp']
          if (not existsInFile(file_path, idp, "entityID", eccsDataTable, date)):
             return jsonify(error="Identity Provider not found with the entityID: %s" % idp)
       if 'reg_auth' in request.args:
          reg_auth = request.args['reg_auth']
          if (not existsInFile(file_path, reg_auth, "registrationAuthority", eccsDataTable, date)):
             return jsonify(error="Identity Providers not found with the Registration Authority: %s" % reg_auth)

       lines = []
       results = []
       try:
          with open(file_path,"r",encoding="utf-8") as fo:
               lines = fo.readlines()

       except FileNotFoundError as e:
           if (eccsDataTable):
              return ''
           else:
              return jsonify(error='FileNotFound: ECCS2 script has not been executed on %s' % date)

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


# /api/fedstats
class FedStats(Resource):
   def get(self):
       list_feds = getListFeds(ECCS2LISTFEDSURL, ECCS2LISTFEDSFILE)
       regAuthDict = getRegAuthDict(list_feds)

       file_path = "%s/eccs2_%s.log" % (ECCS2OUTPUTDIR,DAY)
       date = DAY
       reg_auth = None
       eccsDataTable = False

       if ('date' in request.args):
          date = request.args['date']
          file_path = "%s/eccs2_%s.log" % (ECCS2OUTPUTDIR,date)
       if ('reg_auth' in request.args):
          reg_auth = request.args['reg_auth']
          if (not existsInFile(file_path, reg_auth, "registrationAuthority", eccsDataTable, date)):
             return jsonify(error="Registration Authority not found")

       lines = []
       results = []
       try:
          with open(file_path,"r",encoding="utf-8") as fo:
               lines = fo.readlines()

       except FileNotFoundError as e:
           if (eccsDataTable):
              return ''
           else:
              return jsonify(error='FileNotFound: ECCS2 script has not been executed on %s yet' % date)

       if (reg_auth):
          resultDict = {'date': date, 'registrationAuthority': reg_auth, 'OK': 0, 'ERROR': 0, 'DISABLED': 0}

          for line in lines:
              # Strip the line feed and carriage return characters
              line = line.rstrip("\n\r")

              # Loads the json line into aux
              aux = json.loads(line)

              if (aux['registrationAuthority'] == reg_auth):
                 if (aux['status'] == "OK"):
                    resultDict['OK'] = resultDict['OK'] + 1
                 if (aux['status'] == "ERROR"):
                    resultDict['ERROR'] = resultDict['ERROR'] + 1
                 if (aux['status'] == "DISABLED"):
                    resultDict['DISABLED'] = resultDict['DISABLED'] + 1

          results.append(resultDict)
          return jsonify(results)

       else:
           for name,regAuth in regAuthDict.items():
               resultDict = {'date': date, 'registrationAuthority': regAuth, 'OK': 0, 'ERROR': 0, 'DISABLED': 0}

               for line in lines:
                   # Strip the line feed and carriage return characters
                   line = line.rstrip("\n\r")

                   # Loads the json line into aux
                   aux = json.loads(line)

                   if (regAuth == aux['registrationAuthority']):
                      if (aux['status'] == "OK"):
                         resultDict['OK'] = resultDict['OK'] + 1
                      if (aux['status'] == "ERROR"):
                         resultDict['ERROR'] = resultDict['ERROR'] + 1
                      if (aux['status'] == "DISABLED"):
                         resultDict['DISABLED'] = resultDict['DISABLED'] + 1

               results.append(resultDict)
           return jsonify(results)

# Routes
api.add_resource(Test, '/test') # Route_1
api.add_resource(EccsResults, '/eccsresults') # Route_2
api.add_resource(FedStats, '/fedstats') # Route_3

if __name__ == '__main__':

   # Useful only for API development Server
   #app.config['JSON_AS_ASCII'] = True
   #app.logger.removeHandler(default_handler)
   #app.logger = getLogger("eccs2api.log", ECCS2LOGSDIR, "w", "INFO")
   app.run(port='5002')
