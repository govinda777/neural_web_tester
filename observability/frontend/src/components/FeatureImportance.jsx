import React from 'react';

const FeatureImportance = ({ weights }) => {
  if (!weights) return null;

  const entries = Object.entries(weights);
  const max = Math.max(...entries.map(([_, v]) => Math.abs(v)), 1e-6);

  return (
    <div className="p-4 bg-gray-50 dark:bg-gray-800 rounded border mt-4">
      <h3 className="text-sm font-semibold mb-4 text-gray-700 dark:text-gray-200">Pesos das Features (Target Element)</h3>
      <div className="space-y-3">
        {entries.map(([key, value]) => {
          const percentage = (Math.abs(value) / max) * 100;
          const color = value >= 0 ? 'bg-blue-500' : 'bg-red-400';

          return (
            <div key={key}>
              <div className="flex justify-between text-xs mb-1">
                <span className="font-mono text-gray-600 dark:text-gray-400">{key}</span>
                <span className="font-semibold">{value.toFixed(3)}</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                <div
                  className={`${color} h-2 rounded-full transition-all duration-500`}
                  style={{ width: `${percentage}%` }}
                ></div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default FeatureImportance;
