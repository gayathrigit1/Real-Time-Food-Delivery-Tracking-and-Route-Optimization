import React from 'react';
import { Clock, MapPin, Navigation2, Zap } from 'lucide-react';
import { RouteResponse } from '../types';

interface RouteMapVisualizerProps {
  routeData?: RouteResponse | null;
  height?: number;
}

// Preset planar display coordinates for city graph visualization
const NODE_POSITIONS: Record<string, { x: number; y: number; color: string; label: string }> = {
  Node_R1: { x: 260, y: 220, color: '#f59e0b', label: 'Bistro Gourmet' },
  Node_R2: { x: 380, y: 160, color: '#f59e0b', label: 'Spice Garden' },
  Node_R3: { x: 480, y: 110, color: '#f59e0b', label: 'Tokyo Ramen' },

  Node_D1: { x: 140, y: 90, color: '#10b981', label: 'Courier Hub North' },
  Node_D2: { x: 120, y: 340, color: '#10b981', label: 'Courier Hub South' },
  Node_D3: { x: 560, y: 240, color: '#10b981', label: 'Courier Hub East' },

  Node_A: { x: 240, y: 100, color: '#64748b', label: 'Junction A' },
  Node_B: { x: 320, y: 240, color: '#64748b', label: 'Central B' },
  Node_C: { x: 240, y: 350, color: '#64748b', label: 'Junction C' },
  Node_D: { x: 440, y: 240, color: '#64748b', label: 'Expressway D' },
  Node_E: { x: 160, y: 220, color: '#64748b', label: 'Ring Road E' },

  Node_C1: { x: 500, y: 180, color: '#3b82f6', label: 'Customer Apt 101' },
  Node_C2: { x: 340, y: 360, color: '#3b82f6', label: 'Customer Villa 202' },
  Node_C3: { x: 620, y: 320, color: '#3b82f6', label: 'Tech Park 303' },
  Node_C4: { x: 380, y: 80, color: '#3b82f6', label: 'Residency 404' },
};

const ROAD_EDGES = [
  ['Node_R1', 'Node_B'],
  ['Node_R1', 'Node_E'],
  ['Node_R2', 'Node_B'],
  ['Node_R2', 'Node_D'],
  ['Node_R3', 'Node_A'],
  ['Node_R3', 'Node_D'],
  ['Node_D1', 'Node_A'],
  ['Node_D1', 'Node_E'],
  ['Node_D2', 'Node_C'],
  ['Node_D2', 'Node_E'],
  ['Node_D3', 'Node_D'],
  ['Node_D3', 'Node_C3'],
  ['Node_A', 'Node_B'],
  ['Node_A', 'Node_C4'],
  ['Node_B', 'Node_C'],
  ['Node_B', 'Node_D'],
  ['Node_C', 'Node_C2'],
  ['Node_D', 'Node_C1'],
  ['Node_D', 'Node_C3'],
  ['Node_C1', 'Node_C4'],
  ['Node_C1', 'Node_C3'],
  ['Node_E', 'Node_C'],
];

export const RouteMapVisualizer: React.FC<RouteMapVisualizerProps> = ({ routeData, height = 400 }) => {
  const activePath = routeData?.path || [];

  const isEdgeInPath = (u: string, v: string) => {
    for (let i = 0; i < activePath.length - 1; i++) {
      if (
        (activePath[i] === u && activePath[i + 1] === v) ||
        (activePath[i] === v && activePath[i + 1] === u)
      ) {
        return true;
      }
    }
    return false;
  };

  return (
    <div className="glass-panel" style={{ padding: '16px', position: 'relative', overflow: 'hidden' }}>
      
      {/* Header telemetry */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ padding: '6px', borderRadius: '8px', background: 'rgba(6, 182, 212, 0.15)', color: '#06b6d4' }}>
            <Navigation2 size={16} />
          </div>
          <div>
            <div style={{ fontWeight: 700, fontSize: '0.92rem' }}>Dijkstra Road Network Graph</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Weighted Adjacency Graph • Min-Heap Shortest Path Engine
            </div>
          </div>
        </div>

        {routeData && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
              <Zap size={14} color="#06b6d4" />
              <span><strong>{routeData.distance_km}</strong> km</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.85rem' }}>
              <Clock size={14} color="#fbbf24" />
              <span><strong>~{routeData.estimated_time_mins}</strong> mins</span>
            </div>
            <span className="badge badge-emerald">Optimal Route Found</span>
          </div>
        )}
      </div>

      {/* SVG Canvas */}
      <div style={{ width: '100%', height: `${height}px`, background: 'rgba(10, 15, 29, 0.85)', borderRadius: '12px', position: 'relative', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
        <svg viewBox="0 0 720 440" style={{ width: '100%', height: '100%' }}>
          <defs>
            {/* Glow filter for active route */}
            <filter id="cyan-glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="4" result="blur" />
              <feComposite in="SourceGraphic" in2="blur" operator="over" />
            </filter>
            <linearGradient id="routeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#06b6d4" />
              <stop offset="100%" stopColor="#3b82f6" />
            </linearGradient>
          </defs>

          {/* Draw Road Segments (Edges) */}
          {ROAD_EDGES.map(([u, v], idx) => {
            const p1 = NODE_POSITIONS[u];
            const p2 = NODE_POSITIONS[v];
            if (!p1 || !p2) return null;
            const inRoute = isEdgeInPath(u, v);

            return (
              <g key={`edge-${idx}`}>
                <line
                  x1={p1.x}
                  y1={p1.y}
                  x2={p2.x}
                  y2={p2.y}
                  stroke={inRoute ? 'rgba(6, 182, 212, 0.3)' : 'rgba(255, 255, 255, 0.08)'}
                  strokeWidth={inRoute ? 8 : 2}
                  strokeDasharray={inRoute ? 'none' : '3 3'}
                />
                {inRoute && (
                  <line
                    x1={p1.x}
                    y1={p1.y}
                    x2={p2.x}
                    y2={p2.y}
                    stroke="url(#routeGradient)"
                    strokeWidth={4}
                    filter="url(#cyan-glow)"
                  />
                )}
              </g>
            );
          })}

          {/* Draw Nodes */}
          {Object.entries(NODE_POSITIONS).map(([nodeId, pos]) => {
            const isInPath = activePath.includes(nodeId);
            const isStart = activePath[0] === nodeId;
            const isEnd = activePath[activePath.length - 1] === nodeId;

            let nodeColor = pos.color;
            if (isStart) nodeColor = '#10b981';
            else if (isEnd) nodeColor = '#3b82f6';
            else if (isInPath) nodeColor = '#06b6d4';

            return (
              <g key={nodeId} style={{ cursor: 'pointer' }}>
                {/* Node Ring Indicator */}
                {isInPath && (
                  <circle
                    cx={pos.x}
                    y={pos.y}
                    r={18}
                    fill="none"
                    stroke={nodeColor}
                    strokeWidth={2}
                    opacity={0.6}
                    className="animate-pulse-glow"
                  />
                )}

                {/* Main Node Circle */}
                <circle
                  cx={pos.x}
                  y={pos.y}
                  r={isInPath ? 12 : 8}
                  fill={nodeColor}
                  stroke="#0f172a"
                  strokeWidth={2}
                  filter={isInPath ? 'url(#cyan-glow)' : 'none'}
                />

                {/* Node ID label */}
                <text
                  x={pos.x}
                  y={pos.y - 15}
                  textAnchor="middle"
                  fill={isInPath ? '#f8fafc' : '#94a3b8'}
                  fontSize={10}
                  fontWeight={isInPath ? 700 : 500}
                  fontFamily="var(--font-mono)"
                >
                  {nodeId}
                </text>

                {/* Node Name Subtitle */}
                <text
                  x={pos.x}
                  y={pos.y + 22}
                  textAnchor="middle"
                  fill={isInPath ? '#38bdf8' : '#64748b'}
                  fontSize={9}
                  fontFamily="var(--font-sans)"
                >
                  {pos.label}
                </text>
              </g>
            );
          })}
        </svg>

        {/* Legend Overlay */}
        <div
          style={{
            position: 'absolute',
            bottom: '12px',
            right: '12px',
            background: 'rgba(15, 23, 42, 0.85)',
            backdropFilter: 'blur(8px)',
            border: '1px solid var(--border-color)',
            borderRadius: '8px',
            padding: '8px 12px',
            display: 'flex',
            gap: '12px',
            fontSize: '0.74rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }} /> Restaurant
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} /> Courier Hub
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#3b82f6' }} /> Customer
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
            <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#06b6d4' }} /> Dijkstra Path
          </div>
        </div>
      </div>

      {/* Path sequence breadcrumbs */}
      {activePath.length > 0 && (
        <div style={{ marginTop: '12px', display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>Optimal Path Sequence:</span>
          {activePath.map((node, i) => (
            <React.Fragment key={node}>
              <span className="badge badge-blue" style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem' }}>
                {i + 1}. {node}
              </span>
              {i < activePath.length - 1 && <span style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>➔</span>}
            </React.Fragment>
          ))}
        </div>
      )}

    </div>
  );
};
