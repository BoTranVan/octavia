#    Copyright 2016 Rackspace
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
import pecan
from wsme import types as wtypes
from wsmeext import pecan as wsme_pecan

from octavia.api.v2.controllers import base
from octavia.api.v2.types import clusterquotas as clusterquota_types
from octavia.common import constants

CONF = cfg.CONF


class ClusterQuotasController(base.BaseController):
    RBAC_TYPE = constants.RBAC_CLUSTERQUOTA

    def __init__(self):
        super(ClusterQuotasController, self).__init__()

    @wsme_pecan.wsexpose(clusterquota_types.ClusterQuotaResponse, wtypes.text)
    def get(self):
        """Get cluster quota details."""
        context = pecan.request.context.get('octavia_context')

        self._auth_validate_action(context, context.project_id,
                                   constants.RBAC_GET_ONE)

        db_clusterquotas = self._get_db_clusterquotas(context.session)
        return self._convert_db_to_type(db_clusterquotas,
                                        clusterquota_types.ClusterQuotaResponse
                                        )

    @wsme_pecan.wsexpose(clusterquota_types.ClusterQuotaResponse, wtypes.text,
                         body=clusterquota_types.ClusterQuotaPUT,
                         status_code=202)
    def put(self, clusterquotas):
        """Update cluster quotas."""
        context = pecan.request.context.get('octavia_context')

        self._auth_validate_action(context, context.project_id,
                                   constants.RBAC_PUT)

        clusterquotas_dict = clusterquotas.to_dict()
        self.repositories.clusterquotas.update(context.session,
                                               **clusterquotas_dict)
        db_clusterquotas = self._get_db_clusterquotas(context.session)
        return self._convert_db_to_type(db_clusterquotas,
                                        clusterquota_types.ClusterQuotaResponse
                                        )

    @wsme_pecan.wsexpose(None, wtypes.text, status_code=202)
    def delete(self):
        """Reset cluster quotas to the default values."""
        context = pecan.request.context.get('octavia_context')

        self._auth_validate_action(context, context.project_id,
                                   constants.RBAC_DELETE)

        self.repositories.clusterquotas.delete(context.session)
        db_clusterquotas = self._get_db_clusterquotas(context.session)
        return self._convert_db_to_type(db_clusterquotas,
                                        clusterquota_types.ClusterQuotaResponse
                                        )

    @pecan.expose()
    def _lookup(self, id, *remainder):
        """Overridden pecan _lookup method for routing default endpoint."""
        if id == 'default' and not remainder:
            return ClusterQuotasDefaultController(), ''
        return None


class ClusterQuotasDefaultController(base.BaseController):
    RBAC_TYPE = constants.RBAC_CLUSTERQUOTA

    def __init__(self):
        super(ClusterQuotasDefaultController, self).__init__()

    @wsme_pecan.wsexpose(clusterquota_types.ClusterQuotaResponse, wtypes.text)
    def get(self):
        """Get default cluster quota details."""
        context = pecan.request.context.get('octavia_context')

        self._auth_validate_action(context, context.project_id,
                                   constants.RBAC_GET_DEFAULTS)

        clusterquotas = self._get_default_clusterquotas()
        return self._convert_db_to_type(clusterquotas,
                                        clusterquota_types.ClusterQuotaResponse
                                        )
