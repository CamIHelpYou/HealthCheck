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
        self.problemflag = False

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
        appliance.problemflag = True
        Problems.append(appliance)

    disk = SystemCall("df -h")
    for line in disk.output.split('\n')
        usageSearch = re.search(r'(\w+)(%)', line)
        if int(usageSearch.group(1)) > 60:
            disk.problemflag = True

    load = SystemCall("w")
    usageSearch = re.search(r'load\saverage:\s(.*)', load.output)
    cpu = usageSearch.group(1)
    for number in cpu.split(','):
        if int(number) > 40:
            load.problemflag = True

    





'''
Driver function
'''
Problems = []
authentication()
getoutput(Problems)



