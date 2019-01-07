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

import json
import os
import stat

import mock
import netifaces
from oslo_config import fixture as oslo_fixture

from octavia.amphorae.backends.agent import api_server
from octavia.amphorae.backends.agent.api_server import server
from octavia.common import config
from octavia.common import constants as consts
from octavia.tests.common import utils as test_utils
import octavia.tests.unit.base as base


AMP_AGENT_CONF_PATH = '/etc/octavia/amphora-agent.conf'
RANDOM_ERROR = 'random error'
OK = dict(message='OK')


class BgpTestCase(base.TestCase):
    app = None

    def setUp(self):
        super(BgpTestCase, self).setUp()
        self.conf = self.useFixture(oslo_fixture.Config(config.cfg.CONF))
        self.conf.config(group="haproxy_amphora", base_path='/var/lib/octavia')
        self.conf.config(group="controller_worker",
                         loadbalancer_topology=consts.TOPOLOGY_ACTIVE_ACTIVE)
        with mock.patch('distro.id',
                        return_value='ubuntu'):
            self.ubuntu_test_server = server.Server()
            self.ubuntu_app = self.ubuntu_test_server.app.test_client()

        with mock.patch('distro.id',
                        return_value='centos'):
            self.centos_test_server = server.Server()
            self.centos_app = self.centos_test_server.app.test_client()

    def test_plug_vip(self):
        self._test_plug_VIP4(consts.CENTOS)

    @mock.patch('os.chmod')
    @mock.patch('shutil.copy2')
    @mock.patch('pyroute2.NSPopen')
    @mock.patch('octavia.amphorae.backends.agent.api_server.'
                'plug.Plug._netns_interface_exists')
    @mock.patch('netifaces.interfaces')
    @mock.patch('netifaces.ifaddresses')
    @mock.patch('pyroute2.IPRoute')
    @mock.patch('pyroute2.netns.create')
    @mock.patch('pyroute2.NetNS')
    @mock.patch('subprocess.check_output')
    @mock.patch('shutil.copytree')
    @mock.patch('os.makedirs')
    @mock.patch('os.path.isfile')
    def _test_plug_VIP4(self, distro, mock_isfile, mock_makedirs,
                        mock_copytree, mock_check_output, mock_netns,
                        mock_netns_create, mock_pyroute2, mock_ifaddress,
                        mock_interfaces, mock_int_exists, mock_nspopen,
                        mock_copy2, mock_os_chmod):

        mock_isfile.return_value = True

        self.assertIn(distro, [consts.UBUNTU, consts.CENTOS])
        subnet_info = {
            'subnet_cidr': '203.0.113.0/24',
            'gateway': '203.0.113.1',
            'mac_address': '123'
        }
        # malformed ip
        if distro == consts.UBUNTU:
            rv = self.ubuntu_app.post('/' + api_server.VERSION +
                                      '/plug/vip/error',
                                      data=json.dumps(subnet_info),
                                      content_type='application/json')
        elif distro == consts.CENTOS:
            rv = self.centos_app.post('/' + api_server.VERSION +
                                      '/plug/vip/error',
                                      data=json.dumps(subnet_info),
                                      content_type='application/json')
        self.assertEqual(400, rv.status_code)

        # No subnet info
        if distro == consts.UBUNTU:
            rv = self.ubuntu_app.post('/' + api_server.VERSION +
                                      '/plug/vip/error')
        elif distro == consts.CENTOS:
            rv = self.centos_app.post('/' + api_server.VERSION +
                                      '/plug/vip/error')

        self.assertEqual(400, rv.status_code)

        # Interface already plugged
        mock_int_exists.return_value = True
        if distro == consts.UBUNTU:
            rv = self.ubuntu_app.post('/' + api_server.VERSION +
                                      "/plug/vip/203.0.113.2",
                                      content_type='application/json',
                                      data=json.dumps(subnet_info))
        elif distro == consts.CENTOS:
            rv = self.centos_app.post('/' + api_server.VERSION +
                                      "/plug/vip/203.0.113.2",
                                      content_type='application/json',
                                      data=json.dumps(subnet_info))
        self.assertEqual(409, rv.status_code)
        self.assertEqual(dict(message="Interface already exists"),
                         json.loads(rv.data.decode('utf-8')))
        mock_int_exists.return_value = False

        # No interface at all
        mock_interfaces.side_effect = [[]]
        file_name = '/sys/bus/pci/rescan'
        m = self.useFixture(test_utils.OpenFixture(file_name)).mock_open
        with mock.patch('os.open') as mock_open, mock.patch.object(
                os, 'fdopen', m) as mock_fdopen:
            mock_open.return_value = 123

            if distro == consts.UBUNTU:
                rv = self.ubuntu_app.post('/' + api_server.VERSION +
                                          "/plug/vip/203.0.113.2",
                                          content_type='application/json',
                                          data=json.dumps(subnet_info))
            elif distro == consts.CENTOS:
                rv = self.centos_app.post('/' + api_server.VERSION +
                                          "/plug/vip/203.0.113.2",
                                          content_type='application/json',
                                          data=json.dumps(subnet_info))
            mock_open.assert_called_with(file_name, os.O_WRONLY)
            mock_fdopen.assert_called_with(123, 'w')
        m().write.assert_called_once_with('1')
        self.assertEqual(404, rv.status_code)
        self.assertEqual(dict(details="No suitable network interface found"),
                         json.loads(rv.data.decode('utf-8')))

        # Two interfaces down
        m().reset_mock()
        mock_interfaces.side_effect = [['blah', 'blah2']]
        mock_ifaddress.side_effect = [['blabla'], ['blabla']]
        with mock.patch('os.open') as mock_open, mock.patch.object(
                os, 'fdopen', m) as mock_fdopen:
            mock_open.return_value = 123

            if distro == consts.UBUNTU:
                rv = self.ubuntu_app.post('/' + api_server.VERSION +
                                          "/plug/vip/203.0.113.2",
                                          content_type='application/json',
                                          data=json.dumps(subnet_info))
            elif distro == consts.CENTOS:
                rv = self.centos_app.post('/' + api_server.VERSION +
                                          "/plug/vip/203.0.113.2",
                                          content_type='application/json',
                                          data=json.dumps(subnet_info))
            mock_open.assert_called_with(file_name, os.O_WRONLY)
            mock_fdopen.assert_called_with(123, 'w')
        m().write.assert_called_once_with('1')
        self.assertEqual(404, rv.status_code)
        self.assertEqual(dict(details="No suitable network interface found"),
                         json.loads(rv.data.decode('utf-8')))

        # Happy Path IPv4, with frontend_ip and host route
        full_subnet_info = {
            'subnet_cidr': '203.0.113.0/24',
            'gateway': '203.0.113.1',
            'mac_address': '123',
            'frontend_ip': '203.0.113.4',
            'mtu': 1450,
            'host_routes': [{'destination': '203.0.114.0/24',
                             'nexthop': '203.0.113.5'},
                            {'destination': '203.0.115.1/32',
                             'nexthop': '203.0.113.5'}]
        }

        mock_interfaces.side_effect = [['blah']]
        mock_ifaddress.side_effect = [[netifaces.AF_LINK],
                                      {netifaces.AF_LINK: [{'addr': '123'}]}]

        mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH

        if self.conf.conf.amphora_agent.agent_server_network_file:
            file_name = self.conf.conf.amphora_agent.agent_server_network_file
            flags = os.O_WRONLY | os.O_CREAT | os.O_APPEND
        elif distro == consts.UBUNTU:
            file_name = ('/etc/netns/{netns}/network/interfaces.d/'
                         '{netns_int}.cfg'.format(
                             netns=consts.AMPHORA_NAMESPACE,
                             netns_int=consts.NETNS_PRIMARY_INTERFACE))
            flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        elif distro == consts.CENTOS:
            file_name = ('/etc/netns/{netns}/sysconfig/network-scripts/'
                         'ifcfg-{netns_int}'.format(
                             netns=consts.AMPHORA_NAMESPACE,
                             netns_int=consts.NETNS_PRIMARY_INTERFACE))
            flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC

        m = self.useFixture(test_utils.OpenFixture(file_name)).mock_open

        with mock.patch('os.open') as mock_open, mock.patch.object(
                os, 'fdopen', m) as mock_fdopen:
            mock_open.return_value = 123
            if distro == consts.UBUNTU:
                rv = self.ubuntu_app.post('/' + api_server.VERSION +
                                          "/plug/vip/203.0.113.2",
                                          content_type='application/json',
                                          data=json.dumps(full_subnet_info))
            elif distro == consts.CENTOS:
                rv = self.centos_app.post('/' + api_server.VERSION +
                                          "/plug/vip/203.0.113.2",
                                          content_type='application/json',
                                          data=json.dumps(full_subnet_info))
            self.assertEqual(202, rv.status_code)
            mock_open.assert_any_call(file_name, flags, mode)
            mock_fdopen.assert_any_call(123, 'w')

            plug_inf_file = '/var/lib/octavia/plugged_interfaces'
            flags = os.O_RDWR | os.O_CREAT
            mode = stat.S_IRUSR | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH
            mock_open.assert_any_call(plug_inf_file, flags, mode)
            mock_fdopen.assert_any_call(123, 'r+')

            handle = m()
            if distro == consts.UBUNTU:
                handle.write.assert_any_call(
                    '\n# Generated by Octavia agent\n'
                    'auto {netns_int} {netns_int}:0\n'
                    'iface {netns_int} inet static\n'
                    'address 203.0.113.4\n'
                    'broadcast 203.0.113.255\n'
                    'netmask 255.255.255.0\n'
                    'gateway 203.0.113.1\n'
                    'mtu 1450\n'
                    'up route add -net 203.0.114.0/24 gw 203.0.113.5 '
                    'dev {netns_int}\n'
                    'down route del -net 203.0.114.0/24 gw 203.0.113.5 '
                    'dev {netns_int}\n'
                    'up route add -host 203.0.115.1/32 gw 203.0.113.5 '
                    'dev {netns_int}\n'
                    'down route del -host 203.0.115.1/32 gw 203.0.113.5 '
                    'dev {netns_int}\n'
                    'iface {netns_int}:0 inet static\n'
                    'address 203.0.113.2\n'
                    'broadcast 203.0.113.255\n'
                    'netmask 255.255.255.0\n\n'
                    '# Add a source routing table to allow members to '
                    'access the VIP\n\n'
                    'post-up /sbin/ip route add default via 203.0.113.1 '
                    'dev eth1 onlink table 1\n'
                    'post-down /sbin/ip route del default via 203.0.113.1 '
                    'dev eth1 onlink table 1\n\n\n'
                    'post-up /sbin/ip route add 203.0.113.0/24 '
                    'dev eth1 src 203.0.113.2 scope link table 1\n'
                    'post-down /sbin/ip route del 203.0.113.0/24 '
                    'dev eth1 src 203.0.113.2 scope link table 1\n'
                    'post-up /sbin/ip route add 203.0.114.0/24 '
                    'via 203.0.113.5 dev eth1 onlink table 1\n'
                    'post-down /sbin/ip route del 203.0.114.0/24 '
                    'via 203.0.113.5 dev eth1 onlink table 1\n'
                    'post-up /sbin/ip route add 203.0.115.1/32 '
                    'via 203.0.113.5 dev eth1 onlink table 1\n'
                    'post-down /sbin/ip route del 203.0.115.1/32 '
                    'via 203.0.113.5 dev eth1 onlink table 1\n\n\n'
                    'post-up /sbin/ip rule add from 203.0.113.2/32 table 1 '
                    'priority 100\n'
                    'post-down /sbin/ip rule del from 203.0.113.2/32 table 1 '
                    'priority 100\n\n'
                    'post-up /sbin/iptables -t nat -A POSTROUTING -p udp '
                    '-o eth1 -j MASQUERADE\n'
                    'post-down /sbin/iptables -t nat -D POSTROUTING -p udp '
                    '-o eth1 -j MASQUERADE'.format(
                        netns_int=consts.NETNS_PRIMARY_INTERFACE))
            elif distro == consts.CENTOS:
                handle.write.assert_any_call(
                    '\n# Generated by Octavia agent\n'
                    'NM_CONTROLLED="no"\nDEVICE="{netns_int}"\n'
                    'ONBOOT="yes"\nTYPE="Ethernet"\nUSERCTL="yes" \n'
                    'BOOTPROTO="static"\nIPADDR="203.0.113.4"\n'
                    'NETMASK="255.255.255.0"\nGATEWAY="203.0.113.1"\n'
                    'MTU="1450"  \n'.format(
                        netns_int=consts.NETNS_PRIMARY_INTERFACE))
                handle.write.assert_any_call(
                    '\n# Generated by Octavia agent\n'
                    'NM_CONTROLLED="no"\nDEVICE="{netns_int}"'
                    '\nNAME="{netns_int}"\nONBOOT="yes"\nTYPE="dummy"'
                    '\nARPCHECK="no"\nIPV6INIT="no"\nUSERCTL="no"\n'
                    'BOOTPROTO="static"\nMTU="1450"\nIPADDR="203.0.113.2"\n'
                    'NETMASK="255.255.255.255"'.format(
                        netns_int=consts.NETNS_DUMMY_INTERFACE))
                flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
                mock_open.assert_any_call('/sbin/ifup-local', flags, mode)
                mock_open.assert_any_call('/sbin/ifdown-local', flags, mode)
                calls = [mock.call('/sbin/ifup-local', stat.S_IEXEC),
                         mock.call('/sbin/ifdown-local', stat.S_IEXEC)]
                mock_os_chmod.assert_has_calls(calls)
            mock_check_output.assert_called_with(
                ['ip', 'netns', 'exec', consts.AMPHORA_NAMESPACE,
                 'ifup', '{netns_int}'.format(
                     netns_int=consts.NETNS_DUMMY_INTERFACE)], stderr=-2)
