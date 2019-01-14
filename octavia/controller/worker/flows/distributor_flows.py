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

from oslo_config import cfg
from oslo_log import log as logging
from taskflow.patterns import linear_flow

from octavia.common import constants
from octavia.controller.worker.tasks import database_tasks
from octavia.controller.worker.tasks import lifecycle_tasks

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class DistributorFlows(object):

    def get_create_distributor_flows(self, distributor_driver):
        """Create a flow to create a distributor

        :returns: The flow for create a distributor
        """
        create_distributor_flow = linear_flow.Flow(
            constants.CREATE_DISTRIBUTOR_FLOW)
        create_distributor_flow.add(
            lifecycle_tasks.DistributorToErrorOnRevertTask(
                requires=constants.DISTRIBUTOR))
        create_distributor_flow.add(
            database_tasks.MarkDistributorPendingCreateInDB(
                requires=constants.DISTRIBUTOR))
        create_distributor_flow.add(
            *distributor_driver.get_create_distributor_subflow())
        create_distributor_flow.add(database_tasks.MarkDistributorActiveInDB(
            requires=constants.DISTRIBUTOR))

        return create_distributor_flow

    def get_update_distributor_flows(self, distributor_driver):
        """Creates a flow to update a distributor.

        :returns: The flow for update a distributor
        """
        update_distributor_flow = linear_flow.Flow(
            constants.UPDATE_DISTRIBUTOR_FLOW)
        update_distributor_flow.add(
            lifecycle_tasks.DistributorToErrorOnRevertTask(
                requires=constants.DISTRIBUTOR))
        update_distributor_flow.add(
            database_tasks.MarkDistributorPendingUpdateInDB(
                requires=constants.DISTRIBUTOR))
        update_distributor_flow.add(
            *distributor_driver.get_update_distributor_subflow())
        update_distributor_flow.add(database_tasks.UpdateDistributorInDB(
            requires=[constants.DISTRIBUTOR, constants.UPDATE_DICT]))
        update_distributor_flow.add(database_tasks.MarkDistributorActiveInDB(
            requires=constants.DISTRIBUTOR))

        return update_distributor_flow

    def get_delete_distributor_flows(self, distributor_driver):
        """Creates a flow to delete a distributor

        :returns: The flow for delete a distributor
        """
        delete_distributor_flow = linear_flow.Flow(
            constants.DELETE_DISTRIBUTOR_FLOW)
        delete_distributor_flow.add(
            lifecycle_tasks.DistributorToErrorOnRevertTask(
                requires=constants.DISTRIBUTOR))
        delete_distributor_flow.add(
            database_tasks.MarkDistributorPendingDeleteInDB(
                requires=constants.DISTRIBUTOR))
        delete_distributor_flow.add(
            *distributor_driver.get_delete_distributor_subflow())
        delete_distributor_flow.add(database_tasks.DeleteDistributorInDB(
            requires=constants.DISTRIBUTOR))

        return delete_distributor_flow
