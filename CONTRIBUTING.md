Development guide
=================

This role should not need any external settings to work.

Requirements
------------

Install and configure :

* docker
* molecule
* molecule-docker

Supporting a new distribution / version
---------------------------------------

To add support to a new distribution / version, You can define some defaults if its
packages does not work out of the box.

Use the files in the `vars` directory to do it.

Run tests
---------

```sh
molecule test
```

Develop / Debug
---------------

```sh
molecule create
molecule converge
molecule login -h <instance_name>
# Do your changes by hand
molecule verify
```

Submit your changes
-------------------

Merge request in Gitlab.
