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

Backends
--------

A backend listed in `libvirt_backends` is a directory under `tasks/`, and
`tasks/main.yml` / `tasks/users.yml` loop over the list to reach it. Each backend
directory must provide the three files they include, even if empty :

| File               | Included from | Purpose                                           |
| ------------------ | ------------- | ------------------------------------------------- |
| `checks.yml`       | `main.yml`    | Fail early on an unsupported host                 |
| `post-install.yml` | `main.yml`    | System-wide setup, run as root after the packages |
| `users.yml`        | `users.yml`   | Per-user access: extra groups, per-user resources |

The per-user tasks live in `users.yml` rather than in `post-install.yml` on
purpose: `main.yml` reaches the backends through `include_tasks` (the loop rules
out `import_tasks`), and `--tags` can not descend into a dynamic include. Tagging
the include itself would drag the whole `post-install.yml` into `-t users`, so
`tasks/users.yml` includes the backend's `users.yml` directly, with
`apply: {tags: [users]}` to tag its tasks.

For the same reason nothing under `tasks/<backend>/` should carry a `users` tag
of its own — it would never be selectable.

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

`create.yml` / `destroy.yml` honour four environment variables, with sensible
defaults when unset:

| Variable               | Default              | Purpose                         |
| ---------------------- | -------------------- | ------------------------------- |
| `LIBVIRT_DEFAULT_URI`  | `qemu:///system`     | libvirt connection URI          |
| `LIBVIRT_DEFAULT_POOL` | `default`            | name of the storage pool to use |
| `MOLECULE_MEMORY`      | the platform's value | GB of RAM per VM                |
| `MOLECULE_VCPUS`       | the platform's value | vCPUs per VM                    |

`LIBVIRT_DEFAULT_URI` is the standard libvirt env var; `LIBVIRT_DEFAULT_POOL` is
local to this project but follows the same naming convention.

`MOLECULE_MEMORY` and `MOLECULE_VCPUS` override what the scenario asks for,
which is what you want when a VM has to boot domains of its own rather than
just run the daemon. They apply to every platform of the run, so pair them with
`-p`: `default` and `tls` create twelve VMs each, and twelve times eight
gigabytes is not a number your workstation has.

Those two scenarios run the whole matrix, which is eleven platforms at 2 GB
plus gentoo at 8 GB and 8 vCPU — 30 GB for a full run. gentoo is sized apart
because it is the only platform that compiles libvirt and qemu rather than
installing them.

```sh
MOLECULE_MEMORY=8 MOLECULE_VCPUS=4 molecule test -s attached-volume -p trixie
```

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

The pool also caches the cloud images the VMs are cloned from, one per platform,
as `molecule-image-<platform>-<id>.qcow2`. `<id>` fingerprints the
`Last-Modified` and `Content-Length` the publisher serves for the image URL,
read with a `HEAD` before every create. Most platforms track a rolling `latest/`
or `current/` URL whose file name never changes, so the name alone cannot say
whether the cache is still the published image; those two headers can. A
republished image gets a new fingerprint, hence a new volume, and the one it
supersedes is deleted on the same run.

The sweep only ever considers `molecule-image-<platform>-*` volumes, for the
platform being created — `LIBVIRT_DEFAULT_POOL` may well be your own `default`
pool, and it is also the pool `gwerlas.system` caches into, sharing the images
of the platforms both roles declare. Nothing outside that prefix is a candidate,
and neither is the image of another platform.

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

A failing run destroys its instances; `--destroy never` keeps them. Read its
help line — "the destroy strategy used at the conclusion of a Molecule run" —
as covering both destroy steps of the sequence, not only the trailing one:
that is what makes a second `test` land on the instances the first one left.

```sh
molecule test -s <scenario> --destroy never
molecule login -s <scenario> -h <instance>   # change things by hand
molecule converge -s <scenario>              # re-apply after an edit
molecule destroy -s <scenario>               # when you are done
```

Prefer it to running `create` / `converge` / `verify` by hand. `molecule test
--help` prints the sequence those three leave out, idempotence included, and
this role's defects live there — a daemon reconfigured twice is exactly what a
second converge catches.

Supporting a new distribution / version
---------------------------------------

The cloud images for the supported platforms live in
[`molecule/shared/platforms.yml`][platforms]; `create.yml` resolves the image URL
at runtime via a `lookup` on it. Add an entry there, then reference it by name
(plus any `groups` / `memory` / `extra_disks` override) from the relevant
scenario's `molecule.yml`. `meta/main.yml`'s `galaxy_info.platforms` is
hand-maintained — update it too if the new platform is officially supported.

`molecule/shared/` also hosts the `create.yml` / `destroy.yml` / `prepare.yml`
playbooks every scenario points at via `provisioner.playbooks`; molecule ignores
the directory as a scenario because it carries no `molecule.yml`.

Target properties: `vars/` files and issue labels
-------------------------------------------------

`tasks/facts.yml` reads a handful of properties off the target — service
manager, OS family, distribution, major version, release — and loads
`vars/<value>.yml` for each one it finds, from the least specific to the most.
The last file loaded wins. A second pass does the same for every entry of
`libvirt_backends`, an axis that describes what was asked for rather than what
the host is.

So a value lives in the file named after the property it is *actually* true of,
and the narrowest one that still covers every target it applies to. Something
true of every OpenRC host belongs in `openrc.yml`, not copied into each
distribution's file; something true of Gentoo hosts belongs in
`gentoo-like.yml`. Because the cascade runs from least to most specific,
refining a value at a narrower level is deliberate — `debian-like.yml` can set
a default that `debian12.yml` overrides. What to avoid is setting the same
value at two levels by accident: the wider one is then silently dead.

The axis is a property of the target or of the requested backend, never of this
repository's own layout.

Issue labels follow the same rule, one step wider: an issue carries what it is
true *of*. For the role's behaviour that is a property of the managed host, or
the backend it concerns — and the host properties available are not limited to
the ones this cascade has a file for, `portage` naming the package manager
layer although no `portage.yml` exists here. For the project's own machinery it
is the thing impacted, which is why `ci` and `molecule` exist. What an issue
never carries is the directory it happens to touch: that is a property of this
repository, not of anything the role acts on. An issue true of every target
carries no dimension label at all, and that absence is the correct answer
rather than an oversight. On top of that, one label for the kind: `bug`,
`feature` or `tech-debt`.

Labels are created on demand and never in advance, so the list only ever holds
what some issue actually needed. If none of the existing ones fits, say so in
the issue rather than stretching a label to cover it.

Editing documentation
---------------------

### Where a rationale lives

Every artifact starts empty: a sentence earns its place when its absence would
cost the reader something precise, not when a home can be found for it. A
reason then lives in exactly one of these, the others pointing at it:

| Home                     | What it holds                                       |
| ------------------------ | --------------------------------------------------- |
| Code comment             | what this line does, and under which rule           |
| `CONTRIBUTING` / `docs/` | what the reader has to be able to predict or do     |
| Commit message           | what changes, and why it is right                   |
| Issue / merge request    | how we know: what was run, measured, tried, dropped |
| Upstream documentation   | the rule itself, whenever the rule is not ours      |

Write in that order, narrowest first. A merge request is written **against**
its commits, not from the same head of context: after one opening sentence
naming what it does, it holds only what the diff and the commit messages do not
already say. A one-line pointer beats a restatement every time.

Two boundaries, two tests, both by deletion.

**A comment summarises, it does not narrate.** Remove everything written in the
past tense — when it was observed, what was measured, which false trail was
followed. What is left is the rule.

**A commit is knowable without running anything.** Remove from the merge
request every sentence that would already be true had the work never run: it
belongs to the commit. Remove from the commit every sentence that only became
true by running something: it belongs to the merge request.

**Cite upstream, never re-derive it.** When the reason is a third-party tool's
behaviour — Portage, libvirt, systemd, Jinja — quote one sentence, give the
URL, stop. A reconstruction of your own goes stale the day upstream changes its
mind, and reads as this role's opinion when it is an external constraint.

Submit your changes
-------------------

Merge request in [Gitlab][].

A change comes with its tests and its documentation, in the same commit. A new
variable, or a change in behaviour, is not finished until:

- a molecule scenario exercises it — an existing one where it fits, `tls` for
  the daemon's TLS surface, `add-user` for user access, `qemu-user` for the
  session backend, `default` for the role's own defaults;
- the user-facing half is written in `README.md` or under `docs/`: what the
  variable does, its default, an example;
- the reasoning a future maintainer will need — an upstream constraint, a
  Portage quirk, why two tasks must run in that order — goes in a code comment
  or in this file, not in the user documentation.

Keeping the three together is what makes a commit reviewable on its own: a
change that arrives without its test looks finished when it is not, and one
that arrives without its reason forces the next reader to guess.

The issue is referenced from the commit body, and only from there. `Closes #4`
if the commit settles the whole ticket; a bare `#4` if it settles one of the
three things the ticket asks for, so the other two stay visible. Neither
`README.md` nor `docs/` ever carries an issue number — a user can do nothing
with it, and it goes stale the day the issue closes.

<!-- Links section -->
[Gitlab]: https://gitlab.com/gwerlas/ansible/roles/libvirt/-/merge_requests
[platforms]: molecule/shared/platforms.yml
