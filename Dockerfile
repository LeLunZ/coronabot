FROM python:3

WORKDIR /install
COPY requirements.txt .
RUN pip install --prefix="/install" -r requirements.txt


FROM python:3
COPY --from=0 /install /usr/local
RUN apt-get -y update
RUN apt-get install -y chromium
RUN apt-get install -y chromium-driver


# set display port to avoid crash
ENV DISPLAY=:99

WORKDIR /app
COPY src .
CMD ["python", "__init__.py"]