## Reporting a vulnerability

Please do not open a public issue for security vulnerabilities.

Report it privately instead, through GitHub's security advisory form for this
repository: https://github.com/Kordevance/kordevance-agent/security/advisories/new

This is a solo-maintained project, so I cannot promise fixed response times,
but I will get to it as soon as I can and keep you posted.

Kordi Gateway is self-hosted. It stores your goals, conversations, and
provider API keys locally under `~/.kordevance`, with secrets such as API keys
and the app master key kept in the OS keyring rather than in plaintext.
Vulnerabilities that could expose that data, bypass device pairing, or affect
the installer and release pipeline are all in scope.