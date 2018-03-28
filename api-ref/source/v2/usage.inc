.. -*- rst -*-

Show All Usage
==============

.. rest_method:: GET /v2.0/lbaas/usage

Show all usage for Octavia.

This function is typically available only to administrators.

.. rest_status_code:: success ../http-status.yaml

   - 200

.. rest_status_code:: error ../http-status.yaml

   - 401
   - 500

Request
-------

Curl Example
------------

.. literalinclude:: examples/usage-show-all-curl
   :language: bash

Response Parameters
-------------------

.. rest_parameters:: ../parameters.yaml

   - healthmonitors: usage-healthmonitors
   - l7policies: usage-l7policies
   - l7rules: usage-l7rules
   - listeners: usage-listeners
   - loadbalancers: usage-loadbalancers
   - members: usage-members
   - pools: usage-pools

Response Example
----------------

.. literalinclude:: examples/usage-show-all-response.json
   :language: javascript

Show Project Usage
==================

.. rest_method:: GET /v2.0/lbaas/usage/{project_id}

Show the usage of a project.

This function is typically available only to administrators.

.. rest_status_code:: success ../http-status.yaml

   - 200

.. rest_status_code:: error ../http-status.yaml

   - 401
   - 500

Request
-------

.. rest_parameters:: ../parameters.yaml

   - project_id: path-project-id

Curl Example
------------

.. literalinclude:: examples/usage-show-curl
   :language: bash

Response Parameters
-------------------

.. rest_parameters:: ../parameters.yaml

   - healthmonitors: usage-healthmonitors
   - l7policies: usage-l7policies
   - l7rules: usage-l7rules
   - listeners: usage-listeners
   - loadbalancers: usage-loadbalancers
   - members: usage-members
   - pools: usage-pools

Response Example
----------------

.. literalinclude:: examples/usage-show-response.json
   :language: javascript
