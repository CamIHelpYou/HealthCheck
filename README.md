# HealthCheck
Health Check for DNA Center



Meant to be run through the curl command:

With Proxy:
curl -k -x http://proxy.esl.cisco.com:8080 https://raw.githubusercontent.com/CamIHelpYou/HealthCheck/master/HealthCheck.py | python

Without Proxy:
curl -k https://raw.githubusercontent.com/CamIHelpYou/HealthCheck/master/HealthCheck.py | python
