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

### Installation

| Variable                            | Default                         | Description                                                                          |
| ----------------------------------- | ------------------------------- | ------------------------------------------------------------------------------------ |
| `libvirt_backends`                  | `[qemu]`                        | List of backends to install                                                          |
| `libvirt_install`                   | `[libvirtd, clients]`           | Components to install (`libvirtd`, `clients`, `virt-manager`, `gnome-boxes`, `qemu`) |
| `libvirt_users`                     | `[{{ ansible_facts.user_id }}]` | Users to add to libvirt/kvm groups                                                   |
| `libvirt_retries`                   | `2`                             | Number of retries for package installation                                           |
| `libvirt_dnsmasq_management_method` | `auto`                          | DNSMasq management: `auto`, `bind`, `disable`, or `none`                             |
| `libvirt_dnsmasq_interface_types`   | `[ether]`                       | Interface types for DNSMasq to listen on (when method is `bind`)                     |

### Firewall

| Variable                  | Default   | Description                                                  |
| ------------------------- | --------- | ------------------------------------------------------------ |
| `libvirt_manage_firewall` | `true`    | Whether to manage firewalld rules                            |
| `libvirt_firewall_zone`   | _(unset)_ | Firewalld zone to use (defaults to firewalld's default zone) |

### Provisioning

| Variable                      | Default              | Description                                                              |
| ----------------------------- | -------------------- | ------------------------------------------------------------------------ |
| `libvirt_default_disk_format` | `qcow2`              | Default disk image format for volumes and domains (`qcow2`, `raw`, etc.) |
| `libvirt_default_keymap`      | `en-us`              | Default keymap for VNC graphics                                          |
| `libvirt_default_cpu`         | `{mode: host-model}` | Default CPU configuration for domains                                    |
| `libvirt_pools`               | `[]`                 | List of storage pools to create                                          |
| `libvirt_volumes`             | `[]`                 | List of storage volumes to create                                        |
| `libvirt_networks`            | `[]`                 | List of virtual networks to create                                       |
| `libvirt_domains`             | `[]`                 | List of virtual machines to create                                       |
| `libvirt_uri`                 | `qemu:///system`     | Default libvirt connection URI                                           |

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
            disks:
              - name: os
              - name: data
                size: 200G
                target: vdb
                pool: data-dir
              - name: data-2
                format: raw
                source: /dev/vdb
                target: vdb
                type: block
```

Limitations
-----------

### Add physical disk to domain

It's only possible to add physical disk to domain in `qemu:///system` connection

License
-------

[BSD 3-Clause License](LICENSE).

