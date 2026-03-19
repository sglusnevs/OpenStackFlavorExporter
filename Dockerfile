FROM python:3.14-alpine

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY . /usr/src/app

RUN apk add --no-cache build-base linux-headers && pip3 install --no-cache-dir --root-user-action ignore -r requirements.txt && apk del build-base linux-headers

EXPOSE 8080

CMD ["python3","OpenStackFlavorExporterServer.py"]
