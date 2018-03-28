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

import mock
from oslo_config import cfg
from oslo_config import fixture as oslo_fixture
from oslo_utils import uuidutils

from octavia.common import constants
import octavia.common.context
from octavia.tests.functional.api.v2 import base


def usage_dict(provisioning_status=constants.ACTIVE,
               operating_status=constants.ONLINE,
               **kwargs):
    """Create a sample usage dict for matching output.

    Example empty usage dict:
    {
        "loadbalancers": {
            "total": 0,
            "provisioning_status": {
                "ACTIVE": 0,
                "ERROR": 0,
                "PENDING_DELETE": 0,
                "PENDING_UPDATE": 0,
                "PENDING_CREATE": 0,
                "DELETED": 0
            },
            "operating_status": {
                "ONLINE": 0,
                "OFFLINE": 0,
                "DEGRADED": 0,
                "ERROR": 0,
                "DRAINING": 0,
                "NO_MONITOR": 0
            }
        },
        "listeners": {
            "total": 0,
            "provisioning_status": {
                "ACTIVE": 0,
                "ERROR": 0,
                "PENDING_DELETE": 0,
                "PENDING_UPDATE": 0,
                "PENDING_CREATE": 0,
                "DELETED": 0
            },
            "operating_status": {
                "ONLINE": 0,
                "OFFLINE": 0,
                "DEGRADED": 0,
                "ERROR": 0,
                "DRAINING": 0,
                "NO_MONITOR": 0
            }
        },
        "pools": {
            "total": 0,
            "provisioning_status": {
                "ACTIVE": 0,
                "ERROR": 0,
                "PENDING_DELETE": 0,
                "PENDING_UPDATE": 0,
                "PENDING_CREATE": 0,
                "DELETED": 0
            },
            "operating_status": {
                "ONLINE": 0,
                "OFFLINE": 0,
                "DEGRADED": 0,
                "ERROR": 0,
                "DRAINING": 0,
                "NO_MONITOR": 0
            }
        },
        "healthmonitors": {
            "total": 0,
            "provisioning_status": {
                "ACTIVE": 0,
                "ERROR": 0,
                "PENDING_DELETE": 0,
                "PENDING_UPDATE": 0,
                "PENDING_CREATE": 0,
                "DELETED": 0
            },
            "operating_status": {
                "ONLINE": 0,
                "OFFLINE": 0,
                "DEGRADED": 0,
                "ERROR": 0,
                "DRAINING": 0,
                "NO_MONITOR": 0
            }
        },
        "members": {
            "total": 0,
            "provisioning_status": {
                "ACTIVE": 0,
                "ERROR": 0,
                "PENDING_DELETE": 0,
                "PENDING_UPDATE": 0,
                "PENDING_CREATE": 0,
                "DELETED": 0
            },
            "operating_status": {
                "ONLINE": 0,
                "OFFLINE": 0,
                "DEGRADED": 0,
                "ERROR": 0,
                "DRAINING": 0,
                "NO_MONITOR": 0
            }
        },
        "l7policies": {
            "total": 0,
            "provisioning_status": {
                "ACTIVE": 0,
                "ERROR": 0,
                "PENDING_DELETE": 0,
                "PENDING_UPDATE": 0,
                "PENDING_CREATE": 0,
                "DELETED": 0
            },
            "operating_status": {
                "ONLINE": 0,
                "OFFLINE": 0,
                "DEGRADED": 0,
                "ERROR": 0,
                "DRAINING": 0,
                "NO_MONITOR": 0
            }
        },
        "l7rules": {
            "total": 0,
            "provisioning_status": {
                "ACTIVE": 0,
                "ERROR": 0,
                "PENDING_DELETE": 0,
                "PENDING_UPDATE": 0,
                "PENDING_CREATE": 0,
                "DELETED": 0
            },
            "operating_status": {
                "ONLINE": 0,
                "OFFLINE": 0,
                "DEGRADED": 0,
                "ERROR": 0,
                "DRAINING": 0,
                "NO_MONITOR": 0
            }
        }
    }

    :param provisioning_status: Provisioning status to expect for all objects.
    :param operating_status: Operating status to expect for all objects.
    :param kwargs: A dict of all of the object types to be included.
    :return: a usage dictionary
    """
    objects = ('loadbalancers', 'listeners', 'pools', 'healthmonitors',
               'members', 'l7policies', 'l7rules')
    ret_usage = {}
    for obj_type in objects:
        obj_vals = {
            'total': kwargs.get(obj_type, 0),
            constants.PROVISIONING_STATUS: {},
            constants.OPERATING_STATUS: {}
        }
        for ps in constants.SUPPORTED_PROVISIONING_STATUSES:
            obj_vals[constants.PROVISIONING_STATUS][ps] = (
                kwargs.get(obj_type, 0) if ps == provisioning_status else 0
            )
        for os in constants.SUPPORTED_OPERATING_STATUSES:
            obj_vals[constants.OPERATING_STATUS][os] = (
                kwargs.get(obj_type, 0) if os == operating_status else 0
            )
        ret_usage[obj_type] = obj_vals

    return ret_usage


class TestUsage(base.BaseAPITest):

    root_tag = 'usage'

    def setUp(self):
        super(TestUsage, self).setUp()

        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))

        self.lb = self.create_load_balancer(uuidutils.generate_uuid())
        self.lb_id = self.lb.get('loadbalancer').get('id')
        self.set_lb_status(self.lb_id)
        self.listener = self.create_listener(
            constants.PROTOCOL_HTTP, 80, lb_id=self.lb_id)
        self.listener_id = self.listener.get('listener').get('id')
        self.set_lb_status(self.lb_id)
        self.pool = self.create_pool_with_listener(
            self.lb_id,
            listener_id=self.listener_id,
            protocol=constants.PROTOCOL_HTTP,
            lb_algorithm=constants.LB_ALGORITHM_ROUND_ROBIN)
        self.pool_id = self.pool.get('pool').get('id')
        self.set_lb_status(self.lb_id)
        self.health_monitor = self.create_health_monitor(
            self.pool_id,
            type=constants.HEALTH_MONITOR_TCP,
            delay=1,
            timeout=1,
            max_retries=1,
            max_retries_down=1
        )
        self.health_monitor_id = self.health_monitor.get(
            'healthmonitor').get('id')
        self.set_lb_status(self.lb_id)
        self.l7policy = self.create_l7policy(
            self.listener_id, constants.L7POLICY_ACTION_REJECT)
        self.l7policy_id = self.l7policy.get('l7policy').get('id')
        self.set_lb_status(self.lb_id)
        self.l7rule = self.create_l7rule(
            self.l7policy_id,
            type=constants.L7RULE_TYPE_PATH,
            compare_type=constants.L7RULE_COMPARE_TYPE_CONTAINS,
            value='test'
        )
        self.l7rule_id = self.l7rule.get('rule').get('id')
        self.set_lb_status(self.lb_id)
        self.member = self.create_member(
            self.pool_id,
            address='1.2.3.4',
            protocol_port=80
        )
        self.member_id = self.member.get('member').get('id')
        self.set_lb_status(self.lb_id)

    def test_get_all(self):
        expected_usage = usage_dict(
            loadbalancers=1, listeners=1, pools=1, healthmonitors=1, members=1,
            l7policies=1, l7rules=1
        )
        response = self.get(self.USAGE_PATH).json.get(self.root_tag)
        self.assertEqual(expected_usage, response)

        self.set_lb_status(self.lb_id, status=constants.DELETED)

        deleted_usage = usage_dict(
            provisioning_status=constants.DELETED,
            operating_status=constants.OFFLINE,
            loadbalancers=1, listeners=1, pools=1, healthmonitors=1, members=1,
            l7policies=1, l7rules=1
        )
        response = self.get(self.USAGE_PATH).json.get(self.root_tag)
        self.assertEqual(deleted_usage, response)

    def test_get_for_project(self):
        expected_usage = usage_dict(
            loadbalancers=1, listeners=1, pools=1, healthmonitors=1, members=1,
            l7policies=1, l7rules=1
        )
        response = self.get(self.USAGE_PROJECT_PATH.format(
            project_id=self.project_id)).json.get(self.root_tag)
        self.assertEqual(expected_usage, response)

        empty_usage = usage_dict()
        random_project_id = uuidutils.generate_uuid()
        response = self.get(self.USAGE_PROJECT_PATH.format(
            project_id=random_project_id)).json.get(self.root_tag)
        self.assertEqual(empty_usage, response)

    def _test_get_for_project_authorized(self, role):
        expected_usage = usage_dict(
            loadbalancers=1, listeners=1, pools=1, healthmonitors=1, members=1,
            l7policies=1, l7rules=1
        )
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               self.project_id):
            override_credentials = {
                'service_user_id': None,
                'user_domain_id': None,
                'is_admin_project': True,
                'service_project_domain_id': None,
                'service_project_id': None,
                'roles': [role],
                'user_id': None,
                'is_admin': False,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                response = self.get(
                    self.USAGE_PROJECT_PATH.format(project_id=self.project_id)
                ).json.get(self.root_tag)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(expected_usage, response)

    def test_get_for_project_authorized_member(self):
        self._test_get_for_project_authorized('load-balancer_member')

    def test_get_for_project_authorized_observer(self):
        self._test_get_for_project_authorized('load-balancer_observer')

    def test_get_for_project_authorized_global_observer(self):
        self._test_get_for_project_authorized('load-balancer_global_observer')

    def test_get_for_project_authorized_quota_admin(self):
        self._test_get_for_project_authorized('load-balancer_usage_admin')

    def test_get_for_project_not_authorized(self):
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               uuidutils.generate_uuid()):
            response = self.get(self.USAGE_PROJECT_PATH.format(
                project_id=self.project_id), status=403)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, response.json)

    def test_get_for_project_not_authorized_bogus_role(self):
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               uuidutils.generate_uuid()):
            override_credentials = {
                'service_user_id': None,
                'user_domain_id': None,
                'is_admin_project': True,
                'service_project_domain_id': None,
                'service_project_id': None,
                'roles': ['load-balancer:bogus'],
                'user_id': None,
                'is_admin': False,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                response = self.get(self.USAGE_PROJECT_PATH.format(
                    project_id=self.project_id), status=403)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, response.json)

    def test_get_all_authorized_global_observer(self):
        expected_usage = usage_dict(
            loadbalancers=1, listeners=1, pools=1, healthmonitors=1, members=1,
            l7policies=1, l7rules=1
        )
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               self.project_id):
            override_credentials = {
                'service_user_id': None,
                'user_domain_id': None,
                'is_admin_project': False,
                'service_project_domain_id': None,
                'service_project_id': None,
                'roles': ['load-balancer_global_observer'],
                'user_id': None,
                'is_admin': False,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                response = self.get(self.USAGE_PATH).json.get(self.root_tag)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(expected_usage, response)

    def test_get_all_authorized_admin(self):
        expected_usage = usage_dict(
            loadbalancers=1, listeners=1, pools=1, healthmonitors=1, members=1,
            l7policies=1, l7rules=1
        )
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               self.project_id):
            override_credentials = {
                'service_user_id': None,
                'user_domain_id': None,
                'is_admin_project': False,
                'service_project_domain_id': None,
                'service_project_id': None,
                'roles': [],
                'user_id': None,
                'is_admin': True,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                response = self.get(self.USAGE_PATH).json.get(self.root_tag)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(expected_usage, response)

    def test_get_all_not_authorized(self):
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               self.project_id):
            response = self.get(self.USAGE_PATH, status=403)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, response.json)

    def test_get_all_not_authorized_no_role(self):
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               self.project_id):
            override_credentials = {
                'service_user_id': None,
                'user_domain_id': None,
                'is_admin_project': True,
                'service_project_domain_id': None,
                'service_project_id': None,
                'roles': [],
                'user_id': None,
                'is_admin': False,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                response = self.get(self.USAGE_PATH, status=403)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, response.json)

    def test_get_all_not_authorized_bogus_role(self):
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               self.project_id):
            override_credentials = {
                'service_user_id': None,
                'user_domain_id': None,
                'is_admin_project': True,
                'service_project_domain_id': None,
                'service_project_id': None,
                'roles': ['load-balancer:bogus'],
                'user_id': None,
                'is_admin': False,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                response = self.get(self.USAGE_PATH, status=403)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, response.json)
