#!/bin/bash

# Secure with Lets Encrypt
sudo apt install certbot python3-certbot-apache
sudo ufw allow 'WWW Full'
sudo ufw delete allow 'WWW'
sudo ufw status
certbot --apache -d paint-database.org
ls /etc/letsencrypt/live/
echo "You can test the website by navigating to https://paint-database.org"
