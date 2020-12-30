#!/bin/bash
ARG1=${1:-deploy}
ARG1=${1:-main}

echo "deploying covid19admin branch=$ARG1"
cd /home/covid19-deployer/deploy;
if [ $ARG1 == 'deploy' ]
then
  ./run.py 'covid19-dev' state.apply pillar='{"python_apps":{"covid19admin":{"git":{"branch":'"$ARG2"'}}}}';
 
elif [ $ARG1 == 'command'  ]
then
  ./run.py 'covid19-dev' state.sls_id django-custom-command covid19 pillar='{"custom_command":{"script":'"$ARG2"'}}'
else
  echo "Example: ./deploy.sh command manage.py command_name or ./deploy.sh deploy branch_name"
fi

exit;
