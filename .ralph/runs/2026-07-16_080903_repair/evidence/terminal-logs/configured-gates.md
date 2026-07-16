# Configured Gate Evidence

## Backend

```text
/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py check
System check identified no issues (0 silenced).

/Users/amitkallapa/LMS/.ralph/venv/bin/python manage.py makemigrations --check --dry-run
No changes detected

COVERAGE_FILE=/tmp/ralph-008m3.coverage \
  /Users/amitkallapa/LMS/.ralph/venv/bin/python -m coverage run manage.py test --verbosity 1
Ran 944 tests in 411.105s
OK (skipped=51)

COVERAGE_FILE=/tmp/ralph-008m3.coverage \
  /Users/amitkallapa/LMS/.ralph/venv/bin/python -m coverage report --fail-under=85
TOTAL 39218 statements, 3422 missed, 91%
```

## Frontend

```text
npm test -- --run
36 test files passed; 321 tests passed

npm run typecheck
passed

npm run lint
passed

npm run build
passed (existing Vite CJS/chunk-size warnings only)
```

## Integrity

`git diff --check` passed. The final audit found 22 tracked files and 1,231 changed tracked lines
against limits of 30 and 2,000, zero new dependencies, no migration, no protected/source path, and
no test-generated local storage. `changed-files.txt` exactly matches `git status --short`. No package
installation, git add, git commit, or git push was performed.
