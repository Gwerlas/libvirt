Development guide
=================

| **Important**
|
| The GitHub repository exists only because Ansible Galaxy supports only GitHub.
| Please, do your merge requests on [Gitlab][].

This role should not need any external settings to work.

Inventory format
----------------

The provisioning variables (`libvirt_pools`, `libvirt_volumes`,
`libvirt_networks`, `libvirt_domains`) mirror libvirt's own XML format as closely
as is reasonable, so the [libvirt format reference](https://libvirt.org/format.html)
doubles as the reference for these variables.

The mapping is mechanical :

* an XML element with attributes becomes a dictionary keyed by those attributes
  (`<bridge name='br0'/>` → `bridge: {name: br0}`) ;
* an element holding text becomes a scalar, or a dictionary with a named key when
  it also carries attributes (`<vcpu placement='static'>2</vcpu>` →
  `vcpu: {placement: static, quantity: 2}`) ;
* repeated elements become a list named with the plural of the element
  (`<disk>` → `disks`, `<interface>` → `interfaces`, `<ip>` → `ips`,
  `<range>` → `ranges`, `<host>` → `hosts`), even when a single occurrence is the
  common case. Elements already ending in `s` keep their name
  (`<graphics>` → `graphics`).

Prefer extending an existing element with a new key over inventing a flat
`element_attribute` variable, so the format stays predictable and future-proof.

The mapping has no special case to memorise: every element with attributes is a
dictionary keyed by those attributes, down to single-attribute ones
(`<dir path='…'/>` → `dir: {path: …}`, `<format type='nfs'/>` →
`format: {type: nfs}`).

One **deliberate departure** remains: a domain's `disks` are a convenience DSL
rather than a strict `<disk>` mirror. A disk's `target` is the guest device name
(`target: vda`, not `target: {dev: vda}`) and its `capacity`/`format` stay flat
rather than nested under `target.format.type`, so the common "give a VM a disk"
case stays terse. In the same spirit, the emulated `bus` is not a key: it is
derived from the `target` prefix (`vd*` → virtio, `hd*` → ide) in
`domain.xml.j2`. `sd*` names are rejected upfront (`tasks/domains.yml`) because
their bus is ambiguous in libvirt (`sata`/`scsi`/`usb`) and needs an extra
controller; adding them later is purely additive — an inventory that errors
today starts working, never the reverse — so the `target`-as-string contract is
locked for good. Each non-block disk's backing volume
is then derived (in `volumes_computed`, `vars/main.yml`) into a faithful
`libvirt_volumes` entry, so the same volume is never declared twice — and
`libvirt_volumes` itself mirrors `<volume>` (`capacity`, `target.format.type`).

Requirements
------------

The Molecule scenarios drive their test VMs through **libvirt** (no Vagrant), so
you need:

* libvirt + KVM with **nested virtualisation enabled** on the host
* molecule + molecule-plugins
* the `community.libvirt`, `community.general` and `ansible.posix` collections

The role's own test VMs run libvirt themselves and boot **inner** domains, so the
host must expose hardware virtualisation to the guests. `create.yml` defines the
VMs with `<cpu mode='host-passthrough'/>` so the guest sees the host's `vmx`/`svm`
flag; make sure nesting is on:

```sh
cat /sys/module/kvm_intel/parameters/nested   # or kvm_amd — must print Y or 1
```

libvirt connection and storage pool
-----------------------------------

`create.yml` / `destroy.yml` honour two environment variables, with sensible
defaults when unset:

| Variable               | Default          | Purpose                         |
| ---------------------- | ---------------- | ------------------------------- |
| `LIBVIRT_DEFAULT_URI`  | `qemu:///system` | libvirt connection URI          |
| `LIBVIRT_DEFAULT_POOL` | `default`        | name of the storage pool to use |

`LIBVIRT_DEFAULT_URI` is the standard libvirt env var; `LIBVIRT_DEFAULT_POOL` is
local to this project but follows the same naming convention.

Recommended setup if the system pool sits on a small partition: create a
dedicated pool on a larger filesystem and point molecule at it. For example:

```sh
install -d -m 2775 -g qemu $HOME/.local/share/molecule/images
virsh -c qemu:///system pool-define-as molecule dir --target $HOME/.local/share/molecule/images
virsh -c qemu:///system pool-autostart molecule
virsh -c qemu:///system pool-start molecule

export LIBVIRT_DEFAULT_POOL=molecule
molecule test
```

The directory must be reachable by the `qemu` user (group `qemu` + setgid parent
works, provided your user is in `qemu`).

Run tests
---------

Test the role with its default values in a VM of each supported distro:

```sh
molecule test
```

Test each provisioning use-case:

```sh
molecule test -s add-user          # role adds a user to the libvirt group
molecule test -s attached-volume   # extra disk created in a pool and attached
molecule test -s block-disk        # raw /dev/vdb attached as a block device
molecule test -s qemu-user         # domains provisioned over qemu:///session
molecule test -s tls               # libvirtd TLS config, certs and TLS socket
```

The `libvirt_units` filter (`filter_plugins/libvirt_units.py`) resolves the
libvirt daemon layout (monolithic vs modular) from the installed unit files. Its
logic is plain Python, unit-tested without Ansible:

```sh
python -m pytest tests/unit
```

Develop / Debug
---------------

```sh
molecule create
molecule converge
molecule login -h <instance_name>
# Do your changes by hand
molecule verify
```

Supporting a new distribution / version
---------------------------------------

The cloud images for the supported platforms live in
[`molecule/shared/platforms.yml`][platforms]; `create.yml` resolves the image URL
at runtime via a `lookup` on it. Add an entry there, then reference it by name
(plus any `groups` / `memory` / `extra_disks` override) from the relevant
scenario's `molecule.yml`. `meta/main.yml`'s `galaxy_info.platforms` is
hand-maintained — update it too if the new platform is officially supported.

If the role's packages don't work out of the box on the new distro, define the
needed defaults in the `vars` directory.

`molecule/shared/` also hosts the `create.yml` / `destroy.yml` / `prepare.yml`
playbooks every scenario points at via `provisioner.playbooks`; molecule ignores
the directory as a scenario because it carries no `molecule.yml`.

Submit your changes
-------------------

Merge request in [Gitlab][].

<!-- Links section -->
[Gitlab]: https://gitlab.com/gwerlas/ansible/roles/libvirt/-/merge_requests
[platforms]: molecule/shared/platforms.yml
