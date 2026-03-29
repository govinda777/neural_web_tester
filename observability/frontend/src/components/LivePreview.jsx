import React, { useEffect, useState, useRef } from 'react';

const LivePreview = ({ stepData }) => {
  const containerRef = useRef(null);
  const [imgSize, setImgSize] = useState({ w: 0, h: 0 });

  useEffect(() => {
    if (containerRef.current) {
        // Observa o tamanho do container para redimensionar o overlay
    }
  }, [stepData]);

  if (!stepData) return <div className="p-4 text-gray-500">Aguardando telemetria...</div>;

  return (
    <div className="relative border rounded overflow-hidden bg-gray-900" ref={containerRef}>
      <img
        src={`data:image/png;base64,${stepData.screenshot_base64}`}
        alt="Agent View"
        className="w-full h-auto block"
        onLoad={(e) => setImgSize({ w: e.target.naturalWidth, h: e.target.naturalHeight })}
      />

      {/* SVG Overlay for Bounding Boxes */}
      <svg
        className="absolute top-0 left-0 w-full h-full pointer-events-none"
        viewBox="0 0 1 1"
        preserveAspectRatio="none"
      >
        {stepData.observation?.top_candidates?.map((candidate, i) => {
          const [x, y, w, h] = candidate.coords;
          const color = i === 0 ? "#10b981" : "#f59e0b"; // Verde para o top 1, amarelo para o resto
          const opacity = candidate.prob > 0.5 ? 0.8 : 0.3;

          return (
            <g key={candidate.id}>
              <rect
                x={x - w/2}
                y={y - h/2}
                width={w}
                height={h}
                fill="none"
                stroke={color}
                strokeWidth="0.005"
                strokeOpacity={opacity}
              />
              <text
                x={x - w/2}
                y={y - h/2 - 0.01}
                fontSize="0.02"
                fill={color}
                style={{ filter: 'drop-shadow(1px 1px 1px black)' }}
              >
                {candidate.label} ({Math.round(candidate.prob * 100)}%)
              </text>
            </g>
          );
        })}

        {/* Action Marker */}
        {stepData.action && (
            <circle
                cx={stepData.observation?.top_candidates?.find(c => c.id === stepData.action.element_id)?.coords[0] || 0.5}
                cy={stepData.observation?.top_candidates?.find(c => c.id === stepData.action.element_id)?.coords[1] || 0.5}
                r="0.02"
                fill="none"
                stroke="#ec4899"
                strokeWidth="0.01"
            >
                <animate attributeName="r" from="0.01" to="0.04" dur="0.5s" repeatCount="indefinite" />
                <animate attributeName="opacity" from="1" to="0" dur="0.5s" repeatCount="indefinite" />
            </circle>
        )}
      </svg>

      <div className="absolute bottom-2 left-2 bg-black/60 text-white px-2 py-1 text-xs rounded">
        Step: {stepData.step_number} | State: {stepData.state_hash?.substring(0, 8)}
      </div>
    </div>
  );
};

export default LivePreview;
