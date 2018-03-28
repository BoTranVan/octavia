#    Copyright 2018 GoDaddy
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
import pecan
from wsme import types as wtypes
from wsmeext import pecan as wsme_pecan

from octavia.api.v2.controllers import base
from octavia.api.v2.types import usage as usage_types
from octavia.common import constants


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class UsageController(base.BaseController):
    RBAC_TYPE = constants.RBAC_USAGE

    def __init__(self):
        super(UsageController, self).__init__()

    def _get_usage(self, project_id=None):
        context = pecan.request.context.get('octavia_context')

        rbac = constants.RBAC_GET_ALL_GLOBAL
        if project_id:
            rbac = constants.RBAC_GET_ONE
        self._auth_validate_action(context, context.project_id, rbac)

        db_usage = self._get_db_usage(context.session, project_id)
        usage_model = usage_types.UsageResponse(db_usage)
        return usage_types.UsageRootResponse(usage=usage_model)

    @wsme_pecan.wsexpose(usage_types.UsageRootResponse, wtypes.text)
    def get_one(self, project_id):
        """Gets a single project's usage details."""
        return self._get_usage(project_id)

    @wsme_pecan.wsexpose(usage_types.UsageRootResponse)
    def get_all(self):
        """Gets usage details for the entire system."""
        return self._get_usage()
