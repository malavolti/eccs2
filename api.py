#!/usr/bin/env python3

from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify
from pathlib import PurePath
import logging
from logging.handlers import RotatingFileHandler

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

class AllChecks(Resource):
    def get(self):
       app.logger.info("Richiesta 'AllChecks'")
       file_path = "logs/eccs2checks_2020-02-19.log"
       fo = open(file_path, "r")
       result = []
       date = PurePath(file_path).parts[-1].split('_')[1].split('.')[0]
       lines = fo.readlines()

       for line in lines:
          check = line.split(";")
          idp = check[0]
          sp = check[1]
          check_result = check[2]
          result.append( { 'sp' : sp,
                           'idp' : idp,
                           'check_result' : check_result.rstrip("\n\r"),
                           'date': date
                         } )
       
       return jsonify(result)


class ChecksByStatus(Resource):
    def get(self,status):
       file_path = "logs/eccs2checks_2020-02-19.log"
       fo = open(file_path, "r")
       result = []
       date = PurePath(file_path).parts[-1].split('_')[1].split('.')[0]
       lines = fo.readlines()
     
       for line in lines:
          check_status = line.split(';')[2].rstrip("\n\r")
          if (status == check_status):
             check = line.split(";")
             idp = check[0]
             sp = check[1]
             check_result = check[2]
             result.append( { 'sp' : sp,
                              'idp' : idp,
                              'check_result' : check_result.rstrip("\n\r"),
                              'date': date
                            } )
       
       return jsonify(result)
        

api.add_resource(Test, '/eccs/test') # Route_1
api.add_resource(AllChecks, '/eccs/checks/all') # Route_2
api.add_resource(ChecksByStatus, '/eccs/checks/<status>') # Route_3

if __name__ == '__main__':
   
   app.logger = getLogger("logs/eccs2api.log","INFO")
   app.run(port='5002')
