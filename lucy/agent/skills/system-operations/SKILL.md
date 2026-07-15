---
name: system-operations
description: Use for operating system issues, developer tooling, package management, permissions, hardware, networking, services, containers, shells and environment setup. Prefer inspecting the current system before making recommendations.
---

# Developer Workstation

## When to use

Use this skill whenever the user's request involves their machine rather than only source code. Always first identify the user's OS before trying to execute commands.

Examples:

- install or configure software
- developer environments
- Python, Node, Rust, Go
- Docker
- Git
- SSH
- displays or brightness
- speakers or microphones
- Bluetooth
- Wi-Fi
- USB devices
- drivers
- services
- permissions
- shells
- environment variables
- package management

---

## Principles

- Prefer observing before changing.
- Gather evidence from the user's machine whenever possible.
- Apply the smallest reasonable fix.
- Preserve the user's existing workflow.
- Avoid destructive operations unless explicitly requested.

---

## Investigation

Before recommending changes:

1. Identify the failing component.
2. Inspect the current system.
3. Determine the likely root cause.
4. Apply the minimum necessary change.
5. Verify the result.

Avoid guessing when the system can be inspected directly.

---

## Existing tools

Before recommending installation, check whether the required tool or alternatives are already available.

Examples:

```bash
which <tool>
<tool> --version
```

Prefer existing software over introducing new dependencies.

Before installing packages:

- identify the operating system
- identify the package manager
- check whether the package is already installed

---

## Permissions

Do not assume every permission error requires `sudo`.

Retry with `sudo` only when administrator privileges are genuinely required.

If the elevated command still fails, explain the new error instead of repeatedly retrying.

Avoid changing file permissions unless necessary.

---

## Services

For service-related issues:

- verify the service exists
- check whether it is running
- inspect logs when useful
- restart or reconfigure only when justified

---

## Response style

Be concise.

Explain:

- what you observed
- what you changed
- why the change was made