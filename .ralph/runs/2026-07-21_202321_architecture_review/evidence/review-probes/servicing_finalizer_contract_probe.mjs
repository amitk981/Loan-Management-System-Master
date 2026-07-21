import { readFileSync } from 'node:fs';
import { resolve } from 'node:path';

const findingId = 'AR-010-SERVICING-SEAM-001';
const rootId = 'ROOT-010-SERVICING-OWNER-SEAM';
const file = resolve('sfpcl_credit/tests/test_epic010_terminal_owner_finalizer.py');
const source = readFileSync(file, 'utf8');

console.log(`Finding ID: ${findingId}`);
console.log(`Root ID: ${rootId}`);
console.log('CR-015 requirement 5: touched acceptance classes use public builders, not another TestCase.setUp.');

const importsTestCaseFixture = source.includes('RepaymentAllocationApiTests');
const invokesForeignSetup = source.includes('fixture.setUp()');
console.log(`Imports another TestCase fixture: ${importsTestCaseFixture}`);
console.log(`Calls the imported TestCase.setUp(): ${invokesForeignSetup}`);

if (importsTestCaseFixture && invokesForeignSetup) {
  throw new Error(
    'FAIL: the terminal acceptance regression retains the exact private cross-TestCase fixture dependency CR-015 required removed.'
  );
}
