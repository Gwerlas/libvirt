TLS
===

Enable TLS on the libvirt daemon by deploying, from the Ansible controller, a CA
plus a server and client certificate (see the
[libvirt TLS knowledge base](https://libvirt.org/kbase/tlscerts.html) to create
them). The role writes the daemon configuration, installs the certificates and
opens the TLS socket.

Variables
---------

| Variable             | Default   | Description                                                                                       |
| -------------------- | --------- | ------------------------------------------------------------------------------------------------- |
| `libvirt_config`     | _(unset)_ | Per-file directives, as `{ <file>: { directive: value } }`, written to `/etc/libvirt/<file>.conf` |
| `libvirt_ca_file`    | _(unset)_ | Path **on the controller** to the CA certificate to deploy                                        |
| `libvirt_servercert` | _(unset)_ | Path **on the controller** to the server certificate to deploy                                    |
| `libvirt_serverkey`  | _(unset)_ | Path **on the controller** to the server private key to deploy                                    |
| `libvirt_clientcert` | _(unset)_ | Path **on the controller** to the client certificate to deploy                                    |
| `libvirt_clientkey`  | _(unset)_ | Path **on the controller** to the client private key to deploy                                    |

The TLS files are deployed to the standard libvirt locations:

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

Enabling TLS
------------

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

Setting `listen_tls: 1` also makes the role enable the daemon's TLS socket
(`libvirtd-tls.socket`, or `virtproxyd-tls.socket` on hosts running the modular
daemons), since a socket-activated daemon ignores the directive on its own. When
`libvirt_manage_firewall` is enabled, it also opens the TLS port `16514/tcp`
(see the [firewall](firewall.md) guide).

Clients can then reach the daemon over TLS:

```sh
virsh -c qemu://node.example.com/system list
```

Per-user client credentials
---------------------------

Client credentials can also be deployed per user, so a given user can connect to
a remote daemon over TLS from their own session:

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
a remote host:

```sh
virsh -c qemu://node.example.com/system list
```

The URI carries no `alice@` part: over TLS the identity comes from the client
certificate virsh reads in her home, not from a username (that would only matter
for the SSH transport). The path stays `/system` to reach the remote system
daemon — `/session` is a separate, local per-user daemon.

Certificate rotation
--------------------

The role deploys certificates, it does not generate them. Re-running the role
after replacing any of these files on the controller redeploys it and restarts
the TLS-serving daemon (`libvirtd`, or `virtproxyd` on hosts running the modular
daemons), so a rotated certificate or CA takes effect.

The `ca` and `ssl` tags target this without a full run: `-t ca` redeploys the CA
and `-t ssl` the server/client certificates, each restarting the daemon to apply
the change.
