# Copyright 2016 Rackspace
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
import random

import mock
from oslo_config import cfg
from oslo_config import fixture as oslo_fixture
from oslo_utils import uuidutils

from octavia.common import constants
import octavia.common.context
from octavia.tests.functional.api.v2 import base

CONF = cfg.CONF


class TestClusterQuotas(base.BaseAPITest):

    root_tag = 'clusterquota'

    def setUp(self):
        super(TestClusterQuotas, self).setUp()
        conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
        conf.config(
            group="clusterquotas",
            cluster_total_loadbalancers=random.randrange(
                constants.QUOTA_UNLIMITED, 9000))
        conf.config(
            group="clusterquotas",
            max_healthmonitors_per_pool=random.randrange(
                constants.QUOTA_UNLIMITED, 9000))
        conf.config(
            group="clusterquotas",
            max_listeners_per_loadbalancer=random.randrange(
                constants.QUOTA_UNLIMITED, 9000))
        # We need to make sure unlimited gets tested each pass
        conf.config(
            group="clusterquotas",
            max_members_per_pool=constants.QUOTA_UNLIMITED)
        conf.config(
            group="clusterquotas",
            max_pools_per_loadbalancer=random.randrange(
                constants.QUOTA_UNLIMITED, 9000))
        conf.config(
            group="clusterquotas",
            max_l7policies_per_listener=random.randrange(
                constants.QUOTA_UNLIMITED, 9000))
        conf.config(
            group="clusterquotas",
            max_l7rules_per_l7policy=random.randrange(
                constants.QUOTA_UNLIMITED, 9000))

    def _assert_clusterquotas_equal(self, observed, expected=None):
        if not expected:
            expected = {'cluster_total_loadbalancers':
                        CONF.clusterquotas.cluster_total_loadbalancers,
                        'max_healthmonitors_per_pool':
                            CONF.clusterquotas.max_healthmonitors_per_pool,
                        'max_listeners_per_loadbalancer':
                            CONF.clusterquotas.max_listeners_per_loadbalancer,
                        'max_members_per_pool':
                            CONF.clusterquotas.max_members_per_pool,
                        'max_pools_per_loadbalancer':
                            CONF.clusterquotas.max_pools_per_loadbalancer,
                        'max_l7policies_per_listener':
                            CONF.clusterquotas.max_l7policies_per_listener,
                        'max_l7rules_per_l7policy':
                            CONF.clusterquotas.max_l7rules_per_l7policy}
        self.assertEqual(expected['cluster_total_loadbalancers'],
                         observed['cluster_total_loadbalancers'])
        self.assertEqual(expected['max_healthmonitors_per_pool'],
                         observed['max_healthmonitors_per_pool'])
        self.assertEqual(expected['max_listeners_per_loadbalancer'],
                         observed['max_listeners_per_loadbalancer'])
        self.assertEqual(expected['max_members_per_pool'],
                         observed['max_members_per_pool'])
        self.assertEqual(expected['max_pools_per_loadbalancer'],
                         observed['max_pools_per_loadbalancer'])
        self.assertEqual(expected['max_l7policies_per_listener'],
                         observed['max_l7policies_per_listener'])
        self.assertEqual(expected['max_l7rules_per_l7policy'],
                         observed['max_l7rules_per_l7policy'])

    def test_get(self):
        clusterquota1 = self.set_clusterquota(
            cluster_total_loadbalancers=1, max_members_per_pool=1
        ).get(self.root_tag)

        clusterquotas = self.get(
            self.CLUSTERQUOTAS_PATH
        ).json.get(self.root_tag)
        self._assert_clusterquotas_equal(clusterquotas, clusterquota1)

    def test_get_Authorized_admin(self):
        self._test_get_Authorized('load-balancer_admin')

    def _test_get_Authorized(self, role):
        project1_id = uuidutils.generate_uuid()
        clusterquota1 = self.set_clusterquota(
            cluster_total_loadbalancers=1, max_members_per_pool=1
        ).get(self.root_tag)
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))

        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               project1_id):
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
                'project_id': project1_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                clusterquotas = self.get(
                    self.CLUSTERQUOTAS_PATH
                ).json.get(self.root_tag)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self._assert_clusterquotas_equal(clusterquotas, clusterquota1)

    def test_get_not_Authorized(self):
        self.set_clusterquota(
            cluster_total_loadbalancers=1, max_members_per_pool=1
        ).get(self.root_tag)
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))

        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        clusterquotas = self.get(self.CLUSTERQUOTAS_PATH,
                                 status=403)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, clusterquotas.json)

    def test_get_not_Authorized_bogus_role(self):
        project1_id = uuidutils.generate_uuid()
        self.set_clusterquota(
            cluster_total_loadbalancers=1, max_members_per_pool=1
        ).get(self.root_tag)
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))

        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               project1_id):
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
                'project_id': project1_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                clusterquotas = self.get(
                    self.CLUSTERQUOTAS_PATH,
                    status=403)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, clusterquotas.json)

    def test_get_not_Authorized_no_role(self):
        project1_id = uuidutils.generate_uuid()
        self.set_clusterquota(
            cluster_total_loadbalancers=1, max_members_per_pool=1
        ).get(self.root_tag)
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))

        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               project1_id):
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
                'project_id': project1_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                clusterquotas = self.get(
                    self.CLUSTERQUOTAS_PATH,
                    status=403)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, clusterquotas.json)

    def test_get_default_clusterquotas(self):
        response = self.get(self.CLUSTERQUOTAS_DEFAULT_PATH)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'])

    def test_get_default_clusterquotas_Authorized(self):
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
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
                'roles': ['load-balancer_admin'],
                'user_id': None,
                'is_admin': False,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                response = self.get(self.CLUSTERQUOTAS_DEFAULT_PATH)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'])
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)

    def test_get_default_clusterquotas_not_Authorized(self):
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               uuidutils.generate_uuid()):
            response = self.get(self.CLUSTERQUOTAS_DEFAULT_PATH,
                                status=403)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, response.json)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)

    def test_custom_clusterquotas(self):
        clusterquota_path = self.CLUSTERQUOTAS_PATH
        body = {'clusterquota': {
            'cluster_total_loadbalancers': 30,
            'max_healthmonitors_per_pool': 30,
            'max_listeners_per_loadbalancer': 30,
            'max_members_per_pool': 30,
            'max_pools_per_loadbalancer': 30,
            'max_l7policies_per_listener': 30,
            'max_l7rules_per_l7policy': 30}}
        self.put(clusterquota_path, body, status=202)
        response = self.get(clusterquota_path)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'],
                                         expected=body['clusterquota'])

    def test_custom_clusterquotas_admin(self):
        clusterquota_path = self.CLUSTERQUOTAS_PATH
        body = {'clusterquota': {
            'cluster_total_loadbalancers': 30,
            'max_healthmonitors_per_pool': 30,
            'max_listeners_per_loadbalancer': 30,
            'max_members_per_pool': 30,
            'max_pools_per_loadbalancer': 30,
            'max_l7policies_per_listener': 30,
            'max_l7rules_per_l7policy': 30}}
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
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
                'roles': ['load-balancer_admin'],
                'user_id': None,
                'is_admin': False,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                self.put(clusterquota_path, body, status=202)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        response = self.get(clusterquota_path)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'],
                                         expected=body['clusterquota'])

    def test_custom_clusterquotas_not_Authorized_member(self):
        clusterquota_path = self.CLUSTERQUOTAS_PATH
        body = {'clusterquota': {
            'cluster_total_loadbalancers': 30,
            'max_healthmonitors_per_pool': 30,
            'max_listeners_per_loadbalancer': 30,
            'max_members_per_pool': 30,
            'max_pools_per_loadbalancer': 30,
            'max_l7policies_per_listener': 30,
            'max_l7rules_per_l7policy': 30}}
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
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
                'roles': ['load-balancer_member'],
                'user_id': None,
                'is_admin': False,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                response = self.put(clusterquota_path, body, status=403)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, response.json)

    def test_custom_partial_clusterquotas(self):
        clusterquota_path = self.CLUSTERQUOTAS_PATH
        body = {'clusterquota': {
            'cluster_total_loadbalancers': 30,
            'max_healthmonitors_per_pool': 30,
            'max_listeners_per_loadbalancer': None,
            'max_members_per_pool': 30,
            'max_pools_per_loadbalancer': 30,
            'max_l7policies_per_listener': 30,
            'max_l7rules_per_l7policy': 30}}
        expected_body = {'clusterquota': {
            'cluster_total_loadbalancers': 30,
            'max_healthmonitors_per_pool': 30,
            'max_listeners_per_loadbalancer':
                CONF.clusterquotas.max_listeners_per_loadbalancer,
            'max_members_per_pool': 30,
            'max_pools_per_loadbalancer': 30,
            'max_l7policies_per_listener': 30,
            'max_l7rules_per_l7policy': 30}}
        self.put(clusterquota_path, body, status=202)
        response = self.get(clusterquota_path)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'],
                                         expected=expected_body['clusterquota']
                                         )

    def test_custom_missing_clusterquotas(self):
        clusterquota_path = self.CLUSTERQUOTAS_PATH
        body = {'clusterquota': {
            'cluster_total_loadbalancers': 30,
            'max_healthmonitors_per_pool': 30,
            'max_members_per_pool': 30,
            'max_pools_per_loadbalancer': 30,
            'max_l7policies_per_listener': 30,
            'max_l7rules_per_l7policy': 30}}
        expected_body = {'clusterquota': {
            'cluster_total_loadbalancers': 30,
            'max_healthmonitors_per_pool': 30,
            'max_listeners_per_loadbalancer':
                CONF.clusterquotas.max_listeners_per_loadbalancer,
            'max_members_per_pool': 30,
            'max_pools_per_loadbalancer': 30,
            'max_l7policies_per_listener': 30,
            'max_l7rules_per_l7policy': 30}}
        self.put(clusterquota_path, body, status=202)
        response = self.get(clusterquota_path)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'],
                                         expected=expected_body['clusterquota']
                                         )

    def test_delete_custom_clusterquotas(self):
        clusterquota_path = self.CLUSTERQUOTAS_PATH
        body = {'clusterquota': {
            'cluster_total_loadbalancers': 30,
            'max_healthmonitors_per_pool': 30,
            'max_listeners_per_loadbalancer': 30,
            'max_members_per_pool': 30,
            'max_pools_per_loadbalancer': 30,
            'max_l7policies_per_listener': 30,
            'max_l7rules_per_l7policy': 30}}
        self.put(clusterquota_path, body, status=202)
        response = self.get(clusterquota_path)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'],
                                         expected=body['clusterquota'])
        self.delete(clusterquota_path, status=202)
        response = self.get(clusterquota_path)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'])

    def test_delete_custom_clusterquotas_admin(self):
        clusterquota_path = self.CLUSTERQUOTAS_PATH
        body = {'clusterquota': {
            'cluster_total_loadbalancers': 30,
            'max_healthmonitors_per_pool': 30,
            'max_listeners_per_loadbalancer': 30,
            'max_members_per_pool': 30,
            'max_pools_per_loadbalancer': 30,
            'max_l7policies_per_listener': 30,
            'max_l7rules_per_l7policy': 30}}
        self.put(clusterquota_path, body, status=202)
        response = self.get(clusterquota_path)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'],
                                         expected=body['clusterquota'])
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
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
                'roles': ['load-balancer_admin'],
                'user_id': None,
                'is_admin': False,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                self.delete(clusterquota_path, status=202)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        response = self.get(clusterquota_path)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'])

    def test_delete_clusterquotas_not_Authorized_member(self):
        clusterquota_path = self.CLUSTERQUOTAS_PATH
        body = {'clusterquota': {
            'cluster_total_loadbalancers': 30,
            'max_healthmonitors_per_pool': 30,
            'max_listeners_per_loadbalancer': 30,
            'max_members_per_pool': 30,
            'max_pools_per_loadbalancer': 30,
            'max_l7policies_per_listener': 30,
            'max_l7rules_per_l7policy': 30}}
        self.put(clusterquota_path, body, status=202)
        response = self.get(clusterquota_path)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'],
                                         expected=body['clusterquota'])
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
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
                'roles': ['load-balancer_member'],
                'user_id': None,
                'is_admin': False,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': self.project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                self.delete(clusterquota_path, status=403)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        response = self.get(clusterquota_path)
        clusterquota_dict = response.json
        self._assert_clusterquotas_equal(clusterquota_dict['clusterquota'],
                                         expected=body['clusterquota'])
