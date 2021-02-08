FROM python:3.8

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && \
      apt-get -y install sudo

RUN apt-get -y install nodejs && \
	  apt-get -y install npm

COPY conf/node_setup.bash /
RUN /node_setup.bash

COPY conf/chrome_setup.bash /
RUN /chrome_setup.bash

COPY requirements.txt /
RUN pip install -r /requirements.txt

COPY requirements-dev.txt /
RUN pip install -r /requirements-dev.txt

COPY . /app
WORKDIR "/app"
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]