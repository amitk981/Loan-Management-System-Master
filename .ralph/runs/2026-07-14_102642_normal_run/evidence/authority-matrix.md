# Legal-document authority matrix

| Public caller | Generate | Template reference | Active actor | Application scope | Result before template/frozen/storage reads |
|---|---:|---:|---:|---:|---|
| Direct module | no | yes/no | yes | any | `FORBIDDEN`, zero writes |
| Direct module | yes | no | yes | any | `FORBIDDEN`, zero writes |
| Direct module | yes | yes | no | any | `FORBIDDEN`, zero writes |
| Direct module | yes | yes | yes | no | `OBJECT_ACCESS_DENIED`, zero writes |
| HTTP POST | yes | yes | yes | yes | exact §26.4 success object |
| Direct module replay | yes | yes | yes | yes | same retained result, no new evidence |

Read collection uses the same direct/HTTP module boundary. Missing `documents.loan_document.read`
returns `FORBIDDEN`; unrelated application scope returns `OBJECT_ACCESS_DENIED`; the legal selector
is not called before both checks pass.

Evidence: `red-*authority.txt`, `green-*authority.txt`, `red-direct-object-scope.txt`,
`green-direct-object-scope.txt`, `red-direct-read-scope.txt`, `green-direct-read-scope.txt`, and
`green-complete-legal-document-suite.txt` in `terminal-logs/`.
