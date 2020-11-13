#!/bin/bash

# logs/stderr_$date.log is the Standard Error of ECCS2 python script
# logs/stdout_$date.log is the Standard Output of ECCS2 python script

BASEDIR=$HOME

source $HOME/.profile

# Remove old IdP and Fed List
rm -f $BASEDIR/eccs2/input/*.json

# Run ECCS2
$BASEDIR/eccs2/runEccs2.py

# Run Failed Command again
bash $BASEDIR/eccs2/logs/failed-cmd.sh

# Remove "failed-cmd" and "stdout*" "stderr*" if empty
date=$(date '+%Y-%m-%d')
file="$BASEDIR/eccs2/logs/failed-cmd.sh"
prefix="$BASEDIR/eccs2/eccs2.py '"
suffix="'"
eccs2output="$BASEDIR/eccs2/output/eccs2_$date.log"
declare -a eccs2cmdToRemoveArray

if [ -s $eccsoutput ]; then
   if [ -s $file ]; then
      while IFS= read -r line
      do
         string=$line

         #remove "prefix" from the command string at the beginning.
         prefix_removed_string=${string/#$prefix}

         #remove "suffix" from the command string at the end.
         suffix_removed_string=${prefix_removed_string/%$suffix}

         entityIDidp=$(echo "$suffix_removed_string" | jq '.entityID')

         #remove start and end quotes from the entityIDidp to be able to use "grep"
         entityIDidp="${entityIDidp:1}"
         entityIDidp="${entityIDidp%?}"

         result=$(grep $entityIDidp $eccs2output | wc -l)
   
         if [[ "$result" = 1 ]]; then
            eccs2cmdToRemoveArray+=("$entityIDidp")
         else
            echo "The result for the IdP '$entityIDidp' has been found multiple times on $eccs2output. It is wrong."
         fi

      done <"$file"


      # Remove IdP command that had success from "failed-cmd.sh"
      for idpToRemove in ${eccs2cmdToRemoveArray[@]}
      do
         $(grep -v $idpToRemove $file > temp ; mv -f temp $file)
      done

      if [ -s $file ]; then
         echo "$date - ECCS2 NOT OK: Some eduGAIN IdPs have remained unchecked. See the 'logs/failed-cmd.sh' and logs/stderr_$date.log files"
      else
         echo "$date - ECCS2 OK: All eduGAIN IdPs have been checked successfully"
      fi
   else
      echo "$date - ECCS2 OK: All eduGAIN IdPs have been checked successfully"
   fi
else
   echo "$date - Something went wrong and the ECCS2 check has not been executed"
fi
