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
The migration data port range `49152-49215/tcp` is opened as well, so live
migration between hosts works without further tuning.

### Provisioning

| Variable                         | Default                                    | Description                                                               |
| -------------------------------- | ------------------------------------------ | ------------------------------------------------------------------------- |
| `libvirt_pools`                  | `[]`                                       | List of storage pools to create (see [items](#libvirt_pools-items))       |
| `libvirt_volumes`                | `[]`                                       | List of storage volumes to create (see [items](#libvirt_volumes-items))   |
| `libvirt_networks`               | `[]`                                       | List of virtual networks to create (see [items](#libvirt_networks-items)) |
| `libvirt_domains`                | `[]`                                       | List of virtual machines to create (see [items](#libvirt_domains-items))  |
| `libvirt_default_disk_format`    | `qcow2`                                    | Default disk image format for volumes and domains (`qcow2`, `raw`, etc.)  |
| `libvirt_default_keymap`         | `en-us`                                    | Default keymap for VNC graphics                                           |
| `libvirt_default_cpu`            | `{mode: host-model}`                       | Default CPU configuration for domains                                     |
| `libvirt_uri`                    | `qemu:///system`                           | Default libvirt connection URI                                            |
| `libvirt_remove_default_network` | `false`                                    | Remove libvirt's `default` network                                        |
| `libvirt_active_default_network` | `{{ not libvirt_remove_default_network }}` | Keep libvirt's `default` network active                                   |

The `libvirt_pools`, `libvirt_volumes`, `libvirt_networks` and `libvirt_domains`
variables each take a list of dictionaries. The keys accepted by those list items
are described below.

#### `libvirt_pools` items

| Key         | Default                                  | Description                                                             |
| ----------- | ---------------------------------------- | ----------------------------------------------------------------------- |
| `name`      |                                          | Pool name                                                               |
| `type`      | `netfs` when `source` is set, else `dir` | Pool type (`dir`, `fs`, `netfs`, `logical`, ...)                        |
| `target`    |                                          | Target definition, with a `path` and optional `permissions` (see below) |
| `source`    |                                          | Source definition for `netfs` pools (see below)                         |
| `autostart` |                                          | Start the pool at boot                                                  |
| `state`     | `active`                                 | Desired pool state (`active`, `present`, `absent`)                      |

The `target` key holds the pool location and its permissions:

| Key                 | Default                         | Description                 |
| ------------------- | ------------------------------- | --------------------------- |
| `path`              |                                 | Filesystem path of the pool |
| `permissions.mode`  | `0771` (system) / `0711` (user) | Permissions of the path     |
| `permissions.owner` | qemu user / current user        | Owner of the path           |
| `permissions.group` | owner's primary group           | Group of the path           |

For a system-wide connection (`qemu:///system`), the VMs run as a dedicated
qemu user. When a pool `path` lives under a user's home (e.g.
`/home/alice/.local/share/vms`), that user is granted ownership of the pool, but
the qemu user still cannot reach the disks because intermediate home directories
are usually not traversable (e.g. `~/.local` is `0700`). The role therefore
grants the qemu user execute-only (traverse, no read) access — via an ACL, so
the directories are not opened to everyone — on the home ancestors leading to
the pool. This requires `setfacl` (package `acl`), which the role installs.

For `netfs` pools, the `source` key supports the following properties:

| Key        | Default | Description                                        |
| ---------- | ------- | -------------------------------------------------- |
| `hosts`    |         | List of NFS/CIFS servers, each with a `name`       |
| `dir`      |         | Exported path on the server, as `dir.path`         |
| `format`   | `nfs`   | Source format, as `format.type` (`nfs` or `cifs`)  |
| `protocol` |         | NFS protocol version, as `protocol.ver` (e.g. `4`) |

#### `libvirt_volumes` items

| Key        | Default   | Description                                                  |
| ---------- | --------- | ------------------------------------------------------------ |
| `name`     |           | Volume name                                                  |
| `capacity` | `10G`     | Volume capacity (e.g. `200G`)                                |
| `target`   |           | Target definition, with `format.type` (`qcow2`, `raw`, etc.) |
| `pool`     | `default` | Pool to create the volume in                                 |
| `state`    | `present` | Desired volume state (`present`, `absent`)                   |

The `target.format.type` defaults to `libvirt_default_disk_format`.

A domain's `disks` (see below) are a shorthand: each non-block disk's backing
volume is created automatically, so it does not need a separate `libvirt_volumes`
entry. Use `libvirt_volumes` for volumes that are not a disk of a managed domain.

#### `libvirt_networks` items

| Key         | Default  | Description                                                                                                     |
| ----------- | -------- | --------------------------------------------------------------------------------------------------------------- |
| `name`      |          | Network name                                                                                                    |
| `forward`   |          | Forward definition, with a `mode` (defaults to `nat`); omit for an isolated network                             |
| `bridge`    |          | Bridge definition, with a `name`; omit to let libvirt auto-name the bridge                                      |
| `ips`       |          | List of IP configurations, each with `address`, `netmask` and an optional `dhcp.ranges` (list of `start`/`end`) |
| `autostart` | `true`   | Start the network at boot                                                                                       |
| `state`     | `active` | Desired network state (`active`, `absent`)                                                                      |

#### `libvirt_domains` items

| Key          | Default               | Description                                                                                      |
| ------------ | --------------------- | ------------------------------------------------------------------------------------------------ |
| `name`       |                       | Domain name                                                                                      |
| `type`       | `kvm`                 | Domain type                                                                                      |
| `memory`     |                       | Memory size (e.g. `4G`)                                                                          |
| `vcpu`       |                       | vCPU configuration, with `quantity` and an optional `placement`                                  |
| `cpu`        | `libvirt_default_cpu` | CPU configuration, with `mode` and an optional `model` (`name`, `fallback`)                      |
| `disks`      |                       | List of disks (see below)                                                                        |
| `interfaces` |                       | List of network interfaces, each with a `name` (network) or `type`, and an optional `boot_order` |
| `graphics`   |                       | List of graphics configurations, each with an optional `keymap`                                  |
| `autostart`  | `true`                | Start the domain at boot                                                                         |
| `state`      | `running`             | Desired domain state (`running`, `destroyed`, ...)                                               |

Each entry of a domain's `disks` list supports the following keys:

| Key          | Default                       | Description                                                      |
| ------------ | ----------------------------- | ---------------------------------------------------------------- |
| `name`       |                               | Disk name (volume name or file name in the pool)                 |
| `type`       | `file`                        | Disk source type (`file`, `volume`, `block`)                     |
| `capacity`   | `10G`                         | Capacity of the backing volume created for `file`/`volume` disks |
| `source`     |                               | Device path for `block` disks (e.g. `/dev/vdb`)                  |
| `target`     | `vda`                         | Target device in the guest; its name sets the bus (see below)    |
| `pool`       | `default`                     | Pool holding the disk (for `file` and `volume` types)            |
| `format`     | `libvirt_default_disk_format` | Disk image format (`qcow2`, `raw`, etc.)                         |
| `boot_order` |                               | Boot order of the disk                                           |

The emulated bus is derived from the `target` name, so a disk never needs a
separate `bus` key:

| `target` prefix | Bus      | Status                                             |
| --------------- | -------- | -------------------------------------------------- |
| `vda`, `vdb`, … | `virtio` | Supported                                          |
| `hda`, `hdb`, … | `ide`    | Supported                                          |
| `sda`, `sdb`, … | —        | Rejected for now; `sata`/`scsi`/`usb` come later   |

`sd*` names are refused for now (their bus is ambiguous in libvirt and needs an
extra controller). Support will be added without changing existing inventories.

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
            forward:
              mode: nat
            bridge:
              name: br1
            ips:
              - address: 192.168.0.1
                netmask: 255.255.255.0
                dhcp:
                  ranges:
                    - start: 192.168.0.2
                      end: 192.168.0.254
        libvirt_pools:
          - name: local-dir
            target:
              path: /data/images
          - name: from-nfs
            type: netfs
            target:
              path: /data/images
            source:
              hosts:
                - name: hostname
              dir:
                path: /server-export
          - name: from-nfs4
            type: netfs
            target:
              path: /data/images
            source:
              hosts:
                - name: hostname
              dir:
                path: /server-export
              protocol:
                ver: 4
          - name: from-cifs
            type: netfs
            target:
              path: /data/images
            source:
              hosts:
                - name: hostname
              dir:
                path: /server-share
              format:
                type: cifs
        libvirt_domains:
          - name: my-node
            autostart: false
            cpu:
              mode: host-passthrough
              model:
                fallback: allow
            memory: 4G
            interfaces:
              - name: my-bridge
              - name: my-nat
            vcpu:
              placement: static
              quantity: 2
            disks:
              - name: os
              - name: data
                capacity: 200G
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

Once TLS is enabled on two hosts, a running domain can be live-migrated from one
to the other. Use the **peer-to-peer** mode (`--p2p`) so the *source* daemon —
which holds the CA and client certificate deployed by this role — opens the
connection to the destination itself :

```sh
virsh migrate --live --p2p vm1 qemu+tls://hyp2/system
```

Without `--p2p`, `virsh` connects to the destination from wherever you run it (the
Ansible controller, for instance), which then needs its own client certificate —
otherwise the migration fails on a missing `/etc/pki/CA/cacert.pem`. The migration
data stream flows on the `49152-49215/tcp` range opened by the firewall rules
above.

The remaining options depend on where the domain's disks live :

- **Shared storage** (same NFS / Ceph / iSCSI backing on both hosts) : a plain
  migration works. If libvirt cannot confirm the storage is shared, or the disk
  cache mode is not `none`, add `--unsafe`.
- **Local storage** : copy the disks along with the domain using
  `--copy-storage-all` (full copy) or `--copy-storage-inc` (delta over a base
  image already present on the destination). Pre-create a target volume of the
  same virtual size on the destination pool, unless your libvirt/qemu is recent
  enough to allocate it automatically :

  ```sh
  virsh migrate --live --p2p --copy-storage-all vm1 qemu+tls://hyp2/system
  ```

Limitations
-----------

### Add physical disk to domain

It's only possible to add physical disk to domain in `qemu:///system` connection

License
-------

[BSD 3-Clause License](LICENSE).

