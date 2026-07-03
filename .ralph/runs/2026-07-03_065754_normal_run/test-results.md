# test Results

Command: npm test --if-present


> sfpcl-lms@1.0.0 test
> vitest run

/Users/amitkallapa/Loan Management System Development/.ralph/worktrees/2026-07-03_065754_normal_run/sfpcl-lms/node_modules/rollup/dist/native.js:121
		throw new Error(
		      ^

Error: Cannot find module @rollup/rollup-darwin-arm64. npm has a bug related to optional dependencies (https://github.com/npm/cli/issues/4828). Please try `npm i` again after removing both package-lock.json and node_modules directory.
    at requireWithFriendlyError (/Users/amitkallapa/Loan Management System Development/.ralph/worktrees/2026-07-03_065754_normal_run/sfpcl-lms/node_modules/rollup/dist/native.js:121:9)
    at Object.<anonymous> (/Users/amitkallapa/Loan Management System Development/.ralph/worktrees/2026-07-03_065754_normal_run/sfpcl-lms/node_modules/rollup/dist/native.js:130:76)
    ... 3 lines matching cause stack trace ...
    at Module._load (node:internal/modules/cjs/loader:958:12)
    at ModuleWrap.<anonymous> (node:internal/modules/esm/translators:169:29)
    at ModuleJob.run (node:internal/modules/esm/module_job:194:25) {
  [cause]: Error: Cannot find module '@rollup/rollup-darwin-arm64'
  Require stack:
  - /Users/amitkallapa/Loan Management System Development/.ralph/worktrees/2026-07-03_065754_normal_run/sfpcl-lms/node_modules/rollup/dist/native.js
      at Module._resolveFilename (node:internal/modules/cjs/loader:1075:15)
      at Module._load (node:internal/modules/cjs/loader:920:27)
      at Module.require (node:internal/modules/cjs/loader:1141:19)
      at require (node:internal/modules/cjs/helpers:110:18)
      at requireWithFriendlyError (/Users/amitkallapa/Loan Management System Development/.ralph/worktrees/2026-07-03_065754_normal_run/sfpcl-lms/node_modules/rollup/dist/native.js:103:10)
      at Object.<anonymous> (/Users/amitkallapa/Loan Management System Development/.ralph/worktrees/2026-07-03_065754_normal_run/sfpcl-lms/node_modules/rollup/dist/native.js:130:76)
      at Module._compile (node:internal/modules/cjs/loader:1254:14)
      at Module._extensions..js (node:internal/modules/cjs/loader:1308:10)
      at Module.load (node:internal/modules/cjs/loader:1117:32)
      at Module._load (node:internal/modules/cjs/loader:958:12) {
    code: 'MODULE_NOT_FOUND',
    requireStack: [
      '/Users/amitkallapa/Loan Management System Development/.ralph/worktrees/2026-07-03_065754_normal_run/sfpcl-lms/node_modules/rollup/dist/native.js'
    ]
  }
}

Node.js v18.15.0
