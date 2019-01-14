# Copyright (c) 2019 China Telecom Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import jsonschema

config_data_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Octavia Distributor Noop Driver Metadata Schema",
    "description": "This schema is used to validate new metadata submitted "
                   "for use in an distributor noop driver.",
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "as": {
            "type": "number",
            "description": "The bgp as of l3 distributor",
        },
        "router_id": {
            "type": "string",
            "description": "The bgp router_id of l3 distributor",
        },
        "password": {
            "type": "string",
            "description": "The bgp peer password of l3 distributor",
        },
        "hosts": {
            "type": "array",
            "description": "List of compute nodes managed by the "
                           "distributor(Determined by ToR)"
        },
    },
    'required': ['as', 'router_id'],
}

jsonschema.Draft4Validator.check_schema(config_data_schema)
SCHEMAS = config_data_schema
