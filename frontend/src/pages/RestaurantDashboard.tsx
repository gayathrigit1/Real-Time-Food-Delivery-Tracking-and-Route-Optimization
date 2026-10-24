
import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  ChefHat,
  PackageCheck,
  Plus,
  RefreshCw,
  UtensilsCrossed,
  Zap,
} from 'lucide-react';
import { api } from '../api/client';
import { RouteMapVisualizer } from '../components/RouteMapVisualizer';
import { useAuth } from '../context/AuthContext';
import { Order, OrderStatus, Restaurant, RouteResponse } from '../types';

export const RestaurantDashboard: React.FC = () => {
  const { user } = useAuth();

  const [restaurant, setRestaurant] = useState<Restaurant | null>(null);
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeRouteOrder, setActiveRouteOrder] = useState<Order | null>(null);
  const [routeData, setRouteData] = useState<RouteResponse | null>(null);
  const [message, setMessage] = useState<{
    type: 'success' | 'error';
    text: string;
  } | null>(null);

  const [showAddModal, setShowAddModal] = useState(false);
  const [newItemName, setNewItemName] = useState('');
  const [newItemDesc, setNewItemDesc] = useState('');
  const [newItemPrice, setNewItemPrice] = useState('14.00');
  const [newItemCategory, setNewItemCategory] = useState('Main Course');
  const [newItemPrepTime, setNewItemPrepTime] = useState(15);

  const fetchData = async () => {
    try {
      setLoading(true);

      const allRestaurants = await api.getRestaurants();

      // Never fall back to another restaurant's profile.
      const myRestaurant = allRestaurants.find(
        (r) => Number(r.owner_id) === Number(user?.id)
      );

      if (!myRestaurant) {
        setRestaurant(null);
        setOrders([]);
        setMessage({
          type: 'error',
          text: 'No restaurant profile was found for your account.',
        });
        return;
      }

      setRestaurant(myRestaurant);

      const allOrders = await api.getOrders();

      setOrders(
        allOrders.filter(
          (order) => Number(order.restaurant_id) === Number(myRestaurant.id)
        )
      );

      setMessage((current) =>
        current?.type === 'error' ? null : current
      );
    } catch (err: unknown) {
      console.error('Restaurant dashboard error:', err);

      setMessage({
        type: 'error',
        text:
          err instanceof Error
            ? err.message
            : 'Failed to load restaurant data.',
      });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.id == null) {
      setRestaurant(null);
      setOrders([]);
      setLoading(false);
      return;
    }

    void fetchData();
  }, [user?.id]);

  const handleUpdateStatus = async (
    orderId: number,
    status: OrderStatus
  ) => {
    try {
      setMessage(null);

      const updated = await api.updateOrderStatus(orderId, status);

      setMessage({
        type: 'success',
        text: `Order #${orderId} status changed to ${status}.${
          status === 'READY_FOR_PICKUP'
            ? ' Courier assignment and route calculation requested.'
            : ''
        }`,
      });

      await fetchData();

      if (updated.delivery_assignment) {
        await viewRoute(updated);
      }
    } catch (err: unknown) {
      setMessage({
        type: 'error',
        text:
          err instanceof Error ? err.message : 'Status update failed.',
      });
    }
  };

  const handleAddMenuItem = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!restaurant) {
      setMessage({
        type: 'error',
        text: 'Your restaurant profile is not available.',
      });
      return;
    }

    try {
      await api.addMenuItem(restaurant.id, {
        name: newItemName,
        description: newItemDesc,
        price: Number.parseFloat(newItemPrice),
        category: newItemCategory,
        is_available: true,
        preparation_time_mins: newItemPrepTime,
      });

      setMessage({
        type: 'success',
        text: `Menu item '${newItemName}' added successfully!`,
      });

      setShowAddModal(false);
      setNewItemName('');
      setNewItemDesc('');
      setNewItemPrice('14.00');
      setNewItemCategory('Main Course');
      setNewItemPrepTime(15);

      await fetchData();
    } catch (err: unknown) {
      setMessage({
        type: 'error',
        text:
          err instanceof Error ? err.message : 'Failed to add menu item.',
      });
    }
  };

  const viewRoute = async (order: Order) => {
    setActiveRouteOrder(order);

    try {
      const result = await api.getOrderRoute(order.id);
      setRouteData(result);
    } catch (err) {
      console.error('Failed to load courier route:', err);
      setRouteData(null);
      setMessage({
        type: 'error',
        text: 'Could not load the courier route for this order.',
      });
    }
  };

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
      {message && (
        <div
          className="glass-panel"
          style={{
            padding: '12px 18px',
            marginBottom: '20px',
            borderLeft: `4px solid ${
              message.type === 'success' ? '#10b981' : '#f43f5e'
            }`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {message.type === 'success' ? (
              <CheckCircle2 size={18} color="#10b981" />
            ) : (
              <AlertCircle size={18} color="#f43f5e" />
            )}
            <span style={{ fontSize: '0.9rem' }}>{message.text}</span>
          </div>

          <button
            onClick={() => setMessage(null)}
            className="btn btn-sm btn-outline"
            style={{ padding: '4px 8px' }}
          >
            ✕
          </button>
        </div>
      )}

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          marginBottom: '24px',
          flexWrap: 'wrap',
          gap: '12px',
        }}
      >
        <div>
          <h1
            style={{
              fontSize: '1.75rem',
              fontWeight: 800,
              background: 'linear-gradient(90deg, #fbbf24, #f59e0b)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Restaurant Kitchen & Order Management
          </h1>

          <p
            style={{
              color: 'var(--text-secondary)',
              fontSize: '0.9rem',
              marginTop: '4px',
            }}
          >
            {restaurant
              ? `${restaurant.name} (${restaurant.node_id})`
              : 'Kitchen Portal'}{' '}
            • Manage incoming orders & menu catalog
          </p>
        </div>

        <div style={{ display: 'flex', gap: '10px' }}>
          <button
            onClick={() => setShowAddModal(true)}
            className="btn btn-sm btn-primary"
            disabled={!restaurant}
          >
            <Plus size={14} /> Add Menu Item
          </button>

          <button onClick={() => void fetchData()} className="btn btn-sm btn-outline">
            <RefreshCw size={14} /> Refresh
          </button>
        </div>
      </div>

      {loading ? (
        <div className="glass-panel" style={{ padding: '36px', textAlign: 'center' }}>
          Loading your restaurant dashboard...
        </div>
      ) : !restaurant ? (
        <div className="glass-panel" style={{ padding: '24px' }}>
          <AlertCircle size={20} color="#f43f5e" />
          <p style={{ marginTop: '10px' }}>
            No restaurant profile is linked to this account. Please verify
            that you are logged in with the correct restaurant account.
          </p>
        </div>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))',
            gap: '24px',
          }}
        >
          <div style={{ gridColumn: 'span 2', minWidth: 0 }}>
            <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
              <h3
                style={{
                  fontWeight: 700,
                  fontSize: '1.1rem',
                  marginBottom: '16px',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                }}
              >
                <UtensilsCrossed size={18} color="#fbbf24" />
                Live Kitchen Orders Queue ({orders.length})
              </h3>

              {orders.length === 0 ? (
                <div
                  style={{
                    textAlign: 'center',
                    padding: '36px 0',
                    color: 'var(--text-muted)',
                  }}
                >
                  No active orders for your restaurant yet.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
                  {orders.map((ord) => (
                    <div
                      key={ord.id}
                      className="glass-panel"
                      style={{
                        padding: '16px',
                        border: '1px solid var(--border-color)',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'flex-start',
                          flexWrap: 'wrap',
                          gap: '8px',
                        }}
                      >
                        <div>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                            <span style={{ fontWeight: 800, fontSize: '1.05rem' }}>
                              Order #{ord.id}
                            </span>
                            <span className="badge badge-purple">{ord.status}</span>
                          </div>

                          <div
                            style={{
                              fontSize: '0.82rem',
                              color: 'var(--text-secondary)',
                              marginTop: '4px',
                            }}
                          >
                            Dropoff: <strong>{ord.delivery_node}</strong> (
                            {ord.delivery_address})
                          </div>

                          {ord.special_instructions && (
                            <div
                              style={{
                                fontSize: '0.78rem',
                                color: '#fbbf24',
                                marginTop: '2px',
                              }}
                            >
                              Note: "{ord.special_instructions}"
                            </div>
                          )}
                        </div>

                        <div style={{ textAlign: 'right' }}>
                          <div
                            style={{
                              fontWeight: 800,
                              color: '#38bdf8',
                              fontSize: '1.1rem',
                            }}
                          >
                            ${ord.total_amount.toFixed(2)}
                          </div>
                          <div
                            style={{
                              fontSize: '0.74rem',
                              color: 'var(--text-muted)',
                            }}
                          >
                            {new Date(ord.created_at).toLocaleTimeString()}
                          </div>
                        </div>
                      </div>

                      <div
                        style={{
                          background: 'rgba(15, 23, 42, 0.6)',
                          padding: '10px 14px',
                          borderRadius: '8px',
                          margin: '12px 0',
                          fontSize: '0.82rem',
                        }}
                      >
                        <div
                          style={{
                            fontWeight: 600,
                            color: 'var(--text-muted)',
                            marginBottom: '4px',
                          }}
                        >
                          Ordered Items:
                        </div>

                        {ord.items.map((item) => (
                          <div
                            key={item.id}
                            style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              padding: '2px 0',
                            }}
                          >
                            <span>
                              {item.quantity}× {item.item_name}
                            </span>
                            <span style={{ fontFamily: 'var(--font-mono)' }}>
                              ${item.subtotal.toFixed(2)}
                            </span>
                          </div>
                        ))}
                      </div>

                      <div
                        style={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          alignItems: 'center',
                          flexWrap: 'wrap',
                          gap: '8px',
                        }}
                      >
                        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                          {ord.status === 'PENDING' && (
                            <button
                              onClick={() =>
                                void handleUpdateStatus(ord.id, 'PREPARING')
                              }
                              className="btn btn-sm btn-purple"
                            >
                              <ChefHat size={14} /> Start Preparing
                            </button>
                          )}

                          {ord.status === 'PREPARING' && (
                            <button
                              onClick={() =>
                                void handleUpdateStatus(ord.id, 'READY_FOR_PICKUP')
                              }
                              className="btn btn-sm btn-emerald"
                            >
                              <PackageCheck size={14} /> Mark Ready For Pickup
                              (Auto-Assign Courier)
                            </button>
                          )}

                          {ord.delivery_assignment && (
                            <button
                              onClick={() => void viewRoute(ord)}
                              className="btn btn-sm btn-outline"
                            >
                              <Zap size={14} color="#06b6d4" /> View Courier Route
                            </button>
                          )}
                        </div>

                        {ord.delivery_assignment && (
                          <div style={{ fontSize: '0.78rem', color: '#34d399' }}>
                            Assigned to Courier #{ord.delivery_assignment.agent_id} •{' '}
                            {ord.delivery_assignment.total_distance} km
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          <div>
            <div className="glass-panel" style={{ padding: '20px' }}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  marginBottom: '16px',
                  gap: '8px',
                }}
              >
                <h3 style={{ fontWeight: 700, fontSize: '1.05rem' }}>
                  Active Menu ({restaurant.menu_items.length})
                </h3>
                <span className="badge badge-amber">{restaurant.cuisine_type}</span>
              </div>

              <div
                style={{
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '10px',
                  maxHeight: '520px',
                  overflowY: 'auto',
                }}
              >
                {restaurant.menu_items.length === 0 ? (
                  <p style={{ color: 'var(--text-muted)', padding: '12px 0' }}>
                    Your menu is empty. Select "Add Menu Item" to add your first dish.
                  </p>
                ) : (
                  restaurant.menu_items.map((item) => (
                    <div
                      key={item.id}
                      style={{
                        background: 'rgba(15, 23, 42, 0.5)',
                        padding: '12px',
                        borderRadius: '8px',
                        border: '1px solid var(--border-color)',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', gap: '8px' }}>
                        <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>
                          {item.name}
                        </div>
                        <div style={{ fontWeight: 800, color: '#38bdf8' }}>
                          ${item.price.toFixed(2)}
                        </div>
                      </div>
                      <div
                        style={{
                          fontSize: '0.76rem',
                          color: 'var(--text-secondary)',
                          marginTop: '2px',
                        }}
                      >
                        {item.category} • {item.preparation_time_mins} mins
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {activeRouteOrder && (
        <div style={{ marginTop: '24px' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 800, marginBottom: '12px' }}>
            Courier Path to Order #{activeRouteOrder.id}
          </h3>
          <RouteMapVisualizer routeData={routeData} height={360} />
        </div>
      )}

      {showAddModal && restaurant && (
        <div
          style={{
            position: 'fixed',
            inset: 0,
            background: 'rgba(0,0,0,0.7)',
            backdropFilter: 'blur(6px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1000,
            padding: '20px',
          }}
        >
          <div
            className="glass-panel"
            style={{
              width: '100%',
              maxWidth: '480px',
              padding: '24px',
              background: 'rgba(15, 23, 42, 0.95)',
            }}
          >
            <h3 style={{ fontWeight: 800, fontSize: '1.2rem', marginBottom: '16px' }}>
              Add Dish to Menu
            </h3>

            <form
              onSubmit={handleAddMenuItem}
              style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}
            >
              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  Dish Name
                </label>
                <input
                  type="text"
                  required
                  minLength={2}
                  placeholder="e.g. Saffron Risotto"
                  className="input-field"
                  value={newItemName}
                  onChange={(e) => setNewItemName(e.target.value)}
                />
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  Description
                </label>
                <textarea
                  rows={2}
                  placeholder="Ingredients and culinary style..."
                  className="input-field"
                  value={newItemDesc}
                  onChange={(e) => setNewItemDesc(e.target.value)}
                />
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Price ($)
                  </label>
                  <input
                    type="number"
                    min="0.01"
                    step="0.01"
                    required
                    className="input-field"
                    value={newItemPrice}
                    onChange={(e) => setNewItemPrice(e.target.value)}
                  />
                </div>

                <div>
                  <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    Prep Time (Mins)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="120"
                    required
                    className="input-field"
                    value={newItemPrepTime}
                    onChange={(e) =>
                      setNewItemPrepTime(Number.parseInt(e.target.value, 10) || 15)
                    }
                  />
                </div>
              </div>

              <div>
                <label style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  Category
                </label>
                <select
                  className="input-field"
                  value={newItemCategory}
                  onChange={(e) => setNewItemCategory(e.target.value)}
                >
                  <option value="Main Course">Main Course</option>
                  <option value="Pizza">Pizza</option>
                  <option value="Pasta">Pasta</option>
                  <option value="Biryani">Biryani</option>
                  <option value="Dessert">Dessert</option>
                  <option value="Beverage">Beverage</option>
                </select>
              </div>

              <div
                style={{
                  display: 'flex',
                  justifyContent: 'flex-end',
                  gap: '10px',
                  marginTop: '10px',
                }}
              >
                <button
                  type="button"
                  onClick={() => setShowAddModal(false)}
                  className="btn btn-outline"
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  Save Item
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
