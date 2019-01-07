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

from oslo_config import cfg

from octavia.i18n import _
from octavia import version

bgp_speaker_opts = [
    cfg.IPOpt('router_id', default='127.0.0.1',
              help=_("The router id of local bgp speaker.")),
    cfg.PortOpt('speaker_as', default=62000,
                help=_("The AS of local bgp speaker.")),

]

bgp_peer_opts = [
    cfg.IPOpt('peer_ip', default='127.0.0.1',
              help=_("The peer ip of bgp speaker.")),
    cfg.PortOpt('peer_as', default=62000,
                help=_("The peer AS of bgp speaker.")),
    cfg.BoolOpt('enable_ipv4', default=True,
                help=_("Enables IPv4 address family for the peer.")),
    cfg.BoolOpt('enable_ipv6', default=False,
                help=_("Enables IPv6 address family for the peer.")),
    cfg.StrOpt('password',
               help=_('The peer password'),
               secret=True)
]

cfg.CONF.register_opts(bgp_speaker_opts, group='bgp_speaker')
cfg.CONF.register_opts(bgp_peer_opts, group='bgp_peer')


def init(*args, **kwargs):
    cfg.CONF(args=args, project='osken_bgp',
             version='%%prog %s' % version.version_info.release_string(),
             **kwargs)
