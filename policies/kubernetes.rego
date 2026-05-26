package main

is_workload {
  input.kind == "Deployment"
}

containers[c] {
  is_workload
  c := input.spec.template.spec.containers[_]
}

deny[msg] {
  is_workload
  not input.spec.template.spec.securityContext.runAsNonRoot
  msg := sprintf("%s/%s must set pod securityContext.runAsNonRoot=true", [input.kind, input.metadata.name])
}

deny[msg] {
  is_workload
  input.spec.template.spec.automountServiceAccountToken != false
  msg := sprintf("%s/%s must set automountServiceAccountToken=false unless API access is required", [input.kind, input.metadata.name])
}

deny[msg] {
  is_workload
  input.spec.template.spec.securityContext.seccompProfile.type != "RuntimeDefault"
  msg := sprintf("%s/%s must use seccompProfile RuntimeDefault", [input.kind, input.metadata.name])
}

deny[msg] {
  c := containers[_]
  not c.resources.requests.cpu
  msg := sprintf("container %s must define resources.requests.cpu", [c.name])
}

deny[msg] {
  c := containers[_]
  not c.resources.requests.memory
  msg := sprintf("container %s must define resources.requests.memory", [c.name])
}

deny[msg] {
  c := containers[_]
  not c.resources.limits.cpu
  msg := sprintf("container %s must define resources.limits.cpu", [c.name])
}

deny[msg] {
  c := containers[_]
  not c.resources.limits.memory
  msg := sprintf("container %s must define resources.limits.memory", [c.name])
}

deny[msg] {
  c := containers[_]
  not c.securityContext.runAsNonRoot
  msg := sprintf("container %s must set securityContext.runAsNonRoot=true", [c.name])
}

deny[msg] {
  c := containers[_]
  c.securityContext.allowPrivilegeEscalation
  msg := sprintf("container %s must set allowPrivilegeEscalation=false", [c.name])
}

deny[msg] {
  c := containers[_]
  c.securityContext.privileged
  msg := sprintf("container %s must not run privileged", [c.name])
}

deny[msg] {
  c := containers[_]
  not c.securityContext.readOnlyRootFilesystem
  msg := sprintf("container %s should use readOnlyRootFilesystem=true", [c.name])
}

deny[msg] {
  c := containers[_]
  not drops_all_capabilities(c)
  msg := sprintf("container %s must drop all Linux capabilities", [c.name])
}

drops_all_capabilities(c) {
  c.securityContext.capabilities.drop[_] == "ALL"
}

deny[msg] {
  c := containers[_]
  endswith(c.image, ":latest")
  msg := sprintf("container %s must not use the latest image tag", [c.name])
}

deny[msg] {
  c := containers[_]
  c.image == "IMAGE_PLACEHOLDER"
  msg := sprintf("container %s must be rendered with a real image before policy check", [c.name])
}

deny[msg] {
  c := containers[_]
  not c.readinessProbe
  msg := sprintf("container %s must define a readinessProbe", [c.name])
}

deny[msg] {
  c := containers[_]
  not c.livenessProbe
  msg := sprintf("container %s must define a livenessProbe", [c.name])
}

deny[msg] {
  is_workload
  volume := input.spec.template.spec.volumes[_]
  volume.hostPath
  msg := sprintf("%s/%s must not use hostPath volumes", [input.kind, input.metadata.name])
}
