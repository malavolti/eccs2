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

# Install Python 3.8.x

1. Update the system packages:
   * `sudo apt update ; sudo apt upgrade -y`

2. Install needed packages to build python:
   * `sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev`

3. Download the last version of Python 3.8.x from https://www.python.org/downloads/source/:
   * `sudo wget https://www.python.org/ftp/python/3.8.3/Python-3.8.3.tgz -O /usr/local/src/Python-3.8.3.tar.gz`

4. Extract Python source package:
   * `sudo cd /usr/local/src/`
   * `sudo tar xzf Python-3.8.3.tar.gz`

5. Build Python from the source package:
   * `sudo cd /usr/local/src/Python-3.8.3`
   * `sudo ./configure --enable-optimizations`
   * `sudo make -j 4`

6. Install Python 3.8.x (without replacing the system `python3` command) under `/usr/local/bin/python3.8`:
   * `sudo make altinstall`
   * `python3.8 --version`

7. Create link of Python3.8 for scripts:
   * `sudo ln -s /usr/local/bin/python3.8 /usr/bin/python3.8`

# Install Apache Web Server + WSGI for ECCS2 API

* `sudo apt install libapache2-mod-wsgi-py3 python3-dev`
* `sudo a2enmod wsgi`

# Install requirements for uWSGI used by ECCS2 API:
* `sudo apt-get install libpcre3 libpcre3-dev libapache2-mod-proxy-uwsgi build-essentials python-dev`

# Install Chromium used by Selenium

* `sudo apt install chromium chromium-l10n git jq`

# Install ECCS2

* `cd ~ ; git clone https://github.com/malavolti/eccs2.git`
* `cd eccs2`
* `python3.8 -m pip install --user --upgrade virtualenv`
* `virtualenv -p python38 eccs2venv`
* `source eccs2venv/bin/activate`   (`deactivate` to exit Virtualenv)
  * `pip install --upgrade pip uwsgi`
  * `pip install -r requirements.txt`

# Configure ECCS2

* `cp eccs2properties.py.template eccs2properties.py` (and change it on your needs)
* `sudo cp eccs2.service /etc/systemd/system/eccs2.service`
* `sudo systemctl daemon-reload`
* `sudo systemctl enable eccs2.service`
* `sudo crontab -u debian -e`

  ```bash
  0 0 * * * /bin/bash /opt/eccs2/cleanAndRunEccs2.sh > /opt/eccs2/logs/eccs2cron.log 2>&1  
  ```

# Run ECCS2
  * `./runEccs2.py` or `./cleanAndRunEccs2.py`

# API Development Server

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

# UTILITY FOR WEB INTERFACE

The available dates are provided by the first and the last file created into the `output/` directory
