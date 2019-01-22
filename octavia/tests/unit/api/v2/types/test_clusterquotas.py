# Copyright (c) 2018 China Telecom Corporation
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

from wsme import exc
from wsme.rest import json as wsme_json
from wsme import types as wsme_types

from octavia.api.v2.types import clusterquotas as clusterquota_type
from octavia.common import constants
from octavia.tests.unit.api.v2.types import base


class TestClusterQuotaPut(base.BaseTypesTest):

    _type = clusterquota_type.ClusterQuotaPUT

    def test_clusterquota(self):
        body = {'clusterquota': {'cluster_total_loadbalancers': 5}}
        clusterquota = wsme_json.fromjson(self._type, body)
        self.assertEqual(wsme_types.Unset,
                         clusterquota.clusterquota.max_healthmonitors_per_pool)
        self.assertEqual(
            wsme_types.Unset,
            clusterquota.clusterquota.max_listeners_per_loadbalancer)
        self.assertEqual(wsme_types.Unset,
                         clusterquota.clusterquota.max_members_per_pool)
        self.assertEqual(wsme_types.Unset,
                         clusterquota.clusterquota.max_pools_per_loadbalancer)
        self.assertEqual(wsme_types.Unset,
                         clusterquota.clusterquota.max_l7policies_per_listener)
        self.assertEqual(wsme_types.Unset,
                         clusterquota.clusterquota.max_l7rules_per_l7policy)

    def test_invalid_clusterquota(self):
        body = {'clusterquota':
                {'cluster_total_loadbalancers':
                    constants.MAX_CLUSTERQUOTA + 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)
        body = {'clusterquota':
                {'cluster_total_loadbalancers':
                    constants.MIN_CLUSTERQUOTA - 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)

        body = {'clusterquota':
                {'max_healthmonitors_per_pool':
                    constants.MAX_CLUSTERQUOTA + 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)
        body = {'clusterquota':
                {'max_healthmonitors_per_pool':
                    constants.MIN_CLUSTERQUOTA - 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)

        body = {'clusterquota':
                {'max_listeners_per_loadbalancer':
                    constants.MAX_CLUSTERQUOTA + 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)
        body = {'clusterquota':
                {'max_listeners_per_loadbalancer':
                    constants.MIN_CLUSTERQUOTA - 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)

        body = {'clusterquota':
                {'max_members_per_pool':
                    constants.MAX_CLUSTERQUOTA + 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)
        body = {'clusterquota':
                {'max_members_per_pool':
                    constants.MIN_CLUSTERQUOTA - 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)

        body = {'clusterquota':
                {'max_pools_per_loadbalancer':
                    constants.MAX_CLUSTERQUOTA + 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)
        body = {'clusterquota':
                {'max_pools_per_loadbalancer':
                    constants.MIN_CLUSTERQUOTA - 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)

        body = {'clusterquota':
                {'max_l7policies_per_listener':
                    constants.MAX_CLUSTERQUOTA + 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)
        body = {'clusterquota':
                {'max_l7policies_per_listener':
                    constants.MIN_CLUSTERQUOTA - 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)

        body = {'clusterquota':
                {'max_l7rules_per_l7policy':
                    constants.MAX_CLUSTERQUOTA + 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)
        body = {'clusterquota':
                {'max_l7rules_per_l7policy':
                    constants.MIN_CLUSTERQUOTA - 1}}
        self.assertRaises(exc.InvalidInput, wsme_json.fromjson,
                          self._type, body)
