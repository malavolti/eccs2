#!/bin/bash

# Remove old IdP and Fed List
rm -f /opt/eccs2/input/*.json

# Run ECCS2
/opt/eccs2/runEccs2.py

# Run Failed Command again
bash /opt/eccs2/logs/failed-cmd.sh
