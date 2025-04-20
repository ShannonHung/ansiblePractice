#!/usr/bin/env python3

import argparse
import subprocess
import json
import re
from pathlib import Path

import sys
sys.argv = [
    "check_cluster_nodes.py",
    "--context=kind-app-1-cluster",
    "--inventory=/Users/shannon/Documents/Code/ansible/inventory.ini"
]

def main():
    print("hello")
    parser = argparse.ArgumentParser()
    parser.add_argument('--context', required=True, help='Kubernetes context')
    parser.add_argument('--inventory', default='inventory.ini', help='Path to inventory file')
    args = parser.parse_args()

    context = args.context
    inventory_file = Path(args.inventory)

    # Step 1: 取得 cluster 的 node 名稱
    try:
        kubectl_cmd = [
            "/usr/local/bin/kubectl", f"--context={context}", "get", "nodes",
            "-o", "jsonpath={.items[*].metadata.name}"
        ]
        result = subprocess.run(kubectl_cmd, capture_output=True, text=True, check=True)
        cluster_nodes = result.stdout.strip().split()
    except subprocess.CalledProcessError as e:
        print(json.dumps({
            "error": "Failed to run kubectl",
            "stderr": e.stderr,
        }))
        return

    # Step 2: 解析 inventory，抓出 app-1-cluster-* 名稱
    inventory_nodes = []
    pattern = re.compile(r"^(app-1-cluster[^\s]+)")

    with open(inventory_file) as f:
        for line in f:
            match = pattern.match(line.strip())
            if match:
                inventory_nodes.append(match.group(1))

    # Step 3: 比對
    cluster_set = set(cluster_nodes)
    inventory_set = set(inventory_nodes)

    inventory_missing = sorted(cluster_set - inventory_set)
    cluster_missing = sorted(inventory_set - cluster_set)

    print(json.dumps({
        "inventory_missing": inventory_missing,
        "cluster_missing": cluster_missing,
    }))


if __name__ == "__main__":
    main()
