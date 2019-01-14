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

from jsonschema import exceptions as js_exceptions
from jsonschema import validate

from oslo_log import log as logging
from taskflow.patterns import linear_flow

from octavia.api.drivers import exceptions
from octavia.common import constants
from octavia.distributor.drivers import driver_base
from octavia.distributor.drivers.l3_driver import config_data_schema
from octavia.distributor.drivers.l3_driver import tasks

LOG = logging.getLogger(__name__)


class L3Manager(object):
    def __init__(self):
        super(L3Manager, self).__init__()

    def get_create_distributor_subflow(self):
        LOG.debug('Distributor %s create_distributor', self.__class__.__name__)
        create_distributor_flow = linear_flow.Flow('create-distributor')
        create_distributor_flow.add(tasks.CreateDistributorTask(
            requires=(constants.DISTRIBUTOR)))
        return create_distributor_flow

    def get_update_distributor_subflow(self):
        LOG.debug('Distributor %s update_distributor', self.__class__.__name__)
        update_distributor_flow = linear_flow.Flow('update-distributor')
        update_distributor_flow.add(tasks.UpdateDistributorTask(
            requires=(constants.DISTRIBUTOR)))
        return update_distributor_flow

    def get_delete_distributor_subflow(self):
        LOG.debug('Distributor %s delete_distributor', self.__class__.__name__)
        delete_distributor_flow = linear_flow.Flow('delete-distributor')
        delete_distributor_flow.add(tasks.DeleteDistributorTask(
            requires=(constants.DISTRIBUTOR)))
        return delete_distributor_flow

    def get_register_amphorae_subflow(self):
        LOG.debug('Distributor %s register_amphorae', self.__class__.__name__)
        register_amphorae_flow = linear_flow.Flow('register_amphorae')
        register_amphorae_flow.add(tasks.RegisterAmphoraTask(
            requires=(constants.DISTRIBUTOR, constants.AMPHORA)))
        return register_amphorae_flow

    def get_drain_amphorae_subflow(self):
        LOG.debug('Distributor %s drain_amphorae', self.__class__.__name__)
        drain_amphorae_flow = linear_flow.Flow('drain-amphorae')
        drain_amphorae_flow.add(tasks.DrainAmphoraTask(
            requires=(constants.DISTRIBUTOR)))
        return drain_amphorae_flow

    def get_unregister_amphorae_subflow(self):
        LOG.debug('Distributor %s unregister_amphorae',
                  self.__class__.__name__)
        unregister_amphorae_flow = linear_flow.Flow('unregister_amphora')
        unregister_amphorae_flow.add(tasks.UnregisterAmphoraTask(
            requires=('distributor_id', 'amphorae')))
        return unregister_amphorae_flow


class L3DistributorDriver(driver_base.DistributorDriver):
    def __init__(self):
        super(L3DistributorDriver, self).__init__()
        self.driver = L3Manager()

    @classmethod
    def get_supported_config_data(cls):
        """Returns the valid l3 distributor config data keys and descriptions.

        This extracts the valid config data keys and descriptions
        from the JSON validation schema and returns it as a dictionary.

        :return: Dictionary of config data keys and descriptions.
        :raises DriverError: An unexpected error occurred.
        """
        try:
            props = config_data_schema.SCHEMAS['properties']
            return {k: v.get('description', '') for k, v in props.items()}
        except Exception as e:
            raise exceptions.DriverError(
                user_fault_string='Failed to get the supported distributor '
                                  'config data due to: {}'.format(str(e)),
                operator_fault_string='Failed to get the supported '
                                      'distributor config data due '
                                      'to: {}'.format(str(e)))

    @classmethod
    def validate_config_data(cls, config_data_dict):

        """Validates distributor config data.

        This will validate a distributor config dataset against the config
        settings the distributor l3 driver supports.

        :param config_data_dict: The config data dictionary to validate.
        :type config_data: dict
        :return: None
        :raises DriverError: An unexpected error occurred.
        :raises UnsupportedOptionError: If the driver does not support
          one of the config_data settings.
        """
        try:
            validate(config_data_dict, config_data_schema.SCHEMAS)
        except js_exceptions.ValidationError as e:
            error_object = ''
            if e.relative_path:
                error_object = '{} '.format(e.relative_path[0])
            raise exceptions.UnsupportedOptionError(
                user_fault_string='{0}{1}'.format(error_object, e.message),
                operator_fault_string=str(e))
        except Exception as e:
            raise exceptions.DriverError(
                user_fault_string='Failed to validate the distributor '
                                  'config data due to: {}'.format(str(e)),
                operator_fault_string='Failed to validate the distributor '
                                      'config data due to: {}'.format(str(e)))

    def get_create_distributor_subflow(self):
        return self.driver.get_create_distributor_subflow()

    def get_update_distributor_subflow(self):
        return self.driver.get_update_distributor_subflow()

    def get_delete_distributor_subflow(self):
        return self.driver.get_delete_distributor_subflow()

    def get_add_vip_subflow(self):
        return self.driver.get_add_vip_subflow()

    def get_remove_vip_subflow(self):
        return self.driver.get_remove_vip_subflow()

    def get_register_amphorae_subflow(self):
        register_amphora_flow = linear_flow.Flow(
            constants.REGISTER_AMP_SUBFLOW)
        register_amphora_flow.add(
            tasks.UploadBgpConfig(
                requires=(constants.LOADBALANCER,
                          constants.DISTRIBUTOR)))
        register_amphora_flow.add(
            tasks.StartBbgSpeaker(
                requires=(constants.LOADBALANCER)))
        register_amphora_flow.add(
            tasks.RegisterAmphoraTask(
                requires=(constants.LOADBALANCER)))
        return register_amphora_flow

    def get_drain_amphorae_subflow(self):
        self.driver.get_drain_amphorae_subflow()

    def get_unregister_amphorae_subflow(self):
        self.driver.get_unregister_amphorae_subflow()
