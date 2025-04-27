#!/usr/bin/env python

import sys
import json
from configparser import ConfigParser


def parse_ini_file(path):
    """
    解析 INI 檔案並返回符合 Ansible 動態清單格式的 JSON。
    """
    config = ConfigParser()
    config.read(path)

    # 定義基本結構
    inventory = {
        'all': {
            'children': {}
        }
    }

    # 處理每個群組
    for section in config.sections():
        group = {
            'hosts': [],
            'vars': {}
        }

        # 如果這是變數區塊
        if ':' in section:
            group_name = section.split(':')[0]
            for option in config.options(section):
                # 加入變數
                group['vars'][option] = config.get(section, option)
            inventory['all']['children'][group_name] = group
        else:
            # 加入主機
            for option in config.options(section):
                host_info = config.get(section, option)
                group['hosts'].append(option)

            inventory['all']['children'][section] = group

    return inventory


def main():
    # 設定 INI 檔案路徑
    inventory_file = '/Users/shannon/Documents/Code/ansible/inventory.ini'

    # 解析 INI 檔案並返回 JSON 結果
    inventory = parse_ini_file(inventory_file)

    # 輸出為 JSON 格式
    print(json.dumps(inventory, indent=2))


if __name__ == '__main__':
    main()
