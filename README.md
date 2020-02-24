# HOWTO Install and Configure ECCS-2

* `sudo apt install python3 python3-pip chromium chromium-l10n git`
* `python3 -m pip install --user --upgrade pip virtualenv`
* `python3 -m venv eccs2venv`
* `source eccs2venv/bin/activate`   (`deactivate` di exit Virtualenv)
  * `python3 -m pip install --upgrade wheel setuptools certifi selenium urllib3 flask flask-jsonpify flask-restful`
  * `cd ~ ; git clone https://github.com/malavolti/eccs2.git`
  * `cd eccs2 ; ./eccs2.py`

# API

* `/eccs/test` (Trivial Test)
* `/eccs/checks` (Should return the results of the last checks)
* `/eccs/checks?<parameter>=<value>`:
  * `date=2020-02-20` (select date)
  * `idp=Any%20words%20do%20you%20like%20url%20encoded`
  * `status=`
    * 'OK'
    * 'TIMEOUT'
    * 'No-eduGAIN-Metadata'
    * 'Form-Invalid'
    * 'Excluded'

# API Development Server

* `cd ~/eccs2 ; ./api.py`
