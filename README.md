# Lucy

A terminal-native AI coding copilot focused on fast, transparent, and low-friction software development.

Lucy combines an LLM with local tools, live progress updates, and explicit user approvals to provide an interactive coding experience directly from your terminal.

> **Status:** v1.0.0 (Initial Release)

---

## Features

- 🤖 GPT-5.4-mini powered coding assistant
- 🛠️ Secure local tool execution
- 🔒 Explicit approval for sensitive operations
- 📦 Modular Agent Skills architecture
- ⚡ Live tool execution progress
- 📝 Persistent command history
- 🔑 Secure API key management (`lucy login`)
- 🖥️ Cross-platform support (Linux, macOS, Windows)

---

## Installation

### Option 1 — Install directly from GitHub

```bash
pip install git+https://github.com/aryan-bodhe/lucy.git
```

### Option 2 — Clone the repository

```bash
git clone https://github.com/aryan-bodhe/lucy.git
cd lucy
pip install .
```

---

## Setup

Authenticate with your OpenAI API key:

```bash
lucy login
```

You can create an API key here:

https://platform.openai.com/api-keys

---

## Usage

Start an interactive session:

```bash
lucy
```

Login with your OpenAI API key:

```bash
lucy login
```

Logout and remove your stored credentials:

```bash
lucy logout
```

Show available commands:

```bash
lucy --help
```

Display version:

```bash
lucy --version
```

---

## Requirements

- Python 3.11+
- OpenAI API Key

---

## Security

Lucy never executes sensitive operations without asking for confirmation.

Your API key is stored using your operating system's secure credential storage (Keychain, Credential Manager, Secret Service/KWallet) when available.

---

## Roadmap

- Parallel tool execution improvements
- Better interruption support
- Installation diagnostics (`lucy doctor`)
- Additional model providers
- Additional Agent Skills

---

## Contributing

Issues and pull requests are welcome.

For development:

```bash
git clone https://github.com/aryan-bodhe/lucy.git
cd lucy
pip install -e .
```

---

## License

MIT