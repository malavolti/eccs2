#!/bin/bash

# logs/stderr_$date.log is kept to see which IdP had been errors

# Remove old IdP and Fed List
rm -f /opt/eccs2/input/*.json

# Run ECCS2
/opt/eccs2/runEccs2.py

# Run Failed Command again
bash /opt/eccs2/logs/failed-cmd.sh

# Remove "failed-cmd" and "stdout*" "stderr*" if empty
date=$(date '+%Y-%m-%d')
file="/opt/eccs2/logs/failed-cmd.sh"
prefix="/opt/eccs2/eccs2.py '"
suffix="'"
eccs2output="/opt/eccs2/output/eccs2_$date.log"
declare -a eccs2cmdToRemoveArray

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
