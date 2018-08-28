#!/usr/bin/env python

'''
 Copyright 2014 Skytap Inc.

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.

 #------------------------------------------------------------------------
 A simple python cli to create Skytap environments from template with a few useful parameters 

 NOTE:  This code was tested with python 2.7.10

Usage: ./create_start_env.py -h
'''

import sys
import argparse
import json
try:
    import requests
except ImportError:
    sys.exit("""Before using this script, please run:
                pip install -r requirements.txt
You only need to do this once.""")
from ConfigParser import RawConfigParser as ConfigParser, NoSectionError, NoOptionError


parser = argparse.ArgumentParser(description='Create a new environment from a Skytap template')
parser.add_argument(
    '-n',
    '--name',
    dest='stname',
    required=True,
    help='Required: Name the Skytap environment you are creating from template'
    )
parser.add_argument(
    '-t',
    '--template',
    dest='template',
    help='Optional: ID of the Skytap template to use as a base (Default in .skt/config)'
    )
parser.add_argument(
    '-p',
    '--project',
    dest='project',
    help='Optional: Skytap project to automatically add this environment to'
    )
parser.add_argument(
    '-l',
    '--label',
    dest='label',
    help='Optional: Tag or label on the environment for cost center control'
    )
parser.add_argument(
    '-s',
    '--script',
    dest='bootstrap',
    help='Optional: Script or file to put in Skytap User Data for later retrival via the API'
    )
parser.add_argument(
    '-d',
    dest='start',
    action='store_false',
    help='Optional (Boolean): Do not start the environment after creation'
    )

args = parser.parse_args()
stname = args.stname
template = args.template
project = args.project
label = args.label
bootstrap = args.bootstrap
start = args.start

def configparser(cfile):
    config = ConfigParser()
    try:
        with open(cfile) as f: # catch IOError, file not exist
            config.read(cfile)
    except IOError as e:
        if "credentials" in str(e):
            print "Please first create credentials file in .skt per README"
            sys.exit(1)
        sys.exit(e)
    return config

def getconfig(config,section,key):
    try:
        value = config.get(section,key)
    except NoSectionError as e:
        print("%s: Please review README to create a %s section in .skt" % (e, section))
        sys.exit(1)
    except NoOptionError as e:
        print("%s: Please review README to create a %s key in .skt" % (e, key))
        sys.exit(1)
    return value

# Get api credentials from local config file
creds = configparser('.skt/credentials')
user = getconfig(creds,'auth','user')
token = getconfig(creds,'auth','token')
auth = (user, token)      # login and API token/password

# Import template configuration
if template is None:
    conf = configparser('.skt/config')
    template = getconfig(conf,'env','template')

# Requisite JSON headers for API
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
}

# Base URL for environemnt operations
url = 'https://cloud.skytap.com/configurations/'

# POST to create environment from template
if project is None:
    params = {'template_id': template, 'name': stname}
else:
    params = {'template_id': template, 'project_id': project, 'name': stname}
try:
    result = requests.post(url, headers=headers, auth=auth, params=params)
    result.raise_for_status()
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 404:        
        print("Please make sure user %s has access to requested project or template" % (user))
    if e.response.status_code == 401:
        print "Please make sure your API token is valid and you are connected to VPN" 
    sys.exit(e)
except requests.exceptions.ConnectionError as e:
    print "You may not be connected to the network"
    sys.exit(e)
json_output = json.loads(result.text)
envid=json_output["id"]

# Add a local script or file to environment user data
if bootstrap is not None:
    try:
        with open(bootstrap) as script:
            contents = script.read()
        params = {'contents': contents}
        try:
            result = requests.put(url + envid + "/user_data.json", headers=headers, auth=auth, params=params)
        except requests.exceptions.RequestException as e:
            sys.exit(e)
    except IOError as e:
        print("Cannot open %s, skipping user data..." % (bootstrap))

if label is not None:
    params = [{'value': label}]
    try:
        result = requests.put("https://cloud.skytap.com/v2/configurations/" + envid + "/tags.json", headers=headers, auth=auth, json=params)
    except requests.exceptions.RequestException as e:
        sys.exit(e)

# Start the new environment by ID
if start is True:
    params = {'runstate': 'running'}
    try:
        result = requests.put(url + envid, headers=headers, auth=auth, params=params)
    except requests.exceptions.RequestException as e:
        sys.exit(e)

print("Environment Status: "+url+envid)