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

import eventlet
from os_ken.services.protocols.bgp import bgpspeaker
from os_ken.services.protocols.bgp.rtconf.neighbors import CONNECT_MODE_ACTIVE


class BgpSpeaker(object):

    def __init__(self, speaker_as, routerid,
                 bgp_peer_down_cb=None, bgp_peer_up_cb=None):
        eventlet.monkey_patch(os=False, thread=False)
        self.speaker = bgpspeaker.BGPSpeaker(
            as_number=speaker_as,
            router_id=str(routerid),
            peer_down_handler=bgp_peer_down_cb,
            peer_up_handler=bgp_peer_up_cb)

    def add_bgp_peer(self, peer_ip, peer_as,
                     enable_ipv4=True, enable_ipv6=False,
                     password=None):

        self.speaker.neighbor_add(address=peer_ip,
                                  remote_as=peer_as,
                                  enable_ipv4=enable_ipv4,
                                  enable_ipv6=enable_ipv6,
                                  password=password,
                                  connect_mode=CONNECT_MODE_ACTIVE)

    def delete_bgp_peer(self, peer_ip):
        self.speaker.neighbor_del(address=peer_ip)

    def advertise_route(self, cidr, nexthop):
        self.speaker.prefix_add(prefix=cidr, next_hop=nexthop)

    def withdraw_route(self, cidr, nexthop=None):
        self.speaker.prefix_del(prefix=cidr)

    def get_bgp_speaker_statistics(self):
        self.speaker.neighbor_state_get()

    def get_bgp_peer_statistics(self, peer_ip):
        self.speaker.neighbor_state_get(address=peer_ip)
