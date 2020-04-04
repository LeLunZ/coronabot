FROM python:3

WORKDIR /install
COPY requirements.txt .
RUN pip install --install-option="--prefix=/install" -r requirements.txt


FROM python:3
COPY --from=0 /install /usr/local
RUN apt-get -y update
RUN apt-get install -y chromium

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/

# set display port to avoid crash
ENV DISPLAY=:99

WORKDIR /app
COPY src .
CMD ["python", "__init__.py"]