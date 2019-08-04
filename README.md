[![Build Status](https://travis-ci.com/di-unipi-socc/toskose.svg?branch=master)](https://travis-ci.com/di-unipi-socc/toskose)
[![Bintray](https://img.shields.io/badge/python-%E2%89%A5%203.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![PyPI version](https://badge.fury.io/py/toskose.svg)](https://badge.fury.io/py/toskose)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/a47cb809855b4be3a9440a2762665111)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=matteobogo/toskose&amp;utm_campaign=Badge_Grade)
[![Codacy Badge](https://api.codacy.com/project/badge/Coverage/a47cb809855b4be3a9440a2762665111)](https://www.codacy.com?utm_source=github.com&utm_medium=referral&utm_content=matteobogo/toskose&utm_campaign=Badge_Coverage)

# toskose

# Testing
The two case study used for testing Toskose are

- Thinking - https://github.com/di-unipi-socc/thinking
- Sockshop - https://github.com/microservices-demo/microservices-demo

Unfortunately, the plan execution feature is not available yet (future work).  
However, there are two possibility for booting up a case study application using the Toskose Manager API.

- manually with cURL/SwaggerUI
- automatically with <case_study>-boot.sh (work in progress)

Toskose Manager must be available at ```http://localhost:10000/api/v1/```

Because plan executor is not implemented yet, if there's a dependency, e.g. payment-create -> payment-start, you must check that the dependency is satisfied before start the next lifecycle operation.
In other words, you need to check that the user-create process is the EXITED status with no errors (exit status 0; expected) by looking in the Supervisord logs.

Notes  
- you can monitor the log of each lifecycle operation to know its current status   
e.g payment-create   
``` curl -X GET "http://localhost:10000/api/v1/node/payment_container/payment/create/log?tail=false&std_type=stdout&offset=0&length=0" -H  "accept: application/json" ```
- you can also monitor the status of the lifecycle operation process by querying the Supervisord log  
e.g. payment_container service  
``` docker service logs -f sockshop-stack_payment_container ```

## Requisites
- Docker 
- Swarm Node or initialize one with ``` docker swarm init  ```

## Check stack status
```
docker stack ps <case_study>-stack
docker stack services <case_study>-stack
```

## Thinking
### Setup
```
docker stack deploy --compose-file tests/docker-stack-thinking.yml
```

### Start
The Thinking Plan is the following:

- Maven Service: create -> configure -> push_default -> start
- Node Service: create -> configure -> start

cURL commands:
```
curl -X POST "http://localhost:10000/api/v1/node/maven/api/create" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/maven/api/configure" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/maven/api/push_default" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/maven/api/start" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/node/gui/create" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/node/gui/configure" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/node/gui/start" -H  "accept: application/json"
```

### Play
Thoughts API should be available at ``` http://localhost:8000/thoughts ```  
Thinking should be available at ``` http://localhost:8080/thoughts.html ```

## Sockshop
### Setup
``` 
docker stack deploy --compose-file tests/docker-stack-sockshop.yml sockshop-stack
```

### Start
The Sockshop plan is the following:

- Shipping Service: start
- Payment Service: create -> start
- Carts Service: start
- User Service: create -> start
- Catalogue Service: create -> start
- Orders Service: create -> start
- Front-end Service: create -> configure -> start

cURL commands:
```
curl -X POST "http://localhost:10000/api/v1/node/shipping_container/shipping/start" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/payment_container/payment/create" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/payment_container/payment/start" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/carts_container/carts/start" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/user_container/user/create" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/user_container/user/start" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/catalogue_container/catalogue/create" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/catalogue_container/catalogue/start" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/orders_container/orders/create" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/orders_container/orders/start" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/front-end_container/front-end/create" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/front-end_container/front-end/configure" -H  "accept: application/json"

curl -X POST "http://localhost:10000/api/v1/node/front-end_container/front-end/start" -H  "accept: application/json"
```

### Play
Sockshop should be available at ``` http://localhost/index.html ```

## Remove all
```
docker stack rm <case_study>-stack

//be careful it removes ALL volumes on the host machine
docker volume prune
```