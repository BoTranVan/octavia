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

import time

import six

from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF
LOG = logging.getLogger(__name__)

if six.PY2:
    import Queue as queue  # pylint: disable=wrong-import-order
else:
    import queue  # pylint: disable=wrong-import-order


def run_bpg_speaker(cmd_queue, stat_queue):

    from octavia.amphorae.backends.bgp_speaker_daemon import bgp_cmd
    from octavia.amphorae.backends.bgp_speaker_daemon import config
    config.init("--config-file", "/etc/octavia/amphora-agent.conf",
                "--config-file", "/etc/octavia/osken_bgp.ini")

    LOG.info('BGP Speaker daemon starting.')
    osken_bgp_cmd = bgp_cmd.BgpCmd(stat_queue)

    while True:
        try:
            cmd_dict = cmd_queue.get_nowait()
            if cmd_dict['cmd'] == 'reload':
                LOG.info('Reloading configuration')
                CONF.reload_config_files()
            elif cmd_dict['cmd'] == 'shutdown':
                LOG.info('BGP Speaker daemon shutting down.')
                osken_bgp_cmd.stop_bpg()
                break
            elif cmd_dict['cmd'] == 'announce_route':
                osken_bgp_cmd.register_amphora(**cmd_dict['body'])
            elif cmd_dict['cmd'] == 'get_statistics':
                osken_bgp_cmd.get_statistics()
            else:
                pass
        except queue.Empty:
            pass
        time.sleep(0.5)
