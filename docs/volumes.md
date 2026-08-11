Storage volumes
===============

`libvirt_volumes` takes a list of dictionaries, each describing a storage volume
to create.

| Key        | Default   | Description                                                  |
| ---------- | --------- | ------------------------------------------------------------ |
| `name`     |           | Volume name                                                  |
| `capacity` | `10G`     | Volume capacity (e.g. `200G`)                                |
| `target`   |           | Target definition, with `format.type` (`qcow2`, `raw`, etc.) |
| `pool`     | `default` | Pool to create the volume in                                 |
| `state`    | `present` | Desired volume state (`present`, `absent`)                   |

The `target.format.type` defaults to `libvirt_default_disk_format`.

A [domain](domains.md)'s `disks` are a shorthand: each non-block disk's backing
volume is created automatically, so it does not need a separate `libvirt_volumes`
entry. Use `libvirt_volumes` for volumes that are not a disk of a managed domain.

Example
-------

```yaml
libvirt_volumes:
  - name: shared-data
    capacity: 200G
    pool: data-dir
    target:
      format:
        type: qcow2
```
