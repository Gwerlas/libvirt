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

It defaults to `[]`: no user is granted anything, the account Ansible
connects as included. To grant it access, list it:

```yaml
libvirt_users:
  - name: "{{ ansible_facts.user_id }}"
```

The role only adds users to groups: removing an entry later, or never listing a
user who was granted access before, leaves their memberships as they are.

Provisioning (`libvirt_pools`, `libvirt_networks`, `libvirt_domains`, …) over
`qemu:///system` runs as the account Ansible connects as, with no privilege
escalation. Unless that account is root, it has to be in this list.

On Gentoo the `libvirt` group is not shipped with the daemon: it comes from the
`policykit` USE flag on `app-emulation/libvirt`, which the role requests only
when this list is not empty. An empty `libvirt_users` there leaves the daemon
reachable by root alone, its socket owned `root:root`.

Granting access to a new user on an already provisioned host does not need a full
role run: `--tags users` covers everything the list drives — the `libvirt` group,
the backend groups (`kvm`, `qemu`), the user's `qemu:///session` default pool and
their TLS client credentials.

```sh
ansible-playbook site.yml --tags users
```

Deploying the `ca_file` / `clientcert` / `clientkey` keys lets a user reach a
remote daemon over TLS from their own session; see the
[per-user client credentials](tls.md#per-user-client-credentials) section of the
TLS documentation. These files are read by the user's own `virsh`, not the
daemon, so they are deployed least-privilege: owned by the user, the private key
in mode `0400`, with no qemu group or system SELinux label.
