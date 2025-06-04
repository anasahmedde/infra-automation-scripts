#!/bin/bash

export AWS_PROFILE="dbz-testing"
cluster='space-gold-eks-cluster'
region='me-central-1'

case "$1" in
  "up")
  echo "$cluster -  Going $1 in region $region";
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-gold-eks-cluster-ondemand-app-general-xlarge" --scaling-config minSize=0,maxSize=10,desiredSize=0 --region $region)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-gold-eks-cluster-ondemand-large-ops-a" --scaling-config minSize=1,maxSize=10,desiredSize=1 --region $region)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-gold-eks-cluster-ondemand-xlarge-app-a" --scaling-config minSize=0,maxSize=10,desiredSize=0 --region $region)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-gold-eks-cluster-spot-4xlarge-app-a" --scaling-config minSize=1,maxSize=10,desiredSize=1 --region $region)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-gold-eks-cluster-spot-app-general-g4xlarge" --scaling-config minSize=1,maxSize=10,desiredSize=1 --region $region)
  resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name  "space-gold-eks-cluster-spot-large-ops-a" --scaling-config minSize=1,maxSize=10,desiredSize=1 --region $region)

  ;;
  "down")
  for ng in $(aws eks  list-nodegroups --cluster-name $cluster --region $region --query 'nodegroups[*]' | jq -r '.[]') ;
    do
      echo "$cluster - $ng - Going $1";
      resp=$(aws eks update-nodegroup-config --cluster-name $cluster --nodegroup-name $ng  --scaling-config minSize=0,maxSize=1,desiredSize=0 --region $region)
  done ;
  ;;
  *)
  echo "$cluster - $ng - No Action";
  ;;
esac 