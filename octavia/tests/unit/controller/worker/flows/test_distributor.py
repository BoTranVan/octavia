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


from stevedore import driver as stevedore_driver
from taskflow.patterns import linear_flow as flow

from octavia.common import constants
from octavia.controller.worker.flows import distributor_flows
import octavia.tests.unit.base as base


class TestDistributorFlows(base.TestCase):

    def setUp(self):
        self.distributorFlows = distributor_flows.DistributorFlows()
        self.distributor_driver = stevedore_driver.DriverManager(
            namespace='octavia.distributor.drivers',
            name='l3', invoke_on_load=True).driver

        super(TestDistributorFlows, self).setUp()

    def test_get_create_distributor_flows(self):
        distributor_flow = self.distributorFlows.get_create_distributor_flows(
            self.distributor_driver)
        self.assertIsInstance(distributor_flow, flow.Flow)
        self.assertIn(constants.DISTRIBUTOR, distributor_flow.requires)

    def test_get_update_distributor_flows(self):
        distributor_flow = self.distributorFlows.get_update_distributor_flows(
            self.distributor_driver)
        self.assertIsInstance(distributor_flow, flow.Flow)
        self.assertIn(constants.DISTRIBUTOR, distributor_flow.requires)
        self.assertIn(constants.UPDATE_DICT, distributor_flow.requires)

    def test_get_delete_distributor_flows(self):
        distributor_flow = self.distributorFlows.get_delete_distributor_flows(
            self.distributor_driver)
        self.assertIsInstance(distributor_flow, flow.Flow)
        self.assertIn(constants.DISTRIBUTOR, distributor_flow.requires)
