#!/usr/bin/env python3.8

import asyncio
import eccs2properties
import json
import pathlib
import requests
import sys
import time

from subprocess import Popen,PIPE

# returns a Dict on "{ nameFed:reg_auth }"
def getRegAuthDict(list_feds):
   regAuth_dict = {}

   for key,value in list_feds.items():
      name = value['name']
      reg_auth = value['reg_auth']

      regAuth_dict[name] = reg_auth

   return regAuth_dict


# returns a list of IdP for a single federation
def getIdpList(list_eccs_idps,reg_auth):

   fed_idp_list = []
   for idp in list_eccs_idps:
      if (idp['registrationAuthority'] == reg_auth):
         fed_idp_list.append(idp)

   return fed_idp_list


# Returns a Python Dictionary
def getListFeds(url, filename):
   # If file does not exists... download it into the filename
   path = pathlib.Path(filename)
   if(path.exists() == False):
      with open("%s" % (filename), mode="w+", encoding='utf-8') as f:
         f.write(requests.get(url).text)

   # then open it and work with local file
   with open("%s" % (filename), mode="r", encoding='utf-8') as f:
      return json.loads(f.read())


# Returns a Python List
def getListEccsIdps(url, filename):
   # If file does not exists... download it into the filename
   path = pathlib.Path(filename)
   if(path.exists() == False):
      with open("%s" % (filename), mode="w+", encoding='utf-8') as f:
         f.write(requests.get(url).text)

   # then open it and work with local file
   with open("%s" % (filename), mode="r", encoding='utf-8') as f:
      return json.loads(f.read())

# Prepare input file for ECCS2
def genEccs2input(reg_auth_dict):
   for name,regAuth in reg_auth_dict.items():
      fed_idp_list = getIdpList(list_eccs_idps,regAuth)
      filename = "/tmp/data/inputEccs2/%s.txt" % name
      with open("%s" % (filename), mode="w+", encoding='utf-8') as f:
         f.write(','.join(str(idp) for idp in fed_idp_list))

async def run(name,queue,stdout_file,stderr_file):
   while True:
      # Get a "cmd item" out of the queue.
      cmd = await queue.get()

      # Elaborate "cmd" from shell.
      proc = await asyncio.create_subprocess_shell(
                   cmd,
                   stdout=asyncio.subprocess.PIPE,
                   stderr=asyncio.subprocess.PIPE
             )

      stdout, stderr = await proc.communicate()

      if stdout:
         stdout_file.write(f'-----\n[cmd-out]\n{cmd}\n[stdout]\n{stdout.decode()}')
      if stderr:
         stderr_file.write(f'-----\n[cmd-err]\n{cmd}\n[stderr]\n{stderr.decode()}')

      # Notify the queue that the "work cmd" has been processed.
      queue.task_done()


async def main(cmd_list,stdout_file,stderr_file):
    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue()

    # Put all commands into the queue.
    for cmd in cmd_list:
        queue.put_nowait(cmd)

    # Create worker tasks to process the queue concurrently.
    tasks = []
    #for i in range(15): # !!!-WORKING-!!!
    #for i in range(30): # !!!-WORSTE-!!!
    for i in range(10):
        task = asyncio.create_task(run("cmd-{%d}" % i, queue, stdout_file, stderr_file))
        tasks.append(task)

    # Wait until the queue is fully processed.
    started_at = time.monotonic()
    await queue.join()
    total_slept_for = time.monotonic() - started_at

    # Cancel our worker tasks.
    for task in tasks:
        task.cancel()

    # Wait until all worker tasks are cancelled.
    await asyncio.gather(*tasks, return_exceptions=True)


# MAIN
if __name__=="__main__":

   start = time.time()

   # Setup list_feds
   url = 'https://technical.edugain.org/api.php?action=list_feds&opt=1'
   filename = "/tmp/data/list_feds.txt"
   list_feds = getListFeds(url, filename)

   # Setup list_eccs_idps
   url = 'https://technical.edugain.org/api.php?action=list_eccs_idps'
   filename = "/tmp/data/list_eccs_idps.txt"
   list_eccs_idps = getListEccsIdps(url, filename)

   stdout_file = open(eccs2properties.ECCS2STDOUT,"w+")
   stderr_file = open(eccs2properties.ECCS2STDERR,"w+")

   # Prepare input file for ECCS2
   regAuthDict = getRegAuthDict(list_feds)
   #genEccs2input(regAuthDict)

   for name,regAuth in regAuthDict.items():
      idpJsonList = getIdpList(list_eccs_idps,regAuth)

      num_idps = len(idpJsonList)
      cmd_list = [["%s/eccs2.py \'%s\'" % (eccs2properties.ECCS2PATH, json.dumps(idp))] for idp in idpJsonList]

      proc_list = []
      count = 0
      while (count < num_idps):
         cmd = "".join(cmd_list.pop())
         proc_list.append(cmd)
         count = count + 1
 
      asyncio.run(main(proc_list,stdout_file,stderr_file))
#      asyncio.run(main(cmd_list,stdout_file,stderr_file))

   end = time.time()
   print("Time taken in seconds - ", end - start)
