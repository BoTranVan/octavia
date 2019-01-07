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

import abc

import pyroute2

from oslo_config import cfg
import six
from stevedore import driver as stevedore_driver
from werkzeug import exceptions

from octavia.common import constants

CONF = cfg.CONF


@six.add_metaclass(abc.ABCMeta)
class BgpDriverBase(object):
    """Base bgp speaker driver API

    """

    @abc.abstractmethod
    def upload_bgp_config(self):
        """Upload bgp config file

        :returns: HTTP response with status code

        """
        pass

    @abc.abstractmethod
    def manage_bgp_speaker(self, action):
        """Start, Stop or Reload the bgp speaker

        :param action: the action that we want to do

        :returns: HTTP response with status code

        """
        pass

    @abc.abstractmethod
    def register_amphora(self):
        """Register the amphora to distributor by announce a route

        :returns: HTTP response with status code

        """
        pass

    @abc.abstractmethod
    def unregister_amphora(self):
        """Unreigster the amphora from distributor by withdraw a route

        :returns: HTTP response with status code

        """
        pass

    @abc.abstractmethod
    def get_status(self):
        """Get the bgp speaker status of the amphora.

        :returns: HTTP response with status code

        """
        pass

    def get_vip(self):
        with pyroute2.NetNS(constants.AMPHORA_NAMESPACE) as ns:
            addr = ns.get_addr(label=constants.NETNS_DUMMY_INTERFACE)[0]
            for item in addr['attrs']:
                if 'IFA_ADDRESS' in item:
                    return item[1]
        raise exceptions.Conflict(description="Didn't get vip.")

    def get_frontend_ip(self):
        with pyroute2.NetNS(constants.AMPHORA_NAMESPACE) as ns:
            addr = ns.get_addr(label=constants.NETNS_PRIMARY_INTERFACE)[0]
            for item in addr['attrs']:
                if 'IFA_ADDRESS' in item:
                    return item[1]
        raise exceptions.Conflict(description="Didn't get frontent ip.")


class BgpServer(object):

    BGPSERVER_INSTANCE = None

    @classmethod
    def get_bgpserver(cls):
        if not cls.BGPSERVER_INSTANCE:
            cls.BGPSERVER_INSTANCE = stevedore_driver.DriverManager(
                namespace='octavia.amphora.bgp_driver',
                name=CONF.amphora_agent.amphora_bgp_driver,
                invoke_on_load=True,
            ).driver
        return cls.BGPSERVER_INSTANCE
