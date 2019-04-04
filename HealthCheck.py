#!/usr/bin/python
'''
@Author: camli

Purpose is to run through a DNA Center health check according to
https://apps.na.collabserv.com/wikis/home?lang=en-us#!/wiki/W781b350055ce_4000_b067_8140e4587ba4/page/DNAC%20-%20Checklist%20for%20smooth%20upgrade%20experience
'''


import os
import re


class SystemCall(object):
    '''
    Object for system calls and their results
    '''
    def __init__(self, call):
        self.call = call
        self.output = self.command(call)
        self.problemMessage = ""

    def command(self, call):
        return os.popen(call).read()


def authentication():
    '''
    This function authenticates the user to make all the calls in getoutput()
    '''
    print("serial number is: ")
    os.system("sudo cat /sys/devices/virtual/dmi/id/chassis_serial")


def getoutput(Problems):
    '''
    This function will be all the command line calls to check
    '''
    appliance = SystemCall("cat /sys/devices/virtual/dmi/id/product_name")
    if "DN1-HW-APL" not in appliance.output:
        appliance.problemMessage = "Not a DNAC appliance"
        Problems.append(appliance)

    disk = SystemCall("df -h")
    for line in disk.output.split('\n'):
        usageSearch = re.search(r'(\w+)([0-9]+%)', line)
        if usageSearch is not None:
            if int(usageSearch.group(1)) > 60:
                disk.problemMessage = "Disk usage is high\n\n" + disk.output
                Problems.append(disk)
                break

    load = SystemCall("w")
    usageSearch = re.search(r'load\saverage:\s(.*)', load.output)
    cpu = usageSearch.group(1)
    for number in cpu.split(','):
        if float(number) > 40:
            load.problemMessage = "CPU usage is high\n\n" + load.output
            Problems.append(load)
            break

    memory = SystemCall("free -h | awk '{print $6}'; free -h | awk '{print $3}' | grep B")
    for line in memory.output.split('\n'):
        availableSearch = re.search(r'(\w+)(G)', line)
        swapSearch = re.search(r'(\w+)(B)', line)
        if availableSearch is not None:
            if float(availableSearch.group(1)) < 30:
                memory.problemMessage = "Free memory is low\n\n" + memory.output
                Problems.append(memory)
                break
        elif swapSearch is not None:
            if float(swapSearch.group(1)) > 10:
                memory.problemMessage = "Swap memory is high\n\n" + memory.output
                Problems.append(memory)
                break

    dockerrun = SystemCall("systemctl status docker")
    if "running" not in dockerrun.output:
        dockerrun.problemMessage = "Docker is not running\n\n" + dockerrun.output
        Problems.append(dockerrun)

    kuberun = SystemCall("systemctl status kubelet")
    if "running" not in kuberun.output:
        dockerrun.problemMessage = "Kubelet is not running\n\n" + kuberun.output
        Problems.append(kuberun)

    docker = SystemCall("docker ps -f status=exited | awk -F'  +' '{print $5}'")
    if "days" in docker.output:
        docker.problemMessage = "Exited containers older than a day are present in 'docker ps -f status=exited'. Please use the following command to clear them:\ndocker rm -v $(docker ps -q -f status=exited)"
        Problems.append(docker)

    nodestatus = SystemCall("magctl node display | grep -v STATUS")
    for line in nodestatus.output.split('\n'):
        if "Ready" not in line:
            if line is '':
                continue
            nodestatus.problemMessage = "Nodes not all ready\n" + nodestatus.output
            Problems.append(nodestatus)
            break

    pods = SystemCall("""kubectl get pods --all-namespaces -o json | jq -r '.items[] | select(.status.reason!=null) | select(.status.reason | contains("Evicted")) | .metadata.name + " " + .metadata.namespace'""")
    if len(pods.output) is not 0:
        pods.problemMessage = """Pods are not being reaped appropriately. Use the following to remove pods from the evicted state:\nkubectl get po -a --all-namespaces -o json | jq  '.items[] | select(.status.reason!=null) | select(.status.reason | contains("Evicted")) | "kubectl delete po \(.metadata.name) -n \(.metadata.namespace)"' | xargs -n 1 bash -c"""
        Problems.append(pods)

    maglev = SystemCall("maglev package status")
    if "DEPLOYED" not in maglev.output:
        maglev.problemMessage = "Maglev commands aren't working, check the frontend API gateway (kong)"
        Problems.append(maglev)

    catalog = SystemCall("maglev catalog settings validate")
    if "Parent catalog settings are valid" not in catalog.output:
        catalog.problemMessage = "Catalog server cannot reach the global catalog server at www.ciscoconnectdna.com:443"
        Problems.append(catalog)

    state = SystemCall("maglev catalog system_update_package display | egrep [0-9]+ | grep -v https")
    for line in state.output.split('\n'):
        if "READY" not in line:
            if line is '':
                continue
            state.problemMessage = "System packages are not fully downloaded\n" + state.output
            Problems.append(state)
            break

    return Problems


def printProblems(Problems):
    if len(Problems) is 0:
        print('There are no issues')
        return
    print('SYSTEM IS EXPERIENCING THE FOLLOWING ISSUES:\n')
    for element in Problems:
        print('\n')
        print("--" + element.problemMessage)





'''
Driver function
'''
Problems = []
authentication()
Problems = getoutput(Problems)
printProblems(Problems)
print('done')



