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

import mock

from oslo_utils import uuidutils

from oslo_config import cfg
from oslo_config import fixture as oslo_fixture

from octavia.common import constants
import octavia.common.context
from octavia.db import api as db_api
from octavia.tests.functional.api.v2 import base


class TestDistributor(base.BaseAPITest):
    root_tag = 'distributor'
    root_tag_list = 'distributors'
    root_tag_links = 'distributors_links'

    def setUp(self):
        super(TestDistributor, self).setUp()

    def _assert_request_matches_response(self, req, resp, **optionals):
        self.assertTrue(uuidutils.is_uuid_like(resp.get('id')))
        req_description = req.get('description')
        self.assertEqual(req.get('name'), resp.get('name'))
        if not req_description:
            self.assertEqual('', resp.get('description'))
        else:
            self.assertEqual(req.get('description'), resp.get('description'))
        self.assertEqual(req.get('distributor_driver'),
                         resp.get('distributor_driver'))
        self.assertEqual(req.get('frontend_subnet'),
                         resp.get('frontend_subnet'))
        self.assertEqual(req.get('config_data'), resp.get('config_data'))
        self.assertEqual(constants.PENDING_CREATE,
                         resp.get('provisioning_status'))
        self.assertEqual(constants.OFFLINE, resp.get('operating_status'))
        self.assertEqual(req.get('admin_state_up', True),
                         resp.get('admin_state_up'))
        for key, value in optionals.items():
            self.assertEqual(value, req.get(key))

    def test_empty_list(self):
        response = self.get(self.DISTRIBUTORS_PATH)
        api_list = response.json.get(self.root_tag_list)
        self.assertEqual([], api_list)

    def test_create(self, **optionals):
        distributor_json = {
            'name': 'test1',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        distributor_json.update(optionals)
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body)
        api_distributor = response.json.get(self.root_tag)
        self._assert_request_matches_response(distributor_json,
                                              api_distributor)
        return api_distributor

    def test_create_with_invalid_driver(self):
        distributor_json = {
            'name': 'test2',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'fake_noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body, status=400)
        err_msg = ("fake_noop is not a valid option for distributor_driver")
        self.assertEqual(err_msg, response.json.get('faultstring'))

    def test_create_with_missing_name(self):
        distributor_json = {
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body, status=400)
        err_msg = ("Invalid input for field/attribute name. Value: "
                   "'None'. Mandatory field missing.")
        self.assertEqual(err_msg, response.json.get('faultstring'))

    def test_create_with_missing_frontend_subnet(self):
        distributor_json = {
            'name': 'test1',
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body, status=400)
        err_msg = ("Invalid input for field/attribute frontend_subnet. Value: "
                   "'None'. Mandatory field missing.")
        self.assertEqual(err_msg, response.json.get('faultstring'))

    def test_create_with_missing_distributor_driver(self):
        distributor_json = {
            'name': 'test1',
            'frontend_subnet': uuidutils.generate_uuid(),
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body, status=400)
        err_msg = ("Invalid input for field/attribute distributor_driver. "
                   "Value: 'None'. Mandatory field missing.")
        self.assertEqual(err_msg, response.json.get('faultstring'))

    def test_create_with_missing_config_data(self):
        distributor_json = {
            'name': 'test1',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body, status=400)
        err_msg = ("Invalid input for field/attribute config_data. Value: "
                   "'None'. Mandatory field missing.")
        self.assertEqual(err_msg, response.json.get('faultstring'))

    def test_create_with_long_name(self):
        distributor_json = {
            'name': 'n' * 256,
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        self.post(self.DISTRIBUTORS_PATH, body, status=400)

    def test_create_with_long_description(self):
        distributor_json = {
            'name': 'test-distributor',
            'description': 'n' * 256,
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        self.post(self.DISTRIBUTORS_PATH, body, status=400)

    def test_create_duplicate_names(self):
        distributor1 = self.create_distributor(
            'name', 'noop', uuidutils.generate_uuid(), '{}')
        self.assertTrue(uuidutils.is_uuid_like(distributor1.get('id')))
        distributor_json = {
            'name': 'name',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body, status=409)
        err_msg = "A distributor of name already exists."
        self.assertEqual(err_msg, response.json.get('faultstring'))

    def test_create_authorized(self):
        distributor_json = {
            'name': 'test1',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        project_id = uuidutils.generate_uuid()
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               project_id):
            override_credentials = {
                'service_user_id': None,
                'user_domain_id': None,
                'is_admin_project': True,
                'service_project_domain_id': None,
                'service_project_id': None,
                'roles': ['load-balancer_member'],
                'user_id': None,
                'is_admin': True,
                'service_user_domain_id': None,
                'project_domain_id': None,
                'service_roles': [],
                'project_id': project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                response = self.post(self.DISTRIBUTORS_PATH, body)
        api_flavor = response.json.get(self.root_tag)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self._assert_request_matches_response(distributor_json, api_flavor)

    def test_create_not_authorized(self):
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        distributor_json = {
            'name': 'test1',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body, status=403)
        api_flavor = response.json
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, api_flavor)

    def test_get(self):
        distributor = self.create_distributor(
            'name', 'noop', uuidutils.generate_uuid(), '{}')
        self.assertTrue(uuidutils.is_uuid_like(distributor.get('id')))
        response = self.get(
            self.DISTRIBUTOR_PATH.format(
                distributor_id=distributor.get('id'))).json.get(self.root_tag)
        self.assertEqual('name', response.get('name'))
        self.assertEqual(distributor.get('frontend_subnet'),
                         response.get('frontend_subnet'))
        self.assertEqual(distributor.get('distributor_driver'),
                         response.get('distributor_driver'))
        self.assertEqual(distributor.get('config_data'),
                         response.get('config_data'))
        self.assertTrue(response.get('admin_state_up'))

    def test_get_one_fields_filter(self):
        distributor = self.create_distributor(
            'name', 'noop', uuidutils.generate_uuid(), '{}')
        self.assertTrue(uuidutils.is_uuid_like(distributor.get('id')))
        response = self.get(
            self.DISTRIBUTOR_PATH.format(
                distributor_id=distributor.get('id')),
            params={
                'fields': ['id', 'frontend_subnet']}).json.get(self.root_tag)
        self.assertEqual(distributor.get('id'), response.get('id'))
        self.assertEqual(distributor.get('frontend_subnet'),
                         response.get('frontend_subnet'))
        self.assertIn(u'id', response)
        self.assertIn(u'frontend_subnet', response)
        self.assertNotIn(u'name', response)
        self.assertNotIn(u'description', response)
        self.assertNotIn(u'distributor_drvier', response)

    def test_get_authorized(self):
        distributor = self.create_distributor(
            'name', 'noop', uuidutils.generate_uuid(), '{}')
        self.assertTrue(uuidutils.is_uuid_like(distributor.get('id')))

        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        project_id = uuidutils.generate_uuid()
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               project_id):
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
                'project_id': project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                response = self.get(
                    self.DISTRIBUTOR_PATH.format(
                        distributor_id=distributor.get(
                            'id'))).json.get(self.root_tag)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual('name', response.get('name'))
        self.assertEqual('', response.get('description'))
        self.assertEqual(distributor.get('id'), response.get('id'))
        self.assertEqual(distributor.get('frontend_subnet'),
                         response.get('frontend_subnet'))
        self.assertEqual(distributor.get('distributor_driver'),
                         response.get('distributor_driver'))
        self.assertEqual(distributor.get('config_data'),
                         response.get('config_data'))
        self.assertTrue(response.get('admin_state_up'))

    def test_get_not_authorized(self):
        distributor = self.create_distributor(
            'name', 'noop', uuidutils.generate_uuid(), '{}')
        self.assertTrue(uuidutils.is_uuid_like(distributor.get('id')))
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        response = self.get(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor.get('id')), status=403).json
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, response)

    def test_get_all(self):
        distributor1 = self.create_distributor(
            'name1', 'noop', 'd21bf20d-c323-4004-bf67-f90591ceced9',
            '{}', **{u'description': u'description'})
        self.assertTrue(uuidutils.is_uuid_like(distributor1.get('id')))
        ref_distributor_1 = {
            u'description': u'description', u'admin_state_up': True,
            u'frontend_subnet': u'd21bf20d-c323-4004-bf67-f90591ceced9',
            u'id': distributor1.get('id'), u'config_data': u'{}',
            u'provisioning_status': u'PENDING_CREATE',
            u'operating_status': u'OFFLINE',
            u'distributor_driver': 'noop', u'name': u'name1'}
        distributor2 = self.create_distributor(
            'name2', 'noop', '2a1bf24c-6b23-8a04-5b67-f90591cece10', '{}')
        self.assertTrue(uuidutils.is_uuid_like(distributor2.get('id')))
        ref_distributor_2 = {
            u'provisioning_status': u'PENDING_CREATE',
            u'distributor_driver': u'noop', u'config_data': u'{}',
            u'frontend_subnet': u'2a1bf24c-6b23-8a04-5b67-f90591cece10',
            u'name': u'name2', u'operating_status': u'OFFLINE',
            u'description': u'', u'admin_state_up': True,
            u'id': distributor2.get('id')}
        response = self.get(self.DISTRIBUTORS_PATH)
        api_list = response.json.get(self.root_tag_list)
        self.assertEqual(2, len(api_list))
        self.assertIn(ref_distributor_1, api_list)
        self.assertIn(ref_distributor_2, api_list)

    def test_get_all_fields_filter(self):
        distributor1 = self.create_distributor(
            'name1', 'noop', 'd21bf20d-c323-4004-bf67-f90591ceced9',
            '{}', **{u'description': u'description'})
        self.assertTrue(uuidutils.is_uuid_like(distributor1.get('id')))
        distributor2 = self.create_distributor(
            'name2', 'noop', '2a1bf24c-6b23-8a04-5b67-f90591cece10', '{}')
        self.assertTrue(uuidutils.is_uuid_like(distributor2.get('id')))
        response = self.get(self.DISTRIBUTORS_PATH, params={
            'fields': ['id', 'name']})
        api_list = response.json.get(self.root_tag_list)
        self.assertEqual(2, len(api_list))
        for distributor in api_list:
            self.assertIn(u'id', distributor)
            self.assertIn(u'name', distributor)
            self.assertNotIn(u'frontend_subnet', distributor)
            self.assertNotIn(u'distributor_driver', distributor)
            self.assertNotIn(u'admin_state_up', distributor)

    def test_get_all_authorized(self):
        distributor1 = self.create_distributor(
            'name1', 'noop', 'd21bf20d-c323-4004-bf67-f90591ceced9',
            '{}', **{u'description': u'description'})
        self.assertTrue(uuidutils.is_uuid_like(distributor1.get('id')))
        distributor2 = self.create_distributor(
            'name2', 'noop', '2a1bf24c-6b23-8a04-5b67-f90591cece10', '{}')
        self.assertTrue(uuidutils.is_uuid_like(distributor2.get('id')))
        response = self.get(self.DISTRIBUTORS_PATH)

        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        project_id = uuidutils.generate_uuid()
        with mock.patch.object(octavia.common.context.Context, 'project_id',
                               project_id):
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
                'project_id': project_id}
            with mock.patch(
                    "oslo_context.context.RequestContext.to_policy_values",
                    return_value=override_credentials):
                api_list = response.json.get(self.root_tag_list)
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(2, len(api_list))

    def test_get_all_not_authorized(self):
        distributor1 = self.create_distributor(
            'name1', 'noop', 'd21bf20d-c323-4004-bf67-f90591ceced9',
            '{}', **{u'description': u'description'})
        self.assertTrue(uuidutils.is_uuid_like(distributor1.get('id')))
        distributor2 = self.create_distributor(
            'name2', 'noop', '2a1bf24c-6b23-8a04-5b67-f90591cece10', '{}')
        self.assertTrue(uuidutils.is_uuid_like(distributor2.get('id')))
        self.conf = self.useFixture(oslo_fixture.Config(cfg.CONF))
        auth_strategy = self.conf.conf.api_settings.get('auth_strategy')
        self.conf.config(group='api_settings', auth_strategy=constants.TESTING)
        response = self.get(self.DISTRIBUTORS_PATH, status=403).json
        self.conf.config(group='api_settings', auth_strategy=auth_strategy)
        self.assertEqual(self.NOT_AUTHORIZED_BODY, response)

    def test_update(self):
        distributor_json = {
            'name': 'test1',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body)
        api_distributor = response.json.get(self.root_tag)
        distributor_id = api_distributor.get('id')
        self._assert_request_matches_response(distributor_json,
                                              api_distributor)
        self.set_object_status(self.distributor_repo, distributor_id)

        distributor_json = {
            'name': 'test2',
            'description': "desc test2"}
        body = self._build_body(distributor_json)
        response = self.put(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor_id), body)
        updated_distributor = self.get(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor_id)).json.get(self.root_tag)

        self.assertEqual('test2', updated_distributor['name'])
        self.assertEqual('desc test2', updated_distributor['description'])
        self.assertEqual(distributor_id, updated_distributor['id'])

    def test_update_with_config_data(self):
        distributor_json = {
            'name': 'test1',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body)
        api_distributor = response.json.get(self.root_tag)
        distributor_id = api_distributor.get('id')
        self._assert_request_matches_response(distributor_json,
                                              api_distributor)
        self.set_object_status(self.distributor_repo, distributor_id)

        distributor_json = {
            'config_data': '{"aaa": "bbb"}'}
        body = self._build_body(distributor_json)
        response = self.put(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor_id), body)
        updated_distributor = self.get(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor_id)).json.get(self.root_tag)
        self.assertEqual('{"aaa": "bbb"}', updated_distributor['config_data'])

        project_id = uuidutils.generate_uuid()
        lb = self.create_load_balancer(uuidutils.generate_uuid(),
                                       name='lb1',
                                       project_id=project_id,
                                       description='desc1',
                                       admin_state_up=True)
        lb_dict = lb.get('loadbalancer')
        self.lb_repo.update(db_api.get_session(),
                            lb_dict['id'],
                            distributor_id=distributor_id)

        distributor_json = {
            'config_data': '{"aaa": "111"}'}
        body = self._build_body(distributor_json)
        response = self.put(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor_id), body, status=409)
        err_msg = ("'config_data' cannot be updated, "
                   "because the distributor is in use.")
        self.assertEqual(err_msg, response.json.get('faultstring'))

    def test_delete(self):
        distributor_json = {
            'name': 'test1',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body)
        api_distributor = response.json.get(self.root_tag)
        distributor_id = api_distributor.get('id')
        self._assert_request_matches_response(distributor_json,
                                              api_distributor)
        self.set_object_status(self.distributor_repo, distributor_id)
        self.delete(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor_id))

        response = self.get(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor_id))
        api_distributor = response.json.get(self.root_tag)
        self.assertEqual('PENDING_DELETE',
                         api_distributor.get('provisioning_status'))

    def test_delete_already_deleted(self):
        distributor_json = {
            'name': 'test1',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body)
        api_distributor = response.json.get(self.root_tag)
        distributor_id = api_distributor.get('id')
        self._assert_request_matches_response(distributor_json,
                                              api_distributor)
        self.set_object_status(self.distributor_repo,
                               distributor_id,
                               provisioning_status='DELETED')
        response = self.get(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor_id))
        self.delete(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor_id), status=404)

    def test_delete_in_use(self):
        distributor_json = {
            'name': 'test1',
            'frontend_subnet': uuidutils.generate_uuid(),
            'distributor_driver': 'noop',
            'config_data': '{}'}
        body = self._build_body(distributor_json)
        response = self.post(self.DISTRIBUTORS_PATH, body)
        api_distributor = response.json.get(self.root_tag)
        distributor_id = api_distributor.get('id')
        self._assert_request_matches_response(distributor_json,
                                              api_distributor)
        self.set_object_status(self.distributor_repo, distributor_id)

        project_id = uuidutils.generate_uuid()
        lb = self.create_load_balancer(uuidutils.generate_uuid(),
                                       name='lb1',
                                       project_id=project_id,
                                       description='desc1',
                                       admin_state_up=True)
        lb_dict = lb.get('loadbalancer')
        self.lb_repo.update(db_api.get_session(),
                            lb_dict['id'],
                            distributor_id=distributor_id)

        self.delete(self.DISTRIBUTOR_PATH.format(
            distributor_id=distributor_id), status=409)
