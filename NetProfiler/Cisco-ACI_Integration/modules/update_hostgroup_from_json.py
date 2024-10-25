#!python
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2021 Riverbed Technology Inc.
# The MIT License (MIT) (see https://opensource.org/licenses/MIT)

DOCUMENTATION = """
---
module: update_hostgroup_from_json
short_description: Update a hostgroup via a json file on Netprofiler via REST API
options:
    host:
        description:
            - Hostname or IP Address of the Netprofiler.
        required: True
    access_code:
        description:
            - REST API access code created on the Netprofiler.
        required: True
    json_file:
        description:
            - Hostgroup JSON file.
        required: True
"""
EXAMPLES = """
#Usage Example
    - name: Update Hostgroup on Netprofiler via REST API
      create_hostgroup_from_json:
        host: 192.168.1.1
        access_code: eyJhdWQiOiAiaHR0cHM6Ly9jbGllbnQt==
        json_file: epg.json
      register: results

    - name: Display Hostgroup Update result via REST API 
      debug: var=results
"""
RETURN = r'''
output:
    description: API response in json dict format
    returned: success
    type: dict
'''
import json
from ansible.module_utils.basic import AnsibleModule
from steelscript.common.app import Application
from steelscript.common.service import OAuth
from steelscript.common import Service
from steelscript.common.exceptions import RvbdHTTPException


class NetprofilerCLIApp(Application):

    def __init__(self, host, code, json_file):
        super(Application).__init__()
        self._api_url = "/api/profiler/1.14/host_group_types"
        self._host = host
        self._json_file = json_file
        self._access_code = code

    def get_hostgroup_name(self):
        with open(self._json_file) as f:
            data = json.load(f)
        return data['name']

    def get_hostgroup_id(self,netprofiler,hostgroup_name):
        content_dict = netprofiler.conn.json_request("GET",self._api_url)
        for elem in content_dict:
            for key, value in elem.items():
                if value == hostgroup_name:
                    search_id = elem['id']
        return search_id


    def main(self,module):

        try:
            netprofiler = Service("netprofiler",self.host, auth=OAuth(self.access_code),
                                  enable_auth_detection = False,
                                  supports_auth_basic=True,
                                  supports_auth_oauth=True,
                                  override_services_api='/api/common/1.0/services')

            hostgroup_id = self.get_hostgroup_id(netprofiler,self.get_hostgroup_name())

            contents = open(self._json_file, 'rb').read()

            content_dict = netprofiler.conn.upload(self._api_url+'/'+str(hostgroup_id), contents, method="PUT", extra_headers={'Content-Type': 'application/json'})

            del netprofiler
            if content_dict is None:
                result="Hostgroup "+self.get_hostgroup_name()+" successfully updated"

            module.exit_json(changed=False,output=result)

        except RvbdHTTPException as e:
            results="Error retrieving information on '{}'".format(self.api_url)
            module.fail_json(changed=False,msg=results,reason=str(e))

def main():
    fields = {
        "host": {"required": True, "type": "str"},
        "access_code": {"required": True, "type": "str", "no_log": True},
        "json_file": {"required": True, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    my_app = NetprofilerCLIApp(module.params["host"],module.params["access_code"],module.params["json_file"],)

    my_app.main(module)



if __name__ == '__main__':
    main()
