import React, { useState } from 'react';
import { Calculator, Info, AlertTriangle, ChevronDown, ChevronUp } from 'lucide-react';

interface LoanLimitCalculatorProps {
  sharesHeld?: number;
  shareMode?: 'physical' | 'demat';
  landAreaAcres?: number;
  requestedAmount?: number;
  readonly?: boolean;
}

const SHARE_VALUATION_PER_SHARE = 2000;
const SHAREHOLDING_PERCENTAGE = 0.30;
const SCALE_OF_FINANCE_PER_ACRE = 20000;

const fmt = (n: number) => '₹' + n.toLocaleString('en-IN');

const LoanLimitCalculator: React.FC<LoanLimitCalculatorProps> = ({
  sharesHeld = 0, shareMode = 'physical', landAreaAcres = 0,
  requestedAmount = 0, readonly = false,
}) => {
  const [shares, setShares] = useState(sharesHeld);
  const [land, setLand] = useState(landAreaAcres);
  const [requested, setRequested] = useState(requestedAmount);
  const [showFormula, setShowFormula] = useState(false);

  const shareholdingLimit = Math.round(shares * SHARE_VALUATION_PER_SHARE * SHAREHOLDING_PERCENTAGE);
  const landLimit = Math.round(land * SCALE_OF_FINANCE_PER_ACRE);
  const eligibleLimit = Math.min(shareholdingLimit, landLimit);
  const isExcess = requested > eligibleLimit;
  const excessAmount = Math.max(0, requested - eligibleLimit);

  return (
    <div className="space-y-4">
      {/* Policy Warning */}
      <div className="bg-amber-50 border border-amber-200 rounded-lg px-4 py-3 flex gap-2">
        <AlertTriangle size={16} className="text-amber-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm">
          <span className="font-semibold text-amber-900">Loan limit policy requires confirmation — </span>
          <span className="text-amber-800">SOP references both 30% and 10% of share valuation, and ₹200 per share. Formula applied: 30% of NAV (₹2,000 per share). Confirm before automated sanction.</span>
        </div>
      </div>

      {/* Inputs */}
      {!readonly && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div>
            <label className="field-label">Shares held</label>
            <input type="number" value={shares} onChange={e => setShares(Number(e.target.value))} className="field-input" />
            <p className="text-xs text-slate-400 mt-1">Holding mode: {shareMode === 'physical' ? 'Physical' : 'Demat'}</p>
          </div>
          <div>
            <label className="field-label">Land area (acres)</label>
            <input type="number" step="0.5" value={land} onChange={e => setLand(Number(e.target.value))} className="field-input" />
            <p className="text-xs text-slate-400 mt-1">From 7/12 extract</p>
          </div>
          <div>
            <label className="field-label">Requested amount</label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 text-sm">₹</span>
              <input type="number" value={requested} onChange={e => setRequested(Number(e.target.value))} className="field-input pl-7" />
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Shareholding-based limit</div>
          <div className="text-xl font-bold text-slate-900 num">{fmt(shareholdingLimit)}</div>
          <div className="text-xs text-slate-400 mt-1">{shares} shares × ₹2,000 × 30%</div>
        </div>
        <div className="bg-slate-50 border border-slate-200 rounded-lg p-4">
          <div className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Land-based limit</div>
          <div className="text-xl font-bold text-slate-900 num">{fmt(landLimit)}</div>
          <div className="text-xs text-slate-400 mt-1">{land} acres × ₹20,000/acre</div>
        </div>
        <div className={`border rounded-lg p-4 ${isExcess ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
          <div className={`text-xs font-semibold uppercase tracking-wide mb-1 ${isExcess ? 'text-red-700' : 'text-green-700'}`}>Final eligible amount</div>
          <div className={`text-xl font-bold num ${isExcess ? 'text-red-900' : 'text-green-900'}`}>{fmt(eligibleLimit)}</div>
          <div className={`text-xs mt-1 ${isExcess ? 'text-red-600' : 'text-green-600'}`}>
            Lower of two limits
          </div>
        </div>
      </div>

      {/* Requested vs Eligible */}
      {requested > 0 && (
        <div className={`rounded-lg border px-4 py-3 ${isExcess ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'}`}>
          <div className="flex items-center justify-between">
            <div>
              <span className={`text-sm font-semibold ${isExcess ? 'text-red-900' : 'text-green-900'}`}>
                {isExcess ? 'Requested amount exceeds eligible limit' : 'Requested amount is within eligible limit'}
              </span>
              {isExcess && (
                <p className="text-sm text-red-700 mt-0.5">
                  Excess: {fmt(excessAmount)} — Exception approval required from CFO + two Directors.
                </p>
              )}
            </div>
            <div className="text-right">
              <div className="text-xs text-slate-500">Requested</div>
              <div className={`text-lg font-bold num ${isExcess ? 'text-red-900' : 'text-green-900'}`}>{fmt(requested)}</div>
            </div>
          </div>
        </div>
      )}

      {/* Formula disclosure */}
      <button
        onClick={() => setShowFormula(!showFormula)}
        className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700 transition-colors"
      >
        <Info size={12} />
        View formula details
        {showFormula ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
      </button>

      {showFormula && (
        <div className="bg-slate-50 rounded-lg border border-slate-200 p-4 text-xs text-slate-700 space-y-2 font-mono">
          <p><strong>Shareholding-based limit</strong> = No. of shares held × NAV per share × 30%</p>
          <p><strong>Land-based limit</strong> = Per-acre cost of cultivation × Land area (acres)</p>
          <p><strong>Final eligible amount</strong> = Lower of Shareholding-based limit and Land-based limit</p>
          <hr className="border-slate-200" />
          <p className="font-sans text-slate-500">Policy version: 2025-26 · Share NAV: ₹2,000 (AGM approved) · Scale of finance: ₹20,000/acre</p>
        </div>
      )}
    </div>
  );
};

export default LoanLimitCalculator;
