import { describe, expect, it } from 'vitest';
import { formatMoney } from './formatMoney';

describe('formatMoney', () => {
  it('groups canonical decimal strings without converting through imprecise Number values', () => {
    expect(formatMoney('400000.00')).toBe('₹4,00,000.00');
    expect(formatMoney('9999999999999999.99')).toBe('₹9,99,99,99,99,99,99,999.99');
    expect(formatMoney(null)).toBe('—');
  });
});
