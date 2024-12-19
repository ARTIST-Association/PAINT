#!/bin/bash
PAINT_ROOT=/home/paint/PAINT
ENV_PATH=/home/paint/venv
AVAILABLE_PATH=/etc/apache2/sites-available
ENABLED_PATH=/etc/apache2/sites-enabled

echo "Assuming that you are logged in as a user with sudo rights"

# Initial Server Setup with Debian 11.
echo "Setting Up a Basic Firewall"
sudo apt update
sudo apt install ufw
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status

# Installing Apache
sudo apt update
sudo apt install apache2
sudo ufw app list
echo "Your output will be a list of the application profiles"
sudo ufw allow 'WWW'
sudo ufw status
echo "The output will provide a list of allowed HTTP traffic"
echo "Make sure the service is active by running the command for the systemd init system"
sudo systemctl status apache2
hostname -I
sudo apt install curl
curl -4 icanhazip.com
IP_ADDRESS=$(hostname -I | awk '{print $1}')
echo "Enter http://$IP_ADDRESS in the browser"
sudo mkdir -p /var/www/paint_domain
sudo chown -R $USER:$USER /var/www/paint_domain
sudo chmod -R 755 /var/www/paint_domain

# Install git.
sudo apt-get update
sudo apt-get -y install apache2 git python3-venv

# Enable apache proxy.
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo a2enmod alias
sudo a2enmod cache
sudo a2enmod rewrite

# Enable headers running.
sudo a2enmod headers

# Check if repository exists, if not clone, if it exists pull.
if [ ! -d "$PAINT_ROOT" ]; then
  git clone https://github.com/ARTIST-Association/PAINT.git $PAINT_ROOT
else
  cd "${PAINT_ROOT}" || exit 1
  git pull
fi

# Navigate to repository and create virtual environment if it doesn't exist yet.
cd "${PAINT_ROOT}" || exit 1
if [ ! -d "$ENV_PATH" ]; then
  python3 -m venv $ENV_PATH
fi

# Navigate to html directory.
cd ${PAINT_ROOT}/html || exit 1

# Copy configuration files to correct folder.
sudo cp paint_domain.conf $AVAILABLE_PATH/paint_domain.conf
sudo cp paint_domain-le-ssl.conf $AVAILABLE_PATH/paint_domain-le-ssl.conf

# Create symlinks in enabled folder.
sudo ln -sf $AVAILABLE_PATH/paint_domain.conf $ENABLED_PATH/paint_domain.conf
sudo ln -sf $AVAILABLE_PATH/paint_domain-le-ssl.conf $ENABLED_PATH/paint_domain-le-ssl.conf

# Navigate back to repository root.
cd "${PAINT_ROOT}" || exit 1

sudo a2ensite paint_domain.conf
sudo a2dissite 000-default.conf
sudo apache2ctl configtest
echo "You should recieve: Syntax OK"
sudo systemctl restart apache2

# Activate virtual environment and upgrade pip.
source $ENV_PATH/bin/activate
pip install --upgrade pip

# Install dependencies.
pip install --upgrade .

# Mount to the LSDF if not already mounted.
echo "Checking if LSDF is already mounted..."
if mountpoint -q /mnt/lsdf; then
  echo "LSDF is already mounted."
else
  echo "Mounting to the LSDF..."
  sudo sshfs -o umask=0,uid=0,gid=0,allow_other scc-paint-0001@os-login.lsdf.kit.edu:/lsdf/kit/scc/projects/paint /mnt/lsdf
  if [ $? -eq 0 ]; then
    echo "Mount successful."
  else
    echo "Failed to mount."
  fi
fi
