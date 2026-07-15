# Visual Evidence Attempt

Authenticated MP11 screenshots could not be captured in the coding sandbox because it denied both
required localhost listeners:

- Django `127.0.0.1:8000`: `Error: [Errno 1] Operation not permitted`
- Vite `127.0.0.1:5173`: `listen EPERM: operation not permitted`

The unedited launch output is retained in `evidence/terminal-logs/backend-localhost-server.log` and
`evidence/terminal-logs/frontend-localhost-server.log`. No screenshots were fabricated. The UI
composition and its loading, empty, 401, 403, validation, upload-progress, success, re-upload,
download, and resubmit states are covered by the focused component tests; independent validation
outside this sandbox remains the place to capture mobile visuals.
