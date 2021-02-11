FROM python:3.8-buster

ENV DEBIAN_FRONTEND noninteractive

RUN curl -s https://deb.nodesource.com/gpgkey/nodesource.gpg.key | apt-key add - \
      && echo 'deb https://deb.nodesource.com/node_14.x buster main' > /etc/apt/sources.list.d/nodesource.list

RUN curl -s https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
      && echo 'deb http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list

RUN apt-get -qq update \
      && apt-get -qq install \
            google-chrome-stable \
            nodejs \
         --no-install-recommends \
      && rm -rf /var/lib/apt/lists/*

RUN npm install -g sass

RUN mkdir /app
WORKDIR /app

COPY bin/chrome_setup.bash bin/chrome_setup.bash
RUN bin/chrome_setup.bash

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN bin/populate_if_missing.bash

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
