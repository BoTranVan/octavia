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

import pecan

from oslo_config import cfg
from oslo_db import exception as odb_exceptions
from oslo_log import log as logging
from oslo_serialization import jsonutils
from oslo_utils import excutils
from oslo_utils import importutils
from wsme import types as wtypes
from wsmeext import pecan as wsme_pecan

from octavia.api.drivers import data_models as driver_dm
from octavia.api.drivers import driver_factory
from octavia.api.drivers import exceptions as driver_exceptions
from octavia.api.drivers import utils as driver_utils
from octavia.api.v2.controllers import base
from octavia.api.v2.types import distributor as distributor_types
from octavia.common import constants
from octavia.common import exceptions
from octavia.db import api as db_api
from octavia.db import prepare as db_prepare

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

support_distributor_type = {
    'noop': 'octavia.distributor.drivers.noop_driver.'
            'driver.NoopDistributorDriver',
    'l3': 'octavia.distributor.drivers.l3_driver.driver.'
          'L3DistributorDriver'}


class DistributorController(base.BaseController):
    RBAC_TYPE = constants.RBAC_DISTRIBUTOR

    def __init__(self):
        super(DistributorController, self).__init__()

    @wsme_pecan.wsexpose(distributor_types.DistributorRootResponse,
                         wtypes.text, [wtypes.text],
                         ignore_extra_args=True)
    def get_one(self, id, fields=None):
        """Gets a flavor profile's detail."""
        context = pecan.request.context.get('octavia_context')
        self._auth_validate_action(context, context.project_id,
                                   constants.RBAC_GET_ONE)
        db_distributor = self._get_db_distributor(context.session, id)
        result = self._convert_db_to_type(
            db_distributor,
            distributor_types.DistributorResponse)
        if fields is not None:
            result = self._filter_fields([result], fields)[0]
        return distributor_types.DistributorRootResponse(distributor=result)

    @wsme_pecan.wsexpose(distributor_types.DistributorsRootResponse,
                         [wtypes.text], ignore_extra_args=True)
    def get_all(self, fields=None):
        """Lists all distributors."""
        pcontext = pecan.request.context
        context = pcontext.get('octavia_context')
        self._auth_validate_action(context, context.project_id,
                                   constants.RBAC_GET_ALL)
        db_distributors, links = self.repositories.distributor.get_all(
            context.session,
            pagination_helper=pcontext.get(constants.PAGINATION_HELPER))
        result = self._convert_db_to_type(
            db_distributors, [distributor_types.DistributorResponse])
        if fields is not None:
            result = self._filter_fields(result, fields)
        return distributor_types.DistributorsRootResponse(
            distributors=result, distributors_links=links)

    def _validate_create_distributor(self, lock_session, distributor_dict):
        try:
            return self.repositories.distributor.create(lock_session,
                                                        **distributor_dict)
        except odb_exceptions.DBDuplicateEntry:
            raise exceptions.IDAlreadyExists()
        except odb_exceptions.DBError:
            # TODO(blogan): will have to do separate validation protocol
            # before creation or update since the exception messages
            # do not give any information as to what constraint failed
            raise exceptions.InvalidOption(value='', option='')

    def _test_distributor_status(self, session, id,
                                 distributor_status=constants.PENDING_UPDATE):
        """Verify distributor is in a mutable state."""
        distributor_repo = self.repositories.distributor
        if not distributor_repo.test_and_set_provisioning_status(
                session, id, distributor_status):
            prov_status = distributor_repo.get(session,
                                               id=id).provisioning_status
            LOG.info("Invalid state %(state)s of distributor resource %(id)s",
                     {"state": prov_status, "id": id})
            raise exceptions.DistributorPendingStateError(
                state=prov_status, id=id)

    @wsme_pecan.wsexpose(distributor_types.DistributorRootResponse,
                         body=distributor_types.DistributorRootPOST,
                         status_code=201)
    def post(self, distributor_):
        """Creates a flavor Profile."""
        distributor = distributor_.distributor
        context = pecan.request.context.get('octavia_context')
        self._auth_validate_action(context, context.project_id,
                                   constants.RBAC_POST)
        # Do a basic JSON validation on the config_data
        try:
            config_data_dict = jsonutils.loads(distributor.config_data)
        except Exception:
            raise exceptions.InvalidOption(
                value=distributor.config_data,
                option=constants.CONFIG_DATA)

        # Validate that the distributor driver supports the config_data
        if distributor.distributor_driver not in support_distributor_type:
            raise exceptions.InvalidOption(
                value=distributor.distributor_driver,
                option='distributor_driver')
        distributor_driver_cls = importutils.import_class(
            support_distributor_type.get(distributor.distributor_driver))
        try:
            distributor_driver_cls.validate_config_data(config_data_dict)
        except driver_exceptions.UnsupportedOptionError as e:
            LOG.info("The '%s' type distributor raised an unsupported option "
                     "error: %s", distributor.distributor_driver,
                     e.operator_fault_string)
            raise exceptions.DistributorUnsupportOptionError(
                type=distributor.distributor_driver,
                user_msg=e.user_fault_string)

        driver = driver_factory.get_driver(CONF.distributor.api_driver)

        lock_session = db_api.get_session(autocommit=False)
        try:
            distributor_dict = db_prepare.create_distributor(
                distributor.to_dict(render_unsets=False))
            db_distributor = self.repositories.distributor.create(
                lock_session,
                **distributor_dict)

            # Dispatch to the driver
            LOG.info("Sending create Distributor %s to provider %s",
                     db_distributor.id, driver.name)

            provider_distributor = (
                driver_utils.db_distributor_to_provider_distributor(
                    db_distributor))

            driver_utils.call_provider(
                driver.name, driver.distributor_create, provider_distributor)

            lock_session.commit()
        except odb_exceptions.DBDuplicateEntry:
            lock_session.rollback()
            raise exceptions.RecordAlreadyExists(field='distributor',
                                                 name=distributor.name)
        except Exception:
            with excutils.save_and_reraise_exception():
                lock_session.rollback()
        db_distributor = self._get_db_distributor(
            context.session, db_distributor.id)
        result = self._convert_db_to_type(
            db_distributor, distributor_types.DistributorResponse)
        return distributor_types.DistributorRootResponse(distributor=result)

    @wsme_pecan.wsexpose(distributor_types.DistributorRootResponse,
                         wtypes.text, status_code=200,
                         body=distributor_types.DistributorRootPUT)
    def put(self, id, distributor_):
        """Updates a distributor."""
        distributor = distributor_.distributor
        context = pecan.request.context.get('octavia_context')
        db_distributor = self._get_db_distributor(context.session, id,
                                                  show_deleted=False)
        self._auth_validate_action(context, context.project_id,
                                   constants.RBAC_PUT)
        if not distributor:
            raise exceptions.ValidationException(
                detail='No distributor object supplied.')

        # Do a basic JSON validation on the config_data
        config_data = getattr(distributor, 'config_data', None)
        if config_data and db_distributor.load_balancers:
            raise exceptions.UnsupportUpdateConfigData()
        if config_data:
            try:
                config_data_dict = jsonutils.loads(distributor.config_data)
            except Exception:
                raise exceptions.InvalidOption(
                    value=distributor.config_data,
                    option=constants.FLAVOR_DATA)

            # Validate that the distributor driver supports the config_data
            distributor_driver_cls = importutils.import_class(
                support_distributor_type.get(
                    db_distributor.distributor_driver))
            try:
                distributor_driver_cls.validate_config_data(config_data_dict)
            except driver_exceptions.UnsupportedOptionError as e:
                LOG.info("The '%s' type distributor raised an unsupported "
                         "option error: %s", db_distributor.distributor_driver,
                         e.operator_fault_string)
                raise exceptions.DistributorUnsupportOptionError(
                    type=db_distributor.distributor_driver,
                    user_msg=e.user_fault_string)

        driver = driver_factory.get_driver(CONF.distributor.api_driver)

        with db_api.get_lock_session() as lock_session:
            distributor_dict = distributor.to_dict(render_unsets=False)
            self._test_distributor_status(lock_session, id)
            distributor_dict['id'] = id

            provider_distributor_dict = (
                driver_utils.distributor_dict_to_provider_dict(
                    distributor_dict))

            # Also prepare the baseline object data
            old_provider_distributor = (
                driver_utils.db_distributor_to_provider_distributor(
                    db_distributor))

            # Dispatch to the driver
            LOG.info("Sending update Distributor %s to provider %s", id,
                     driver.name)
            driver_utils.call_provider(
                driver.name, driver.distributor_update,
                old_provider_distributor,
                driver_dm.Distributor.from_dict(provider_distributor_dict))

            db_distributor = self.repositories.distributor.update(
                lock_session, **distributor_dict)

        # Force SQL alchemy to query the DB, otherwise we get inconsistent
        # results
        context.session.expire_all()
        db_distributor = self._get_db_distributor(context.session, id)
        result = self._convert_db_to_type(
            db_distributor, distributor_types.DistributorResponse)
        return distributor_types.DistributorRootResponse(distributor=result)

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, id):
        """Deletes a Distributor"""
        context = pecan.request.context.get('octavia_context')
        db_distributor = self._get_db_distributor(context.session, id,
                                                  show_deleted=False)

        if db_distributor.load_balancers:
            raise exceptions.ObjectInUse(object='Distributor',
                                         id=db_distributor.id)

        self._auth_validate_action(context, context.project_id,
                                   constants.RBAC_DELETE)

        driver = driver_factory.get_driver(CONF.distributor.api_driver)
        with db_api.get_lock_session() as lock_session:
            self._test_distributor_status(
                lock_session, id,
                distributor_status=constants.PENDING_DELETE)

            LOG.info("Sending delete Distributor %s to provider %s", id,
                     driver.name)
            provider_listener = (
                driver_utils.db_distributor_to_provider_distributor(
                    db_distributor))
            driver_utils.call_provider(driver.name, driver.distributor_delete,
                                       provider_listener)

            self.repositories.distributor.update(
                context.session, db_distributor.id,
                provisioning_status=constants.PENDING_DELETE)
