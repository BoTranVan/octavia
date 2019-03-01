#    Copyright 2016 Rackspace
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

"""distributor-data-model

Revision ID: d5cf3da30ed8
Revises: 11e4bb2bb8ef
Create Date: 2017-12-15 16:39:05.765206

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd5cf3da30ed8'
down_revision = '11e4bb2bb8ef'


def upgrade():
    op.create_table(
        u'distributor',
        sa.Column(u'id', sa.String(36), primary_key=True),
        sa.Column(u'name', sa.String(255), nullable=True),
        sa.Column(u'enabled', sa.Boolean, nullable=False),
        sa.Column(u'description', sa.String(255), nullable=True),
        sa.Column(u'frontend_subnet', sa.String(36), nullable=False),
        sa.Column(u'distributor_driver', sa.String(64), nullable=False),
        sa.Column(u'provisioning_status', sa.String(16), nullable=False),
        sa.Column(u'operating_status', sa.String(16), nullable=False),
        sa.Column(u'config_data', sa.String(4096), nullable=True),
        sa.UniqueConstraint(u'name',
                            name=u'uq_distributor_name'))

    op.create_foreign_key(u'fk_distributor_provisioning_status_name',
                          u'distributor', u'provisioning_status',
                          [u'provisioning_status'], [u'name'])

    op.create_foreign_key(u'fk_distributor_operating_status_name',
                          u'distributor', u'operating_status',
                          [u'operating_status'], [u'name'])

    op.add_column(
        u'amphora',
        sa.Column(u'frontend_ip', sa.String(64), nullable=True))
    op.add_column(
        u'amphora',
        sa.Column(u'frontend_port_id', sa.String(36), nullable=True))
    op.add_column(
        u'amphora',
        sa.Column(u'frontend_interface', sa.String(16), nullable=True))

    op.add_column(
        u'load_balancer',
        sa.Column(u'distributor_id', sa.String(36), nullable=True))

    op.create_foreign_key(u'fk_load_balancer_distributor_id', u'load_balancer',
                          u'distributor', [u'distributor_id'], [u'id'])
