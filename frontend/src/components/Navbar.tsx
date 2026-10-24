import React from 'react';
import {
  Activity,
  Cpu,
  LogOut,
  Navigation,
  ShieldAlert,
  ShoppingBag,
  Store,
  Truck,
  UserCheck,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { UserRole } from '../types';

interface NavbarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ activeTab, setActiveTab }) => {
  const { user, logout, demoLogin } = useAuth();

  const getRoleBadge = (role?: UserRole) => {
    switch (role) {
      case 'ADMIN':
        return <span className="badge badge-rose">Admin</span>;
      case 'RESTAURANT':
        return <span className="badge badge-amber">Restaurant</span>;
      case 'DELIVERY_AGENT':
        return <span className="badge badge-emerald">Courier</span>;
      case 'CUSTOMER':
      default:
        return <span className="badge badge-blue">Customer</span>;
    }
  };

  return (
    <header className="glass-panel" style={{ borderRadius: 0, borderTop: 'none', borderLeft: 'none', borderRight: 'none', position: 'sticky', top: 0, zIndex: 100 }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '12px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
        
        {/* Logo & Title */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => setActiveTab('customer')}>
          <div style={{ width: '40px', height: '40px', borderRadius: '12px', background: 'linear-gradient(135deg, #3b82f6, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)' }}>
            <Navigation size={22} color="#fff" />
          </div>
          <div>
            <div style={{ fontWeight: 800, fontSize: '1.05rem', letterSpacing: '-0.02em', background: 'linear-gradient(90deg, #60a5fa, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
              RouteFlow AI
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Real-Time Food Delivery Tracking & Route optimization
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(15, 23, 42, 0.6)', padding: '4px', borderRadius: '10px', border: '1px solid var(--border-color)', overflowX: 'auto' }}>
          <button
            onClick={() => setActiveTab('customer')}
            className={`btn btn-sm ${activeTab === 'customer' ? 'btn-primary' : 'btn-outline'}`}
            style={{ border: 'none' }}
          >
            <ShoppingBag size={15} /> Customer
          </button>

          <button
            onClick={() => setActiveTab('restaurant')}
            className={`btn btn-sm ${activeTab === 'restaurant' ? 'btn-primary' : 'btn-outline'}`}
            style={{ border: 'none' }}
          >
            <Store size={15} /> Restaurant
          </button>

          <button
            onClick={() => setActiveTab('delivery')}
            className={`btn btn-sm ${activeTab === 'delivery' ? 'btn-primary' : 'btn-outline'}`}
            style={{ border: 'none' }}
          >
            <Truck size={15} /> Delivery
          </button>

          <button
            onClick={() => setActiveTab('algorithms')}
            className={`btn btn-sm ${activeTab === 'algorithms' ? 'btn-purple' : 'btn-outline'}`}
            style={{ border: 'none' }}
          >
            <Cpu size={15} /> 6 Algorithms Lab
          </button>

          <button
            onClick={() => setActiveTab('concurrency')}
            className={`btn btn-sm ${activeTab === 'concurrency' ? 'btn-emerald' : 'btn-outline'}`}
            style={{ border: 'none' }}
          >
            <Activity size={15} /> Concurrency Lab
          </button>

          <button
            onClick={() => setActiveTab('admin')}
            className={`btn btn-sm ${activeTab === 'admin' ? 'btn-primary' : 'btn-outline'}`}
            style={{ border: 'none' }}
          >
            <ShieldAlert size={15} /> Admin
          </button>
        </nav>

        {/* User Status / Quick Role Switcher */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <div style={{ textAlign: 'right' }}>
                <div style={{ fontSize: '0.86rem', fontWeight: 600 }}>{user.full_name}</div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', justifyContent: 'flex-end', marginTop: '2px' }}>
                  {getRoleBadge(user.role)}
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>{user.node_id}</span>
                </div>
              </div>

              {/* Quick switch dropdown simulation */}
              <div style={{ display: 'flex', gap: '4px' }}>
                <button
                  title="Switch to Customer"
                  onClick={() => demoLogin('CUSTOMER')}
                  className="btn btn-sm btn-outline"
                  style={{ padding: '6px 8px' }}
                >
                  <ShoppingBag size={14} color="#60a5fa" />
                </button>
                <button
                  title="Switch to Restaurant"
                  onClick={() => demoLogin('RESTAURANT')}
                  className="btn btn-sm btn-outline"
                  style={{ padding: '6px 8px' }}
                >
                  <Store size={14} color="#fbbf24" />
                </button>
                <button
                  title="Switch to Delivery Agent"
                  onClick={() => demoLogin('DELIVERY_AGENT')}
                  className="btn btn-sm btn-outline"
                  style={{ padding: '6px 8px' }}
                >
                  <Truck size={14} color="#34d399" />
                </button>
              </div>

              <button onClick={logout} className="btn btn-sm btn-outline" title="Sign Out">
                <LogOut size={15} />
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '8px' }}>
              <button onClick={() => demoLogin('CUSTOMER')} className="btn btn-sm btn-primary">
                <UserCheck size={15} /> Quick Demo Login
              </button>
            </div>
          )}
        </div>

      </div>
    </header>
  );
};
