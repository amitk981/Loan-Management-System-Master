export interface AvailableAction {
  action_code: string;
  label: string;
  enabled: boolean;
  disabled_reason: string | null;
  required_permission: string;
}

export const findAction = (
  actions: AvailableAction[],
  actionCode: string,
): AvailableAction | undefined => actions.find(action => action.action_code === actionCode);

export const isActionEnabled = (
  actions: AvailableAction[],
  actionCode: string,
): boolean => findAction(actions, actionCode)?.enabled === true;
