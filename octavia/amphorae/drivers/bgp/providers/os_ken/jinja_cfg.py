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

import os

import jinja2

from oslo_config import cfg
from oslo_serialization import jsonutils


BGP_TEMPLATE = os.path.abspath(
    os.path.join(os.path.dirname(__file__),
                 'templates/bgp_base.template'))
CONF = cfg.CONF


class OsKenBGPJinjaTemplater(object):

    def __init__(self, bgp_template=None):
        """Os-ken BGP configuration generation

        :param bgp_template: Absolute path os-ken bgp Jinja template
        """
        super(OsKenBGPJinjaTemplater, self).__init__()
        self.bgp_template = (bgp_template if bgp_template else BGP_TEMPLATE)
        self._jinja_env = None

    def get_template(self, template_file):
        """Returns the specified Jinja configuration template."""
        if not self._jinja_env:
            template_loader = jinja2.FileSystemLoader(
                searchpath=os.path.dirname(template_file))
            self._jinja_env = jinja2.Environment(
                autoescape=True,
                loader=template_loader,
                trim_blocks=True,
                lstrip_blocks=True)
        return self._jinja_env.get_template(os.path.basename(template_file))

    def build_bgp_config(self, distributor, amphora):
        config_data = jsonutils.loads(distributor.config_data)
        if 'password' in config_data:
            return self.get_template(self.bgp_template).render(
                {'speaker_as': config_data['as'],
                 'peer_as': config_data['as'],
                 'router_id': amphora.lb_network_ip,
                 'peer_ip': config_data['router_id'],
                 'password': config_data['password']})
        return self.get_template(self.bgp_template).render(
            {'speaker_as': config_data['as'],
             'peer_as': config_data['as'],
             'router_id': amphora.lb_network_ip,
             'peer_ip': config_data['router_id']})
