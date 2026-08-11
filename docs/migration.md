Live migration
==============

Once [TLS](tls.md) is enabled on two hosts, a running domain can be live-migrated
from one to the other. Use the **peer-to-peer** mode (`--p2p`) so the *source*
daemon — which holds the CA and client certificate deployed by this role — opens
the connection to the destination itself:

```sh
virsh migrate --live --p2p vm1 qemu+tls://hyp2/system
```

Without `--p2p`, `virsh` connects to the destination from wherever you run it (the
Ansible controller, for instance), which then needs its own client certificate —
otherwise the migration fails on a missing `/etc/pki/CA/cacert.pem`.

TLS here is only the *control* transport this role sets up; live migration itself
does not require it (`qemu+ssh://` or `qemu+tcp://` work too). The migration data
stream — the domain's memory, and its disks when migrating local storage — flows
on the `49152-49215/tcp` range **regardless of the control transport**, which is
why the role opens that range unconditionally (see the [firewall](firewall.md)
documentation). The sole exception is a `--tunnelled` migration, which routes the
data through the control connection instead and leaves that range unused.

Everything beyond this — shared vs. local storage, the `virsh migrate` flags,
copying disks, ejecting read-only media, and diagnosing a stalled transfer — is
standard libvirt/QEMU territory, not specific to this role. The upstream
references cover it:

- [libvirt guest migration guide][libvirt-migration] — modes (managed / p2p /
  direct) and native vs. tunnelled transports, including non-shared storage;
- [`virsh migrate` manual page][virsh-migrate] — the exact flags
  (`--copy-storage-all`, `--copy-storage-inc`, `--unsafe`, `--tunnelled`, …);
- [QEMU migration troubleshooting][qemu-migration] — diagnosing a migration that
  fails or does not converge.

[libvirt-migration]: https://libvirt.org/migration.html
[virsh-migrate]: https://www.libvirt.org/manpages/virsh.html#migrate
[qemu-migration]: https://wiki.qemu.org/Features/Migration/Troubleshooting
