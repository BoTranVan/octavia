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

from wsme import types as wtypes

from octavia.api.common import types as base
from octavia.common import constants as consts


class ClusterQuotaBase(base.BaseType):
    """Individual cluster quota definitions."""
    cluster_total_loadbalancers = wtypes.wsattr(wtypes.IntegerType(
        minimum=consts.MIN_CLUSTERQUOTA, maximum=consts.MAX_CLUSTERQUOTA))
    max_healthmonitors_per_pool = wtypes.wsattr(wtypes.IntegerType(
        minimum=consts.MIN_CLUSTERQUOTA, maximum=consts.MAX_CLUSTERQUOTA))
    max_listeners_per_loadbalancer = wtypes.wsattr(wtypes.IntegerType(
        minimum=consts.MIN_CLUSTERQUOTA, maximum=consts.MAX_CLUSTERQUOTA))
    max_members_per_pool = wtypes.wsattr(wtypes.IntegerType(
        minimum=consts.MIN_CLUSTERQUOTA, maximum=consts.MAX_CLUSTERQUOTA))
    max_pools_per_loadbalancer = wtypes.wsattr(wtypes.IntegerType(
        minimum=consts.MIN_CLUSTERQUOTA, maximum=consts.MAX_CLUSTERQUOTA))
    max_l7policies_per_listener = wtypes.wsattr(wtypes.IntegerType(
        minimum=consts.MIN_CLUSTERQUOTA, maximum=consts.MAX_CLUSTERQUOTA))
    max_l7rules_per_l7policy = wtypes.wsattr(wtypes.IntegerType(
        minimum=consts.MIN_CLUSTERQUOTA, maximum=consts.MAX_CLUSTERQUOTA))

    def to_dict(self, render_unsets=False):
        clusterquota_dict = super(ClusterQuotaBase, self
                                  ).to_dict(render_unsets)
        return clusterquota_dict


class ClusterQuotaResponse(base.BaseType):
    """Wrapper object for cluster quotas responses."""
    clusterquota = wtypes.wsattr(ClusterQuotaBase)

    @classmethod
    def from_data_model(cls, data_model, children=False):
        clusterquotas = super(ClusterQuotaResponse, cls).from_data_model(
            data_model, children=children)
        clusterquotas.clusterquota = ClusterQuotaBase.from_data_model(
            data_model)
        return clusterquotas


class ClusterQuotaPUT(base.BaseType):
    """Overall object for quota PUT request."""
    clusterquota = wtypes.wsattr(ClusterQuotaBase)
