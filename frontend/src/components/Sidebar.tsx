import React from 'react';
import { Link } from 'react-router-dom';

const items = [
  { to: '/', label: 'Overview' },
  { to: '/camera', label: 'Camera' },
];

export function Sidebar() {
  return (
    <nav className="w-64 bg-gray-900 text-white h-full p-4">
      <h2 className="text-2xl font-bold mb-6">Menu</h2>
      <ul className="space-y-2">
        {items.map((it) => (
          <li key={it.to}>
            <Link
              to={it.to}
              className="block px-3 py-2 rounded hover:bg-gray-700"
            >
              {it.label}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
