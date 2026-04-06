with open('/etc/kubernetes/manifests/kube-scheduler.yaml', 'r') as f:
    content = f.read()
if 'name: ml-scheduler-config' not in content:
    content = content.replace(
        '    - mountPath: /etc/kubernetes/scheduler.conf\n      name: kubeconfig\n      readOnly: true',
        '    - mountPath: /etc/kubernetes/scheduler.conf\n      name: kubeconfig\n      readOnly: true\n    - mountPath: /etc/kubernetes/ml-scheduler-config.yaml\n      name: ml-scheduler-config\n      readOnly: true'
    )
    content = content.replace(
        '  - hostPath:\n      path: /etc/kubernetes/scheduler.conf\n      type: FileOrCreate\n    name: kubeconfig',
        '  - hostPath:\n      path: /etc/kubernetes/scheduler.conf\n      type: FileOrCreate\n    name: kubeconfig\n  - hostPath:\n      path: /etc/kubernetes/ml-scheduler-config.yaml\n      type: File\n    name: ml-scheduler-config'
    )
    with open('/etc/kubernetes/manifests/kube-scheduler.yaml', 'w') as f:
        f.write(content)
    print('Volume mount added.')
else:
    print('Volume mount already present, skipping.')