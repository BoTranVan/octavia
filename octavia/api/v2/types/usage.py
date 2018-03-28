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

from wsme import types as wtypes

from octavia.common import constants


class ProvisioningStatusUsage(wtypes.DynamicBase):
    def __init__(self, status_tuples):
        super(ProvisioningStatusUsage, self).__init__()

        for status_name in constants.SUPPORTED_PROVISIONING_STATUSES:
            setattr(self, status_name, 0)

        for status_name, status_value in status_tuples:
            setattr(self, status_name, status_value)

provisioning_status_attrs = {
    status_name: wtypes.wsattr(wtypes.IntegerType())
    for status_name in constants.SUPPORTED_PROVISIONING_STATUSES}
ProvisioningStatusUsage.add_attributes(**provisioning_status_attrs)


class OperatingStatusUsage(wtypes.DynamicBase):
    def __init__(self, status_tuples):
        super(OperatingStatusUsage, self).__init__()

        for status_name in constants.SUPPORTED_OPERATING_STATUSES:
            setattr(self, status_name, 0)

        for status_name, status_value in status_tuples:
            setattr(self, status_name, status_value)

operating_status_attrs = {
    status_name: wtypes.wsattr(wtypes.IntegerType())
    for status_name in constants.SUPPORTED_OPERATING_STATUSES}
OperatingStatusUsage.add_attributes(**operating_status_attrs)


class TypedUsage(wtypes.Base):
    total = wtypes.wsattr(wtypes.IntegerType())
    provisioning_status = ProvisioningStatusUsage
    operating_status = OperatingStatusUsage

    def __init__(self, type_dict):
        super(TypedUsage, self).__init__()

        self.provisioning_status = ProvisioningStatusUsage(
            type_dict[constants.PROVISIONING_STATUS])
        self.operating_status = OperatingStatusUsage(
            type_dict[constants.OPERATING_STATUS])
        self.total = type_dict['total']


class UsageResponse(wtypes.Base):
    """Usage definitions."""
    loadbalancers = TypedUsage
    listeners = TypedUsage
    pools = TypedUsage
    members = TypedUsage
    healthmonitors = TypedUsage
    l7policies = TypedUsage
    l7rules = TypedUsage

    def __init__(self, usage_dict):
        super(UsageResponse, self).__init__()

        self.loadbalancers = TypedUsage(usage_dict.get('load_balancer'))
        self.listeners = TypedUsage(usage_dict.get('listener'))
        self.pools = TypedUsage(usage_dict.get('pool'))
        self.members = TypedUsage(usage_dict.get('member'))
        self.healthmonitors = TypedUsage(usage_dict.get('health_monitor'))
        self.l7policies = TypedUsage(usage_dict.get('l7policy'))
        self.l7rules = TypedUsage(usage_dict.get('l7rule'))


class UsageRootResponse(wtypes.DynamicBase):
    """Wrapper object for quotas responses."""
    usage = wtypes.wsattr(UsageResponse)
