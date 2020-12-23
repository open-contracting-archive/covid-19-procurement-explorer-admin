#!/bin/bash
ARG1=${1:-main}
ARG2=${2:-main}
echo "deploying covid19admin branch=$ARG1"
echo "deploying covid19 public branch=$ARG2"
cd /home/covid19-deployer/deploy;
./run.py 'covid19-dev' state.apply pillar='{"python_apps":{"covid19admin":{"git":{"branch":'"$ARG1"'}}},"reactjs_apps":{"covid19public":{"git":{"branch":'"$ARG2"'}}}}';
exit;
