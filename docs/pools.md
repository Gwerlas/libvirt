Storage pools
=============

`libvirt_pools` takes a list of dictionaries, each describing a storage pool to
create.

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

Example
-------

```yaml
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
```
