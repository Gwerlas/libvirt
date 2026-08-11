#!/usr/bin/python

# The libvirt daemon ships in two layouts:
#   * monolithic - a single libvirtd, reached through the libvirtd*.socket units
#                  (Debian/Ubuntu, Gentoo's default) or, on old releases, run as
#                  a plain service with no socket activation at all;
#   * modular    - one daemon per driver (virtqemud, virtnetworkd, ...) with
#                  virtproxyd fronting remote access (EL9+, Arch, Fedora).
#
# Which layout a host runs cannot be derived from the libvirt version: Debian
# ships the monolithic daemon even at 9.x. Detect it from the unit files that are
# actually installed so the role starts/restarts the right units and enables the
# matching TLS socket. virtlogd/virtlockd are shared by both layouts, so the
# modular probe only looks at units that exist exclusively in the modular split.

_HELPERS = ['virtlogd', 'virtlockd', 'virtnetworkd', 'virtnodedevd', 'virtstoraged']
_BACKEND_DAEMONS = {'qemu': 'virtqemud', 'lxc': 'virtlxcd'}
_MODULAR_PROBES = ['virtproxyd.socket', 'virtqemud.socket']


class FilterModule(object):
    def filters(self):
        return {'libvirt_units': self.libvirt_units}

    def libvirt_units(self, unit_files, backends=None):
        """Map ``systemctl list-unit-files`` output to the libvirt unit layout.

        ``unit_files`` is the list of lines produced by
        ``systemctl list-unit-files --type=service,socket`` (only the first
        column, the unit name, is used). ``backends`` is the list of enabled
        libvirt backends (``qemu``, ``lxc``).

        Returns a dict with:
          * ``modular``       - whether the host runs the modular daemons;
          * ``boot_units``    - units to enable and start so the local system
                                daemon and its helpers are up;
          * ``restart_units`` - daemon services to restart for a libvirtd.conf
                                change to take effect;
          * ``tls_socket``    - the socket that makes the daemon listen on TLS,
                                or ``None`` when the host has no such unit.
        All lists are filtered to the units actually installed.
        """
        backends = backends or []
        available = {line.split()[0] for line in unit_files if line.split()}
        backend_daemons = [_BACKEND_DAEMONS[b] for b in backends if b in _BACKEND_DAEMONS]

        modular = any(probe in available for probe in _MODULAR_PROBES)
        socket_activated = 'libvirtd.socket' in available

        if modular:
            # Helpers and per-backend daemons run locally; virtproxyd only fronts
            # remote access, so it is left for its socket to activate on demand.
            daemons = _HELPERS + backend_daemons
            boot_units = ['libvirt-guests.service'] + [d + '.socket' for d in daemons]
            restart_units = [d + '.service' for d in daemons + ['virtproxyd']]
            tls_socket = 'virtproxyd-tls.socket'
        elif socket_activated:
            boot_units = ['libvirt-guests.service', 'libvirtd.socket',
                          'virtlockd.socket', 'virtlogd.socket']
            restart_units = ['libvirtd.service', 'virtlogd.service', 'virtlockd.service']
            tls_socket = 'libvirtd-tls.socket'
        else:  # legacy: no socket activation, libvirtd runs as a plain service
            boot_units = ['libvirtd.service']
            restart_units = ['libvirtd.service']
            tls_socket = None

        def keep(units):
            return [unit for unit in units if unit in available]

        return {
            'modular': modular,
            'boot_units': keep(boot_units),
            'restart_units': keep(restart_units),
            'tls_socket': tls_socket if tls_socket in available else None,
        }
