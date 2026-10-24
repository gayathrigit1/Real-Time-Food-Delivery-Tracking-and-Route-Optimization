
import React, { useState } from 'react';
import { Navbar } from './components/Navbar';
import { AuthProvider, useAuth } from './context/AuthContext';
import { AdminDashboard } from './pages/AdminDashboard';
import { AlgorithmsLab } from './pages/AlgorithmsLab';
import { ConcurrencyLab } from './pages/ConcurrencyLab';
import { CustomerDashboard } from './pages/CustomerDashboard';
import { DeliveryDashboard } from './pages/DeliveryDashboard';
import { LoginPage } from './pages/LoginPage';
import { RestaurantDashboard } from './pages/RestaurantDashboard';

const MainLayout: React.FC = () => {
  const { user, loading } = useAuth();
  const [activeTab, setActiveTab] = useState<string>('customer');

  if (loading) {
    return (
      <div
        style={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'var(--bg-primary)',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: '50%',
              border: '3px solid rgba(59, 130, 246, 0.2)',
              borderTopColor: '#3b82f6',
              animation: 'spinSlow 1s linear infinite',
              margin: '0 auto 16px',
            }}
          />
          <div
            style={{
              fontSize: '0.9rem',
              color: 'var(--text-secondary)',
            }}
          >
            Initializing Intelligent Delivery System...
          </div>
        </div>
      </div>
    );
  }

  // Show login and signup to every visitor who is not logged in.
  if (!user) {
    return (
      <>
        <Navbar
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />
        <LoginPage />
      </>
    );
  }

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />

      <main style={{ flex: 1, paddingBottom: '40px' }}>
        {activeTab === 'customer' && <CustomerDashboard />}

        {activeTab === 'restaurant' && <RestaurantDashboard />}

        {activeTab === 'delivery' && <DeliveryDashboard />}

        {activeTab === 'algorithms' && <AlgorithmsLab />}

        {activeTab === 'concurrency' && <ConcurrencyLab />}

        {activeTab === 'admin' && <AdminDashboard />}
      </main>

      <footer
        style={{
          borderTop: '1px solid var(--border-color)',
          background: 'rgba(10, 13, 20, 0.8)',
          padding: '16px 24px',
          textAlign: 'center',
          fontSize: '0.78rem',
          color: 'var(--text-muted)',
        }}
      >
        <div>
          Real-Time Food Delivery Tracking and Route optimization
          {' '}• Academic Research & Implementation
        </div>

        <div
          style={{
            marginTop: '4px',
            fontSize: '0.72rem',
          }}
        >
          FastAPI Backend • React TypeScript Frontend • Dijkstra Routing
          {' '}• 6 Algorithm Modules • Asyncio/Threading/Multiprocessing
        </div>
      </footer>
    </div>
  );
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <MainLayout />
    </AuthProvider>
  );
};

export default App;
