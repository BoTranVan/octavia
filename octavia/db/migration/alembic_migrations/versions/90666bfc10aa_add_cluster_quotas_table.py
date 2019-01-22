#    Copyright 2017 Walmart Stores Inc.
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

"""add cluster_quotas table

Revision ID: 90666bfc10aa
Revises: 32e5c35b26a8
Create Date: 2019-01-18 10:54:25.493550

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '90666bfc10aa'
down_revision = '4f65b4f91c39'


def upgrade():

    op.create_table(
        u'cluster_quotas',
        sa.Column(u'id', sa.String(36), nullable=False),
        sa.Column(u'cluster_total_loadbalancers', sa.Integer(), nullable=True),
        sa.Column(u'max_healthmonitors_per_pool', sa.Integer(), nullable=True),
        sa.Column(u'max_listeners_per_loadbalancer',
                  sa.Integer(), nullable=True),
        sa.Column(u'max_members_per_pool', sa.Integer(), nullable=True),
        sa.Column(u'max_pools_per_loadbalancer', sa.Integer(), nullable=True),
        sa.Column(u'max_l7policies_per_listener', sa.Integer(), nullable=True),
        sa.Column(u'max_l7rules_per_l7policy', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint(u'id')
    )
