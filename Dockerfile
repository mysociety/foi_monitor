FROM python:3.8

RUN apt-get update && \
      apt-get -y install sudo

RUN apt-get -y install nodejs && \
	  apt-get -y install npm

COPY scripts/node_setup.bash /
RUN /node_setup.bash

COPY scripts/chrome_setup.bash /
RUN /chrome_setup.bash

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY requirements-dev.txt /
RUN pip install -r /requirements-dev.txt

COPY . /app

RUN /app/scripts/populate_if_missing.bash

WORKDIR "/app"
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]