#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r"""
  name: warn
  author: Yoann Gauthier-Colin <yoann@gwerlas.net>
  version_added: "0.21"
  short_description: emit a real Ansible warning from a task
  description:
      - ansible-core ships no module to warn - C(debug) prints in green and
        reads as ordinary output, C(fail) stops the play. Any task result
        carrying a C(warnings) key is surfaced by the task executor as a
        genuine C([WARNING]:), which is all this action does.
      - It runs on the controller, so it ships nothing to the target and needs
        no connection.
      - Warnings are deduplicated on their exact text, so include
        C(inventory_hostname) in the message to keep one line per host.
  options:
    msg:
      description: the warning to emit
      type: str
      required: True
"""

EXAMPLES = r"""
- name: Report unknown segments
  when: _system_unknown_profiles | length > 0
  warn:
    msg: "[{{ inventory_hostname }}] unknown: {{ _system_unknown_profiles | join(', ') }}"
"""

from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    _requires_connection = False
    _supports_check_mode = True
    _supports_async = False

    def run(self, tmp=None, task_vars=None):
        result = super(ActionModule, self).run(tmp, task_vars)
        del tmp  # legacy, unused

        msg = self._task.args.get('msg')
        if not msg:
            raise AnsibleActionFail("the 'msg' option is required")

        result['changed'] = False
        result['warnings'] = [msg]

        return result
