import React, { useState } from 'react';

export interface Tab {
  id: string;
  label: string;
  badge?: number;
  icon?: React.ReactNode;
}

interface TabsProps {
  tabs: Tab[];
  children: React.ReactNode[];
  defaultTab?: string;
  activeIndex?: number;
  onChange?: (index: number) => void;
}

const Tabs: React.FC<TabsProps> = ({ tabs, children, defaultTab, activeIndex, onChange }) => {
  const [internalActive, setInternalActive] = useState(defaultTab || tabs[0]?.id);

  const isControlled = activeIndex !== undefined && onChange !== undefined;
  const currentIndex = isControlled ? activeIndex : tabs.findIndex(t => t.id === internalActive);
  const active = tabs[currentIndex]?.id || tabs[0]?.id;

  const handleClick = (idx: number) => {
    if (isControlled) {
      onChange(idx);
    } else {
      setInternalActive(tabs[idx]?.id);
    }
  };

  return (
    <div className="flex flex-col flex-1 min-h-0">
      <div className="border-b border-slate-200 overflow-x-auto">
        <div className="flex gap-0 min-w-max">
          {tabs.map((tab, idx) => (
            <button
              key={tab.id}
              onClick={() => handleClick(idx)}
              className={`flex items-center gap-1.5 px-4 py-3 text-sm font-medium border-b-2 transition-colors whitespace-nowrap ${
                active === tab.id
                  ? 'border-green-600 text-green-700'
                  : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
              }`}
            >
              {tab.icon}
              {tab.label}
              {tab.badge !== undefined && (
                <span className={`text-xs px-1.5 py-0.5 rounded-full font-semibold ${active === tab.id ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'}`}>
                  {tab.badge}
                </span>
              )}
            </button>
          ))}
        </div>
      </div>
      <div className="flex-1 overflow-y-auto pt-5">
        {children[currentIndex] ?? children[0]}
      </div>
    </div>
  );
};

export default Tabs;
