# EduGAIN Connectivity Check Service 2 - ECCS2

The purpose of the eduGAIN Connectivity Check is to identify eduGAIN Identity Providers (IdP) that are not properly configured. In particular it checks if an IdP properly loads and consumes SAML2 metadata which contains the eduGAIN Service Providers (SP). The check results are published on the public eduGAIN Connectivity Check web page (### NOT-AVAILABLE-YET ###). The main purpose is to increase the service overall quality and user experience of the eduGAIN interfederation service by making federation and Identity Provider operators aware of configuration problems.

The check is performed by sending a SAML authentication request to each eduGAIN IdP and then follow the various HTTP redirects. The expected result is a login form that allows users to authenticate (typically with username/password) or an error message of some form. For those Identity Providers that output an error message, it can be assumed that they don't consume eduGAIN metadata properly or that they suffer from another configuration problem. There are some cases where the check will generate false positives, therefore IdPs can be excluded from checks as is described below.

The Identity Providers are checked once per day. Therefore, the login requests should not have any significant effect on the log entries/statistics of an Identity Provider. Also, no actual login is performed because the check cannot authenticate users due to missing username and password for the IdPs. Only Identity Providers are checked but not the Service Providers.

# Check Performed on the IdPs

The check executed by the service follows these steps:

1. It retrieves the eduGAIN IdPs from eduGAIN Operator Team database via a JSON interface

2. For each IdP that is was not manually disabled by the eduGAIN Operations Team, the check creates a Wayfless URL for each SP involved and retrieves the IdP login page. It expects to find the HTML form with a username and password field. Therefore, no complete login will happen at the Identity Provider because the check stops at the login page.
The SPs used for the check are "Test SP shib 2.4" (https://sp24-test.garr.it/shibboleth) from IDEM GARR AAI and the "AAI Viewer Interfederation Test" (https://attribute-viewer.aai.switch.ch/interfederation-test/shibboleth) from SWITCHaai. These SPs might change in the future if needed.
The SAML authenticatin request is not signed. Therefore, authentication request for any eduGAIN SP could be created because the SP's private key is not needed.

# Limitations

There are some situations where the check cannot work reliably. In those cases it is possible to disable the check for a particular IdP. The so far known cases where the check might generate a false negative are:

* IdP does not support HTTP or HTTPS with at least SSLv3 or TLS1 or newer (these IdPs are insecure anyway)
* IdP is part of a Hub & Spoke federation (some of them manually have to first approve eduGAIN SPs)
* IdP does not use web-based login form (e.g. HTTP Basic Authentication or X.509 login)

# Disable Checks

In cases where an IdP cannot be reliably checked, it might be necessary to [disable the checks for an IdP](mailto:edugain@geant.org?subject=%5BECCS%5D%20Disable%20check%20for%20IdP&amp;body=Dear%20eduGAIN-ECCS%20Admins%0A%0APlease%20exclude%20the%20Identity%20Provider%20with%20the%20following%20entityID%20from%20the%20ECCS%20checks%3A%0A%23entityID%23%0A%0AThe%20reason%20why%20this%20IdP%20should%20be%20excluded%20is%20...%0A%0ABest%20regards%2C%0A%23Your-Name%23).

# On-line interface

The eduGAIN Connectivity Check web pages is available at: https://dev-mm.aai-test.garr.it/eccs2

The tool uses following status for IdPs:

* ERROR (red):
  * The IdP's response contains an HTTP Error or the web page returned does not look like a login page. The most probable causes for this error are HTTP errors (e.g.: 404 error)
  * The IdP most likely does not consume the eduGAIN metadata correctly or it hasn't does not return a web page that looks like a login form. A typical case that falls into this category is when an IdP returns a message "No return endpoint available for relying party" or "No metadata found for relying party".
* OK (green):
  * The IdP most likely correctly consumes eduGAIN metadata and returns a valid login page. This is no guarantee that login on this IdP works for all eduGAIN services but if the check is passed for an IdP, this is probable.
* DISABLE (white)
  * The IdP is excluded from checks because it cannot be checked reliably (see limitations below) affected by some problems that prevent them to consume correctly eduGAIN metadata. The "Page Source" column, when an entity is disabled, shows the reason of the disabling.


# Requirements Hardware

* OS: Debian 9, CentOS 7.8 (tested)
* HDD: 10 GB
* RAM: 4 GB
* CPU: >= 2 vCPU

# Requirements Software

* Apache Server + WSGI
* Python 3.8 (tested with v3.8.3)
* Selenim + Chromium Web Brower

# HOWTO Install and Configure

## Install Python 3.8.x

### CentOS 7 requirements

1. Update the system packages:
   * `sudo yum -y update`

2. Install the Development Tools:
   * `sudo yum -y groupinstall "Development Tools"`

3. Install needed packages to build python:
   * `sudo yum -y install openssl-devel bzip2-devel libffi-devel wget`

### Debian requirements

1. Update the system packages:
   * `sudo apt update ; sudo apt upgrade -y`

2. Install needed packages to build python:
   * `sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev`

### Python 3.8

1. Download the last version of Python 3.8.x from https://www.python.org/downloads/source/:
   * `wget https://www.python.org/ftp/python/3.8.3/Python-3.8.3.tgz -O /usr/local/src/Python-3.8.3.tar.gz`

2. Extract Python source package:
   * `cd /usr/local/src/`
   * `tar xzf Python-3.8.3.tar.gz`

3. Build Python from the source package:
   * `cd /usr/local/src/Python-3.8.3`
   * `./configure --enable-optimizations`
   * `make -j 4`

4. Install Python 3.8.x (without replacing the system `python3` command) under `/usr/local/bin/python3.8`:
   * `sudo make altinstall`
   * `python3.8 --version`

5. Create link of Python3.8 for scripts:
   * `sudo ln -s /usr/local/bin/python3.8 /usr/bin/python3.8`

# Install requirements for uWSGI used by ECCS2 API:

* Debian:
  * `sudo apt-get install libpcre3 libpcre3-dev libapache2-mod-proxy-uwsgi build-essentials python3-dev unzip`
* CentOS:
  * `sudo yum install mod_proxy_uwsgi unzip`
  * `sudo getsebool -a | grep httpd`
  * Enable ECCS2 for SELinux:
    * `semanage fcontext -a -t httpd_sys_content_t "/opt/eccs2(/.*)?"`
    * `restorecon -R -a /opt/eccs2/`

# Install Selenium & Chromedriver

* `python3.8 -m pip install --upgrade pip`
* `python3.8 -m pip install selenium virtualenv uwsgi`
* `sudo wget https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip -O /usr/local/src/chromedriver_linux64.zip`
* `cd /usr/bin/`
* `sudo unzip /usr/local/src/chromedriver_linux64.zip`

Note: Pay attetion on the chromedriver version:
* Debian 9 (stretch):
  * `chromium -version` => Chromium 73.0.3683.75 => https://chromedriver.storage.googleapis.com/73.0.3683.68/chromedriver_linux64.zip
* CentOS 7.8:
  * `chromium-browser -version` => Chromium 83.0.4103.116 => https://chromedriver.storage.googleapis.com/83.0.4103.39/chromedriver_linux64.zip

# Install Chromium needed by Selenium

* Debian:
  * `sudo apt install chromium git jq`

* CentOS:
  * `sudo yum install -y epel-release`
  * `sudo yum install -y chromium git jq`

# ECCS2

## Install

* `cd /opt ; git clone https://github.com/malavolti/eccs2.git`
* `cd eccs2`
* `virtualenv -p python38 eccs2venv`
* `source eccs2venv/bin/activate`   (`deactivate` to exit Virtualenv)
  * `pip install --upgrade pip`
  * `pip install -r requirements.txt`

## Configure

1. Configure ECCS2 properties:
   * `vim eccs2properties.py` (and change it upon your needs)

2. Configure ECCS2 cron job for your local user (`debian` into this example):
   * `sudo crontab -u debian -e` (Debian) or `sudo crontab -u centos -e` (CentOS)

     ```bash
     0 4 * * * /bin/bash /opt/eccs2/cleanAndRunEccs2.sh > /opt/eccs2/logs/eccs2cron.log 2>&1  
     ```

3. Configure the ECCS2 systemd service to enable its API:
   * `vim /opt/eccs2/eccs2.ini` (and change the "`User`" and the "`Group`" values)
   * `vim /opt/eccs2/eccs2.service` (and change the "`User`" and the "`Group`" values)
   * `sudo cp /opt/eccs2/eccs2.service /etc/systemd/system/eccs2.service`
   * `sudo systemctl daemon-reload`
   * `sudo systemctl enable eccs2.service`
   * `sudo systemctl start eccs2.service`

4. Configure Apache for the ECCS2 Web side:
   * Debian:
     * `sudo cp /opt/eccs2/eccs2-debian.conf /etc/apache2/conf-available/eccs2.conf`
     * `sudo a2enconf eccs2.conf`
     * `sudo systemctl restart apache2.service`
   * CentOS:
     * `sudo cp /opt/eccs2/eccs2-centos.conf /etc/httpd/conf.d/eccs2.conf`
     * `sudo systemctl restart httpd.service`

## Execute

  * `cd /opt/eccs2`
  * `./cleanAndRunEccs2.py` (to run a full and clean check)
  * `./runEccs2.py` (to run a full check on the existing inputs)
  * `./runEccs2.py --idp <IDP-ENTITYID>` (to run check on a single IdP)
  * `./runEccs2.py --test` (to run a full check without effects)
  * `./runEccs2.py --idp <IDP-ENTITYID> --test` (to run check on a single IdP without effects)

  The check will run a second time for those IdPs that failed the first execution of the script. If something prevent the good execution of the check, the `/opt/eccs2/output/failed-cmd.sh` file will be not empty.

  The "--test" parameter will not change the result of ECCS2, but will write the output on the `logs/stdout_idp_YYYY-MM-DD.log`,`logs/stderr_idp_YYYY-MM-DD.log` and `output/failed-cmd-idp.sh` files.

# ECCS2 API Development Server

* `cd /opt/eccs2 ; ./api.py`

# ECCS2 API JSON

* `/api/test` (Trivial Test)
* `/api/eccsresults` (Return the results of the last check ready for ECCS Gui)
* `/api/eccsresults?<parameter1>=<value1>&<parameter2>=<value2>`:
  * `date=2020-02-20` (select date)
  * `idp=https://idp.example.org/idp/shibboleth` (select a specific idp)
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
