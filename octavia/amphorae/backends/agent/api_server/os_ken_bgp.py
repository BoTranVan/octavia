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

import multiprocessing as multiproc
import os
import stat
import time

import flask
import six
import webob

from oslo_log import log as logging
from oslo_serialization import jsonutils

from octavia.amphorae.backends.agent.api_server import bgp_base
from octavia.amphorae.backends.agent.api_server import listener
from octavia.amphorae.backends.bgp_speaker_daemon import bgp_speaker_daemon
from octavia.common import constants as consts

LOG = logging.getLogger(__name__)
BUFFER = 100

if six.PY2:
    import Queue as queue  # pylint: disable=wrong-import-order
else:
    import queue  # pylint: disable=wrong-import-order


class OsKenBgpDriver(bgp_base.BgpDriverBase):

    def __init__(self):
        self.cmd_queue = multiproc.Queue()
        self.stat_queue = multiproc.Queue()
        self.speaker_daemon = None

    def bgp_dir(self):
        return "/etc/octavia"

    def bgp_cfg_path(self):
        return os.path.join(self.bgp_dir(), 'osken_bgp.ini')

    def upload_bgp_config(self):
        stream = listener.Wrapped(flask.request.stream)

        if not os.path.exists(self.bgp_dir()):
            os.makedirs(self.bgp_dir())

        conf_file = self.bgp_cfg_path()
        mode = stat.S_IRUSR | stat.S_IWUSR
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC

        with os.fdopen(os.open(conf_file, flags, mode), 'wb') as f:
            b = stream.read(BUFFER)
            while b:
                f.write(b)
                b = stream.read(BUFFER)

        res = webob.Response(json={'message': 'OK'}, status=200)
        res.headers['ETag'] = stream.get_md5()

        return res

    def manage_bgp_speaker(self, action):
        action = action.lower()
        res = webob.Response(json={'message': 'OK'}, status=200)
        if action not in [consts.AMP_ACTION_START,
                          consts.AMP_ACTION_STOP,
                          consts.AMP_ACTION_RELOAD]:
            return webob.Response(json=dict(
                message='Invalid Request',
                details="Unknown action: {0}".format(action)), status=400)
        if action == consts.AMP_ACTION_START:
            if self.speaker_daemon and self.speaker_daemon.is_alive():
                return res
            if self.speaker_daemon and not self.speaker_daemon.is_alive():
                self.speaker_daemon = None
            if not self.speaker_daemon:
                self.speaker_daemon = multiproc.Process(
                    name='BGP_Speaker_daemon',
                    target=bgp_speaker_daemon.run_bpg_speaker,
                    args=(self.cmd_queue, self.stat_queue,))
                self.speaker_daemon.daemon = True
                self.speaker_daemon.start()
        if action == consts.AMP_ACTION_STOP:
            if not self.speaker_daemon:
                return res
            if not self.speaker_daemon.is_alive():
                self.speaker_daemon = None
                return res
            self.cmd_queue.put({'cmd': 'shutdown'})
            self.speaker_daemon = None

        return res

    def register_amphora(self):
        vip = self.get_vip()
        nexthop = self.get_frontend_ip()
        message = {'cmd': 'announce_route',
                   'body': {'cidr': vip + '/32',
                            'nexthop': nexthop}}
        self.cmd_queue.put(message)
        res = webob.Response(json={'message': 'OK'}, status=200)
        return res

    def unregister_amphora(self):
        pass

    def get_status(self):
        if not self.speaker_daemon:
            status = 'stopped'
        elif not self.speaker_daemon.is_alive():
            status = 'down'
        else:
            statics = None
            self.cmd_queue.put({'cmd': 'get_statistics'})
            for i in range(0, 20):
                try:
                    while True:
                        # Constantly read data from stat_queue until
                        # we get statistics data.
                        statics = self.stat_queue.get_nowait()
                        if statics['event_type'] == 'statistics':
                            break
                    break
                except queue.Empty:
                    pass
                time.sleep(1)
            if not statics or isinstance(statics['data'], Exception):
                status = 'ERROR'
            else:
                stat_dict = jsonutils.loads(statics['data'])
                for key, value in stat_dict.items():
                    status = value['info']['bgp_state']
        res = webob.Response(json={'message': 'OK', 'status': status},
                             status=200)
        return res
