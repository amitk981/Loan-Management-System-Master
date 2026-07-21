export const formatMoney = (value: string | null): string => {
  if (value === null) return '—';
  const match = /^(-?)(\d+)(?:\.(\d{1,2}))?$/.exec(value);
  if (!match) return `₹${value}`;
  const [, sign, digits, rawFraction = ''] = match;
  const trailing = digits.slice(-3);
  const leading = digits.slice(0, -3).replace(/\B(?=(\d{2})+(?!\d))/g, ',');
  const grouped = leading ? `${leading},${trailing}` : trailing;
  return `₹${sign}${grouped}.${rawFraction.padEnd(2, '0')}`;
};
