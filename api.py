#!/usr/bin/env python3

from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask import jsonify

app = Flask(__name__)
api = Api(app)

class Test(Resource):
    def get(self):
        return {'test': 'ciao'} # Fetches first column that is Employee ID

class EccsCheck(Resource):
    def get(self, idp):
        result = { 'sp':'https://sp24-test.garr.it/secure',
                   'idp':idp,
                   'check_result':'OK',
                   'date':'19-02-2020'
                 }
        return jsonify(result)
        

api.add_resource(Test, '/test') # Route_1
api.add_resource(EccsCheck, '/eccs/<idp>') # Route_3


if __name__ == '__main__':
     app.run(port='5002')
