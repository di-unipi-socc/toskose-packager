[![Build Status](https://travis-ci.com/matteobogo/toskose.svg?token=jguSttdQLntpxgiqp3py&branch=master)](https://travis-ci.com/matteobogo/toskose)
[![Bintray](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Bintray](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-370/)
[![Bintray](https://img.shields.io/badge/python-3.7.1-blue.svg)](https://www.python.org/downloads/release/python-371/)
[![Bintray](https://img.shields.io/badge/version-0.1.0-blue.svg)]()
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a47cb809855b4be3a9440a2762665111)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=matteobogo/toskose&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/a47cb809855b4be3a9440a2762665111)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=matteobogo/toskose&utm_campaign=Badge_Coverage)


# toskose
toskose is a tool for translating a TOSCA-based configuration into docker-compose.

## TOSCA
TOSCA (Topology and Orchestration Specification for Cloud Application) is an OASIS standard to enhance the portability and operational management of cloud and other types of applications and services across their entire lifecycle.

TOSCA permits to define the interoperable description of services and applications hosted on the cloud and elsewhere; including their components, relationships, dependencies, requirements and capabilities.[1]

TOSCA is an emerging standard whose main goal is to enable the creation of portable cloud applications and the automation of their deployment. In order to achieve this goal, TOSCA focuses on the following three sub-goals.

- Automated application deployment and management. TOSCA aims at providing a language to express how to automatically deploy and manage complex cloud applications.This objective is achieved by requiring developers to define an abstract topology of a complex application and to create plans describing its deployment and management.
- Portability of application descriptions and their management. TOSCA aims at addressing the portability of application descriptions and their management (but not the actual portability of the applications themselves). To this end, TOSCA provides a standardized way to describe the topology of multi-component applications. It also addresses management portability by relying on the portability of workflow languages used to describe deployment and management plans.
- Interoperability and reusability of components. TOSCA aims at describing the components of complex cloud applications in an interoperable and reusable way. [2]

## SOCC tool-chain
TODO

## Motivations


## References
[1] OASIS TOSCA. https://www.oasis-open.org/committees/tosca/
[2] Antonio Brogi, Jacopo Soldani, PengWei Wang. TOSCA in a nutshell: Promises and perspectives. 2014. ISBN: 978-3-662-44878-6. Service-oriented and Cloud Computing. Volume: 8745. pages: 171-186. Villari Massimo and Zimmermann Wolf and Lau Kung-Kiu. Springer Berlin Heidelberg.
[3] Antonio Brogi, Davide Neri, Luca Rinaldi, Jacopo Soldani. Orchestrating incomplete TOSCA applications with Docker.
