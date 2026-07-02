Virtual networks
================

`libvirt_networks` takes a list of dictionaries, each describing a virtual
network to create.

| Key         | Default  | Description                                                                                                     |
| ----------- | -------- | --------------------------------------------------------------------------------------------------------------- |
| `name`      |          | Network name                                                                                                    |
| `forward`   |          | Forward definition, with a `mode` (defaults to `nat`); omit for an isolated network                             |
| `bridge`    |          | Bridge definition, with a `name`; omit to let libvirt auto-name the bridge                                      |
| `ips`       |          | List of IP configurations, each with `address`, `netmask` and an optional `dhcp.ranges` (list of `start`/`end`) |
| `autostart` | `true`   | Start the network at boot                                                                                       |
| `state`     | `active` | Desired network state (`active`, `absent`)                                                                      |

Example
-------

```yaml
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
```
