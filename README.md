# HOWTO Install and Configure ECCS-2

* `sudo apt install python3-pip chromium chromium-l10n git`
* `pip3 install certifi selenium urllib3 flask flask-jsonpify flask-restful`
* `cd /opt ; git clone https://github.com/malavolti/eccs2.git`
* `cd /opt/eccs2 ; ./eccs2.py`

# Create and configure the ECCS-2 database (not used now)
* `sudo mysql`
* `CREATE DATABASE eccs2db;`
* `CREATE USER 'eccs2user'@'localhost' IDENTIFIED BY '<password>';`
* `GRANT ALL PRIVILEGES ON eccs2db.* TO 'eccs2user'@'localhost'`
* `SHOW GRANTS FOR 'eccs2user'@'localhost';`
* `FLUSH PRIVILEGES;`

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

* `cd /opt/eccs2 ; ./api.py`
