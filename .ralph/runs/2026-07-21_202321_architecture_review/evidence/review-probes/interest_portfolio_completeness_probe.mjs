import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const findingId = 'AR-010-INTEREST-UI-001';
const rootId = 'ROOT-010-INTEREST-PORTFOLIO-COMPLETENESS';
const file = resolve('sfpcl-lms/src/pages/interest/InterestManagement.tsx');
const source = readFileSync(file, 'utf8');

console.log(`Finding ID: ${findingId}`);
console.log(`Root ID: ${rootId}`);
console.log('Command contract: a portfolio-wide accrual must not submit only page 1 account ids.');

const loadsOnlyFirstHundred = source.includes('fetchLoanAccounts(1, 100)');
const submitsLoadedIds = source.includes('accounts.map(row => row.loan_account_id)');
console.log(`Loads only page 1/100: ${loadsOnlyFirstHundred}`);
console.log(`Submits only loaded account ids: ${submitsLoadedIds}`);

if (loadsOnlyFirstHundred && submitsLoadedIds) {
  throw new Error(
    'FAIL: the one-click monthly accrual silently omits scoped loan 101 and later.'
  );
}
