Libvirt
======

[![pipeline status](https://gitlab.com/yoanncolin/ansible/roles/libvirt/badges/main/pipeline.svg)](https://gitlab.com/yoanncolin/ansible/roles/libvirt/-/commits/main)

Install, configure and provision libvirt resources.

GitLab project: [yoanncolin/ansible/roles/libvirt](https://gitlab.com/yoanncolin/ansible/roles/libvirt)

Requirements
------------

The Linux base system configured with:

- SSH
- Python (for Ansible)
- Sudo
- Package manager ready to use

The `gwerlas.system` role can help You:

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

Defined facts of this role:

- `libvirt_packages`

You can get the facts only, without doing any changes on your nodes:

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

You can filter on some specific tasks using this tags:

- `provision`: Provision resources only
- `users`: Set users environment and permissions
- `ca`: Redeploy the CA certificate and restart the daemon to apply it
- `ssl`: Redeploy the server/client certificates and restart the daemon to apply them

Role Variables
--------------

### Installation

| Variable                            | Default                                 | Description                                                                          |
| ----------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------ |
| `libvirt_backends`                  | `[qemu]`                                | List of backends to install                                                          |
| `libvirt_install`                   | `[libvirtd, clients]`                   | Components to install (`libvirtd`, `clients`, `virt-manager`, `gnome-boxes`, `qemu`) |
| `libvirt_users`                     | `[{name: {{ ansible_facts.user_id }}}]` | Users granted libvirt access (see [users][])                                         |
| `libvirt_retries`                   | `2`                                     | Number of retries for package installation                                           |
| `libvirt_dnsmasq_management_method` | `auto`                                  | DNSMasq management: `auto`, `bind`, `disable`, or `none`                             |
| `libvirt_dnsmasq_interface_types`   | `[ether]`                               | Interface types for DNSMasq to listen on (when method is `bind`)                     |

### Configuration

| Variable         | Default   | Description                                                                                       |
| ---------------- | --------- | ------------------------------------------------------------------------------------------------- |
| `libvirt_config` | _(unset)_ | Per-file directives, as `{ <file>: { directive: value } }`, written to `/etc/libvirt/<file>.conf` |

Enabling TLS on the daemon (certificates, socket, per-user access, rotation) is
covered in the [TLS][] guide, and the firewalld rules in the [firewall][] one.

### Provisioning

| Variable                         | Default                                    | Description                                             |
| -------------------------------- | ------------------------------------------ | ------------------------------------------------------- |
| `libvirt_pools`                  | `[]`                                       | List of storage pools to create (see [pools][])         |
| `libvirt_volumes`                | `[]`                                       | List of storage volumes to create (see [volumes][])     |
| `libvirt_networks`               | `[]`                                       | List of virtual networks to create (see [networks][])   |
| `libvirt_domains`                | `[]`                                       | List of virtual machines to create (see [domains][])    |
| `libvirt_default_disk_format`    | `qcow2`                                    | Default disk image format for volumes and domains       |
| `libvirt_default_keymap`         | `en-us`                                    | Default keymap for VNC graphics                         |
| `libvirt_default_cpu`            | `{mode: host-model}`                       | Default CPU configuration for domains                   |
| `libvirt_uri`                    | `qemu:///system`                           | Default libvirt connection URI                          |
| `libvirt_remove_default_network` | `false`                                    | Remove libvirt's `default` network                      |
| `libvirt_active_default_network` | `{{ not libvirt_remove_default_network }}` | Keep libvirt's `default` network active                 |

Documentation
-------------

- [TLS][] — enable TLS, deploy certificates, per-user access, rotation
- [Live migration][migration] — migrate running domains between hosts
- [Firewall][] — firewalld rules and ports
- [Users][] — grant users libvirt access
- [Pools][], [Volumes][], [Networks][] and [Domains][] — provisioning resources

Upgrading to 0.7.0
------------------

`0.7.0` reworks the provisioning variables (`libvirt_pools`, `libvirt_networks`
and `libvirt_domains`) to mirror libvirt's own XML structure. Existing
inventories from `0.6.x` must be migrated as follows:

| Resource | `0.6.x`                  | `0.7.0`                             |
| -------- | ------------------------ | ----------------------------------- |
| Networks | `forward_mode: nat`      | `forward: {mode: nat}`              |
| Networks | `bridge: virbr0`         | `bridge: {name: virbr0}`            |
| Networks | `ip: {address, netmask}` | `ips: [{address, netmask}]`         |
| Networks | `ip.dhcp: {start, end}`  | `ips[].dhcp.ranges: [{start, end}]` |
| Pools    | `path: …`                | `target: {path: …}`                 |
| Pools    | `owner`, `group`, `mode` | moved under `target.permissions`    |
| Pools    | `source.host: server`    | `source.hosts: [{name: server}]`    |
| Pools    | `source.dir: /export`    | `source.dir: {path: /export}`       |
| Pools    | `source.type: nfs`       | `source.format: {type: nfs}`        |
| Pools    | `source.protocol: 4`     | `source.protocol: {ver: 4}`         |
| Volumes  | `size: 200G`             | `capacity: 200G`                    |
| Volumes  | `format: qcow2`          | `target: {format: {type: qcow2}}`   |
| Domains  | `disks[].size: 2G`       | `disks[].capacity: 2G`              |
| Domains  | `networks: [...]`        | `interfaces: [...]`                 |

Dependencies
------------

Be sure to have the `community.libvirt >= 2.0` installad on your system,
or present in your `requirements.yml`.

Example Playbook
----------------

Install and configure libvirt on a node:

```yaml
- name: Libvirt
  hosts: all
  roles:
    - name: gwerlas.libvirt
```

Provisioning resources, enabling TLS and live-migrating domains are covered in the
[documentation](#documentation) above.

Limitations
-----------

### Add physical disk to domain

It's only possible to add physical disk to domain in `qemu:///system` connection

License
-------

[BSD 3-Clause License](LICENSE).

<!-- Documentation links -->
[TLS]: https://gitlab.com/yoanncolin/ansible/roles/libvirt/-/blob/main/docs/tls.md
[migration]: https://gitlab.com/yoanncolin/ansible/roles/libvirt/-/blob/main/docs/migration.md
[firewall]: https://gitlab.com/yoanncolin/ansible/roles/libvirt/-/blob/main/docs/firewall.md
[users]: https://gitlab.com/yoanncolin/ansible/roles/libvirt/-/blob/main/docs/users.md
[pools]: https://gitlab.com/yoanncolin/ansible/roles/libvirt/-/blob/main/docs/pools.md
[volumes]: https://gitlab.com/yoanncolin/ansible/roles/libvirt/-/blob/main/docs/volumes.md
[networks]: https://gitlab.com/yoanncolin/ansible/roles/libvirt/-/blob/main/docs/networks.md
[domains]: https://gitlab.com/yoanncolin/ansible/roles/libvirt/-/blob/main/docs/domains.md
