# install node for post processors

npm install -g postcss-cli autoprefixer

#get dart sass
wget -q https://github.com/sass/dart-sass/releases/download/1.26.8/dart-sass-1.26.8-linux-x64.tar.gz --retry-connrefused --waitretry=1 --read-timeout=20 --timeout=15 -t 0
tar -xzf dart-sass-1.26.8-linux-x64.tar.gz
mv dart-sass /usr/bin/dart-sass
chown root:root /usr/bin/dart-sass
chmod +x /usr/bin/dart-sass
