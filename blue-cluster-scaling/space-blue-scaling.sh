#!/bin/bash

cluster='space-blue-eks-cluster'

export AWS_REGION="eu-west-1"
export AWS_DEFAULT_OUTPUT="json"

ondemand_large_ops_a="harmless-adder"
ondemand_xlarge_app_a="fresh-donkey"
spot_large_ops_a="amazing-quail"
spot_4xlarge_app_a="hopeful-crawdad"
spot_app_general_g4xlarge="usable-mallard"

case "$1" in
  "up")
  echo "$cluster -  Going $1";
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-blue-eks-cluster-ondemand-large-ops-a-$ondemand_large_ops_a" --scaling-config minSize=0,maxSize=10,desiredSize=0)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-blue-eks-cluster-ondemand-xlarge-app-a-$ondemand_xlarge_app_a" --scaling-config minSize=0,maxSize=10,desiredSize=0)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-blue-eks-cluster-spot-large-ops-a-$spot_large_ops_a" --scaling-config minSize=4,maxSize=10,desiredSize=6)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-blue-eks-cluster-spot-4xlarge-app-a-$spot_4xlarge_app_a" --scaling-config minSize=5,maxSize=20,desiredSize=7)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-blue-eks-cluster-spot-app-general-g4xlarge-$spot_app_general_g4xlarge" --scaling-config minSize=1,maxSize=10,desiredSize=1)

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
