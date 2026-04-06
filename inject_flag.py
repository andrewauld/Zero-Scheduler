with open('/etc/kubernetes/manifests/kube-scheduler.yaml', 'r') as f:
    content = f.read()
if '--config=/etc/kubernetes/ml-scheduler-config.yaml' not in content:
    content = content.replace(
        '    - kube-scheduler',
        '    - kube-scheduler\n    - --config=/etc/kubernetes/ml-scheduler-config.yaml',
        1
    )
    with open('/etc/kubernetes/manifests/kube-scheduler.yaml', 'w') as f:
        f.write(content)
    print('Config flag injected.')
else:
    print('Config flag already present, skipping.')