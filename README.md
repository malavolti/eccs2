# EduGAIN Connectivity Check Service 2 - ECCS2

1. [Introduction](#introduction)
2. [Check Performed on the IdPs](#check-performed-on-the-idps)
3. [Limitations](#limitations)
4. [Disable Checks](#disable-checks)
5. [On-line interface](#on-line-interface)
6. [Requirements Hardware](#requirements-hardware)
7. [Requirements Software](#requirements-software)
8. [HOWTO Install and Configure](#howto-install-and-configure)
   * [Install Python 3.8.x](#install-python-38x)
     + [CentOS 7 requirements](#centos-7-requirements)
     + [Debian requirements](#debian-requirements)
     + [Python 3.8](#python-38)
9. [Install the Chromedriver](#install-the-chromedriver)
10. [Install Chromium needed by Selenium](#install-chromium-needed-by-selenium)
11. [ECCS2 Script](#eccs2-script)
    * [Install](#install)
    * [Configure](#configure)
    * [Execute](#execute)    
12. [ECCS2 API Server (UWSGI)](#eccs2-api-server-uwsgi)
    * [Install](#install-1)
    * [Configure](#configure-1)
    * [Utility](#utility)
13. [ECCS2 API JSON](#eccs2-api-json)
14. [Utility for web interface](#utility-for-web-interface)
15. [Utility for developers](#utility-for-developers)
    * [ECCS2 API Development Server](#eccs2-api-development-server)
16. [Authors](#authors)

# Introduction

The purpose of the eduGAIN Connectivity Check is to identify eduGAIN Identity Providers (IdP) that are not properly configured. In particular it checks if an IdP properly loads and consumes SAML2 metadata which contains the eduGAIN Service Providers (SP). The check results are published on the public eduGAIN Connectivity Check web page (### NOT-AVAILABLE-YET ###). The main purpose is to increase the service overall quality and user experience of the eduGAIN interfederation service by making federation and Identity Provider operators aware of configuration problems.

The check is performed by sending a SAML authentication request to each eduGAIN IdP and then follow the various HTTP redirects. The expected result is a login form that allows users to authenticate (typically with username/password) or an error message of some form. For those Identity Providers that output an error message, it can be assumed that they don't consume eduGAIN metadata properly or that they suffer from another configuration problem. There are some cases where the check will generate false positives, therefore IdPs can be excluded from checks as is described below.

The Identity Providers are checked once per day. Therefore, the login requests should not have any significant effect on the log entries/statistics of an Identity Provider. Also, no actual login is performed because the check cannot authenticate users due to missing username and password for the IdPs. Only Identity Providers are checked but not the Service Providers.

# Check Performed on the IdPs

The check executed by the service follows these steps:

1. It retrieves the eduGAIN IdPs from eduGAIN Operator Team database via a JSON interface

2. For each IdP that is was not manually disabled by the eduGAIN Operations Team, the check creates a Wayfless URL for each SP involved and retrieves the IdP login page. It expects to find the HTML form with a username and password field. Therefore, no complete login will happen at the Identity Provider because the check stops at the login page.
The SPs used for the check are "Test SP shib 2.4" (https://sp-demo.idem.garr.it/shibboleth) from IDEM GARR AAI and the "AAI Viewer Interfederation Test" (https://attribute-viewer.aai.switch.ch/interfederation-test/shibboleth) from SWITCHaai. These SPs might change in the future if needed.
The SAML authenticatin request is not signed. Therefore, authentication request for any eduGAIN SP could be created because the SP's private key is not needed.

# Limitations

There are some situations where the check cannot work reliably. In those cases it is possible to disable the check for a particular IdP. The so far known cases where the check might generate a false negative are:

* IdP does not support HTTP or HTTPS with at least SSLv3 or TLS1 or newer (these IdPs are insecure anyway)
* IdP is part of a Hub & Spoke federation (some of them manually have to first approve eduGAIN SPs)
* IdP does not use web-based login form (e.g. HTTP Basic Authentication or X.509 login)

# Disable Checks

In cases where an IdP cannot be reliably checked, it is necessary to create or enrich the `robots.txt` file on the IdP's web root with:

```bash
User-agent: ECCS
Disallow: /
```

# On-line interface

The test eduGAIN Connectivity Check web pages is available at: https://technical-test.edugain.org/eccs2

The tool uses following status for IdPs:

* ERROR (red):
  * The IdP's response contains an HTTP Error or the web page returned does not look like a login page. The most probable causes for this error are HTTP errors (e.g.: 404 error)
  * The IdP most likely does not consume the eduGAIN metadata correctly or it hasn't does not return a web page that looks like a login form. A typical case that falls into this category is when an IdP returns a message "No return endpoint available for relying party" or "No metadata found for relying party".
  * The IdP has a problem with its SSL certificate.
* OK (green):
  * The IdP most likely correctly consumes eduGAIN metadata and returns a valid login page. This is no guarantee that login on this IdP works for all eduGAIN services but if the check is passed for an IdP, this is probable.
* DISABLED (white)
  * The IdP is excluded because it cannot be checked reliably. The "Page Source" column, when an entity is disabled, shows the reason of the disabling.

# Requirements Hardware

* OS: Debian 9, CentOS 7.8 (tested)
* HDD: 10 GB
* RAM: 4 GB
* CPU: >= 2 vCPU (suggested)

# Requirements Software

* Apache Server + WSGI
* Python 3.8 (tested with v3.8.3,v3.8.5)
* Selenim + Chromium Web Brower

# HOWTO Install and Configure

## Download ECCS2 Repository

* `cd $HOME ; git clone https://github.com/malavolti/eccs2.git`

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

1. Download the last version of Python 3.8.x from https://www.python.org/downloads/source/ into your home:
   * `wget https://www.python.org/ftp/python/3.8.5/Python-3.8.5.tgz -O $HOME/eccs2/Python-3.8.5.tgz`

2. Extract Python source package:
   * `cd $HOME/eccs2/`
   * `tar xzf Python-3.8.5.tgz`

3. Build Python from the source package:
   * `cd $HOME/eccs2/Python-3.8.5`
   * `./configure --prefix=$HOME/eccs2/python`
   * `make`

4. Install Python 3.8.x under `$HOME/eccs2/python`:
   * `make install`
   * `$HOME/eccs2/python/bin/python3.8 --version`
 
   This will install python under your $HOME directory.
   
5. Remove useless things:
   * `rm -Rf $HOME/eccs2/Python-3.8.5 $HOME/eccs2/Python-3.8.5.tgz`

# Install Chromium needed by Selenium

* Debian:
  * `sudo apt install chromium git jq`

* CentOS:
  * `sudo yum install -y epel-release`
  * `sudo yum install -y chromium git jq`

# Install the Chromedriver

1. Find out which version of Chromium you are using:
   * Debian 9 (stretch):
     * `chromium -version` => Chromium 73.0.3683.75
   * CentOS 7.8:
     * `chromium-browser -version` => Chromium 83.0.4103.116

2. Take the Chrome version number, remove the last part, and append the result to URL "`https://chromedriver.storage.googleapis.com/LATEST_RELEASE_`". For example, with Chrome version 73.0.3683.75, you'd get a URL "`https://chromedriver.storage.googleapis.com/LATEST_RELEASE_73.0.3683`".

3. Use the URL created in the last step to discover the version of ChromeDriver to use. For example, the above URL will get your a file containing "73.0.3683.68".

4. Use the version number retrieved from the previous step to construct the URL to download ChromeDriver. With version `72.0.3626.69`, the URL would be "https://chromedriver.storage.googleapis.com/index.html?path=73.0.3683.68/"

5. Download the Chromedriver and extract it with:
   * `wget https://chromedriver.storage.googleapis.com/73.0.3683.75/chromedriver_linux64.zip -O $HOME/eccs2/chromedriver_linux64.zip`
   * `cd $HOME/eccs2`
   * `unzip chromedriver_linux64.zip`
   * `rm chromedriver_linux64.zip`

**Note:**
After the initial download, it is recommended that you occasionally go through the above process again to see if there are any bug fix releases.

# ECCS2 Script

## Install

* `cd $HOME/eccs2`
* `./python/bin/python3.8 -m pip install virtualenv`
* `$HOME/eccs2/python/bin/virtualenv --python=$HOME/eccs2/python/bin/python3.8 eccs2venv`
* `source eccs2venv/bin/activate`   (`deactivate` to exit Virtualenv)
  * `python -m pip install -r requirements.txt`

## Configure

1. Configure ECCS2 properties:
   * `vim eccs2properties.py` (and change it upon your needs)

2. Change `PATH` by adding the virtualenv Python `bin` dir:
   * CentOS:
     * `vim $HOME/.bash_profile`
     * Add the following lines at the tail:
       
       ```bash
       # set PATH for ECCS2
       if [ -d "$HOME/eccs2" ] ; then
          PATH="$HOME/eccs2/eccs2venv/bin:$PATH"
       fi
       ```

   * Debian:
     * `vim $HOME/.profile`
     * Add the following lines at the tail:
       
       ```bash
       # set PATH for ECCS2
       if [ -d "$HOME/eccs2" ] ; then
          PATH="$HOME/eccs2/eccs2venv/bin:$PATH"
       fi
       ```

3. Configure ECCS2 cron job for the local user:
   * `crontab -e`

     ```bash
     SHELL=/bin/bash

     0 4 * * * /bin/bash $HOME/eccs2/cleanAndRunEccs2.sh > $HOME/eccs2/logs/eccs2cron.log 2>&1
     ```

## Execute

  * `cd $HOME/eccs2`
  * `./cleanAndRunEccs2.py` (to run a full and clean check)
  * `./runEccs2.py` (to run a full check on the existing inputs)
  * `./runEccs2.py --idp <IDP-ENTITYID>` (to run check on a single IdP)
  * `./runEccs2.py --test` (to run a full check without effects)
  * `./runEccs2.py --idp <IDP-ENTITYID> --test` (to run check on a single IdP without effects)

  The check will run a second time for those IdPs that failed the first execution of the script.
  If something prevent the good execution of the ECCS2's check, the `logs/failed-cmd.sh` file will be not empty at the end of the execution.

  The "--test" parameter will not change the result of ECCS2, but will write the output on the `logs/stdout_idp_YYYY-MM-DD.log`,`logs/stderr_idp_YYYY-MM-DD.log` and `logs/failed-cmd-idp.sh` files.

# ECCS2 API Server (uWSGI)

## Install

1. Install requirements:
   * Debian:
     * `sudo apt-get install libpcre3 libpcre3-dev libapache2-mod-proxy-uwsgi build-essentials python3-dev unzip`
   * CentOS:
     * `sudo yum install mod_proxy_uwsgi unzip`
     * Configure SElinux to enable ECCS2:
       * `sudo semanage fcontext -a -t httpd_sys_content_t "$HOME/eccs2(/.*)?"`
       * `sudo restorecon -R -e $HOME/eccs2/`
       * `sudo setsebool -P httpd_can_network_connect 1`
 
## Configure

1. Add the systemd service to enable ECCS2 API:
   * `cd $HOME/eccs2`
   * `cp eccs2.ini.template eccs2.ini`
   * `cp eccs2.service.template eccs2.service`
   * `vim eccs2.ini` (and change "`uid`", "`gid`" and "`base`" values opportunely)
   * `vim eccs2.service` (and change "`User`","`Group`","`WorkingDirectory`","`RuntimeDirectory`","`ExecStart`" values opportunely)
   * `sudo cp $HOME/eccs2/eccs2.service /etc/systemd/system/eccs2.service`
   * `sudo systemctl daemon-reload`
   * `sudo systemctl enable eccs2.service`
   * `sudo systemctl start eccs2.service`

2. Configure Apache for ECCS2 web side:
   * Debian:
     * `sudo cp $HOME/eccs2/eccs2-debian.conf /etc/apache2/conf-available/eccs2.conf`
     * `sudo a2enconf eccs2.conf`
     * `sudo chgrp www-data $HOME ; sudo chmod g+rx $HOME` (Apache needs permission to access the $HOME dir)
     * `sudo systemctl restart apache2.service`
   * CentOS:
     * `sudo cp $HOME/eccs2/eccs2-centos.conf /etc/httpd/conf.d/eccs2.conf`
     * `sudo chgrp apache $HOME ; sudo apache g+rx $HOME` (Apache needs permission to access the $HOME dir)
     * `sudo systemctl restart httpd.service`

## Utility

To perform a restart after an API change use the following command:

* `touch $HOME/eccs2/eccs2.ini`

# ECCS2 API JSON

* `/api/eccsresults` (Return the results of the last check ready for ECCS web interface)
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

# Utility for web interface

The available dates are provided by the first and the last file created into the `output/` directory

To clean the ECCS2 results from files older than last 7 days use (modify it on your needs):

* `crontab -e`

  ```bash
  SHELL=/bin/bash

  0 5 * * * /bin/bash $HOME/eccs2/clean7daysOldFiles.sh > $HOME/eccs2/logs/clean7daysOldFiles.log 2>&1  
  ```

# Utility for developers

## ECCS2 API Development Server

* `cd $HOME/eccs2 ; ./api.py`

# Authors

## Original Author

 * Marco Malavolti (marco.malavolti@garr.it)
