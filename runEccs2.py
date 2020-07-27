#!/usr/bin/env python3

import argparse
import asyncio
import datetime
import eccs2properties
import json
import time
from utils import getListFeds, getListEccsIdps, getRegAuthDict, getIdpList

from eccs2properties import ECCS2FAILEDCMD, ECCS2FAILEDCMDIDP, ECCS2STDOUT, ECCS2STDERR, ECCS2STDOUTIDP, ECCS2STDERRIDP, ECCS2DIR, ECCS2NUMPROCESSES, ECCS2LISTIDPSURL, ECCS2LISTIDPSFILE, ECCS2LISTFEDSURL, ECCS2LISTFEDSFILE 
from subprocess import PIPE


# Run Command
async def run(name,queue,stdout_file,stderr_file,cmd_file):
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
         stdout_file.write('-----\n[cmd-out]\n%s\n\n[stdout]\n%s' % (cmd,stdout.decode()))
      if stderr:
         stderr_file.write('-----\n[cmd-err]\n%s\n\n[stderr]\n%s' % (cmd,stderr.decode()))
         cmd_file.write('%s\n' % cmd)

      # Notify the queue that the "work cmd" has been processed.
      queue.task_done()


async def main(cmd_list,stdout_file,stderr_file,cmd_file):
    # Create a queue that we will use to store our "workload".
    queue = asyncio.Queue()

    # Put all commands into the queue.
    for cmd in cmd_list:
        queue.put_nowait(cmd)

    # Create worker tasks to process the queue concurrently.
    tasks = []

    for i in range(ECCS2NUMPROCESSES):
        task = asyncio.create_task(run("cmd-{%d}" % i, queue, stdout_file, stderr_file, cmd_file))
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

   parser = argparse.ArgumentParser(description='This script will call another script in parallel to check one or more IdP on the correct consuming of the eduGAIN metadata')

   parser.add_argument("--idp", metavar="entityid", dest="idp_entityid", nargs=1, help="An IdP entityID")
   parser.add_argument("--test", action='store_true', dest="test", help="Test without effects")
      
   args = parser.parse_args()
         
   start = time.time()

   # Setup list_feds
   url = ECCS2LISTFEDSURL
   dest_file = ECCS2LISTFEDSFILE
   list_feds = getListFeds(url, dest_file)

   # Setup list_eccs_idps
   url = ECCS2LISTIDPSURL
   dest_file = ECCS2LISTIDPSFILE
   list_eccs_idps = getListEccsIdps(url, dest_file)

   if (args.idp_entityid):
      stdout_file = open(ECCS2STDOUTIDP,"w+")
      stderr_file = open(ECCS2STDERRIDP,"w+")
      cmd_file = open(ECCS2FAILEDCMDIDP,"w+")
      idpJsonList = getIdpList(list_eccs_idps,idp_entityid=args.idp_entityid[0])

      if (args.test is not True):
         cmd = "%s/eccs2.py \'%s\'" % (ECCS2DIR,json.dumps(idpJsonList[0]))
      else:
         cmd = "%s/eccs2.py \'%s\' --test" % (ECCS2DIR,json.dumps(idpJsonList[0]))

      proc_list = [cmd]
      asyncio.run(main(proc_list,stdout_file,stderr_file,cmd_file))

   else:
      stdout_file = open(ECCS2STDOUT,"w+")
      stderr_file = open(ECCS2STDERR,"w+")
      cmd_file = open(ECCS2FAILEDCMD,"w+")

      # Prepare input file for ECCS2
      regAuthDict = getRegAuthDict(list_feds)

      for name,regAuth in regAuthDict.items():
          idpJsonList = getIdpList(list_eccs_idps,regAuth)

          num_idps = len(idpJsonList)
          if (args.test is not True):
             cmd_list = [["%s/eccs2.py \'%s\'" % (ECCS2DIR, json.dumps(idp))] for idp in idpJsonList]
          else:
             cmd_list = [["%s/eccs2.py \'%s\' --test" % (ECCS2DIR, json.dumps(idp))] for idp in idpJsonList]

          proc_list = []
          count = 0
          while (count < num_idps):
                cmd = "".join(cmd_list.pop())
                proc_list.append(cmd)
                count = count + 1
 
          asyncio.run(main(proc_list,stdout_file,stderr_file,cmd_file))

   end = time.time()
   print("Time taken in hh:mm:ss - ", str(datetime.timedelta(seconds=end - start)))
