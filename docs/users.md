Users
=====

`libvirt_users` grants users access to libvirt. It takes a list of dictionaries;
each entry adds the user to the libvirt/kvm groups and, optionally, deploys their
personal TLS client credentials.

| Key          | Description                                                                                            |
| ------------ | ------------------------------------------------------------------------------------------------------ |
| `name`       | User name to add to the libvirt/kvm groups                                                             |
| `ca_file`    | Path **on the controller** to the CA certificate, deployed to `~/.pki/cacert.pem`                      |
| `clientcert` | Path **on the controller** to the user client certificate, deployed to `~/.pki/libvirt/clientcert.pem` |
| `clientkey`  | Path **on the controller** to the user client private key, deployed to `~/.pki/libvirt/clientkey.pem`  |

It defaults to `[{name: {{ ansible_facts.user_id }}}]`, i.e. the connecting user
is granted access.

Deploying the `ca_file` / `clientcert` / `clientkey` keys lets a user reach a
remote daemon over TLS from their own session; see the
[per-user client credentials](tls.md#per-user-client-credentials) section of the
TLS documentation.
