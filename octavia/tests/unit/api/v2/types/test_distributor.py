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

from oslo_utils import uuidutils
from wsme import exc
from wsme.rest import json as wsme_json
from wsme import types as wsme_types

from octavia.api.v2.types import distributor as distributor_type
from octavia.tests.unit.api.common import base


class TestDistributor(object):

    _type = None

    def test_distributor(self):
        body = {"name": "test_name", "description": "test_description",
                "frontend_subnet": uuidutils.generate_uuid(),
                "distributor_driver": "fake-driver",
                "config_data": "{}"}
        distributor = wsme_json.fromjson(self._type, body)
        self.assertTrue(distributor.admin_state_up)

    def test_invalid_name(self):
        body = {"name": 0}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson, self._type,
                          body)

    def test_name_length(self):
        body = {"name": "x" * 256}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson, self._type,
                          body)

    def test_invalid_description(self):
        body = {"description": 0}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson, self._type,
                          body)

    def test_description_length(self):
        body = {"name": "x" * 256}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson, self._type,
                          body)

    def test_invalid_config_data(self):
        body = {"config_data": 0}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson, self._type,
                          body)

    def test_config_data_length(self):
        body = {"config_data": "x" * 4097}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson, self._type,
                          body)

    def test_invalid_enabled(self):
        body = {"name": "test_name", "description": "test_description",
                "admin_state_up": "notvalid",
                "config_data": "{}"}
        self.assertRaises(ValueError, wsme_json.fromjson, self._type,
                          body)


class TestDistributorPOST(base.BaseTypesTest, TestDistributor):

    _type = distributor_type.DistributorPOST

    def test_non_uuid_project_id(self):
        body = {"name": "test_name", "description": "test_description",
                "frontend_subnet": uuidutils.generate_uuid(),
                "distributor_driver": "fake-driver",
                "config_data": "{}"}
        distributor = wsme_json.fromjson(self._type, body)
        self.assertEqual(distributor.frontend_subnet, body['frontend_subnet'])

    def test_invalid_frontend_subnet(self):
        body = {"frontend_subnet": "invalid_uuid"}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson, self._type,
                          body)

    def test_invalid_distributor_driver(self):
        body = {"distributor_driver": 0}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson, self._type,
                          body)

    def test_distributor_driver_length(self):
        body = {"distributor_driver": "X" * 65}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson, self._type,
                          body)


class TestDistributorPUT(base.BaseTypesTest, TestDistributor):

    _type = distributor_type.DistributorPUT

    def test_distributor(self):
        body = {"name": "test_name", "description": "test_description"}
        distributor = wsme_json.fromjson(self._type, body)
        self.assertEqual(wsme_types.Unset, distributor.admin_state_up)
