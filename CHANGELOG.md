# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-09-03

### Added

- Initial release.
- FastAPI gateway service with the codebase split into
  `domain`, `application`, and `adapters` layers, with the layering enforced in
  CI with `import-linter`.
- **Goal orchestration**. Goals are checked in on and adapted on a schedule,
  every 2 hours by default, through APScheduler, so they are not left as
  static to-do items.
- **Multi-provider LLM support**. Anthropic, OpenAI, Gemini, Mistral, xAI,
  DeepSeek, OpenRouter, and any OpenAI-compatible endpoint are supported.
  Each of three roles, primary, triage, and discovery, can be assigned its
  own model.
- **Device pairing**. On first boot, if no owner device is paired, the gateway
  logs a claim code. A Kordi client app pairs against that code as the owner,
  and the owner can invite further devices as members.
- Profile management, chat, and conversation history.
- **Connector management**. OAuth and credential handling for connectors is
  delegated to a separate service. That logic out of this process.
- `kordi` CLI with `status`, `repair`, and `reset` commands for local
  operational control.
- Local storage under `~/.kordevance`. Provider API keys and the app master
  key are held in the OS keyring, not written to disk in plaintext.
- Signed and notarized macOS `.pkg` installers for arm64 and x86_64, a
  Windows installer that sets up a Windows service, and a Linux installer,
  run with `curl | sh`, that sets up a systemd service. Each platform also
  has a matching uninstaller.
- CI checks on every change: ruff and mypy.