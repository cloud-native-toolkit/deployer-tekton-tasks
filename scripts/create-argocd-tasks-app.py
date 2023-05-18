from pathlib import Path
import yaml
import os


def is_tekton_task(filename):
  with open(filename, 'r') as stream:
    try:
      content = yaml.safe_load(stream)

      return 'tekton.dev' in content['apiVersion'] and content['kind'] == 'Task'
    except yaml.YAMLError as exc:
      pass
      # print(
      #     f"Ignoring {filename}. Unlikely to be a Tekton Task if it contains more than 1 manifest.")


tasks_app= yaml.safe_load("""
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: tasks
  namespace: openshift-gitops
  annotations:
    argocd.argoproj.io/sync-wave: '10'
  labels:
    app.kubernetes.io/instance: bootstrap
spec:
  project: default
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  sources: []
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
""")


for path in Path('tasks').rglob('*.yaml'):
  is_task = is_tekton_task(path.absolute())
  
  if is_task:
    tasks_app['spec']['sources'].append({
        'repoURL': f"{os.environ['GITHUB_SERVER_URL']}/{os.environ['GITHUB_REPOSITORY']}.git",
        'targetRevision': f"{os.environ['GITHUB_REF_NAME']}",
        'path': os.path.dirname(path.absolute())
    })
  
print(yaml.safe_dump(tasks_app))