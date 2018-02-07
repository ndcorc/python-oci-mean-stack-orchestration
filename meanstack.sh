#!/bin/sh
sudo iptables -F

#yum install wget –y
wget -O bitnami-mean-linux-installer.run https://bitnami.com/redirect/to/159963/bitnami-meanstack-3.4.9-0-linux-x64-installer.run
chmod +x bitnami-mean-linux-installer.run
./bitnami-mean-linux-installer.run --mode unattended --enable-components rockmongo --apache_server_port 8080 --apache_server_ssl_port 8443 --mongodb_password welcome1