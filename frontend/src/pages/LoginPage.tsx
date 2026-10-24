import React, { useState } from 'react';
import {
  AlertCircle,
  KeyRound,
  Lock,
  Mail,
  Navigation,
  ShieldAlert,
  ShoppingBag,
  Store,
  Truck,
  User,
  UserPlus,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';

export const LoginPage: React.FC = () => {
  const { login, register, demoLogin } = useAuth();
  const [isRegister, setIsRegister] = useState(false);

  // Form states
  const [identifier, setIdentifier] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [username, setUsername] = useState('');
  const [role, setRole] = useState<UserRole>('CUSTOMER');
  const [address, setAddress] = useState('');
  const [nodeId, setNodeId] = useState('Node_C1');

  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      if (isRegister) {
        await register({
          email: identifier,
          username,
          password,
          full_name: fullName,
          role,
          address,
          node_id: nodeId,
        });
      } else {
        await login(identifier, password);
      }
    } catch (err: any) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoSelect = async (demoRole: UserRole) => {
    setError(null);
    setLoading(true);
    try {
      await demoLogin(demoRole);
    } catch (err: any) {
      setError(err.message || 'Demo login failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: 'calc(100vh - 70px)', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
      <div style={{ width: '100%', maxWidth: '520px' }}>
        
        {/* Brand Banner */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{ width: '56px', height: '56px', borderRadius: '16px', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 25px rgba(59, 130, 246, 0.4)', marginBottom: '14px' }}>
            <Navigation size={28} color="#fff" />
          </div>
          <h1 style={{ fontSize: '1.8rem', fontWeight: 800, letterSpacing: '-0.02em', background: 'linear-gradient(90deg, #60a5fa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Intelligent Food Delivery System
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '6px' }}>
            Academic demonstration platform for algorithmic routing and order optimization.
          </p>
        </div>

        {/* 1-Click Quick Demo Sign In Bar */}
        <div className="glass-panel" style={{ padding: '16px 20px', marginBottom: '20px' }}>
          <div style={{ fontSize: '0.8rem', fontWeight: 700, color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            ⚡ 1-Click Instant Demo Login (Role Presets)
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
            <button onClick={() => handleDemoSelect('CUSTOMER')} className="btn btn-sm btn-outline" style={{ justifyContent: 'flex-start' }}>
              <ShoppingBag size={14} color="#60a5fa" /> Customer (Alice)
            </button>
            <button onClick={() => handleDemoSelect('RESTAURANT')} className="btn btn-sm btn-outline" style={{ justifyContent: 'flex-start' }}>
              <Store size={14} color="#fbbf24" /> Restaurant (Marco)
            </button>
            <button onClick={() => handleDemoSelect('DELIVERY_AGENT')} className="btn btn-sm btn-outline" style={{ justifyContent: 'flex-start' }}>
              <Truck size={14} color="#34d399" /> Courier (Sam Swift)
            </button>
            <button onClick={() => handleDemoSelect('ADMIN')} className="btn btn-sm btn-outline" style={{ justifyContent: 'flex-start' }}>
              <ShieldAlert size={14} color="#f43f5e" /> Administrator
            </button>
          </div>
        </div>

        {/* Main Auth Form Card */}
        <div className="glass-panel" style={{ padding: '28px' }}>
          <div style={{ display: 'flex', borderBottom: '1px solid var(--border-color)', marginBottom: '20px' }}>
            <button
              type="button"
              onClick={() => setIsRegister(false)}
              style={{
                flex: 1,
                padding: '10px',
                background: 'none',
                border: 'none',
                borderBottom: !isRegister ? '2px solid #3b82f6' : '2px solid transparent',
                color: !isRegister ? '#fff' : 'var(--text-muted)',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              Sign In
            </button>
            <button
              type="button"
              onClick={() => setIsRegister(true)}
              style={{
                flex: 1,
                padding: '10px',
                background: 'none',
                border: 'none',
                borderBottom: isRegister ? '2px solid #3b82f6' : '2px solid transparent',
                color: isRegister ? '#fff' : 'var(--text-muted)',
                fontWeight: 700,
                cursor: 'pointer',
              }}
            >
              Register New User
            </button>
          </div>

          {error && (
            <div style={{ background: 'rgba(244, 63, 94, 0.12)', border: '1px solid rgba(244, 63, 94, 0.3)', padding: '10px 14px', borderRadius: '8px', color: '#fb7185', fontSize: '0.86rem', display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            {isRegister && (
              <>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Full Name</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Eleanor Vance"
                    className="input-field"
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Username</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. eleanor_v"
                    className="input-field"
                    value={username}
                    onChange={(e) => setUsername(e.target.value)}
                  />
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div>
                    <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Account Role</label>
                    <select className="input-field" value={role} onChange={(e) => setRole(e.target.value as UserRole)}>
                      <option value="CUSTOMER">Customer</option>
                      <option value="RESTAURANT">Restaurant Owner</option>
                      <option value="DELIVERY_AGENT">Delivery Agent</option>
                      <option value="ADMIN">Administrator</option>
                    </select>
                  </div>

                  <div>
                    <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Road Network Node</label>
                    <select className="input-field" value={nodeId} onChange={(e) => setNodeId(e.target.value)}>
                      <option value="Node_C1">Node_C1 (Downtown)</option>
                      <option value="Node_C2">Node_C2 (Green Park)</option>
                      <option value="Node_C3">Node_C3 (Tech Park)</option>
                      <option value="Node_R1">Node_R1 (Bistro Gourmet)</option>
                      <option value="Node_D1">Node_D1 (Courier North)</option>
                    </select>
                  </div>
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Street Address</label>
                  <input
                    type="text"
                    placeholder="e.g. 789 Horizon Way"
                    className="input-field"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                  />
                </div>
              </>
            )}

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Email Address or Username</label>
              <input
                type="text"
                required
                placeholder={isRegister ? 'name@example.com' : 'customer@fooddelivery.local'}
                className="input-field"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
              />
            </div>

            <div>
              <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>Password</label>
              <input
                type="password"
                required
                placeholder="••••••••"
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>

            <button type="submit" disabled={loading} className="btn btn-primary" style={{ marginTop: '8px', padding: '12px' }}>
              {loading ? 'Authenticating...' : isRegister ? 'Complete Registration' : 'Sign In'}
            </button>
          </form>
        </div>

      </div>
    </div>
  );
};
