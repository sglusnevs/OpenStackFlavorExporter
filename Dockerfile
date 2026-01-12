FROM python:3.12-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY requirements.txt /usr/src/app/

RUN apk add --no-cache build-base linux-headers && pip3 install --no-cache-dir --root-user-action ignore -r requirements.txt && apk del build-base linux-headers

COPY . /usr/src/app

EXPOSE 8080

CMD ["python3","OpenStackFlavorExporterServer.py"]
