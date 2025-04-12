#!/bin/bash

kubectl delete all --all -n teamflow-namespace  # Deletes pods, services, deployments, etc.
kubectl delete configmap,secret --all -n teamflow-namespace  # Delete configs and secrets
