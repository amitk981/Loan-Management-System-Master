const EPIC_009_SPEC = 'epic-009-staff-disbursement-closure.e2e.spec.ts';
const SPEC_ARGUMENT = /(?:\.e2e\.spec\.ts|\.spec\.ts)$/;

export type FixtureFamily = 'staff' | 'portal' | 'epic009';

export function requiredFixtureFamilies(arguments_: readonly string[]): FixtureFamily[] {
  const selectedSpecs = arguments_.filter(argument => SPEC_ARGUMENT.test(argument));
  const selectsEpic009 = selectedSpecs.some(argument => argument.includes(EPIC_009_SPEC));
  const selectsAnotherSpec = selectedSpecs.some(argument => !argument.includes(EPIC_009_SPEC));

  if (selectsEpic009 && !selectsAnotherSpec) {
    return ['epic009'];
  }
  if (!selectsEpic009 && selectedSpecs.length > 0) {
    return ['staff', 'portal'];
  }
  return ['staff', 'portal', 'epic009'];
}

export function fixtureSeedCommands(manage: string, arguments_: readonly string[]): string {
  const commands: Record<FixtureFamily, string[]> = {
    staff: [`${manage} seed_role_catalogue`, `${manage} seed_e2e_users`],
    portal: [`${manage} seed_portal_e2e_fixture`],
    epic009: [`${manage} seed_epic_009_e2e_fixture`],
  };
  const selected = requiredFixtureFamilies(arguments_).flatMap(family => commands[family]);
  return `${[...new Set(selected)].join(' && ')} && `;
}
