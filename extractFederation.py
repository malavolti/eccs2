#!/usr/bin/env python3

def getIdPs():
   import certifi
   import urllib3
   import json

   manager = urllib3.PoolManager(
               cert_reqs='CERT_REQUIRED',
               ca_certs=certifi.where()
             )

   url = "https://technical.edugain.org/api.php?action=list_eccs_idps"
   idp_json = manager.request('GET', url)

   idp_dict = json.loads(idp_json.data.decode('utf-8'))

   idp_list = []

   #federation = input("Insert the registrationAuthority: ")
   federation = "http://www.idem.garr.it/"

   for idp in idp_dict:
      if (idp['registrationAuthority'] == federation):
         idp_list.append(idp)

   return json.dumps(idp_list)


# MAIN
if __name__=="__main__":

 data = getIdPs()

 f = open('federation_idps.txt', 'w')
 f.write(data)
 f.close()

