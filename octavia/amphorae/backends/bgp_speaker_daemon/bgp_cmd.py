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
from oslo_log import log as logging

from octavia.amphorae.backends.bgp_speaker_daemon import osken_bgp_speaker

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


class BgpCmd(object):

    BGP_INSTANCE = None

    def __init__(self, status_queue):
        self.report_status = status_queue
        if not self.BGP_INSTANCE:
            self.BGP_INSTANCE = osken_bgp_speaker.BgpSpeaker(
                CONF.bgp_speaker.speaker_as,
                CONF.bgp_speaker.router_id,
                self.bgp_peer_down_cb, self.bgp_peer_up_cb)
        self.BGP_INSTANCE.add_bgp_peer(CONF.bgp_peer.peer_ip,
                                       CONF.bgp_peer.peer_as,
                                       CONF.bgp_peer.enable_ipv4,
                                       CONF.bgp_peer.enable_ipv6,
                                       CONF.bgp_peer.password)

    def stop_bpg(self):
        if not self.BGP_INSTANCE:
            return
        self.BGP_INSTANCE.delete_bgp_peer(CONF.bgp_peer.peer_ip)

    def register_amphora(self, cidr, nexthop):
        try:
            self.BGP_INSTANCE.advertise_route(cidr, nexthop)
            message = {'event_type': 'advertise_route', 'data': 'success'}
        except Exception as e:
            message = {'event_type': 'advertise_route', 'data': e}
        self.report_status.put(message)

    def unregister_amphora(self, cidr):
        try:
            self.BGP_INSTANCE.prefix_del(prefix=cidr)
            message = {'event_type': 'prefix_del', 'data': 'success'}
        except Exception as e:
            message = {'event_type': 'prefix_del', 'data': e}
        self.report_status.put(message)

    def get_statistics(self):
        try:
            stats = self.BGP_INSTANCE.neighbor_state_get(
                CONF.bgp_peer.peer_ip)
            message = {'event_type': 'statistics', 'data': stats}
        except Exception as e:
            message = {'event_type': 'statistics', 'data': e}
        self.report_status.put(message)

    def bgp_peer_down_cb(self, remote_ip, remote_as):
        LOG.info('BGP Peer %s for remote_as=%d went DOWN.',
                 remote_ip, remote_as)
        message = {'event_type': 'peer_down',
                   'data': {'remote_ip': remote_ip,
                            'remote_as': remote_as}}
        self.report_status.put(message)

    def bgp_peer_up_cb(self, remote_ip, remote_as):
        LOG.info('BGP Peer %s for remote_as=%d is UP.',
                 remote_ip, remote_as)
        message = {'event_type': 'peer_up',
                   'data': {'remote_ip': remote_ip,
                            'remote_as': remote_as}}
        self.report_status.put(message)
