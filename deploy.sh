#!/bin/bash

ARG1=${1:-deploy}
ARG2=${1:-main}
ssh covid19-deployer@covid19admin.py.staging.yipl.com.np 'bash -s' < script.sh $ARG1 $ARG2
