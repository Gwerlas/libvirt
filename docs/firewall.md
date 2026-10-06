Firewall
========

| Variable                     | Default   | Description                                                  |
| ---------------------------- | --------- | ------------------------------------------------------------ |
| `libvirt_manage_firewall`    | `true`    | Whether to manage firewalld rules                            |
| `libvirt_firewall_migration` | `false`   | Whether to open the live migration data port range           |
| `libvirt_firewall_zone`      | _(unset)_ | Firewalld zone to use (defaults to firewalld's default zone) |
| `libvirt_firewall_backend`   | _(unset)_ | Firewalld packet filtering backend to install and select     |

With no variable set, the role opens nothing. When `libvirt_manage_firewall` is
`true`, it enables:

- the `libvirt` firewalld service (`16509/tcp`, libvirtd's unencrypted remote
  access) **only when the daemon is configured to listen on TCP**, i.e. when
  `listen_tcp: 1` is set under `libvirt_config.libvirtd`. The role enables no
  TCP socket: on a socket-activated daemon, nothing listens on the port until
  you enable the daemon's TCP socket yourself;
- the `libvirt-tls` service (TLS port `16514/tcp`) **only when the daemon is
  configured to listen on TLS**, i.e. when `listen_tls: 1` is set under
  `libvirt_config.libvirtd` (see the [TLS](tls.md) guide). Without it the port
  stays closed, since nothing listens on it;
- the migration data port range `49152-49215/tcp` **only when
  `libvirt_firewall_migration` is `true`**, so [live migration](migration.md)
  to the host works without further tuning, whatever the control transport.

The role does not close the `libvirt` service or the migration range an earlier
run opened, the stale range below being its only exception. A host converged by
a version that opened them on every run keeps them until you close them:

```sh
firewall-cmd --permanent --remove-service=libvirt
firewall-cmd --permanent --remove-port=49152-49215/tcp
firewall-cmd --reload
```

Add `--zone=<zone>` to the first two commands when `libvirt_firewall_zone` is
set.

Earlier versions opened `19215-49152/tcp` instead of the migration range. On a
host where that entry is still in firewalld's permanent configuration, the role
removes it, and only it, from the zone it manages, then reloads firewalld and
prints a warning naming the host; a check run reports the removal and says the
entry would be closed. A host without the entry sees nothing. This cleanup goes
away in 1.0.0, so run the role once on every host that predates 0.7.0 before
upgrading to 1.0.0.

Set `libvirt_firewall_backend` to pick firewalld's packet filtering backend:
the role installs the package it names and writes `FirewallBackend=<value>` in
`/etc/firewalld/firewalld.conf`. Left unset, firewalld keeps the backend its
distribution ships.

Providing firewalld itself is the operator's job — the role only adds its own
rules on top of it.
