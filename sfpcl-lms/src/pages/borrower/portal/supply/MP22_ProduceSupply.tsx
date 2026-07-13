import React, { useEffect, useState } from 'react';
import { AlertTriangle, Calendar, CheckCircle2, IndianRupee, Leaf, Scale } from 'lucide-react';
import StatusBadge from '../../../../components/ui/StatusBadge';
import { AuthSessionError } from '../../../../services/authSession';
import { fetchPortalProduceSupply, type PortalProduceSupply } from '../../../../services/portalApi';

const MP22_ProduceSupply: React.FC = () => {
  const [supply, setSupply] = useState<PortalProduceSupply | null>(null);
  const [message, setMessage] = useState('Loading produce supply history...');

  useEffect(() => {
    let mounted = true;
    fetchPortalProduceSupply()
      .then(data => {
        if (mounted) setSupply(data);
      })
      .catch((error: AuthSessionError) => {
        if (mounted) setMessage(error.message || 'Produce supply history could not be loaded.');
      });
    return () => {
      mounted = false;
    };
  }, []);

  if (!supply) {
    return <SupplyPanel title="Produce supply unavailable" message={message} />;
  }
  return <MP22ProduceSupplyView supply={supply} />;
};

export const MP22ProduceSupplyView: React.FC<{ supply: PortalProduceSupply }> = ({ supply }) => {
  const hasRecords = supply.records.length > 0;

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Produce Supply History</h2>
          <p className="text-sm text-slate-500 mt-1">Track your agricultural supply to SFPCL for loan eligibility.</p>
        </div>
        <div className="bg-green-50 border border-green-200 px-4 py-2 rounded-lg flex items-center gap-2">
          <CheckCircle2 size={18} className="text-green-600" />
          <span className="text-sm font-medium text-green-800">{formatLabel(supply.source_status)}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Metric icon={<Calendar size={24} />} label="Continuous Supply" value={supply.summary.continuous_supply_years || 'Not recorded'} color="text-blue-600" bg="bg-blue-50" />
        <Metric icon={<Scale size={24} />} label="Total Volume" value={supply.summary.total_quantity || 'Not recorded'} color="text-amber-600" bg="bg-amber-50" />
        <Metric icon={<IndianRupee size={24} />} label="Total Value" value={supply.summary.total_value || 'Not recorded'} color="text-green-600" bg="bg-green-50" />
      </div>

      <div className="bg-white rounded-xl border border-slate-100 overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 bg-slate-50">
          <h3 className="font-semibold text-slate-900">Historical Supply Records</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-white border-b border-slate-200">
              <tr>
                <th className="text-left px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Financial Year</th>
                <th className="text-left px-4 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Crop</th>
                <th className="text-right px-4 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Quantity</th>
                <th className="text-right px-4 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Value Delivered</th>
                <th className="text-center px-6 py-4 text-xs font-semibold text-slate-500 uppercase tracking-wider">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {hasRecords ? supply.records.map(row => (
                <tr key={`${row.financial_year}-${row.crop_type || 'crop'}`} className="hover:bg-slate-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-800 whitespace-nowrap">{row.financial_year}</td>
                  <td className="px-4 py-4 text-slate-600 whitespace-nowrap flex items-center gap-2">
                    <Leaf size={14} className="text-green-600" />
                    {row.crop_type || 'Not recorded'}
                  </td>
                  <td className="px-4 py-4 text-right font-medium text-slate-700 whitespace-nowrap">{row.quantity || 'Not recorded'}</td>
                  <td className="px-4 py-4 text-right text-slate-600 whitespace-nowrap">{row.value_amount || 'Not recorded'}</td>
                  <td className="px-6 py-4 text-center whitespace-nowrap"><StatusBadge label={row.verified_flag ? 'verified' : 'pending'} size="sm" /></td>
                </tr>
              )) : (
                <tr>
                  <td colSpan={5} className="px-6 py-6 text-sm text-slate-500">No produce supply records are available yet.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 flex gap-3 text-sm text-blue-800">
        <div className="mt-0.5">
          <CheckCircle2 size={18} className="text-blue-600" />
        </div>
        <div>
          <span className="font-semibold block mb-1">Eligibility Note</span>
          Eligibility uses verified supply records and continuous financial-year history shown above.
        </div>
      </div>
    </div>
  );
};

const Metric: React.FC<{ icon: React.ReactNode; label: string; value: string; color: string; bg: string }> = ({ icon, label, value, color, bg }) => (
  <div className="bg-white rounded-xl border border-slate-100 p-5 flex items-center gap-4">
    <div className={`w-12 h-12 rounded-full ${bg} flex items-center justify-center flex-shrink-0 ${color}`}>{icon}</div>
    <div>
      <p className="text-xs text-slate-500 font-medium uppercase tracking-wider">{label}</p>
      <p className="text-xl font-bold text-slate-900 mt-0.5">{value}</p>
    </div>
  </div>
);

const SupplyPanel: React.FC<{ title: string; message: string }> = ({ title, message }) => (
  <div className="bg-white rounded-xl border border-slate-100 p-6">
    <h3 className="font-semibold text-slate-900 mb-2 flex items-center gap-2">
      <AlertTriangle size={16} className="text-amber-600" />
      {title}
    </h3>
    <p className="text-sm text-slate-500">{message}</p>
  </div>
);

const formatLabel = (value: string) => value.replace(/_/g, ' ');

export default MP22_ProduceSupply;
