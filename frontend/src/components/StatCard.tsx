// src/components/StatCard.tsx
import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  color?: string; // Tailwind text color class e.g. "text-accentCyan"
}

export const StatCard: React.FC<StatCardProps> = ({ title, value, icon: Icon, color = 'text-accentCyan' }) => (
  <div className="bg-secondary rounded-lg p-4 flex items-center space-x-4 shadow-md">
    <div className={`p-2 rounded-full bg-primary ${color}`}> <Icon size={24} /></div>
    <div>
      <div className="text-sm text-gray-400">{title}</div>
      <div className="text-xl font-semibold text-white">{value}</div>
    </div>
  </div>
);
