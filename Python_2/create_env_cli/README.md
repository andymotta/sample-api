# Skytap CLI

## Authentication 
For Skytap API Authentication you need to create `api_automation/.skt/credentials` with your username (e-mail address) and Skytap API security token (under 'My Account')

eg: `cat .skt/credentials`

```ini
[auth]  
user = email@domain.com
token = <skytap_api_token>
```
The auth section is required and this file is added to .gitignore

## pip modules
This script accesses a REST API so `pip install -r requirements.txt` to install the required requests module

## Template Management
Store any golden templates in `.skt/config`.  When testing, the -t flag can be used to specify a template outside of that config temporarily 

## Usage

`./create_start_env.py -h` will always show the latest usage

Exmaple:
```bash
usage: create_start_env.py [-h] -n STNAME [-t TEMPLATE] [-p PROJECT]
                           [-l LABEL] [-s BOOTSTRAP] [-d]

Create a new environment from a Skytap template

optional arguments:
  -h, --help            show this help message and exit
  -n STNAME, --name STNAME
                        Required: Name the Skytap environment you are creating
                        from template
  -t TEMPLATE, --template TEMPLATE
                        Optional: ID of the Skytap template to use as a base
                        (Default in .skt/config)
  -p PROJECT, --project PROJECT
                        Optional: Skytap project to automatically add this
                        environment to
  -l LABEL, --label LABEL
                        Optional: Tag or label on the environment for cost
                        center control
  -s BOOTSTRAP, --script BOOTSTRAP
                        Optional: Script or file to put in Skytap User Data
                        for later retrival via the API
  -d                    Optional (Boolean): Do not start the environment after
                        creation
```

### **Optional**: Retriving the file we put in user data after environment creation
If we want any machines in our new environment to access 
the script or file we uploaded with the cli, we could do something like this:
```python
import requests
import json
import os

result = requests.get("http://gw/skytap")
json_output = json.loads(result.text)
script = json_output["configuration_user_data"]
os.system(script)
```