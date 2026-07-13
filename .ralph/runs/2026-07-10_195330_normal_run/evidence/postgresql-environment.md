# PostgreSQL Environment Evidence

- Installed server binary: PostgreSQL 14.20 (Homebrew).
- Installed Django driver: psycopg 3.3.4.
- Homebrew service status: `postgresql@14 started` for the current OS user.
- Non-secret test settings: engine `django.db.backends.postgresql`; database default
  `sfpcl_credit`; test database default `test_sfpcl_credit`; Unix socket host `/tmp`; port `5432`;
  password omitted/unset.
- Socket file `/tmp/.s.PGSQL.5432` was visible and the host service log reported the database ready.
- Every sandboxed client attempt failed with `Operation not permitted` before authentication or test
  database creation. No credentials were printed.
- An isolated `/tmp` cluster was also attempted. PostgreSQL bootstrap failed because the sandbox
  denied its required SysV shared-memory segment (`shmget ... Operation not permitted`).

The exact combined acceptance output is in
`terminal-logs/postgresql-concurrency-acceptance.txt`. It found four tests and executed none, so it
is failure evidence, not acceptance evidence.
