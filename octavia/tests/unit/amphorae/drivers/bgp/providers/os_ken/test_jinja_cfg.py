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

import mock

from octavia.amphorae.drivers.bgp.providers.os_ken import jinja_cfg
import octavia.tests.unit.base as base


class TestBGPRestDriver(base.TestCase):

    def setUp(self):
        super(TestBGPRestDriver, self).setUp()
        self.distributor_mock = mock.MagicMock()
        self.amphora_mock = mock.MagicMock()
        self.lb_network_ip = "2.2.2.2"
        self.amphora_mock.lb_network_ip = self.lb_network_ip
        self.templater = jinja_cfg.OsKenBGPJinjaTemplater()

    def test_build_bgp_config_no_password(self):
        self.distributor_mock.config_data = ('{"as": 123, '
                                             '"router_id": "3.3.3.3"}')
        expect_conf = ("[bgp_speaker]\nspeaker_as = 123\n"
                       "router_id = 2.2.2.2\n[bgp_peer]\n"
                       "peer_as = 123\npeer_ip = 3.3.3.3\n")
        config = self.templater.build_bgp_config(
            self.distributor_mock,
            self.amphora_mock)
        self.assertEqual(expect_conf, config)

    def test_build_bgp_config_with_password(self):
        self.distributor_mock.config_data = ('{"as": 123, '
                                             '"router_id": "3.3.3.3", '
                                             '"password": "123456"}')
        expect_conf = ("[bgp_speaker]\nspeaker_as = 123\n"
                       "router_id = 2.2.2.2\n[bgp_peer]\n"
                       "peer_as = 123\npeer_ip = 3.3.3.3\n"
                       "password = 123456\n")
        config = self.templater.build_bgp_config(
            self.distributor_mock,
            self.amphora_mock)
        self.assertEqual(expect_conf, config)
