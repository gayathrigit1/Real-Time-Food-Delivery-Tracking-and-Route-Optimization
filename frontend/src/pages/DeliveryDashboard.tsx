import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  Bike,
  CheckCircle2,
  Clock,
  Compass,
  MapPin,
  Navigation,
  Package,
  RefreshCw,
  Shield,
  Star,
  Truck,
  Zap,
} from 'lucide-react';
import { api } from '../api/client';
import { RouteMapVisualizer } from '../components/RouteMapVisualizer';
import { useAuth } from '../context/AuthContext';
import { DeliveryAgent, Order, OrderStatus, RouteResponse } from '../types';

export const DeliveryDashboard: React.FC = () => {
  const { user } = useAuth();
  const [agentProfile, setAgentProfile] = useState<DeliveryAgent | null>(null);
  const [assignedOrders, setAssignedOrders] = useState<Order[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null);
  const [routeData, setRouteData] = useState<RouteResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [agents, allOrders] = await Promise.all([api.getDeliveryAgents(), api.getOrders()]);

      const myProfile = agents.find((a) => a.user_id === user?.id) || agents[0];
      setAgentProfile(myProfile);

      if (myProfile) {
        // Filter orders assigned to this agent
        const myOrders = allOrders.filter(
          (o) => o.delivery_assignment && o.delivery_assignment.agent_id === myProfile.id
        );
        setAssignedOrders(myOrders);
        if (myOrders.length > 0 && !selectedOrder) {
          viewRoute(myOrders[0]);
        }
      }
    } catch (err: any) {
      console.error(err);
      setMessage({ type: 'error', text: err.message || 'Failed to load delivery profile.' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user]);

  const toggleAvailability = async () => {
    if (!agentProfile) return;
    try {
      const updated = await api.updateAgentStatus({ is_available: !agentProfile.is_available });
      setAgentProfile(updated);
      setMessage({
        type: 'success',
        text: `Availability status set to ${updated.is_available ? 'ONLINE (Ready for dispatch)' : 'OFFLINE'}.`,
      });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to update availability.' });
    }
  };

  const handleUpdateNode = async (node: string) => {
    try {
      const updated = await api.updateAgentStatus({ current_node: node });
      setAgentProfile(updated);
      setMessage({ type: 'success', text: `Current courier location node updated to ${node}.` });
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to update location node.' });
    }
  };

  const handleStatusTransition = async (orderId: number, status: OrderStatus) => {
    try {
      setMessage(null);
      await api.updateOrderStatus(orderId, status);
      setMessage({
        type: 'success',
        text: `Order #${orderId} marked as ${status}! Timestamp recorded.`,
      });
      fetchData();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to transition order state.' });
    }
  };

  const viewRoute = async (order: Order) => {
    setSelectedOrder(order);
    try {
      const res = await api.getOrderRoute(order.id);
      setRouteData(res);
    } catch (err) {
      console.error(err);
      setRouteData(null);
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
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, background: 'linear-gradient(90deg, #34d399, #10b981)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Delivery Courier Dispatch Hub
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            Greedy assignment evaluation • Dijkstra multi-stop shortest routes • Live order fulfillment
          </p>
        </div>

        <button onClick={fetchData} className="btn btn-sm btn-outline">
          <RefreshCw size={14} /> Refresh Deliveries
        </button>
      </div>

      {/* Agent Status Bar */}
      {agentProfile && (
        <div className="glass-panel" style={{ padding: '18px 24px', marginBottom: '24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <div style={{ width: '48px', height: '48px', borderRadius: '12px', background: 'linear-gradient(135deg, #10b981, #059669)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <Bike size={24} color="#fff" />
            </div>
            <div>
              <div style={{ fontWeight: 800, fontSize: '1.1rem' }}>{user?.full_name || 'Courier Agent'}</div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '3px', color: '#fbbf24' }}>
                  <Star size={13} fill="#fbbf24" /> {agentProfile.rating}
                </span>
                <span>•</span>
                <span>Vehicle: {agentProfile.vehicle_type}</span>
                <span>•</span>
                <span>Total Completed: {agentProfile.total_deliveries}</span>
                <span>•</span>
                <span>Active Load: <strong>{agentProfile.current_workload} / {agentProfile.max_capacity}</strong></span>
              </div>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Location:</span>
              <select
                className="input-field"
                style={{ padding: '6px 10px', fontSize: '0.82rem', width: 'auto' }}
                value={agentProfile.current_node}
                onChange={(e) => handleUpdateNode(e.target.value)}
              >
                <option value="Node_D1">Node_D1 (North Hub)</option>
                <option value="Node_D2">Node_D2 (South Hub)</option>
                <option value="Node_D3">Node_D3 (East Hub)</option>
                <option value="Node_R1">Node_R1 (Bistro)</option>
                <option value="Node_B">Node_B (Central)</option>
              </select>
            </div>

            <button
              onClick={toggleAvailability}
              className={`btn btn-sm ${agentProfile.is_available ? 'btn-emerald' : 'btn-outline'}`}
            >
              {agentProfile.is_available ? 'Online (Accepting Orders)' : 'Offline (Paused)'}
            </button>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '24px' }}>
        
        {/* Left: Assigned Orders Queue */}
        <div>
          <div className="glass-panel" style={{ padding: '20px' }}>
            <h3 style={{ fontWeight: 700, fontSize: '1.1rem', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Package size={18} color="#34d399" /> Assigned Delivery Orders ({assignedOrders.length})
            </h3>

            {assignedOrders.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '36px 0', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                No active orders assigned yet. When a restaurant marks an order READY_FOR_PICKUP, the Greedy Algorithm assigns the closest available courier!
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                {assignedOrders.map((ord) => {
                  const isSelected = selectedOrder?.id === ord.id;
                  return (
                    <div
                      key={ord.id}
                      className="glass-panel"
                      style={{
                        padding: '16px',
                        cursor: 'pointer',
                        border: isSelected ? '1px solid #06b6d4' : '1px solid var(--border-color)',
                        background: isSelected ? 'rgba(6, 182, 212, 0.08)' : 'var(--bg-card)',
                      }}
                      onClick={() => viewRoute(ord)}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <div style={{ fontWeight: 800, fontSize: '1rem' }}>Order #{ord.id}</div>
                        <span className="badge badge-emerald">{ord.status}</span>
                      </div>

                      <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>
                        Restaurant: <strong>Node_R1</strong> ➔ Customer: <strong>{ord.delivery_node}</strong>
                      </div>

                      <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                        Address: {ord.delivery_address}
                      </div>

                      {ord.delivery_assignment && (
                        <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '8px 12px', borderRadius: '6px', margin: '10px 0', fontSize: '0.78rem', display: 'flex', justifyContent: 'space-between' }}>
                          <span>Est. Distance: <strong>{ord.delivery_assignment.total_distance} km</strong></span>
                          <span>Score: <strong>{ord.delivery_assignment.assignment_score}</strong></span>
                        </div>
                      )}

                      {/* Status Action Buttons */}
                      <div style={{ display: 'flex', gap: '8px', marginTop: '10px' }}>
                        {ord.status === 'READY_FOR_PICKUP' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStatusTransition(ord.id, 'DELIVERING');
                            }}
                            className="btn btn-sm btn-purple"
                            style={{ flex: 1 }}
                          >
                            <Truck size={14} /> Confirm Pickup (Delivering)
                          </button>
                        )}

                        {ord.status === 'DELIVERING' && (
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleStatusTransition(ord.id, 'DELIVERED');
                            }}
                            className="btn btn-sm btn-emerald"
                            style={{ flex: 1 }}
                          >
                            <CheckCircle2 size={14} /> Mark Delivered
                          </button>
                        )}

                        {ord.status === 'DELIVERED' && (
                          <span className="badge badge-emerald" style={{ padding: '6px 12px' }}>
                            ✓ Delivery Completed
                          </span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        {/* Right: Live Route Telemetry & Dijkstra Visualizer */}
        <div style={{ gridColumn: 'span 2' }}>
          {selectedOrder ? (
            <div>
              <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <h3 style={{ fontWeight: 800, fontSize: '1.15rem' }}>
                  Live Navigation: Order #{selectedOrder.id}
                </h3>
                <span className="badge badge-blue">Path: {routeData?.path.join(' ➔ ')}</span>
              </div>
              <RouteMapVisualizer routeData={routeData} height={420} />
            </div>
          ) : (
            <RouteMapVisualizer height={420} />
          )}
        </div>

      </div>

    </div>
  );
};
