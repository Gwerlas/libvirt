Firewall
========

| Variable                  | Default   | Description                                                  |
| ------------------------- | --------- | ------------------------------------------------------------ |
| `libvirt_manage_firewall` | `true`    | Whether to manage firewalld rules                            |
| `libvirt_firewall_zone`   | _(unset)_ | Firewalld zone to use (defaults to firewalld's default zone) |

When `libvirt_manage_firewall` is `true`, the role enables:

- the `libvirt` firewalld service, always;
- the `libvirt-tls` service (TLS port `16514/tcp`) **only when the daemon is
  configured to listen on TLS**, i.e. when `listen_tls: 1` is set under
  `libvirt_config.libvirtd` (see the [TLS](tls.md) guide). Without it the port
  stays closed, since nothing listens on it;
- the migration data port range `49152-49215/tcp`, always, so
  [live migration](migration.md) between hosts works without further tuning.

Providing firewalld itself is the operator's job — the role only adds its own
rules on top of it.
