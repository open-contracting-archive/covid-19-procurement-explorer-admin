#!/bin/bash
ARG1=${1:-main}
echo "deploying covid19admin branch=$ARG1"
cd /home/covid19-deployer/deploy;
./run.py 'covid19-dev' state.apply pillar='{"python_apps":{"covid19admin":{"git":{"branch":'"$ARG1"'}}}}';
exit;
