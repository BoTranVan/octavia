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

from oslo_log import log as logging
import six

from octavia.amphorae.drivers.bgp.providers.os_ken import jinja_cfg
from octavia.amphorae.drivers import driver_base
from octavia.common import constants

LOG = logging.getLogger(__name__)
API_VERSION = constants.API_VERSION


class BGPAmphoraDriverMixin(driver_base.BGPDriverMixin):
    def __init__(self):
        super(BGPAmphoraDriverMixin, self).__init__()

        # The Mixed class must define a self.client object for the
        # AmphoraApiClient

    def update_bgp_conf(self, loadbalancer, distributor):
        """Update amphorae of the loadbalancer with a new BGP configuration

        :param loadbalancer: loadbalancer object
        :param distributor: distributor object
        """
        templater = jinja_cfg.OsKenBGPJinjaTemplater()

        LOG.debug("Update loadbalancer %s amphora BGP configuration.",
                  loadbalancer.id)

        for amp in six.moves.filter(
            lambda amp: amp.status == constants.AMPHORA_ALLOCATED,
                loadbalancer.amphorae):

            # Generate os-ken bgp configuration from loadbalancer object
            config = templater.build_bgp_config(distributor, amp)
            self.client.upload_bgp_config(amp, config)

    def stop_bgp_service(self, loadbalancer):
        """Stop the BGP speaker services running on the loadbalancer's amphorae

        :param loadbalancer: loadbalancer object
        """
        LOG.info("Stop loadbalancer %s amphora BGP speaker Service.",
                 loadbalancer.id)

        for amp in six.moves.filter(
            lambda amp: amp.status == constants.AMPHORA_ALLOCATED,
                loadbalancer.amphorae):

            self.client.stop_bgp_speaker(amp)

    def start_bgp_service(self, loadbalancer):
        """Start the BGP speaker services of all amphorae of the loadbalancer

        :param loadbalancer: loadbalancer object
        """
        LOG.info("Start loadbalancer %s amphora BGP speaker Service.",
                 loadbalancer.id)

        for amp in six.moves.filter(
            lambda amp: amp.status == constants.AMPHORA_ALLOCATED,
                loadbalancer.amphorae):

            LOG.debug("Start BGP speaker Service on amphora %s .",
                      amp.lb_network_ip)
            self.client.start_bgp_speaker(amp)

    def register_to_distributor(self, loadbalancer):
        for amp in six.moves.filter(
            lambda amp: amp.status == constants.AMPHORA_ALLOCATED,
                loadbalancer.amphorae):
            self.client.register_to_distributor(amp)

    def get_frontend_interface(self, amphora, timeout_dict=None):
        return self.client.get_interface(
            amphora, amphora.frontend_ip,
            timeout_dict=timeout_dict)['interface']
