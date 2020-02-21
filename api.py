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

class Test(Resource):
    def get(self):
        app.logger.info("Test Superato!")
        return {'test':'It Works!'}

class Checks(Resource):
    def get(self):
       app.logger.info("Richiesta 'Checks'")

       file_path = "logs/eccs2checks_2020-02-19.log"
       date = PurePath(file_path).parts[-1].split('_')[1].split('.')[0]
       pretty = 0
       status = None 
       idp = None

       if 'date' in request.args:
          app.logger.info("Parametro 'date' inserito")
          file_path = "logs/eccs2checks_"+request.args['date']+".log"
          date = request.args['date']
       if 'pretty' in request.args:
          app.logger.info("Parametro 'pretty' inserito")
          pretty = request.args['pretty']
       if 'status' in request.args:
          app.logger.info("Parametro 'status' inserito")
          status = request.args['status']
       if 'idp' in request.args:
          app.logger.info("Parametro 'idp' inserito")
          idp = request.args['idp']
          app.logger.info(idp)

       fo = open(file_path, "r")
       result = []
       lines = fo.readlines()

       for line in lines:
          check = line.split(";")

          check_idp = check[0]
          check_sp = check[1]
          check_status = check[2].rstrip("\n\r")

          if (idp and status):
              if (idp == check_idp and status == check_status):
                 result.append( { 'sp' : check_sp,
                                  'idp' : check_idp,
                                  'status' : check_status,
                                  'date': date
                                } )
          elif (idp):
              #app.logger.info(re.search(".*."+idp+".*.", check_idp, re.IGNORECASE))
              #app.logger.info(check_idp))
              if (re.search(".*."+idp+".*.", check_idp, re.IGNORECASE)):
                 result.append( { 'sp' : check_sp,
                                  'idp' : check_idp,
                                  'status' : check_status,
                                  'date': date
                                } )
          elif (status):
              if (status == check_status):
                 result.append( { 'sp' : check_sp,
                                  'idp' : check_idp,
                                  'status' : check_status,
                                  'date': date
                                } )
          else:
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
          

api.add_resource(Test, '/eccs/test') # Route_1
api.add_resource(Checks, '/eccs/checks') # Route_2

if __name__ == '__main__':
   
   app.logger = getLogger("logs/eccs2api.log","INFO")
   app.run(port='5002')
