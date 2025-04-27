# ~/.ansible/collections/ansible_collections/my_namespace/my_collection/plugins/inventory/my_plugin.py

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.inventory import BaseInventoryPlugin
from ansible.errors import AnsibleError

DOCUMENTATION = r'''
name: my_plugin
plugin_type: inventory
short_description: My custom inventory plugin
description: >
    This plugin adds a hello group with one host called world-node.
options:
  plugin:
    description: The name of the plugin
    required: true
    choices: ['my_namespace.my_collection.my_plugin']
'''

class InventoryModule(BaseInventoryPlugin):

    NAME = 'my_plugin'

    def verify_file(self, path):
        return path.endswith(('inventory.ini', 'my_inventory.yaml'))

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path)
        # Debugging line to check if parse is called
        self.display.display("Parsing inventory file: {}".format(path))

        # 建立 hello 群組
        self.inventory.add_group('hello')

        # 加入 world-node
        self.inventory.add_host('world-node', group='hello')
