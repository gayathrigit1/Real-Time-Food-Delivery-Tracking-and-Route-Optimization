import React, { useEffect, useState } from 'react';
import {
  Activity,
  Binary,
  CheckCircle2,
  Clock,
  Compass,
  Cpu,
  GitBranch,
  Layers,
  Play,
  RefreshCw,
  Scale,
  Sparkles,
  Zap,
} from 'lucide-react';
import { api } from '../api/client';
import { RouteMapVisualizer } from '../components/RouteMapVisualizer';
import { AlgorithmBenchmarkComparison, RouteResponse } from '../types';

export const AlgorithmsLab: React.FC = () => {
  const [activeAlgorithmTab, setActiveAlgorithmTab] = useState<
    'benchmark' | 'greedy' | 'dijkstra' | 'dp' | 'backtracking' | 'branch_bound' | 'divide_conquer'
  >('benchmark');

  const [benchmarkData, setBenchmarkData] = useState<AlgorithmBenchmarkComparison | null>(null);
  const [benchmarking, setBenchmarking] = useState(false);

  // 1. Dijkstra State
  const [dijkStart, setDijkStart] = useState('Node_R1');
  const [dijkEnd, setDijkEnd] = useState('Node_C3');
  const [dijkResult, setDijkResult] = useState<any>(null);
  const [dijkRouteVisual, setDijkRouteVisual] = useState<RouteResponse | null>(null);

  // 2. DP State
  const [dpWindow, setDpWindow] = useState(120);
  const [dpResult, setDpResult] = useState<any>(null);

  // 3. Backtracking State
  const [btStops, setBtStops] = useState(['Node_C1', 'Node_C2', 'Node_C3']);
  const [btMaxDist, setBtMaxDist] = useState(35.0);
  const [btResult, setBtResult] = useState<any>(null);

  // 4. Branch & Bound State
  const [bbLocations, setBbLocations] = useState(['Node_R1', 'Node_C1', 'Node_C2', 'Node_C3', 'Node_C4']);
  const [bbResult, setBbResult] = useState<any>(null);

  // 5. Divide & Conquer State
  const [dacSampleSize, setDacSampleSize] = useState(250);
  const [dacResult, setDacResult] = useState<any>(null);

  const runBenchmarkSuite = async () => {
    try {
      setBenchmarking(true);
      const res = await api.benchmarkAllAlgorithms();
      setBenchmarkData(res);
    } catch (err) {
      console.error('Benchmark failed:', err);
    } finally {
      setBenchmarking(false);
    }
  };

  useEffect(() => {
    runBenchmarkSuite();
  }, []);

  const handleRunDijkstra = async () => {
    const res = await api.runDijkstra(dijkStart, dijkEnd);
    setDijkResult(res);
    const routeVisual = await api.calculateRoute(dijkStart, dijkEnd);
    setDijkRouteVisual(routeVisual);
  };

  const handleRunDP = async () => {
    const res = await api.runDPSchedule(dpWindow);
    setDpResult(res);
  };

  const handleRunBacktracking = async () => {
    const res = await api.runBacktracking(btStops, 'Node_R1', btMaxDist);
    setBtResult(res);
  };

  const handleRunBranchAndBound = async () => {
    const res = await api.runBranchAndBound(bbLocations);
    setBbResult(res);
  };

  const handleRunDivideAndConquer = async () => {
    const res = await api.runDivideAndConquer(dacSampleSize);
    setDacResult(res);
  };

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, background: 'linear-gradient(90deg, #c084fc, #8b5cf6)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Computational Thinking & 6 Algorithms Lab
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            Comprehensive verification, time/space complexity analysis, and interactive parameter tuning.
          </p>
        </div>

        <button onClick={runBenchmarkSuite} disabled={benchmarking} className="btn btn-purple">
          {benchmarking ? <RefreshCw className="animate-spin" size={16} /> : <Play size={16} />}
          {benchmarking ? 'Benchmarking System...' : 'Run All-Algorithms Benchmark'}
        </button>
      </div>

      {/* Algorithm Tabs */}
      <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', flexWrap: 'wrap', background: 'rgba(15, 23, 42, 0.6)', padding: '6px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
        {[
          { id: 'benchmark', label: '1. Live Benchmark Suite', icon: Activity },
          { id: 'greedy', label: '2. Greedy Agent Selection', icon: Scale },
          { id: 'dijkstra', label: '3. Dijkstra Routing', icon: Compass },
          { id: 'dp', label: '4. Dynamic Programming (0/1 Knapsack)', icon: Layers },
          { id: 'backtracking', label: '5. Backtracking (Permutations)', icon: GitBranch },
          { id: 'branch_bound', label: '6. Branch & Bound (TSP)', icon: Sparkles },
          { id: 'divide_conquer', label: '7. Divide & Conquer Analytics', icon: Binary },
        ].map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveAlgorithmTab(id as any)}
            className={`btn btn-sm ${activeAlgorithmTab === id ? 'btn-purple' : 'btn-outline'}`}
            style={{ border: 'none' }}
          >
            <Icon size={14} /> {label}
          </button>
        ))}
      </div>

      {/* Tab Content */}

      {/* 1. Benchmark Suite Overview Table */}
      {activeAlgorithmTab === 'benchmark' && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '18px', flexWrap: 'wrap', gap: '10px' }}>
            <div>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 800 }}>Algorithm Execution & Performance Comparison</h2>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                Empirical benchmarks executed on native host hardware. Zero fabricated data.
              </p>
            </div>

            {benchmarkData && (
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                Hardware: {benchmarkData.system_specs.os} • Python {benchmarkData.system_specs.python_version}
              </div>
            )}
          </div>

          {!benchmarkData ? (
            <div style={{ textAlign: 'center', padding: '40px 0' }}>
              <RefreshCw className="animate-spin" size={24} color="#8b5cf6" style={{ margin: '0 auto 12px' }} />
              <div>Running algorithm suite benchmarks...</div>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.88rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '12px' }}>Algorithm</th>
                    <th style={{ padding: '12px' }}>Paradigm / Type</th>
                    <th style={{ padding: '12px' }}>Input Size</th>
                    <th style={{ padding: '12px' }}>Time Complexity</th>
                    <th style={{ padding: '12px' }}>Space Complexity</th>
                    <th style={{ padding: '12px' }}>Measured Latency</th>
                    <th style={{ padding: '12px' }}>Verification Output</th>
                  </tr>
                </thead>
                <tbody>
                  {benchmarkData.algorithms.map((item, idx) => (
                    <tr key={idx} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', background: idx % 2 === 0 ? 'rgba(255,255,255,0.01)' : 'transparent' }}>
                      <td style={{ padding: '12px', fontWeight: 700 }}>{item.algorithm}</td>
                      <td style={{ padding: '12px' }}>
                        <span className="badge badge-purple" style={{ fontSize: '0.7rem' }}>{item.category}</span>
                      </td>
                      <td style={{ padding: '12px', color: 'var(--text-secondary)' }}>{item.input_size}</td>
                      <td style={{ padding: '12px', fontFamily: 'var(--font-mono)', color: '#60a5fa' }}>{item.time_complexity}</td>
                      <td style={{ padding: '12px', fontFamily: 'var(--font-mono)', color: '#34d399' }}>{item.space_complexity}</td>
                      <td style={{ padding: '12px', fontWeight: 800, color: '#fbbf24', fontFamily: 'var(--font-mono)' }}>
                        {item.execution_time_ms.toFixed(4)} ms
                      </td>
                      <td style={{ padding: '12px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{item.result_summary}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* 2. Greedy Agent Selection Lab */}
      {activeAlgorithmTab === 'greedy' && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '8px' }}>
            Greedy Delivery Agent Selection Heuristic
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '16px' }}>
            Scoring Formula: <code>Score = (0.50 × NormDist) + (0.30 × NormLoad) - (0.20 × NormRating)</code>
          </p>

          <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', fontSize: '0.84rem', lineHeight: 1.7, marginBottom: '20px' }}>
            <div style={{ fontWeight: 700, color: '#38bdf8', marginBottom: '4px' }}>Theoretical Analysis:</div>
            • <strong>Time Complexity:</strong> O(N) linear scan over N candidate couriers.<br />
            • <strong>Space Complexity:</strong> O(N) auxiliary space for scoring telemetry.<br />
            • <strong>Design Trade-offs:</strong> Fast immediate local optimum; does not forecast batch regret.
          </div>
        </div>
      )}

      {/* 3. Dijkstra Shortest Path Lab */}
      {activeAlgorithmTab === 'dijkstra' && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '8px' }}>
            Dijkstra Shortest Path Routing Engine
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '16px' }}>
            Computes provably optimal single-source shortest path using a Min-Heap (<code>heapq</code>) Priority Queue.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr auto', gap: '14px', alignItems: 'flex-end', marginBottom: '20px' }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Origin Node</label>
              <select className="input-field" value={dijkStart} onChange={(e) => setDijkStart(e.target.value)}>
                <option value="Node_R1">Node_R1 (Bistro Gourmet)</option>
                <option value="Node_R2">Node_R2 (Spice Garden)</option>
                <option value="Node_D1">Node_D1 (Courier North)</option>
                <option value="Node_D2">Node_D2 (Courier South)</option>
              </select>
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Destination Node</label>
              <select className="input-field" value={dijkEnd} onChange={(e) => setDijkEnd(e.target.value)}>
                <option value="Node_C1">Node_C1 (Downtown Tower)</option>
                <option value="Node_C2">Node_C2 (Green Park Villa)</option>
                <option value="Node_C3">Node_C3 (Tech Park 303)</option>
                <option value="Node_C4">Node_C4 (Residency 404)</option>
              </select>
            </div>

            <button onClick={handleRunDijkstra} className="btn btn-primary">
              <Play size={15} /> Compute Shortest Path
            </button>
          </div>

          {dijkResult && (
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Computed Path:</div>
                <div style={{ fontWeight: 800, fontSize: '1.05rem', color: '#38bdf8' }}>{dijkResult.shortest_path.join(' ➔ ')}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Total Cost:</div>
                <div style={{ fontWeight: 800, fontSize: '1.05rem', color: '#10b981' }}>{dijkResult.total_cost_km} km</div>
              </div>
              <div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Execution Latency:</div>
                <div style={{ fontWeight: 800, fontSize: '1.05rem', color: '#fbbf24', fontFamily: 'var(--font-mono)' }}>{dijkResult.execution_time_ms} ms</div>
              </div>
            </div>
          )}

          <RouteMapVisualizer routeData={dijkRouteVisual} height={360} />
        </div>
      )}

      {/* 4. Dynamic Programming Lab */}
      {activeAlgorithmTab === 'dp' && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '8px' }}>
            Dynamic Programming: 0/1 Knapsack Courier Shift Batch Selection
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '16px' }}>
            Maximizes aggregate order priority/profit under delivery time window budget W via bottom-up memoization.
          </p>

          <div style={{ display: 'flex', gap: '14px', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Time Window Budget W (Mins):</label>
              <input
                type="number"
                className="input-field"
                style={{ width: '140px' }}
                value={dpWindow}
                onChange={(e) => setDpWindow(parseInt(e.target.value) || 120)}
              />
            </div>

            <button onClick={handleRunDP} className="btn btn-purple" style={{ marginTop: '18px' }}>
              <Play size={15} /> Solve DP Knapsack
            </button>
          </div>

          {dpResult && (
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px' }}>
              <div style={{ display: 'flex', gap: '20px', marginBottom: '14px' }}>
                <div>Max Profit / Utility: <strong style={{ color: '#38bdf8' }}>{dpResult.max_profit_or_priority}</strong></div>
                <div>Time Used: <strong style={{ color: '#10b981' }}>{dpResult.total_time_used} / {dpResult.time_window} mins</strong></div>
                <div>Runtime: <strong style={{ color: '#fbbf24' }}>{dpResult.execution_time_ms} ms</strong></div>
              </div>

              <div style={{ fontSize: '0.84rem' }}>
                <div style={{ fontWeight: 600, color: 'var(--text-muted)', marginBottom: '6px' }}>Selected Optimal Orders:</div>
                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                  {dpResult.selected_orders.map((o: any) => (
                    <span key={o.order_id} className="badge badge-emerald">
                      Order #{o.order_id} (Prep: {o.preparation_time}m, Priority: {o.profit_or_priority})
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 5. Backtracking Lab */}
      {activeAlgorithmTab === 'backtracking' && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '8px' }}>
            Backtracking: Constrained Multi-Drop Tour Sequencing
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '16px' }}>
            Permutation state space search with distance bounding & deadline pruning.
          </p>

          <button onClick={handleRunBacktracking} className="btn btn-purple" style={{ marginBottom: '16px' }}>
            <Play size={15} /> Explore Feasible Permutations
          </button>

          {btResult && (
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px' }}>
              <div style={{ display: 'flex', gap: '20px', marginBottom: '12px', flexWrap: 'wrap' }}>
                <div>Valid Permutations Found: <strong style={{ color: '#38bdf8' }}>{btResult.valid_sequences.length}</strong></div>
                <div>Best Tour Distance: <strong style={{ color: '#10b981' }}>{btResult.best_distance_km} km</strong></div>
                <div>Pruned Sub-Trees: <strong style={{ color: '#f43f5e' }}>{btResult.pruned_branches_count}</strong></div>
                <div>Runtime: <strong style={{ color: '#fbbf24' }}>{btResult.execution_time_ms} ms</strong></div>
              </div>

              {btResult.best_sequence && (
                <div style={{ fontSize: '0.86rem' }}>
                  Optimal Delivery Sequence: <strong>{btResult.best_sequence.join(' ➔ ')}</strong>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* 6. Branch and Bound Lab */}
      {activeAlgorithmTab === 'branch_bound' && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '8px' }}>
            Branch & Bound: Multi-Stop TSP Delivery Route Optimizer
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '16px' }}>
            Best-First Search state-space tree exploration with lower bound pruning (Minimum Outgoing Edge Relaxation).
          </p>

          <button onClick={handleRunBranchAndBound} className="btn btn-purple" style={{ marginBottom: '16px' }}>
            <Play size={15} /> Solve Branch & Bound TSP
          </button>

          {bbResult && (
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px' }}>
              <div style={{ display: 'flex', gap: '20px', marginBottom: '12px', flexWrap: 'wrap' }}>
                <div>Minimum Round-Trip Tour: <strong style={{ color: '#10b981' }}>{bbResult.minimum_distance_km} km</strong></div>
                <div>Nodes Explored: <strong>{bbResult.nodes_explored}</strong></div>
                <div>Sub-Trees Pruned: <strong style={{ color: '#f43f5e' }}>{bbResult.nodes_pruned}</strong></div>
                <div>Runtime: <strong style={{ color: '#fbbf24' }}>{bbResult.execution_time_ms} ms</strong></div>
              </div>

              <div style={{ fontSize: '0.86rem' }}>
                Optimal Tour: <strong>{bbResult.optimal_tour.join(' ➔ ')}</strong>
              </div>
            </div>
          )}
        </div>
      )}

      {/* 7. Divide and Conquer Lab */}
      {activeAlgorithmTab === 'divide_conquer' && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '8px' }}>
            Divide & Conquer: High-Throughput Stream Order Analytics
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '16px' }}>
            Master Theorem Case 2: <code>T(N) = 2T(N/2) + O(N) ⇒ Θ(N log N)</code>.
          </p>

          <div style={{ display: 'flex', gap: '14px', alignItems: 'center', marginBottom: '20px' }}>
            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Sample Stream Size N:</label>
              <input
                type="number"
                className="input-field"
                style={{ width: '140px' }}
                value={dacSampleSize}
                onChange={(e) => setDacSampleSize(parseInt(e.target.value) || 100)}
              />
            </div>

            <button onClick={handleRunDivideAndConquer} className="btn btn-purple" style={{ marginTop: '18px' }}>
              <Play size={15} /> Execute Divide & Conquer
            </button>
          </div>

          {dacResult && (
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px' }}>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px' }}>
                <div>Orders Processed: <strong>{dacResult.total_orders_analyzed}</strong></div>
                <div>Total Revenue: <strong style={{ color: '#38bdf8' }}>${dacResult.total_revenue}</strong></div>
                <div>Min Order: <strong>${dacResult.min_order_value}</strong></div>
                <div>Max Order: <strong>${dacResult.max_order_value}</strong></div>
                <div>Median Order: <strong style={{ color: '#10b981' }}>${dacResult.median_order_value}</strong></div>
                <div>Recursion Depth: <strong style={{ color: '#c084fc' }}>{dacResult.recursion_depth}</strong></div>
                <div>Latency: <strong style={{ color: '#fbbf24' }}>{dacResult.execution_time_ms} ms</strong></div>
              </div>
            </div>
          )}
        </div>
      )}

    </div>
  );
};
