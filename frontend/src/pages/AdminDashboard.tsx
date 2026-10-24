import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  Database,
  Layers,
  Package,
  RefreshCw,
  ShieldAlert,
  Store,
  Truck,
  Users,
} from 'lucide-react';
import { api } from '../api/client';

export const AdminDashboard: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [resetting, setResetting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchSummary = async () => {
    try {
      setLoading(true);
      const data = await api.getAdminSummary();
      setSummary(data);
    } catch (err: any) {
      console.error(err);
      setMessage({ type: 'error', text: err.message || 'Failed to fetch admin telemetry.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  const handleResetSeed = async () => {
    if (!window.confirm('Reset and re-seed database with default demo data?')) return;
    try {
      setResetting(true);
      const res = await api.resetSeedData();
      setMessage({ type: 'success', text: res.message || 'Database re-seeded successfully.' });
      fetchSummary();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Re-seeding failed.' });
    } finally {
      setResetting(false);
    }
  };

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
      
      {/* Alerts */}
      {message && (
        <div
          className="glass-panel"
          style={{
            padding: '12px 18px',
            marginBottom: '20px',
            borderLeft: `4px solid ${message.type === 'success' ? '#10b981' : '#f43f5e'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {message.type === 'success' ? <CheckCircle2 size={18} color="#10b981" /> : <AlertCircle size={18} color="#f43f5e" />}
            <span style={{ fontSize: '0.9rem' }}>{message.text}</span>
          </div>
          <button onClick={() => setMessage(null)} className="btn btn-sm btn-outline" style={{ padding: '4px 8px' }}>✕</button>
        </div>
      )}

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, background: 'linear-gradient(90deg, #f43f5e, #fb7185)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            System Administration & Telemetry
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            Platform metrics, order state distributions, and database maintenance controls.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button onClick={handleResetSeed} disabled={resetting} className="btn btn-sm btn-primary" style={{ background: '#f43f5e' }}>
            <Database size={14} /> {resetting ? 'Seeding...' : 'Reset & Seed Demo Data'}
          </button>
          <button onClick={fetchSummary} className="btn btn-sm btn-outline">
            <RefreshCw size={14} /> Refresh Metrics
          </button>
        </div>
      </div>

      {/* Metrics Cards */}
      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '18px', marginBottom: '24px' }}>
          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Registered Users</span>
              <Users size={18} color="#3b82f6" />
            </div>
            <div style={{ fontWeight: 800, fontSize: '1.6rem', marginTop: '6px', color: '#f8fafc' }}>
              {summary.total_users}
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Active Restaurants</span>
              <Store size={18} color="#f59e0b" />
            </div>
            <div style={{ fontWeight: 800, fontSize: '1.6rem', marginTop: '6px', color: '#f8fafc' }}>
              {summary.total_restaurants}
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Menu Catalog Dishes</span>
              <Layers size={18} color="#8b5cf6" />
            </div>
            <div style={{ fontWeight: 800, fontSize: '1.6rem', marginTop: '6px', color: '#f8fafc' }}>
              {summary.total_menu_items}
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Total Orders</span>
              <Package size={18} color="#10b981" />
            </div>
            <div style={{ fontWeight: 800, fontSize: '1.6rem', marginTop: '6px', color: '#f8fafc' }}>
              {summary.total_orders}
            </div>
          </div>

          <div className="glass-panel" style={{ padding: '18px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Couriers (Online / Total)</span>
              <Truck size={18} color="#06b6d4" />
            </div>
            <div style={{ fontWeight: 800, fontSize: '1.6rem', marginTop: '6px', color: '#34d399' }}>
              {summary.available_delivery_agents} / {summary.total_delivery_agents}
            </div>
          </div>
        </div>
      )}

      {/* Orders By Status Grid */}
      {summary && summary.orders_by_status && (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <h3 style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '16px' }}>Order Status Breakdown</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '14px' }}>
            {Object.entries(summary.orders_by_status).map(([st, count]: any) => (
              <div key={st} style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '14px', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{st}</div>
                <div style={{ fontWeight: 800, fontSize: '1.3rem', color: '#38bdf8', marginTop: '4px' }}>{count}</div>
              </div>
            ))}
          </div>
        </div>
      )}

    </div>
  );
};
