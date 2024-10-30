Libvirt
======

[![pipeline status](https://gitlab.com/yoanncolin/ansible/roles/libvirt/badges/main/pipeline.svg)](https://gitlab.com/yoanncolin/ansible/roles/libvirt/-/commits/main)

Install, configure and provision libvirt resources.

GitLab project : [yoanncolin/ansible/roles/libvirt](https://gitlab.com/yoanncolin/ansible/roles/libvirt)

Requirements
------------

The Linux base system configured with :

- SSH
- Python (for Ansible)
- Sudo
- Package manager ready to use
- EPEL installed for EL7 distros

The `gwerlas.system` role can help You :

```sh
ansible-galaxy install gwerlas.system
```

```yaml
- name: My playbook
  hosts: all
  roles:
    - role: gwerlas.system
    - role: gwerlas.libvirt
```

Facts
-----

Defined facts of this role :

- `libvirt_packages`

You can get the facts only, without doing any changes on your nodes :

```yaml
- name: My playbook
  hosts: all
  tasks:
    - name: Get facts
      ansible.builtin.import_role:
        name: gwerlas.libvirt
        tasks_from: facts

    - name: Display
      ansible.builtin.debug:
        var: libvirt_packages
```

Tags
----

You can filter on some specific tasks using this tags :

- `provision` : Provision resources only
- `users` : Set users environment and permissions

Role Variables
--------------

Available variables are listed below, along with default values
(see `defaults/main/*.yml`):

Dependencies
------------

Be sure to have the `community.libvirt` installad on your system, or present
in your `requirements.yml`.

Example Playbook
----------------

An exemple of the way to install and configure libvirt on a node :

```yaml
- name: Libvirt
  hosts: all
  roles:
    - name: gwerlas.libvirt
```

Provision some resources :

```yaml
- name: Libvirt
  hosts: all
  tasks:
    - name: Just provision some resources
  tasks:
    - name: Just provision some resources
      ansible.builtin.import_role:
        name: gwerlas.libvirt
        tasks_from: provision
      vars:
        libvirt_networks:
          - name: my-bridge
            forward:
              mode: bridge
            bridge:
              name: br0
          - name: my-nat
            bridge:
              name: br1
            ip:
              address: 192.168.0.1
              netmask: 255.255.255.0
              dhcp:
                start: 192.168.0.2
                end: 192.168.0.254
        libvirt_pools:
          - name: local-dir
            path: /data/images
          - name: from-nfs
            type: netfs
            path: /data/images
            source:
              host: hostname
              dir: /server-export
        libvirt_domains:
          - name: my-node
            autostart: false
            cpu:
              mode: host-passthrough
              model:
                fallback: allow
            memory: 4G
            networks:
              - name: my-bridge
              - name: my-nat
            vcpu:
              placement: static
              quantity: 2
            volumes:
              - name: os
              - name: data
                size: 200G
                device: vdb
                pool: data-dir
```

License
-------

[BSD 3-Clause License](LICENSE).

