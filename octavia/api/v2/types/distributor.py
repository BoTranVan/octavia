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

from wsme import types as wtypes

from octavia.api.common import types


class BaseDistributorType(types.BaseType):
    _type_to_model_map = {'admin_state_up': 'enabled'}
    _child_map = {}


class DistributorResponse(BaseDistributorType):
    """Defines which attributes are to be shown on any response."""
    id = wtypes.wsattr(wtypes.UuidType())
    name = wtypes.wsattr(wtypes.StringType())
    description = wtypes.wsattr(wtypes.StringType())
    distributor_driver = wtypes.wsattr(wtypes.StringType())
    admin_state_up = wtypes.wsattr(bool)
    frontend_subnet = wtypes.wsattr(wtypes.UuidType())
    provisioning_status = wtypes.wsattr(wtypes.StringType())
    operating_status = wtypes.wsattr(wtypes.StringType())
    config_data = wtypes.wsattr(wtypes.StringType())

    @classmethod
    def from_data_model(cls, data_model, children=False):
        distributor = super(DistributorResponse, cls).from_data_model(
            data_model, children=children)
        return distributor


class DistributorRootResponse(types.BaseType):
    distributor = wtypes.wsattr(DistributorResponse)


class DistributorsRootResponse(types.BaseType):
    distributors = wtypes.wsattr([DistributorResponse])
    distributors_links = wtypes.wsattr([types.PageType])


class DistributorPOST(BaseDistributorType):
    """Defines mandatory and optional attributes of a POST request."""
    name = wtypes.wsattr(wtypes.StringType(max_length=255), mandatory=True)
    description = wtypes.wsattr(wtypes.StringType(max_length=255))
    admin_state_up = wtypes.wsattr(bool, default=True)
    distributor_driver = wtypes.wsattr(wtypes.StringType(max_length=64),
                                       mandatory=True)
    frontend_subnet = wtypes.wsattr(wtypes.UuidType(), mandatory=True)
    config_data = wtypes.wsattr(wtypes.StringType(max_length=4096),
                                mandatory=True)


class DistributorRootPOST(types.BaseType):
    distributor = wtypes.wsattr(DistributorPOST)


class DistributorPUT(BaseDistributorType):
    """Defines the attributes of a PUT request."""
    name = wtypes.wsattr(wtypes.StringType(max_length=255))
    description = wtypes.wsattr(wtypes.StringType(max_length=255))
    admin_state_up = wtypes.wsattr(bool)
    config_data = wtypes.wsattr(wtypes.StringType(max_length=4096))


class DistributorRootPUT(types.BaseType):
    distributor = wtypes.wsattr(DistributorPUT)
