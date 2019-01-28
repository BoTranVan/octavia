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
from oslo_utils import uuidutils

from octavia.amphorae.drivers.bgp import bgp_rest_driver
from octavia.common import constants
import octavia.tests.unit.base as base


class TestBGPRestDriver(base.TestCase):

    def setUp(self):
        self.bgp_mixin = bgp_rest_driver.BGPAmphoraDriverMixin()
        self.bgp_mixin.client = mock.MagicMock()
        self.client = self.bgp_mixin.client
        self.FAKE_CONFIG = 'FAKE CONFIG'
        self.lb_mock = mock.MagicMock()
        self.amphora_mock = mock.MagicMock()
        self.amphora_mock.id = uuidutils.generate_uuid()
        self.amphora_mock.status = constants.AMPHORA_ALLOCATED
        self.frontend_ip = "1.1.1.2"
        self.amphora_mock.frontend_ip = self.frontend_ip
        self.lb_mock.amphorae = [self.amphora_mock]
        self.distributor_mock = mock.MagicMock()

        super(TestBGPRestDriver, self).setUp()

    @mock.patch('octavia.amphorae.drivers.bgp.providers.os_ken.'
                'jinja_cfg.OsKenBGPJinjaTemplater.build_bgp_config')
    def test_update_bgp_conf(self, mock_templater):

        mock_templater.return_value = self.FAKE_CONFIG

        self.bgp_mixin.update_bgp_conf(self.lb_mock,
                                       self.distributor_mock)

        self.client.upload_bgp_config.assert_called_once_with(
            self.amphora_mock,
            self.FAKE_CONFIG)

    def test_stop_bgp_service(self):
        self.bgp_mixin.stop_bgp_service(self.lb_mock)
        self.client.stop_bgp_speaker.assert_called_once_with(
            self.amphora_mock)

    def test_start_bgp_service(self):
        self.bgp_mixin.start_bgp_service(self.lb_mock)
        self.client.start_bgp_speaker.assert_called_once_with(
            self.amphora_mock)

    def test_register_to_distributor(self):
        self.bgp_mixin.register_to_distributor(self.lb_mock)
        self.client.register_to_distributor.assert_called_once_with(
            self.amphora_mock)

    def test_get_frontend_interface(self):
        self.bgp_mixin.get_frontend_interface(self.amphora_mock)
        self.client.get_interface.assert_called_once_with(
            self.amphora_mock, self.frontend_ip, timeout_dict=None)
