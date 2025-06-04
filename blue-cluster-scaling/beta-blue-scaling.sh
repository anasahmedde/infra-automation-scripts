#!/bin/bash

cluster='beta-blue-eks-cluster'

export AWS_REGION="eu-west-1"
export AWS_DEFAULT_OUTPUT="json"

ondemand_xlarge_app_c="tight-lab"
twoxlarge_ops_c="striking-monitor"
spot_2xlarge_ops_c="sharing-monitor"
spot_4xlarge_app_c="climbing-joey"

case "$1" in
  "up")
  echo "$cluster -  Going $1";
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "beta-blue-eks-cluster-ondemand-2xlarge-ops-c-$twoxlarge_ops_c" --scaling-config minSize=0,maxSize=10,desiredSize=0)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "beta-blue-eks-cluster-ondemand-xlarge-app-c-$ondemand_xlarge_app_c" --scaling-config minSize=0,maxSize=10,desiredSize=0)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "beta-blue-eks-cluster-spot-2xlarge-ops-c-$spot_2xlarge_ops_c" --scaling-config minSize=2,maxSize=30,desiredSize=2)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "beta-blue-eks-cluster-spot-4xlarge-app-c-$spot_4xlarge_app_c" --scaling-config minSize=1,maxSize=20,desiredSize=1)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "beta-blue-eks-cluster-spot-glarge-app-c-primary-slug" --scaling-config minSize=1,maxSize=50,desiredSize=1)

  ;;
  "down")
  for ng in $(aws eks  list-nodegroups --cluster-name $cluster --query 'nodegroups[*]' | jq -r '.[]') ;
    do
      echo "$cluster - $ng - Going $1";
      resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name $ng  --scaling-config minSize=0,maxSize=1,desiredSize=0)
    done ;
  ;;
  *)
  echo "$cluster - $ng - No Action";
  ;;
esac
