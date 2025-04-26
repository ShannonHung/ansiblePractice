# plugins/action/check_node_status.py

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleError
import json

class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = {}

        result = dict(
            changed=False,
            desired_missing_list=[],
            current_missing_list=[],
            ping_failed_list=[],
            unhealthy_label_list=[],
            node_not_ready_list=[],
            unhealthy_node_list=[],
        )

        # 接收參數
        module_args = self._task.args.copy()
        targets = module_args.get('targets', [])
        env_config = module_args.get('env_config', None)
        desired_missing = module_args.get('desired_missing', True)
        current_missing = module_args.get('current_missing', True)
        ping_failed = module_args.get('ping_failed', True)
        unhealthy_label = module_args.get('unhealthy_label', [])
        node_not_ready = module_args.get('node_not_ready', True)

        # --- Step 1: 取得 k8s nodes ---
        rc, out, err = self._low_level_execute_command([
            'kubectl', '--context', env_config, 'get', 'nodes', '-o', 'json'
        ])
        if rc != 0:
            raise AnsibleError(f"kubectl failed: {err}")

        try:
            nodes_json = json.loads(out)
        except Exception as e:
            raise AnsibleError(f"Failed to parse kubectl output: {e}")

        k8s_node_names = [n['metadata']['name'] for n in nodes_json['items']]
        result['all_k8s_nodes'] = k8s_node_names

        # 下一步會寫邏輯來做檢查
        return result
