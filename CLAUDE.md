# Claude Code Rules (Python-only)

## Scope
You are ONLY allowed to create/edit Python application code and Python tests.

Allowed:
- *.py
- pyproject.toml / poetry.lock / requirements*.txt
- README.md (only for Python usage/docs)
- config templates under /configs (yaml/json) IF used by Python at runtime

Not allowed:
- Dockerfile, docker-compose.yml, any container build files
- Kubernetes manifests, Helm charts, Kustomize
- Terraform, CloudFormation, Pulumi, Ansible
- GitHub Actions / Jenkinsfile / CI/CD pipelines
- Any changes under /infra, /k8s, /helm, /deploy, /terraform, /ansible

## If a task touches infra:
Stop and respond with: "Infra changes are out of scope. I can provide app-side changes only."

## Coding requirements
- Use FastAPI for services unless otherwise noted
- Add unit tests (pytest) for new logic
- Type hints for public functions
- Structured logging (json) and correlation IDs
- Keep dependencies minimal

## Workflow
- Always propose file list + plan first
- Then implement in small commits/steps
