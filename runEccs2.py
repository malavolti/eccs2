#!/usr/bin/env python3.8

import asyncio
import eccs2properties
import json
import sys
import time

from subprocess import Popen,PIPE

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


def getIdpListFromFile():
   import json

   #with open('list_eccs_idps-idem.txt','r',encoding='utf-8') as f:
   with open('federation_idps.txt','r',encoding='utf-8') as f:
      json_data = json.loads(f.read())
      return json_data


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
         stdout_file.write(f'[stdout]\n{stdout.decode()}')
      if stderr:
         stderr_file.write(f'[stderr]\n{stderr.decode()}\n\n[cmd]\n{cmd}')

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
    for i in range(30):
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

 '''
 data = getIdPs()

 f = open('federation_idps.txt', 'w')
 f.write(data)
 f.close()
 '''
 stdout_file = open(eccs2properties.ECCS2STDOUT,"w+")
 stderr_file = open(eccs2properties.ECCS2STDERR,"w+")

 idpJsonList = getIdpListFromFile()
 num_idps = len(idpJsonList)
 cmd_list = [["%s/eccs2.py \'%s\'" % (eccs2properties.ECCS2PATH, json.dumps(idp))] for idp in idpJsonList]

 proc_list = []
 count = 0
 while (count < num_idps):
       cmd = "".join(cmd_list.pop())
       proc_list.append(cmd)
       count = count + 1
 
 asyncio.run(main(proc_list,stdout_file,stderr_file))

 end = time.time()
 print("Time taken in seconds - ", end - start)
