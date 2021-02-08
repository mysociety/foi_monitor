wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt-get -y install ./google-chrome-stable_current_amd64.deb
wget -q https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/bin/chromedriver
chown root:root /usr/bin/chromedriver
chmod +x /usr/bin/chromedriver