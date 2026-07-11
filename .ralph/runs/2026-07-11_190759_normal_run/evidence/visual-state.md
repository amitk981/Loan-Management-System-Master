# Visual State Evidence

## Affected consumer

`SanctionWorkbench` is the only consumer of the removed `App.tsx` application state chain.

With the shell's explicit empty authoritative input, the existing sanction empty card renders:

- Heading: `Sanction queue data is not connected yet`
- Supporting copy: `No application records are shown until sanction API wiring is complete.`
- No application number or plausible business row.

`SanctionWorkbench.test.tsx` renders the real component composition to static markup and asserts
both lines, the absence of the former `Sanction queue is clear` claim, and the absence of a mock
`LOAN-` record. See `terminal-logs/tdd-green.txt` and `terminal-logs/frontend-tests.txt`.

## Screenshot limitation

The local Vite listener was denied by the sandbox (`listen EPERM`), and the in-app browser runtime
inventory was empty. No genuine screenshot could be captured in this run. No unrelated browser
controller or fabricated screenshot was substituted.
