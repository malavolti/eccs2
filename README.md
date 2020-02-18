# HOWTO Install and Configure ECCS-2

* `sudo apt install mysql-server python3-pip`
* `pip3 install mysql-connector certifi selenium urllib3`

# Create and configure the ECCS-2 database
* `sudo mysql`
* `CREATE DATABASE eccs2db;`
* `CREATE USER 'eccs2user'@'localhost' IDENTIFIED BY '<password>';`
* `GRANT ALL PRIVILEGES ON eccs2db.* TO 'eccs2user'@'localhost'`
* `SHOW GRANTS FOR 'eccs2user'@'localhost';`
* `FLUSH PRIVILEGES;`

