"""
This is a simple script to print the background jobs and webapps that do not have autoscaling configured.

REQUIREMENTS:
> kubectl (`brew install kubectl`)
> Access to the cluster (e.g. - `aws eks update-kubeconfig --name beta-eks-cluster --region eu-west-1`)
  (Refer to the guide - https://naspersclassifieds.atlassian.net/wiki/spaces/DBZInfra/pages/1149634177/EKS+Developer+Onboarding+-+Cron+Jobs+Background+Jobs)

NOTES:
> Make sure to do aws-okta login and switch to the apprpriate aws profile.
> Check if the correct context is selected for kubectl (`kubectl config current-context`)

INPUTS:
> List of namespaces
"""

import argparse
import subprocess

COLOUR_GREEN = '\033[92m'
COLOUR_RED = '\033[91m'
COLOUR_END = '\033[0m'

def get_current_context():
    out = subprocess.Popen(
        ['kubectl', 'config', 'current-context'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    context = out.communicate()[0].decode('utf-8').strip("'").split("/")[1]
    return context


def check_authorized():
    out = subprocess.Popen(
        ['kubectl', 'cluster-info'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout = out.communicate()[0].decode('utf-8').strip("'")
    if 'error' in stdout:
        print("ERROR: ", stdout)
        return False
    return True


def get_hpa_list_by_target_kind(target_kind, namespace):
    out = subprocess.Popen(
        ['kubectl', 'get', 'hpa', '-n', namespace, '-o',
            'jsonpath=\'{range .items[?(@.spec.scaleTargetRef.kind == "' + target_kind + '")]}{@.spec.scaleTargetRef.name}{\"\\n\"}{end}\''],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout = out.communicate()[0].decode('utf-8').strip("'")
    hpa_list = stdout.split('\n')
    hpa_list = list(filter(None, hpa_list))
    return hpa_list


def get_resource_list(resource_kind, namespace):
    out = subprocess.Popen(
        ['kubectl', 'get', resource_kind, '-n', namespace, '-o',
            'jsonpath=\'{range .items[*]}{@.metadata.name}{\"\\n\"}{end}\''],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    stdout = out.communicate()[0].decode('utf-8').strip("'")
    resource_list = stdout.split('\n')
    resource_list = list(filter(None, resource_list))
    return resource_list


def check_autoscaling(namespace):
    deployment_hpa_list = get_hpa_list_by_target_kind('Deployment', namespace)
    rollout_hpa_list = get_hpa_list_by_target_kind('Rollout', namespace)
    deployment_list = get_resource_list('deployment', namespace)
    rollout_list = get_resource_list('rollout', namespace)
    deployments_no_hpa = list(set(deployment_list)-set(deployment_hpa_list))
    rollouts_no_hpa = list(set(rollout_list)-set(rollout_hpa_list))
    print("\n---------------------------------------------------------------------")
    print(f'{COLOUR_GREEN}Namespace : {namespace}{COLOUR_END}')
    print(f'{COLOUR_GREEN}\nWebapps :-{COLOUR_END}')
    print(f'Out of {len(rollout_list)} webapps, autoscaling has been configured for {len(rollout_list) - len(rollouts_no_hpa)} webapps')
    if rollouts_no_hpa:
        print('{COLOUR_RED}Autoscaling needs to be configured for the following webapps:{COLOUR_END}')
        for rollout in rollouts_no_hpa:
            print(rollout)
    print(f'{COLOUR_GREEN}\nBackground Jobs :-{COLOUR_END}')
    print(f'Out of {len(deployment_list)} background jobs, autoscaling has been configured for {len(deployment_list) - len(deployments_no_hpa)} background jobs')
    if deployments_no_hpa:
        print(f'{COLOUR_RED}Autoscaling needs to be configured for the following background jobs:{COLOUR_END}')
        for deployment in deployments_no_hpa:
            print(deployment)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--namespaces',
        '-n',
        nargs='+',
        help='The namespaces in which you want to check missing autoscaling configuration for background jobs and rollouts',
        type=str,
        required=True
    )
    args = parser.parse_args()
    namespaces = args.namespaces
    context = get_current_context()
    print(f'{COLOUR_GREEN}Current context: {context}{COLOUR_END}')
    if check_authorized():
        for namespace in namespaces:
            check_autoscaling(namespace)


if __name__ == '__main__':
    main()
