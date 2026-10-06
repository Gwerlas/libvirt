# gwerlas\.libvirt Release Notes

**Topics**

- <a href="#v0-8-0">v0\.8\.0</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide">Breaking Changes / Porting Guide</a>
    - <a href="#bugfixes">Bugfixes</a>
- <a href="#v0-7-0">v0\.7\.0</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide-1">Breaking Changes / Porting Guide</a>
    - <a href="#bugfixes-1">Bugfixes</a>
- <a href="#v0-6-2">v0\.6\.2</a>
    - <a href="#bugfixes-2">Bugfixes</a>
- <a href="#v0-6-1">v0\.6\.1</a>
    - <a href="#bugfixes-3">Bugfixes</a>
- <a href="#v0-6-0">v0\.6\.0</a>
    - <a href="#minor-changes-2">Minor Changes</a>
- <a href="#v0-5-1">v0\.5\.1</a>
    - <a href="#bugfixes-4">Bugfixes</a>
- <a href="#v0-5-0">v0\.5\.0</a>
    - <a href="#minor-changes-3">Minor Changes</a>
    - <a href="#breaking-changes--porting-guide-2">Breaking Changes / Porting Guide</a>
- <a href="#v0-4-3">v0\.4\.3</a>
    - <a href="#bugfixes-5">Bugfixes</a>
- <a href="#v0-4-2">v0\.4\.2</a>
    - <a href="#bugfixes-6">Bugfixes</a>
- <a href="#v0-4-1">v0\.4\.1</a>
    - <a href="#bugfixes-7">Bugfixes</a>
- <a href="#v0-4-0">v0\.4\.0</a>
    - <a href="#minor-changes-4">Minor Changes</a>
    - <a href="#bugfixes-8">Bugfixes</a>
- <a href="#v0-3-3">v0\.3\.3</a>
    - <a href="#bugfixes-9">Bugfixes</a>
- <a href="#v0-3-2">v0\.3\.2</a>
    - <a href="#minor-changes-5">Minor Changes</a>
- <a href="#v0-3-1">v0\.3\.1</a>
    - <a href="#bugfixes-10">Bugfixes</a>
- <a href="#v0-3-0">v0\.3\.0</a>
    - <a href="#minor-changes-6">Minor Changes</a>
- <a href="#v0-2-0">v0\.2\.0</a>
    - <a href="#minor-changes-7">Minor Changes</a>
- <a href="#v0-1-1">v0\.1\.1</a>
    - <a href="#minor-changes-8">Minor Changes</a>
- <a href="#v0-1-0">v0\.1\.0</a>
    - <a href="#minor-changes-9">Minor Changes</a>

<a id="v0-8-0"></a>
## v0\.8\.0

<a id="minor-changes"></a>
### Minor Changes

* On Gentoo\, the <code>policykit</code> USE flag\, which creates the <code>libvirt</code> group\, is requested on <code>app\-emulation/libvirt</code> and <code>sys\-apps/systemd</code> only when <code>libvirt\_users</code> is not empty\. With an empty list the daemon stays reachable by root alone\.
* The archive Galaxy installs no longer holds the test scenarios\, the CI configuration and the contributor files\.
* The role\'s metadata now declares the platforms its tests run on\: Debian trixie and EL 10 are added\, and Debian bullseye\, which is neither tested nor supported upstream any more\, is dropped\.
* <code>libvirt\_</code> now names only what an inventory may set\: every variable\, fact\, register and loop variable the role keeps for itself carries <code>\_libvirt\_</code>\. A playbook that read one of those\, such as <code>libvirt\_layout</code> \(now <code>\_libvirt\_daemon\_layout</code>\)\, has to follow the new name\, and none of them is part of the role\'s interface\. \([\#6](https\://gitlab\.com/yoanncolin/ansible/roles/libvirt/\-/issues/6)\)

<a id="breaking-changes--porting-guide"></a>
### Breaking Changes / Porting Guide

* The role needs <code>ansible\-core</code> 2\.20 or later\, up from 2\.18\. Earlier versions read a Gentoo host as ClearLinux\, so none of the role\'s variables for it were loaded\.
* The variable that picks firewalld\'s packet filtering backend is <code>libvirt\_firewall\_backend</code>\, no longer <code>firewall\_backend</code>\. An inventory that sets the old name keeps firewalld\'s own backend until it is renamed\. \([\#6](https\://gitlab\.com/yoanncolin/ansible/roles/libvirt/\-/issues/6)\)
* With <code>libvirt\_manage\_firewall</code> true\, the role opens the <code>libvirt</code> firewalld service only when <code>libvirt\_config\.libvirtd\.listen\_tcp</code> is 1\, and the migration range <code>49152\-49215/tcp</code> only when the new <code>libvirt\_firewall\_migration</code> is true\, where it opened both on every host before\. A host that migrates or takes TCP connections must set them\. A host already converged keeps both entries open\, since the role closes neither of them\; close them with <code>firewall\-cmd \-\-permanent \-\-remove\-service\=libvirt</code>\, <code>firewall\-cmd \-\-permanent \-\-remove\-port\=49152\-49215/tcp</code> and <code>firewall\-cmd \-\-reload</code>\, adding <code>\-\-zone\=\<zone\></code> to the first two when <code>libvirt\_firewall\_zone</code> is set\. \([\#12](https\://gitlab\.com/yoanncolin/ansible/roles/libvirt/\-/issues/12)\)
* <code>libvirt\_config\.libvirtd\.listen\_tcp</code> set to 1 now makes the daemon listen\, as <code>listen\_tls</code> does\: the role enables the TCP socket unit\. A host whose inventory already sets it listens on <code>16509/tcp</code>\, unencrypted\, and libvirt\'s default <code>auth\_tcp</code> is <code>sasl</code>\, so clients are refused until SASL is set up\. \([\#31](https\://gitlab\.com/yoanncolin/ansible/roles/libvirt/\-/issues/31)\)
* <code>libvirt\_users</code> defaults to <code>\[\]</code>\, so the account Ansible connects as is no longer added to the <code>libvirt</code>\, <code>kvm</code> and <code>qemu</code> groups and no longer gets a <code>qemu\:///session</code> default pool\. Memberships already granted stay\. To keep the previous behaviour\, set <code>libvirt\_users</code> to <code>\[\{name\: \"\{\{ ansible\_facts\.user\_id \}\}\"\}\]</code>\, and list the account that provisions over <code>qemu\:///system</code> when it is not root\. \([\#2](https\://gitlab\.com/yoanncolin/ansible/roles/libvirt/\-/issues/2)\)

<a id="bugfixes"></a>
### Bugfixes

* On Gentoo\, <code>libvirt\_manage\_firewall\: false</code> no longer stops the play when the USE flags are written\.
* On Gentoo\, firewalld is restarted after the packages are built\, so it knows the <code>libvirt</code> zone libvirt installs and the network driver can start a network\.
* On Gentoo\, with the firewall managed\, the role declares the <code>json</code>\, <code>python</code> and <code>xtables</code> USE flags that <code>net\-firewall/nftables</code> needs for firewalld\, so the installation no longer stops asking for them\.
* The role waits for libvirtd only when something restarted it\. On Gentoo it no longer blocks on a daemon that nobody had started yet\.
* firewalld no longer keeps <code>19215\-49152/tcp</code>\, the mistyped migration range that 0\.3\.0 to 0\.6\.2 opened instead of the real one\. The role removes that entry\, and only it\, from the zone it manages\, reloads firewalld and warns once per host\. Run the role once on every host that predates 0\.7\.0 before upgrading to 1\.0\.0\, which drops this cleanup\. \([\#5](https\://gitlab\.com/yoanncolin/ansible/roles/libvirt/\-/issues/5)\)

<a id="v0-7-0"></a>
## v0\.7\.0

<a id="minor-changes-1"></a>
### Minor Changes

* A <code>libvirt\_users</code> entry takes <code>ca\_file</code>\, <code>clientcert</code> and <code>clientkey</code>\, deployed under the user\'s <code>\~/\.pki</code> with the least privileges\, so the user reaches a remote daemon over TLS\.
* Add <code>libvirt\_config</code>\, which writes directives to <code>/etc/libvirt/\<file\>\.conf</code>\.
* Configure the daemon over TLS\. <code>libvirt\_ca\_file</code>\, <code>libvirt\_servercert</code>\, <code>libvirt\_serverkey</code>\, <code>libvirt\_clientcert</code> and <code>libvirt\_clientkey</code> deploy the certificates and keys from the controller to libvirt\'s standard locations\.
* On Gentoo\, <code>app\-emulation/qemu</code> is built with <code>virtfs</code> for the <code>qemu</code> backend\.
* Re\-running the role after rotating the CA restarts the daemon that serves TLS\.
* The role detects whether the host runs the monolithic daemon or the modular ones from the installed units\, and manages the services in a single place\.
* The tags <code>ca</code> and <code>ssl</code> redeploy and apply the certificates\.
* With <code>listen\_tls</code> enabled\, the role starts the TLS socket of the daemon and opens the <code>libvirt\-tls</code> firewalld service\.

<a id="breaking-changes--porting-guide-1"></a>
### Breaking Changes / Porting Guide

* Domains follow libvirt\'s XML structure\: <code>disks\[\]\.size\: 2G</code> becomes <code>disks\[\]\.capacity\: 2G</code> and <code>networks\: \[\.\.\.\]</code> becomes <code>interfaces\: \[\.\.\.\]</code>\.
* Each entry of <code>libvirt\_users</code> is a dictionary\, so <code>\- alice</code> becomes <code>\- \{name\: alice\}</code>\.
* Networks follow libvirt\'s XML structure\: <code>forward\_mode\: nat</code> becomes <code>forward\: \{mode\: nat\}</code>\, <code>bridge\: virbr0</code> becomes <code>bridge\: \{name\: virbr0\}</code>\, <code>ip\: \{address\, netmask\}</code> becomes <code>ips\: \[\{address\, netmask\}\]</code> and <code>ip\.dhcp\: \{start\, end\}</code> becomes <code>ips\[\]\.dhcp\.ranges\: \[\{start\, end\}\]</code>\.
* Pools follow libvirt\'s XML structure\: <code>path\: \.\.\.</code> becomes <code>target\: \{path\: \.\.\.\}</code>\, <code>owner</code>\, <code>group</code> and <code>mode</code> move under <code>target\.permissions</code>\, <code>source\.host\: server</code> becomes <code>source\.hosts\: \[\{name\: server\}\]</code>\, <code>source\.dir\: /export</code> becomes <code>source\.dir\: \{path\: /export\}</code>\, <code>source\.type\: nfs</code> becomes <code>source\.format\: \{type\: nfs\}</code> and <code>source\.protocol\: 4</code> becomes <code>source\.protocol\: \{ver\: 4\}</code>\.
* The role requires ansible\-core 2\.18 or later\, and no longer claims 2\.13\.
* Volumes follow libvirt\'s XML structure\: <code>size\: 200G</code> becomes <code>capacity\: 200G</code> and <code>format\: qcow2</code> becomes <code>target\: \{format\: \{type\: qcow2\}\}</code>\.

<a id="bugfixes-1"></a>
### Bugfixes

* A pool under a user\'s home is reachable by the QEMU user\, which gets an execute\-only ACL on the home directories leading to it\.
* The libvirt sockets start from the installed unit files\, so <code>qemu\:///system</code> has its socket on a fresh install\.
* The package <code>bridge\-utils</code> is no longer installed on EL9 and later and on Arch Linux\, where it no longer exists\.
* The role declares the <code>ansible\.posix</code> and <code>community\.general</code> collections it uses\.
* The role opens the migration port range <code>49152\-49215/tcp</code>\, where it opened <code>19215\-49152/tcp</code> before\.
* The role reads the facts of the provisioned resources from <code>ansible\_facts\.libvirt\_pools</code> and <code>ansible\_facts\.libvirt\_networks</code>\, which ansible\-core 2\.19 and later require\.
* The role reloads dbus instead of restarting it\, which dropped every connected client and wedged the desktop\.
* The tag <code>users</code> reaches all the user access tasks\, and no longer stops on an undefined <code>libvirt\_system\_groups</code>\.

<a id="v0-6-2"></a>
## v0\.6\.2

<a id="bugfixes-2"></a>
### Bugfixes

* The <code>source</code> of a <code>netfs</code> pool follows libvirt\'s XML\, where <code>source\.version</code> becomes <code>source\.protocol</code> and <code>source\.format</code> becomes <code>source\.type</code>\.

<a id="v0-6-1"></a>
## v0\.6\.1

<a id="bugfixes-3"></a>
### Bugfixes

* The role activates only the libvirt units the host provides\. Debian bookworm ships libvirt 6\.0 or later without the modular daemon units\, and the role no longer fails on them\.

<a id="v0-6-0"></a>
## v0\.6\.0

<a id="minor-changes-2"></a>
### Minor Changes

* <code>netfs</code> pools support NFS and CIFS\, and the NFS version\.

<a id="v0-5-1"></a>
## v0\.5\.1

<a id="bugfixes-4"></a>
### Bugfixes

* The role manages the services of libvirt whether the distribution ships the modular daemons or the monolithic one\.

<a id="v0-5-0"></a>
## v0\.5\.0

<a id="minor-changes-3"></a>
### Minor Changes

* Add <code>libvirt\_default\_disk\_format</code>\, which defaults to <code>qcow2</code>\.
* Add the cached facts <code>libvirt\_system\_users</code> and <code>libvirt\_system\_groups</code>\.
* Each storage pool takes an explicit owner\, group and mode\.
* Package lists are updated across distributions\.
* Pool permissions are resolved with <code>getent</code> instead of shell commands\.
* The role configures QEMU\'s security driver\, AppArmor or SELinux\, by itself\.
* The role reads facts from the <code>ansible\_facts</code> namespace\.
* The role requires <code>community\.libvirt</code> 2\.0 or later\.
* The role waits for libvirtd to answer after restarting it\.
* The volume format is written in the volume XML\.

<a id="breaking-changes--porting-guide-2"></a>
### Breaking Changes / Porting Guide

* The default type of a domain disk changes from <code>volume</code> to <code>file</code>\.
* The internal variable <code>pools</code> is renamed <code>libvirt\_pools</code>\, which affects custom task includes\.
* The loop variable <code>pool</code> is renamed <code>libvirt\_pool</code> in the pool templates\.

<a id="v0-4-3"></a>
## v0\.4\.3

<a id="bugfixes-5"></a>
### Bugfixes

* <code>libvirt\_dnsmasq\_interface\_types</code> defaults to <code>\[ether\]</code>\, so dnsmasq no longer binds bonding interfaces\.

<a id="v0-4-2"></a>
## v0\.4\.2

<a id="bugfixes-6"></a>
### Bugfixes

* The dnsmasq binding finds the network interfaces whose name holds a dash\.

<a id="v0-4-1"></a>
## v0\.4\.1

<a id="bugfixes-7"></a>
### Bugfixes

* On Arch Linux\, firewalld uses the <code>iptables\-nft</code> backend instead of <code>iptables</code>\.

<a id="v0-4-0"></a>
## v0\.4\.0

<a id="minor-changes-4"></a>
### Minor Changes

* Raw block devices can be attached to domains\, system wide\.

<a id="bugfixes-8"></a>
### Bugfixes

* dnsmasq no longer prevents libvirt\'s default network from starting\. <code>libvirt\_dnsmasq\_management\_method</code> \(<code>auto</code>\, <code>bind</code>\, <code>disable</code> or <code>none</code>\) chooses what the role does with dnsmasq\, and <code>libvirt\_dnsmasq\_interface\_types</code> lists the interface types it binds\. <code>auto</code> binds dnsmasq on Debian bookworm and leaves it alone elsewhere\.

<a id="v0-3-3"></a>
## v0\.3\.3

<a id="bugfixes-9"></a>
### Bugfixes

* Check mode no longer fails on the tasks that read the state of domains\, pools\, services and the QEMU user\.

<a id="v0-3-2"></a>
## v0\.3\.2

<a id="minor-changes-5"></a>
### Minor Changes

* The tag <code>users</code> runs the user access tasks alone\.

<a id="v0-3-1"></a>
## v0\.3\.1

<a id="bugfixes-10"></a>
### Bugfixes

* The tag <code>provision</code> selects the provisioning tasks\, and only them\.

<a id="v0-3-0"></a>
## v0\.3\.0

<a id="minor-changes-6"></a>
### Minor Changes

* Gentoo is supported\, including its Portage USE flags\.
* The role opens the <code>libvirt</code> and <code>libvirt\-tls</code> firewalld services and the migration port range\, in the zone <code>libvirt\_firewall\_zone</code> names\. Setting <code>libvirt\_manage\_firewall</code> to <code>false</code> leaves the firewall alone\.

<a id="v0-2-0"></a>
## v0\.2\.0

<a id="minor-changes-7"></a>
### Minor Changes

* Domains take an <code>autostart</code> key to start with the host\.

<a id="v0-1-1"></a>
## v0\.1\.1

<a id="minor-changes-8"></a>
### Minor Changes

* Domain disks and network interfaces take a <code>boot\_order</code>\. A domain no longer forces a boot from the network then the disk\, so a domain without any <code>boot\_order</code> boots as libvirt decides\.

<a id="v0-1-0"></a>
## v0\.1\.0

<a id="minor-changes-9"></a>
### Minor Changes

* First release\. The role installs libvirt with the <code>qemu</code> backend\, grants <code>libvirt\_users</code> access to it\, and provisions the storage pools\, volumes\, networks and domains listed in <code>libvirt\_pools</code>\, <code>libvirt\_volumes</code>\, <code>libvirt\_networks</code> and <code>libvirt\_domains</code>\.
