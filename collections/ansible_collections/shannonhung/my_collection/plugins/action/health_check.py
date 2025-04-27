from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import json
from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError


def _parse_kubectl_nodes(output):
    try:
        data = json.loads(output)
        nodes = {}
        for item in data.get('items', []):
            name = item['metadata']['name']
            labels = item['metadata'].get('labels', {})
            conditions = item['status'].get('conditions', [])
            ready_status = 'False'
            for cond in conditions:
                if cond.get('type') == 'Ready':
                    ready_status = cond.get('status', 'False')
                    break
            nodes[name] = {
                'labels': labels,
                'ready': ready_status
            }
        return nodes
    except Exception as e:
        raise AnsibleError(f"Failed to parse kubectl nodes output: {str(e)}")


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = {}

        # 取得參數
        targets = self._task.args.get('targets', [])
        envconfig = self._task.args.get('envconfig', "")
        desired_missing = self._task.args.get('desired_missing', True)
        current_missing = self._task.args.get('current_missing', True)
        unhealthy_label = self._task.args.get('unhealthy_label', [])
        node_not_ready = self._task.args.get('node_not_ready', True)

        if not targets:
            raise AnsibleError("Missing required parameter: targets")

        results = {
            "desired_missing_list": [],
            "current_missing_list": [],
            "unhealthy_label_list": [],
            "node_not_ready_list": [],
            "unhealthy_node_list": []
        }

        # Step 1: 取得 k8s nodes
        rc, kube_output, err = self._execute_kubectl_get_nodes(envconfig)
        if rc != 0:
            raise AnsibleError(f"Failed to run kubectl get nodes: {err}")

        kube_nodes_info = _parse_kubectl_nodes(kube_output)
        kube_node_names = set(kube_nodes_info.keys())

        # Step 3: 開始比對整理

        # desired_missing_list
        if desired_missing:
            desired_missing_list = [node for node in kube_node_names if node not in targets]
            results['desired_missing_list'] = desired_missing_list

        # current_missing_list
        if current_missing:
            current_missing_list = [host for host in targets if host not in kube_node_names]
            results['current_missing_list'] = current_missing_list

        # unhealthy_label_list
        if unhealthy_label:
            unhealthy_label_list = []
            for node, info in kube_nodes_info.items():
                # pydevd_pycharm.settrace('localhost', port=5566, stdoutToServer=True, stderrToServer=True)
                node_labels = info.get('labels', {})
                for label_condition in unhealthy_label:
                    for key, value in label_condition.items():
                        if node_labels.get(key) == value:
                            unhealthy_label_list.append(node)
                            break
            results['unhealthy_label_list'] = unhealthy_label_list

        # node_not_ready_list
        if node_not_ready:
            node_not_ready_list = [node for node, info in kube_nodes_info.items()
                                   if info.get('ready', '').lower() != 'true']
            results['node_not_ready_list'] = node_not_ready_list

        # unhealthy_node_list: 統整所有 unique 的
        combined = set()
        combined.update(results['desired_missing_list'])
        combined.update(results['current_missing_list'])
        combined.update(results['unhealthy_label_list'])
        combined.update(results['node_not_ready_list'])
        results['unhealthy_node_list'] = list(combined)

        return {
            "changed": False,
            "results": results
        }

    def _execute_kubectl_get_nodes(self, env_config):
        cmd = ['kubectl', f'--context={env_config}', 'get', 'nodes', '-o', 'json']
        rc, out, err = self._module_execution('command',
                                              {'_raw_params': ' '.join(cmd)}
                                              )
        return rc, out, err

    def _module_execution(self, module_name, module_args=None, task_vars=None):
        res = self._execute_module(
            module_name=module_name,
            module_args=module_args,
            task_vars=task_vars
        )
        rc = res.get('rc', 1)
        out = res.get('stdout', '')
        err = res.get('stderr', '')
        return rc, out, err
