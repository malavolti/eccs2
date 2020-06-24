# EduGAIN Connectivity Check Service 2

# Requirements Hardware

* OS: Debian 9,10 (tested)
* HDD: 10 GB
* RAM: 4 GB
* CPU: >= 2 vCPU

# Requirements Software

* Apache Server + WSGI
* Python 3.8
* Selenim + Chromium Web Brower

# HOWTO Install and Configure

* `sudo apt install chromium chromium-l10n git jq`
* `python3 -m pip install --user --upgrade pip virtualenv`
* `python3 -m venv eccs2venv`
* `source eccs2venv/bin/activate`   (`deactivate` to exit Virtualenv)
  * `python3 -m pip install --upgrade wheel setuptools certifi selenium urllib3 flask flask-jsonpify flask-restful`
  * `cd ~ ; git clone https://github.com/malavolti/eccs2.git`
  * `cd eccs2`
  * `cp eccs2properties.py.template eccs2properties.py` (and change it with your needs)
  * `./runEccs2.py`

# API Development Server

* `sudo apt install libapache2-mod-wsgi-py3 python3-dev`
* `sudo a2enmod wsgi`
* `cd ~/eccs2 ; ./api.py`

# API

* `/eccs/test` (Trivial Test)
* `/eccs/checks` (Return the results of the last checks)
* `/eccs/checks?<parameter>=<value>`:
  * `date=2020-02-20` (select date)
  * `idp=Any%20words%20do%20you%20like%20url%20encoded`
  * `status=`
    * 'OK'
    * 'TIMEOUT'
    * 'No-eduGAIN-Metadata'
    * 'Form-Invalid'
    * 'Excluded'
* /eccs/eccsresults (Return the results of the last check ready for ECCS Gui)

# APACHE CONFIGURATION

* `sudo vim /etc/apache2/sites-availabled/eccs2.conf

  ```apache
  <IfModule mod_alias.c>
     Alias /eccs2 /opt/eccs2/web
     Alias /eccs2html /opt/eccs2/html

     <Directory /opt/eccs2/web>
        DirectoryIndex index.php
        Require all granted
     </Directory>

     <Directory /opt/eccs2/html>
        Require all granted
     </Directory>
  </IfModule>
  ```

* `sudo a2ensite eccs2.conf`
* `sudo systemctl reload apache2.service`
