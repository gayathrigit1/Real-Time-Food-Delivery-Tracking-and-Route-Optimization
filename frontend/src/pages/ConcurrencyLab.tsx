import React, { useState } from 'react';
import {
  Activity,
  AlertCircle,
  CheckCircle2,
  Clock,
  Cpu,
  Layers,
  Play,
  RefreshCw,
  Server,
  Zap,
} from 'lucide-react';
import { api } from '../api/client';
import { ConcurrencyBenchmarkResponse } from '../types';

export const ConcurrencyLab: React.FC = () => {
  const [activeModel, setActiveModel] = useState<'asyncio' | 'threading' | 'multiprocessing'>('asyncio');
  const [taskCount, setTaskCount] = useState(8);
  const [workerCount, setWorkerCount] = useState(4);
  const [loading, setLoading] = useState(false);
  const [benchmarkResult, setBenchmarkResult] = useState<ConcurrencyBenchmarkResponse | null>(null);

  const runBenchmark = async () => {
    try {
      setLoading(true);
      let res: ConcurrencyBenchmarkResponse;
      if (activeModel === 'asyncio') {
        res = await api.benchmarkAsyncio(taskCount);
      } else if (activeModel === 'threading') {
        res = await api.benchmarkThreading(taskCount, workerCount);
      } else {
        res = await api.benchmarkMultiprocessing(taskCount, workerCount);
      }
      setBenchmarkResult(res);
    } catch (err) {
      console.error('Concurrency benchmark failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
      
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, background: 'linear-gradient(90deg, #34d399, #06b6d4)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Concurrency & Parallelism Architecture Lab
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            Empirical comparisons between <code>asyncio</code>, <code>threading</code>, and <code>multiprocessing</code> under the Python Global Interpreter Lock (GIL).
          </p>
        </div>

        <button onClick={runBenchmark} disabled={loading} className="btn btn-emerald">
          {loading ? <RefreshCw className="animate-spin" size={16} /> : <Play size={16} />}
          {loading ? 'Executing Workload...' : `Run ${activeModel.toUpperCase()} Benchmark`}
        </button>
      </div>

      {/* Model Selection Tabs */}
      <div style={{ display: 'flex', gap: '12px', marginBottom: '24px' }}>
        {[
          { id: 'asyncio', title: '1. Asyncio Event Loop', subtitle: 'I/O-Bound (Single Thread, Non-blocking Coroutines)', color: '#38bdf8' },
          { id: 'threading', title: '2. Multi-Threading', subtitle: 'I/O-Bound (OS Threads with GIL Release on Sleep/Network)', color: '#a78bfa' },
          { id: 'multiprocessing', title: '3. Multi-Processing', subtitle: 'CPU-Bound (True Multi-Core Parallelism, Independent GILs)', color: '#34d399' },
        ].map((tab) => {
          const isSelected = activeModel === tab.id;
          return (
            <div
              key={tab.id}
              onClick={() => {
                setActiveModel(tab.id as any);
                setBenchmarkResult(null);
              }}
              className="glass-panel glass-panel-interactive"
              style={{
                flex: 1,
                padding: '16px',
                cursor: 'pointer',
                border: isSelected ? `1px solid ${tab.color}` : '1px solid var(--border-color)',
                background: isSelected ? 'rgba(16, 185, 129, 0.08)' : 'var(--bg-card)',
              }}
            >
              <div style={{ fontWeight: 800, fontSize: '1rem', color: tab.color }}>{tab.title}</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '4px' }}>{tab.subtitle}</div>
            </div>
          );
        })}
      </div>

      {/* Parameters Panel */}
      <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px', display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
        <div>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Task Batch Size N:</label>
          <input
            type="number"
            className="input-field"
            style={{ width: '120px' }}
            value={taskCount}
            min={1}
            max={30}
            onChange={(e) => setTaskCount(parseInt(e.target.value) || 4)}
          />
        </div>

        {activeModel !== 'asyncio' && (
          <div>
            <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Worker Pool Size (Threads / Processes):</label>
            <input
              type="number"
              className="input-field"
              style={{ width: '120px' }}
              value={workerCount}
              min={1}
              max={8}
              onChange={(e) => setWorkerCount(parseInt(e.target.value) || 4)}
            />
          </div>
        )}

        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Workload Profile:</div>
          <div style={{ fontSize: '0.86rem', fontWeight: 600, color: '#f8fafc' }}>
            {activeModel === 'asyncio' && 'Non-blocking I/O order verification coroutines'}
            {activeModel === 'threading' && 'Blocking outbound SMS/notification dispatches (OS threads)'}
            {activeModel === 'multiprocessing' && 'CPU-intensive SHA-256 cryptographic chain proofs'}
          </div>
        </div>

        <button onClick={runBenchmark} disabled={loading} className="btn btn-emerald">
          <Zap size={15} /> Execute
        </button>
      </div>

      {/* Results Telemetry */}
      {benchmarkResult && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          
          {/* Key Metrics Cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px', marginBottom: '24px' }}>
            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Workload Type</div>
              <div style={{ fontWeight: 800, fontSize: '1rem', color: '#38bdf8', marginTop: '4px' }}>
                {benchmarkResult.workload_type}
              </div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Concurrent Elapsed Time</div>
              <div style={{ fontWeight: 800, fontSize: '1.25rem', color: '#34d399', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
                {benchmarkResult.total_elapsed_time_ms.toFixed(2)} ms
              </div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Sequential Baseline (Sum)</div>
              <div style={{ fontWeight: 800, fontSize: '1.25rem', color: '#fbbf24', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
                {benchmarkResult.sequential_baseline_ms.toFixed(2)} ms
              </div>
            </div>

            <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '16px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Measured Speedup Ratio</div>
              <div style={{ fontWeight: 800, fontSize: '1.35rem', color: '#c084fc', fontFamily: 'var(--font-mono)', marginTop: '4px' }}>
                {benchmarkResult.speedup_ratio}×
              </div>
            </div>
          </div>

          {/* Architectural Analysis Box */}
          <div style={{ background: 'rgba(16, 185, 129, 0.08)', border: '1px solid rgba(16, 185, 129, 0.25)', padding: '16px 20px', borderRadius: '10px', marginBottom: '24px' }}>
            <div style={{ fontWeight: 700, fontSize: '0.92rem', color: '#34d399', marginBottom: '6px' }}>
              Architectural & GIL Analysis:
            </div>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-primary)', marginBottom: '6px' }}>{benchmarkResult.explanation}</p>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
              <strong>GIL Behavior:</strong> {benchmarkResult.gil_impact_analysis}
            </p>
          </div>

          {/* Detailed Task Execution Breakdown */}
          <h3 style={{ fontWeight: 700, fontSize: '1.05rem', marginBottom: '12px' }}>
            Task Worker Telemetry Stream ({benchmarkResult.detailed_tasks.length} tasks)
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
            {benchmarkResult.detailed_tasks.map((task) => (
              <div key={task.task_id} style={{ background: 'rgba(15, 23, 42, 0.5)', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 600 }}>
                  <span>{task.task_name}</span>
                  <span style={{ color: '#34d399', fontFamily: 'var(--font-mono)' }}>{task.duration_ms} ms</span>
                </div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.72rem', marginTop: '4px' }}>
                  Execution Context: <code>{task.thread_or_process_id}</code>
                </div>
                <div style={{ color: 'var(--text-secondary)', marginTop: '4px' }}>{task.result}</div>
              </div>
            ))}
          </div>

        </div>
      )}

    </div>
  );
};
