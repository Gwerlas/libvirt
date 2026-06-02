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

| Variable                            | Default                                 | Description                                                                          |
| ----------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------ |
| `libvirt_backends`                  | `[qemu]`                                | List of backends to install                                                          |
| `libvirt_install`                   | `[libvirtd, clients]`                   | Components to install (`libvirtd`, `clients`, `virt-manager`, `gnome-boxes`, `qemu`) |
| `libvirt_users`                     | `[{name: {{ ansible_facts.user_id }}}]` | Users granted libvirt access (see below)                                             |
| `libvirt_retries`                   | `2`                                     | Number of retries for package installation                                           |
| `libvirt_dnsmasq_management_method` | `auto`                                  | DNSMasq management: `auto`, `bind`, `disable`, or `none`                             |
| `libvirt_dnsmasq_interface_types`   | `[ether]`                               | Interface types for DNSMasq to listen on (when method is `bind`)                     |

Each `libvirt_users` entry is a dictionary supporting the following keys :

| Key          | Description                                                                                            |
| ------------ | ------------------------------------------------------------------------------------------------------ |
| `name`       | User name to add to the libvirt/kvm groups                                                             |
| `ca_file`    | Path **on the controller** to the CA certificate, deployed to `~/.pki/cacert.pem`                      |
| `clientcert` | Path **on the controller** to the user client certificate, deployed to `~/.pki/libvirt/clientcert.pem` |
| `clientkey`  | Path **on the controller** to the user client private key, deployed to `~/.pki/libvirt/clientkey.pem`  |

### Configuration

| Variable             | Default   | Description                                                                                       |
| -------------------- | --------- | ------------------------------------------------------------------------------------------------- |
| `libvirt_config`     | _(unset)_ | Per-file directives, as `{ <file>: { directive: value } }`, written to `/etc/libvirt/<file>.conf` |
| `libvirt_ca_file`    | _(unset)_ | Path **on the controller** to the CA certificate to deploy                                        |
| `libvirt_servercert` | _(unset)_ | Path **on the controller** to the server certificate to deploy                                    |
| `libvirt_serverkey`  | _(unset)_ | Path **on the controller** to the server private key to deploy                                    |
| `libvirt_clientcert` | _(unset)_ | Path **on the controller** to the client certificate to deploy                                    |
| `libvirt_clientkey`  | _(unset)_ | Path **on the controller** to the client private key to deploy                                    |

The TLS files are deployed to the standard libvirt locations (see the
[libvirt TLS knowledge base](https://libvirt.org/kbase/tlscerts.html)) :

| Variable             | Destination on the node                  |
| -------------------- | ---------------------------------------- |
| `libvirt_ca_file`    | `/etc/pki/CA/cacert.pem`                 |
| `libvirt_servercert` | `/etc/pki/libvirt/servercert.pem`        |
| `libvirt_serverkey`  | `/etc/pki/libvirt/private/serverkey.pem` |
| `libvirt_clientcert` | `/etc/pki/libvirt/clientcert.pem`        |
| `libvirt_clientkey`  | `/etc/pki/libvirt/private/clientkey.pem` |

The CA and server destinations follow the matching `libvirtd` directives when set
in `libvirt_config` (`ca_file`, `cert_file` and `key_file`), so they stay
consistent with the daemon configuration.

### Firewall

| Variable                  | Default   | Description                                                  |
| ------------------------- | --------- | ------------------------------------------------------------ |
| `libvirt_manage_firewall` | `true`    | Whether to manage firewalld rules                            |
| `libvirt_firewall_zone`   | _(unset)_ | Firewalld zone to use (defaults to firewalld's default zone) |

The `libvirt` and `libvirt-tls` firewalld services (the latter opens the
TLS port `16514/tcp`) are both enabled when `libvirt_manage_firewall` is `true`.

### Provisioning

| Variable                      | Default              | Description                                                              |
| ----------------------------- | -------------------- | ------------------------------------------------------------------------ |
| `libvirt_default_disk_format` | `qcow2`              | Default disk image format for volumes and domains (`qcow2`, `raw`, etc.) |
| `libvirt_default_keymap`      | `en-us`              | Default keymap for VNC graphics                                          |
| `libvirt_default_cpu`         | `{mode: host-model}` | Default CPU configuration for domains                                    |
| `libvirt_pools`               | `[]`                 | List of storage pools to create                                          |

For `netfs` pools, the `source` key supports the following properties:

| Property           | Default          | Description                               |
| ------------------ | ---------------- | ----------------------------------------- |
| `source.host`      |                  | NFS/CIFS server hostname                  |
| `source.dir`       |                  | Exported path on the server               |
| `source.type`      | `nfs`            | Protocol format: `nfs` or `cifs`          |
| `source.protocol`  |                  | NFS protocol version (e.g. `4` for NFSv4) |
| `libvirt_volumes`  | `[]`             | List of storage volumes to create         |
| `libvirt_networks` | `[]`             | List of virtual networks to create        |
| `libvirt_domains`  | `[]`             | List of virtual machines to create        |
| `libvirt_uri`      | `qemu:///system` | Default libvirt connection URI            |

Dependencies
------------

Be sure to have the `community.libvirt >= 2.0` installad on your system,
or present in your `requirements.yml`.

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
          - name: from-nfs4
            type: netfs
            path: /data/images
            source:
              host: hostname
              dir: /server-export
              protocol: 4
          - name: from-cifs
            type: netfs
            path: /data/images
            source:
              host: hostname
              dir: /server-share
              type: cifs
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

Enable TLS on the libvirt daemon, deploying the certificates generated on the
controller (see the [libvirt TLS knowledge base](https://libvirt.org/kbase/tlscerts.html)
to create them) :

```yaml
- name: Libvirt over TLS
  hosts: all
  roles:
    - role: gwerlas.libvirt
      vars:
        # Directives written to /etc/libvirt/libvirtd.conf
        libvirt_config:
          libvirtd:
            listen_tls: 1
            listen_tcp: 0
            tls_no_verify_cert: 0
        # Certificates and keys stored on the Ansible controller
        libvirt_ca_file: files/pki/cacert.pem
        libvirt_servercert: files/pki/servercert.pem
        libvirt_serverkey: files/pki/private/serverkey.pem
        libvirt_clientcert: files/pki/clientcert.pem
        libvirt_clientkey: files/pki/private/clientkey.pem
```

Clients can then reach the daemon over TLS :

```sh
virsh -c qemu://node.example.com/system list
```

Per-user client credentials can also be deployed, so a given user can connect to
a remote daemon over TLS from their own session :

```yaml
- name: Libvirt user TLS access
  hosts: all
  roles:
    - role: gwerlas.libvirt
      vars:
        libvirt_users:
          - name: alice
            ca_file: files/pki/cacert.pem
            clientcert: files/pki/alice/clientcert.pem
            clientkey: files/pki/alice/clientkey.pem
```

The certificates are installed under `alice`'s home (`~/.pki`), letting her reach
a remote host :

```sh
virsh -c qemu://node.example.com/system list
```

The URI carries no `alice@` part : over TLS the identity comes from the client
certificate virsh reads in her home, not from a username (that would only matter
for the SSH transport). The path stays `/system` to reach the remote system
daemon — `/session` is a separate, local per-user daemon.

Limitations
-----------

### Add physical disk to domain

It's only possible to add physical disk to domain in `qemu:///system` connection

License
-------

[BSD 3-Clause License](LICENSE).

