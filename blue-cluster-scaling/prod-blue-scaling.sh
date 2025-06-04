#!/bin/bash

cluster='prod-blue-eks-cluster'

export AWS_REGION="eu-west-1"
export AWS_DEFAULT_OUTPUT="json"

on_demand_4xlarge_app_a="stirring-camel"
on_demand_4xlarge_app_b="maximum-crappie"
on_demand_4xlarge_app_c="cosmic-turkey"
on_demand_ops_prom_b_amd="saving-mutt"
on_demand_xlarge_web_amd="humble-seahorse"
spot_4xlarge_app_a="mint-swan"
spot_4xlarge_app_b="actual-crappie"
spot_4xlarge_app_c="funny-coral"
spot_8xlarge_app_a="resolved-lobster"
spot_8xlarge_app_b="humble-catfish"
spot_8xlarge_app_c="rich-foxhound"
spot_xlarge_ops_amd="first-mudfish"

case "$1" in
  "up")
  echo "$cluster -  Going $1";
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-on-demand-4xlarge-app-a-$on_demand_4xlarge_app_a" --scaling-config minSize=1,desiredSize=1)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-on-demand-4xlarge-app-b-$on_demand_4xlarge_app_b" --scaling-config minSize=1,desiredSize=1)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-on-demand-4xlarge-app-c-$on_demand_4xlarge_app_c" --scaling-config minSize=1,desiredSize=1)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-on-demand-ops-prom-b-amd-$on_demand_ops_prom_b_amd" --scaling-config minSize=2,desiredSize=2)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-on-demand-xlarge-web-amd-$on_demand_xlarge_web_amd" --scaling-config minSize=2,desiredSize=2)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-spot-4xlarge-app-a-$spot_4xlarge_app_a" --scaling-config minSize=2,desiredSize=2)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-spot-4xlarge-app-b-$spot_4xlarge_app_b" --scaling-config minSize=2,desiredSize=2)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-spot-4xlarge-app-c-$spot_4xlarge_app_c" --scaling-config minSize=2,desiredSize=2)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-spot-8xlarge-a-$spot_8xlarge_app_a" --scaling-config minSize=1,desiredSize=1)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-spot-8xlarge-b-$spot_8xlarge_app_b" --scaling-config minSize=1,desiredSize=1)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-spot-8xlarge-c-$spot_8xlarge_app_c" --scaling-config minSize=1,desiredSize=1)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "prod-blue-eks-cluster-spot-xlarge-ops-amd-$spot_xlarge_ops_amd" --scaling-config minSize=2,desiredSize=2)

  ;;
  "down")
  for ng in $(aws eks  list-nodegroups --cluster-name $cluster --query 'nodegroups[*]' | jq -r '.[]') ;
    do
      echo "$cluster - $ng - Going $1";
      resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name $ng  --scaling-config minSize=0,desiredSize=0)
    done ;
  ;;
  *)
  echo "$cluster - $ng - No Action";
  ;;
esac
