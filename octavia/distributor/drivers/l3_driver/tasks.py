# Copyright (c) 2018 China Telecom Corporation
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

from taskflow import task

from octavia.controller.worker.tasks import amphora_driver_tasks


class BaseL3DistributorTask(task.Task):
    """Base task to l3 distributor common to the tasks"""

    def __init__(self, **kwargs):
        super(BaseL3DistributorTask, self).__init__(**kwargs)


class CreateDistributorTask(BaseL3DistributorTask):
    """Create a l3 distributor in ToR"""

    def execute(self, distributor):
        pass


class UpdateDistributorTask(BaseL3DistributorTask):
    """Update a l3 distributor in ToR"""

    def execute(self, distributor):
        pass


class DeleteDistributorTask(BaseL3DistributorTask):
    """Delete a l3 distributor in ToR"""

    def execute(self, distributor):
        pass


class UploadBgpConfig(amphora_driver_tasks.BaseAmphoraTask):

    def execute(self, distributor, loadbalancer):
        self.amphora_driver.update_bgp_conf(loadbalancer, distributor)


class StartBbgSpeaker(amphora_driver_tasks.BaseAmphoraTask):

    def execute(self, loadbalancer):
        self.amphora_driver.start_bgp_service(loadbalancer)


class RegisterAmphoraTask(amphora_driver_tasks.BaseAmphoraTask):
    """Register a amphora to a specified distributor."""

    def execute(self, loadbalancer):
        self.amphora_driver.register_to_distributor(loadbalancer)


class UnregisterAmphoraTask(amphora_driver_tasks.BaseAmphoraTask):
    """Ungister a amphora from a specified distributor"""

    def execute(self, distributor, amphora):
        pass


class DrainAmphoraTask(amphora_driver_tasks.BaseAmphoraTask):
    """Ungister all amphora of a specified distributor"""

    def execute(self, distributor):
        pass
