Firewall
========

| Variable                   | Default   | Description                                                  |
| -------------------------- | --------- | ------------------------------------------------------------ |
| `libvirt_manage_firewall`  | `true`    | Whether to manage firewalld rules                            |
| `libvirt_firewall_zone`    | _(unset)_ | Firewalld zone to use (defaults to firewalld's default zone) |
| `libvirt_firewall_backend` | _(unset)_ | Firewalld packet filtering backend to install and select     |

When `libvirt_manage_firewall` is `true`, the role enables:

- the `libvirt` firewalld service, always;
- the `libvirt-tls` service (TLS port `16514/tcp`) **only when the daemon is
  configured to listen on TLS**, i.e. when `listen_tls: 1` is set under
  `libvirt_config.libvirtd` (see the [TLS](tls.md) guide). Without it the port
  stays closed, since nothing listens on it;
- the migration data port range `49152-49215/tcp`, always, so
  [live migration](migration.md) between hosts works without further tuning.

Set `libvirt_firewall_backend` to pick firewalld's packet filtering backend:
the role installs the package it names and writes `FirewallBackend=<value>` in
`/etc/firewalld/firewalld.conf`. Left unset, firewalld keeps the backend its
distribution ships.

Providing firewalld itself is the operator's job — the role only adds its own
rules on top of it.
