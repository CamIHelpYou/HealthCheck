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
    os.system("maglev login")
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

    load = SystemCall("w")
    usageSearch = re.search(r'load\saverage:\s(.*)', load.output)
    cpu = usageSearch.group(1)
    for number in cpu.split(','):
        if float(number) > 40:
            load.problemMessage = "CPU usage is high\n\n" + load.output

    memory = SystemCall("free -h | awk '{print $6}'; free -h | awk '{print $3}' | grep B")
    for line in memory.output.split('\n'):
        availableSearch = re.search(r'(\w+)(G)', line)
        swapSearch = re.search(r'(\w+)(B)', line)
        if availableSearch is not None:
            if float(freavailableSearch.group(1)) < 30:
                memory.problemMessage = "Free memory is low\n\n" + memory.output
        elif swapSearch is not None:
            if float(swapSearch.group(1)) > 10:
                memory.problemMessage = "Swap memory is high\n\n" + memory.output

    dockerrun = SystemCall("systemctl status docker")
    if "running" not in dockerrun.output:
        dockerrun.problemMessage = "Docker is not running\n\n" + dockerrun.output

    kuberun = SystemCall("systemctl status kubelet")
    if "running" not in kuberun.output:
        dockerrun.problemMessage = "Kubelet is not running\n\n" + kuberun.output

    docker = SystemCall("docker ps -f status=exited | awk -F'  +' '{print $5}'")
    for line in docker.output.split('\n'):
        


    





'''
Driver function
'''
Problems = []
authentication()
getoutput(Problems)



