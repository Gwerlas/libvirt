# gwerlas\.libvirt Release Notes

**Topics**

- <a href="#v0-7-0">v0\.7\.0</a>
    - <a href="#breaking-changes--porting-guide">Breaking Changes / Porting Guide</a>

<a id="v0-7-0"></a>
## v0\.7\.0

<a id="breaking-changes--porting-guide"></a>
### Breaking Changes / Porting Guide

* Domains follow libvirt\'s XML structure\: <code>disks\[\]\.size\: 2G</code> becomes <code>disks\[\]\.capacity\: 2G</code> and <code>networks\: \[\.\.\.\]</code> becomes <code>interfaces\: \[\.\.\.\]</code>\.
* Networks follow libvirt\'s XML structure\: <code>forward\_mode\: nat</code> becomes <code>forward\: \{mode\: nat\}</code>\, <code>bridge\: virbr0</code> becomes <code>bridge\: \{name\: virbr0\}</code>\, <code>ip\: \{address\, netmask\}</code> becomes <code>ips\: \[\{address\, netmask\}\]</code> and <code>ip\.dhcp\: \{start\, end\}</code> becomes <code>ips\[\]\.dhcp\.ranges\: \[\{start\, end\}\]</code>\.
* Pools follow libvirt\'s XML structure\: <code>path\: \.\.\.</code> becomes <code>target\: \{path\: \.\.\.\}</code>\, <code>owner</code>\, <code>group</code> and <code>mode</code> move under <code>target\.permissions</code>\, <code>source\.host\: server</code> becomes <code>source\.hosts\: \[\{name\: server\}\]</code>\, <code>source\.dir\: /export</code> becomes <code>source\.dir\: \{path\: /export\}</code>\, <code>source\.type\: nfs</code> becomes <code>source\.format\: \{type\: nfs\}</code> and <code>source\.protocol\: 4</code> becomes <code>source\.protocol\: \{ver\: 4\}</code>\.
* Volumes follow libvirt\'s XML structure\: <code>size\: 200G</code> becomes <code>capacity\: 200G</code> and <code>format\: qcow2</code> becomes <code>target\: \{format\: \{type\: qcow2\}\}</code>\.
