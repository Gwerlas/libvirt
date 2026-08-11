"""Unit tests for the ``libvirt_units`` filter plugin.

Run from the role root with::

    python -m pytest tests/unit
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'filter_plugins'))

from libvirt_units import FilterModule  # noqa: E402


def units(*names):
    """Fake ``systemctl list-unit-files`` output for the given unit names."""
    return ['{0} enabled enabled'.format(name) for name in names]


# Debian/Ubuntu (and Gentoo's default): a single libvirtd behind its sockets.
DEBIAN = units(
    'libvirt-guests.service',
    'libvirtd.service', 'libvirtd.socket', 'libvirtd-ro.socket',
    'libvirtd-admin.socket', 'libvirtd-tls.socket', 'libvirtd-tcp.socket',
    'virtlogd.service', 'virtlogd.socket',
    'virtlockd.service', 'virtlockd.socket',
)

# EL9+/Arch/Fedora: one daemon per driver, virtproxyd fronting remote access.
# The monolithic libvirtd.service is still shipped but unused.
MODULAR = units(
    'libvirt-guests.service',
    'libvirtd.service',
    'virtqemud.service', 'virtqemud.socket',
    'virtnetworkd.service', 'virtnetworkd.socket',
    'virtnodedevd.service', 'virtnodedevd.socket',
    'virtstoraged.service', 'virtstoraged.socket',
    'virtproxyd.service', 'virtproxyd.socket', 'virtproxyd-tls.socket',
    'virtlogd.service', 'virtlogd.socket',
    'virtlockd.service', 'virtlockd.socket',
)

# Old releases: no socket activation, libvirtd is a plain service.
LEGACY = units('libvirtd.service', 'virtlogd.service', 'virtlockd.service')


def layout(unit_files, backends=None):
    return FilterModule().libvirt_units(unit_files, backends or ['qemu'])


def test_debian_is_monolithic_socket_activated():
    result = layout(DEBIAN)
    assert result['modular'] is False
    assert result['boot_units'] == [
        'libvirt-guests.service', 'libvirtd.socket',
        'virtlockd.socket', 'virtlogd.socket',
    ]
    assert result['restart_units'] == [
        'libvirtd.service', 'virtlogd.service', 'virtlockd.service',
    ]
    assert result['tls_socket'] == 'libvirtd-tls.socket'


def test_modular_uses_per_driver_daemons():
    result = layout(MODULAR)
    assert result['modular'] is True
    assert result['boot_units'] == [
        'libvirt-guests.service',
        'virtlogd.socket', 'virtlockd.socket', 'virtnetworkd.socket',
        'virtnodedevd.socket', 'virtstoraged.socket', 'virtqemud.socket',
    ]
    assert result['tls_socket'] == 'virtproxyd-tls.socket'


def test_modular_restart_excludes_the_unused_monolithic_daemon():
    # libvirtd.service is installed but must never be restarted on modular hosts,
    # or it fights the per-driver daemons for the sockets.
    result = layout(MODULAR)
    assert 'libvirtd.service' not in result['restart_units']
    assert result['restart_units'] == [
        'virtlogd.service', 'virtlockd.service', 'virtnetworkd.service',
        'virtnodedevd.service', 'virtstoraged.service', 'virtqemud.service',
        'virtproxyd.service',
    ]


def test_legacy_runs_libvirtd_as_a_plain_service():
    result = layout(LEGACY)
    assert result['modular'] is False
    assert result['boot_units'] == ['libvirtd.service']
    assert result['restart_units'] == ['libvirtd.service']
    assert result['tls_socket'] is None


def test_lists_are_filtered_to_installed_units():
    # A modular host without the storage driver must not be told to manage it.
    trimmed = [u for u in MODULAR if not u.startswith('virtstoraged')]
    result = layout(trimmed)
    assert 'virtstoraged.socket' not in result['boot_units']
    assert 'virtstoraged.service' not in result['restart_units']


def test_tls_socket_absent_yields_none():
    no_tls = [u for u in DEBIAN if not u.startswith('libvirtd-tls')]
    assert layout(no_tls)['tls_socket'] is None


def test_lxc_backend_adds_its_daemon():
    result = layout(MODULAR + units('virtlxcd.service', 'virtlxcd.socket'),
                    backends=['qemu', 'lxc'])
    assert 'virtlxcd.socket' in result['boot_units']
    assert 'virtlxcd.service' in result['restart_units']
