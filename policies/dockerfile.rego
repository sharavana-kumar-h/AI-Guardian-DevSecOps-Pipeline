package main

# Dockerfile policy checks for Day 5.
# Conftest Dockerfile parser exposes each instruction with Cmd and Value fields.

instruction_value(instr) = value {
  value := lower(concat(" ", instr.Value))
}

deny[msg] {
  instr := input[_]
  lower(instr.Cmd) == "from"
  contains(instruction_value(instr), ":latest")
  msg := "Dockerfile must not use the latest tag for base images"
}

deny[msg] {
  not has_user_instruction
  msg := "Dockerfile must define a non-root USER instruction"
}

deny[msg] {
  instr := input[_]
  lower(instr.Cmd) == "user"
  user := instruction_value(instr)
  user == "root"
  msg := "Dockerfile USER must not be root"
}

deny[msg] {
  instr := input[_]
  lower(instr.Cmd) == "run"
  value := instruction_value(instr)
  contains(value, "apt-get install")
  not contains(value, "--no-install-recommends")
  msg := "apt-get install must use --no-install-recommends"
}

deny[msg] {
  instr := input[_]
  lower(instr.Cmd) == "run"
  value := instruction_value(instr)
  contains(value, "apt-get install")
  not contains(value, "rm -rf /var/lib/apt/lists")
  msg := "apt package cache must be removed in the same RUN instruction"
}

deny[msg] {
  not has_healthcheck
  msg := "Dockerfile must define a HEALTHCHECK instruction"
}

has_user_instruction {
  instr := input[_]
  lower(instr.Cmd) == "user"
}

has_healthcheck {
  instr := input[_]
  lower(instr.Cmd) == "healthcheck"
}
