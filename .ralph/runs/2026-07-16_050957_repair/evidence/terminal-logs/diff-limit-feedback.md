# Diff-limit feedback loop

Validator-equivalent command: sum `git diff --numstat HEAD -- . ':(exclude).ralph'` additions and
deletions, then add line counts for non-ignored untracked files outside `.ralph/`.

## Red

Before repair: `tracked=1945 untracked=56 total=2001`.

The untracked contribution included:

`3 sfpcl_credit/e2e-document-storage/document-files/.../term-sheet-LO000008L4.pdf`

## Green

After moving the Playwright storage default and deleting the generated survivor:

`tracked=1947 untracked=52 total=1999`

After a real Playwright invocation started both servers, seeded Django, and reached the health
endpoint, the result remained:

`tracked=1947 untracked=52 total=1999`

The fixture existed only at `${TMPDIR}/sfpcl-e2e-document-storage/2026-07-16_033311_repair/...`
and `sfpcl_credit/e2e-document-storage` did not exist.

Final handoff bookkeeping reduced the tracked contribution by one more line:

`tracked=1946 untracked=52 total=1998`
