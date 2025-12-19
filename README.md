# OpenStackFlavorExporter

## Overview

This service provides a REST-API to retrieve information about OpenStack flavors (total and available). 
It is written for [de.NBI cloud](https://cloud.denbi.de) OpenStack setups especially in Bielefeld, 
but can easily be adapted to any OpenStack installation providing GPU (or other) resources.

The current implementation is not yet fully compatible with 
[OpenStack Unified Resources](https://docs.openstack.org/nova/latest/admin/unified-limits.html), when  
using _special_ resources like GPUs.

_The OpenStackFlavorExporter is the successor to the 
[OpenstackGPUService](https://github.com/deNBI/OpenstackGPUService) and, for compatibility reasons, 
adopts its API._

### Prerequisites 

Without special resources (such as GPUs), the Flavor Exporter should run with any reasonably current
OpenStack implementation (tested with OpenStack Caracal - 2024.1).


Provided that GPU-supported flavor or the specified GPUs are taken into account, it needs some
additional configuration of aggregates and flavors to work properly.

#### Aggregates
GPU hypervisors have to be grouped into different aggregates based on their GPU type (`gpu_type`) 
and on the number of GPUs they provide (`gpu_count`). Every aggregate has to make some extra 
metadata available:

  - **gpu='<boolean>'** Whether this aggregate provides GPU resources.
  - **gpu_count='<integer>'** Number of GPUs provided.
  - **gpu_type='<string>'** Type (**alias name**) of GPU provided.

##### Example
```
$ openstack aggregate show 'Delta GPU V100'
+-------------------+--------------------------------------------------------------------------------+
| Field             | Value                                                                          |
+-------------------+--------------------------------------------------------------------------------+
| availability_zone | default                                                                        |
| created_at        | 2018-10-13T19:08:59.000000                                                     |
| deleted_at        | None                                                                           |
| hosts             | host1,host2,...                                                                |
| id                | 10                                                                             |
| is_deleted        | False                                                                          |
| name              | Delta GPU V100                                                                 |
| properties        | cores='28', gpu='True', gpu_count='2', gpu_type='V100', hyperthreading='false' |
| updated_at        | 2022-03-23T14:31:00.000000                                                     |
| uuid              | xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx                                           |
+-------------------+--------------------------------------------------------------------------------+
```

#### Flavors

Currently GPU are supported using the 
[PCI-passthrough feature](https://docs.openstack.org/nova/pike/admin/pci-passthrough.html)
of Openstack. Flavors must be configured setting the _pci_passthrough:alias_ property='<alias name>:<count>. The service
matches the **alias name** with aggregates gpu_type (aggregates metadata) to calculate the
total count and current available number of each flavor.

**There is of course more configuration work to do to support GPU(PCI) devices properly.**

## Requirements
Python 3.10+

## Usage

It recommend to install dependencies in a separate virtual environment.

```
$ python3 -m venv venv
$ source venv/bin/activate
(venv)$ pip3 install -r requirements.txt
```

When connecting to a "real" Openstack Setup, you have to source your
RC file beforehand.  The Openstack user should has at  least the
capability to list all servers, flavors, hypervisor and aggregates.

```
(venv)$ source my_project-openrc.sh
``` 

### Server

For performance reasons (and better user feelings) the server returns only cached
data. The cache (only memcached is supported) is updated continuously.

![](images/openstack_gpu_service.png)

1. A user/client requests for data.
2. The server ask the cache if the requested resources are available.
3. Depending on the cache status, the result is returned immediately or calculated (long running task!).
4. Independent of the REST API, the cache is updated continuously (every 150 seconds by default).


To run the server, please execute the following from the root directory:

```
(venv)$ python3 OpenStackFlavorExporterServer.py 
```

When running OpenstackGPUServer without further arguments a memcached service listening on
127.0.0.1:11211 is expected and REST is bind to http://127.0.0.1:8080.

The swagger documentation is available at:

```
http://localhost:8080/docs/
```

Your OpenAPI definition lives here:

```
http://localhost:8080/openapi.json
```

### Example API Call (using curl)

#### Legacy (V1)

```
curl -X 'GET' 'http://localhost:8080/gpus/flavors/'  -H 'accept: application/json'
```

### Current Version (V2)
```
curl -X 'GET' 'http://localhost:8080/v2/flavors/'  -H 'accept: application/json'
```

##  (Units-)Test

OpenstackGPUService comes with a full set of units test. All external dependencies concerning 
the Openstack API are mocked using unittest.mock functionality.

###  Mock Test Setup
The Mock test setup "simulates" the following setup.
- two aggregates (for GPU and non GPU based hypervisors)
- three hypervisors available (28 cores, 384 cores, 4 TB local disc space), two of them having 
  two GPUs on board
- two instances running (de.NBI large, de.NBI GPU V100 medium)

Calling the `gpu_flavors_get` methods should return a list of three GPU flavors.
- de.NBI GPU V100 medium (4 total, 3 available)
- de.NBI GPU V100 large (4 total, 3 available)
- de.NBI 2 GPU V100 large (2 total, 1 available)

### Integration test
To launch the integration tests, use tox from the root directory:
```
(venv)$ pip install tox
(venv)$ tox
```

## Running with Docker

To run the server inside a Docker container, please execute the following from the root directory:

```bash
# building the image
docker build -t openapi_server .

# start up a container in the host network
docker run --network host --env-file ./env.file denbi/openstackgpuservice
```

where `env.file` contains the Openstack environment :
```
OS_REGION_NAME=Bielefeld
OS_PROJECT_DOMAIN_ID=default
OS_INTERFACE=public
OS_AUTH_URL=https://openstack.cebitec.uni-bielefeld.de:5000/v3/
OS_USERNAME=XXXX
OS_PROJECT_ID=XXXXX
OS_USER_DOMAIN_NAME=Default
OS_PROJECT_NAME=XXXXX
OS_PASSWORD=XXXXXX
```

## Running with Docker Compose
Run a OpenstackGPUService together with a memcached service container with docker compose is also
supported. 


## Security considarations

The OpenStackFlavorExporter is based on FastAPI and therefore does not implement
any authentication or authorization for protection. It is strongly recommended
to run the OpenStackFlavorExporter behind a reverse proxy.

## License

The project is licensed under Apache License Version 2.0.

