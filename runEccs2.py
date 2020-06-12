#!/usr/bin/env python3.8

import asyncio
import datetime
import eccs2properties
import json
import pathlib
import requests
import sys
import time

from eccs2properties import ECCS2STDOUT, ECCS2STDERR, ECCS2PATH, ECCS2NUMPROCESSES, ECCS2LISTIDPSURL, ECCS2LISTIDPSFILE, ECCS2LISTFEDSURL, ECCS2LISTFEDSFILE 
from subprocess import Popen,PIPE

# Returns a Dict on "{ nameFed:reg_auth }"
def getRegAuthDict(list_feds):
   regAuth_dict = {}

   for key,value in list_feds.items():
      name = value['name']
      reg_auth = value['reg_auth']

      regAuth_dict[name] = reg_auth

   return regAuth_dict


# Returns a list of IdP for a single federation
def getIdpList(list_eccs_idps,reg_auth):

   fed_idp_list = []
   for idp in list_eccs_idps:
      if (idp['registrationAuthority'] == reg_auth):
         fed_idp_list.append(idp)

   return fed_idp_list


# Returns a Python Dictionary
def getListFeds(url, dest_file):
   # If file does not exists... download it into the dest_file
   path = pathlib.Path(dest_file)
   if(path.exists() == False):
      with open("%s" % (dest_file), mode="w+", encoding='utf-8') as f:
         f.write(requests.get(url).text)

   # then open it and work with local file
   with open("%s" % (dest_file), mode="r", encoding='utf-8') as f:
      return json.loads(f.read().replace("'", "&apos;"))


# Returns a Python List
def getListEccsIdps(url, dest_file):
   # If file does not exists... download it into the dest_file
   path = pathlib.Path(dest_file)
   if(path.exists() == False):
      with open("%s" % (dest_file), mode="w+", encoding='utf-8') as f:
         f.write(requests.get(url).text)

   # then open it and work with local file
   with open("%s" % (dest_file), mode="r", encoding='utf-8') as f:
      return json.loads(f.read().replace("'", "&apos;"))

# Run Command
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
         stdout_file.write(f'-----\n[cmd-out]\n{cmd}\n\n[stdout]\n{stdout.decode()}')
      if stderr:
         stderr_file.write(f'-----\n[cmd-err]\n{cmd}\n\n[stderr]\n{stderr.decode()}')

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

    for i in range(ECCS2NUMPROCESSES):
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
   url = ECCS2LISTFEDSURL
   dest_file = ECCS2LISTFEDSFILE
   list_feds = getListFeds(url, dest_file)

   # Setup list_eccs_idps
   url = ECCS2LISTIDPSURL
   dest_file = ECCS2LISTIDPSFILE
   list_eccs_idps = getListEccsIdps(url, dest_file)

   stdout_file = open(ECCS2STDOUT,"w+")
   stderr_file = open(ECCS2STDERR,"w+")

   # Prepare input file for ECCS2
   regAuthDict = getRegAuthDict(list_feds)

   for name,regAuth in regAuthDict.items():
      idpJsonList = getIdpList(list_eccs_idps,regAuth)

      num_idps = len(idpJsonList)
      cmd_list = [["%s/eccs2.py \'%s\'" % (ECCS2PATH, json.dumps(idp))] for idp in idpJsonList]

      proc_list = []
      count = 0
      while (count < num_idps):
         cmd = "".join(cmd_list.pop())
         proc_list.append(cmd)
         count = count + 1
 
      asyncio.run(main(proc_list,stdout_file,stderr_file))

   end = time.time()
   print("Time taken in hh:mm:ss - %s", str(datetime.timedelta(seconds=end - start)))
