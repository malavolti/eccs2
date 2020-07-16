# EduGAIN Connectivity Check Service 2 - ECCS2

# Requirements Hardware

* OS: Debian 9,10 (tested)
* HDD: 10 GB
* RAM: 4 GB
* CPU: >= 2 vCPU

# Requirements Software

* Apache Server + WSGI
* Python 3.8 (tested with v3.8.3)
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


# Install requirements for uWSGI used by ECCS2 API:

* `sudo apt-get install libpcre3 libpcre3-dev libapache2-mod-proxy-uwsgi build-essentials python3-dev`


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

1. Configure ECCS2 properties
   * `vim eccs2properties.py` (and change it on your needs)

2. Configure ECCS2 cron job for your local user (`debian` into this example):
   * `sudo crontab -u debian -e`

     ```bash
     0 4 * * * /bin/bash /opt/eccs2/cleanAndRunEccs2.sh > /opt/eccs2/logs/eccs2cron.log 2>&1  
     ```

3. Configure the ECCS2 systemd service to enable its API:
   * `sudo cp eccs2.service /etc/systemd/system/eccs2.service`
   * `sudo systemctl daemon-reload`
   * `sudo systemctl enable eccs2.service`
   * `sudo systemctl start eccs2.service`

4. Configure Apache for the ECCS2 Web side:
   * `sudo cp eccs2.conf /etc/apache2/conf-available/eccs2.conf`
   * `sudo a2enconf eccs2.conf`
   * `sudo systemctl reload apache2.service`


# Run ECCS2 manually

  * `cd ~/eccs2`
  * `./cleanAndRunEccs2.py` (to run a full and clean check)
  * `./runEccs2.py` (to run a full check on the existing inputs)
  * `./runEccs2.py --idp <IDP-ENTITYID>` (to run check on a single IdP)
  * `./runEccs2.py --idp --test` (to run a full check on a single IdP without effects)
  * `./runEccs2.py --idp <IDP-ENTITYID> --test` (to run check on a single IdP without effects)


# ECCS2 API Development Server

* `cd ~/eccs2 ; ./api.py`


# ECCS2 API JSON

* `/api/test` (Trivial Test)
* `/api/eccsresults` (Return the results of the last check ready for ECCS Gui)
* `/api/eccsresults?<parameter>=<value>`:
  * `date=2020-02-20` (select date)
  * `idp=https://idp.example.org/idp/shibboleth`  (select a specific idp)
  * `status=` (select specific ECCS2 status)
    * 'OK'
    * 'ERROR'
    * 'DISABLED'
  * `reg_auth=https://reg.auth.example.org` (select a specific Registration Authority)
* `/api/fedstats`
* `/api/fedstats?reg_auth=https://reg.auth.example.org`:


# UTILITY FOR WEB INTERFACE

The available dates are provided by the first and the last file created into the `output/` directory

To clean the ECCS2 results from files older than last 7 days use:

* `clean7daysOldFiles.sh`
