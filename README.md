<center>
<img src=img/toskose-logo-v3.png width=300>
</center>

[![Build Status](https://travis-ci.com/di-unipi-socc/toskose.svg?branch=master)](https://travis-ci.com/di-unipi-socc/toskose)
[![Bintray](https://img.shields.io/badge/python-%E2%89%A5%203.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![PyPI version](https://badge.fury.io/py/toskose.svg)](https://badge.fury.io/py/toskose)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a47cb809855b4be3a9440a2762665111)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=matteobogo/toskose&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/a47cb809855b4be3a9440a2762665111)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=matteobogo/toskose&utm_campaign=Badge_Coverage)

# Toskose

Toskose is a command-line tool that takes a Cloud Service ARchive (CSAR), which includes a [Topology and Orchestration Specification of Cloud Application (TOSCA)](https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=tosca), describing a multi-component cloud application, along with its artifacts, and it returns a [Docker Compose](https://docs.docker.com/compose/compose-file/) (v.3.7) deployment artifact that can be distributed on top of existing container orchestrators that support Docker as container runtime.

In particular, we start from an existing implementation of the TOSCA standardization, i.e., the [TosKer](https://github.com/di-unipi-socc/TosKer) specification, presented in

> A. Brogi, L. Rinaldi, J. Soldani  
> TosKer: A synergy between TOSCA and Docker for orchestrating multicomponent applications.  
> Software: Practice and Experience, vol.48, num. 11, pp. 2061-2079

The TosKer specification also permits to define the lifecycle of a software component separately from the lifecycle of the container that hosts it. In addition, it allows to define multiple components hosted in the same container. Toskose also recognizes self-managed containers, i.e., containers that do not support component-aware orchestration and are coordinated only by the container orchestrator as usual.

<center>
<img src=img/tosca_specification.png>
</center>

The Docker Compose produced by Toskose can be deployed natively on [Docker Swarm](https://docs.docker.com/engine/swarm/). In addition, it can be deployed on [Kubernetes](https://kubernetes.io/) using third-party tools such as [Kompose](http://kompose.io/) or [Compose on Kubernetes](https://github.com/docker/compose-on-kubernetes), which comes installed on [Docker Desktop](https://docs.docker.com/docker-for-windows/kubernetes/) and [Docker Enterprise](https://www.docker.com/products/docker-enterprise).

<center>
<img src=img/toskose-existing-orchestrators.png>
</center>

# How does it work?

Toskose produces new Docker images, i.e., the "toskosed" images. The Docker images associated to the containers (defined in the TOSCA specification) are enriched with a Process Management System ([Supervisor](http://supervisord.org/)), which becomes the main process of the container, maintaining it running. Subprocesses spawned by Supervisor represent implementations of the lifecycle operations of software components hosted in a container.

<center>
<img src=img/supervisor-orchestration.png>
</center>

Supervisor is "freezed" with a Python interpreter as a single executable and it is shipped in a standalone Docker image, i.e., the [Toskose Unit](https://github.com/di-unipi-socc/toskose-unit) (available on the [Docker Hub](https://hub.docker.com/r/diunipisocc/toskose-unit)). The Toskose Unit image is pulled on demand by Toskose during the "toskosing" process for copying the Supervisor executable inside the "toskosed" images, along with a self-generated configuration and the component(s) context.

<center>
<img src=img/toskose-unit.png>
</center>

Toskose enables a component-aware orchestration by adding an extra service, i.e., the [Toskose Manager](https://github.com/di-unipi-socc/toskose-manager), which is also containerized as well as the software components it coordinates. Toskose Manager is shipped as a standalone Docker image (available on the [Docker Hub](https://hub.docker.com/r/diunipisocc/toskose-manager)). Using the Docker DNS and the XML-RPC API exposed by Supervisor, the Toskose Manager is capable to find and orchestrate the lifecycle of software components, even if they are containerized in different nodes of a cluster.

<center>
<img src=img/toskose-manager.png>
</center>

Toskose generates a Docker Compose file from the TOSCA specification in the following way:

- Each TosKer container node becomes a Docker service with the "toskosed" image as the Docker image to start the container from.
- Each TosKer volume node becomes a Docker volume.
- A Docker Overlay Network, i.e. the Toskose Network, is defined with the [Overlay](https://docs.docker.com/network/overlay/) driver.

Toskose also sets the `init` flag for each service (available from Docker Compose v.3.7), which enables the [Tini](https://github.com/krallin/tini) init process for zombie fighting and signal forwarding.

<center>
<img src=img/toskose-ecosystem.png>
</center>

# Configuration

Toskose can be provided with an (optional) YAML-based configuration file, i.e., the Toskose Configuration. Mainly, it defines the "toskosed" images names (private Docker registries are supported), the XML-RPC API port (not exposed) and the network alias of each Supervisor instance, and other customisations (e.g. Supervisor log level). It also defines settings for the Toskose Manager (e.g., the Web API port). If the configuration file is not provided, Toskose is capable to generate a default one, using default values for ports and prompting the user for Docker-related information.

# Install

`pip install toskose`

# An Example - Thinking 2.0

Thinking 2.0 is an open source web application that allows its users to share their thoughts, so that all other users can read them through a web-based graphical user interface.

Thinking 2.0 extends the original [Thinking](https://github.com/di-unipi-socc/thinking) application with a [Log sniffer](https://github.com/mbok/logsniffer) containerized together with the Java Web API component, sharing the same Java 8 runtime.

Thinking 2.0 is structured as follows:

- A Web-based GUI written in Javascript in containerized in a [NodeJS environment](https://hub.docker.com/_/node/)
- A Web API and a Log sniffer both written in Java are containerized in a [Maven environment](https://hub.docker.com/_/maven)
- A self-managed MongoDB database as a [standalone container](https://hub.docker.com/_/mongo)

<center>
<img src=img/thinking-3.png>
</center>

Thinking 2.0 can be processed by Toskose as follows:

```
toskose -p -o /path/to/output \
tests/data/thinking-v2/thinking-v2.csar \
tests/data/thinking-v2/configurations/toskose.yml
```

Note: `toskose.yml` contains "toskosed" images information related to our Docker Hub repository, change those information if you want to push the "toskosed" images on you personal Docker registry.

An example of a Docker Compose for Thinking 2.0 generated by Toskose can be found in  

`tests/data/thinking-v2/docker-compose.yml`

The Docker Compose produced by Toskose can be deployed on top of existing container orchestrators that support Docker as container runtime such as Docker Swarm or Kubernetes.

## Docker Swarm

### Requirements

A Docker Swarm cluster initialized.

### Deploy

```
docker stack deploy -c tests/data/thinking-v2/docker-compose.yml thinking-stack
```

### Usage

Thinking 2.0 needs to be initialized using the component-aware orchestration offered by Toskose Manager.

Toskose Manager API should be available at `http://localhost:12000/api/v1`

<center>
<img src=img/toskose-manager-api.png>
</center>

Note: change the `localhost` hostname according to your cluster settings.

```
curl -X POST "http://localhost:12000/api/v1/node/maven/api/create" -H  "accept: application/json"

curl -X POST "http://localhost:12000/api/v1/node/maven/api/configure" -H  "accept: application/json"

curl -X POST "http://localhost:12000/api/v1/node/maven/api/push_default" -H  "accept: application/json"

curl -X POST "http://localhost:12000/api/v1/node/maven/api/start" -H  "accept: application/json"

curl -X POST "http://localhost:12000/api/v1/node/node/gui/create" -H  "accept: application/json"

curl -X POST "http://localhost:12000/api/v1/node/node/gui/configure" -H  "accept: application/json"

curl -X POST "http://localhost:12000/api/v1/node/node/gui/start" -H  "accept: application/json"
```

<center>
<img src=img/thinking-orchestration.png >
</center>

# Future Work

- Software components horizontal scaling (a) and (b)
- Component-aware self-healing (c)
- Management automation (d)

<center>
<img src=img/future-work.png>
</center>