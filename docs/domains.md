Domains
=======

`libvirt_domains` takes a list of dictionaries, each describing a virtual machine
to create.

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

Disks
-----

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

The backing volume of a `file`/`volume` disk is created automatically, so it does
not need a separate [`libvirt_volumes`](volumes.md) entry.

The emulated bus is derived from the `target` name, so a disk never needs a
separate `bus` key:

| `target` prefix | Bus      | Status                                             |
| --------------- | -------- | -------------------------------------------------- |
| `vda`, `vdb`, … | `virtio` | Supported                                          |
| `hda`, `hdb`, … | `ide`    | Supported                                          |
| `sda`, `sdb`, … | —        | Rejected for now; `sata`/`scsi`/`usb` come later   |

`sd*` names are refused for now (their bus is ambiguous in libvirt and needs an
extra controller). Support will be added without changing existing inventories.

Example
-------

```yaml
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
