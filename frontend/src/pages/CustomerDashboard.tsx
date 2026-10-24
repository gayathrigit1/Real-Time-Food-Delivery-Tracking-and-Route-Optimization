import React, { useEffect, useState } from 'react';
import {
  AlertCircle,
  CheckCircle2,
  ChevronRight,
  Clock,
  Flame,
  Info,
  MapPin,
  Minus,
  Plus,
  RefreshCw,
  ShoppingBag,
  Star,
  Trash2,
  Truck,
  Utensils,
  Zap,
} from 'lucide-react';
import { api } from '../api/client';
import { RouteMapVisualizer } from '../components/RouteMapVisualizer';
import { useAuth } from '../context/AuthContext';
import { MenuItem, Order, Restaurant, RouteResponse } from '../types';

export const CustomerDashboard: React.FC = () => {
  const { user } = useAuth();
  const [restaurants, setRestaurants] = useState<Restaurant[]>([]);
  const [selectedRestaurant, setSelectedRestaurant] = useState<Restaurant | null>(null);
  const [cart, setCart] = useState<{ [itemId: number]: { item: MenuItem; quantity: number } }>({});
  const [orders, setOrders] = useState<Order[]>([]);
  const [activeRouteOrder, setActiveRouteOrder] = useState<Order | null>(null);
  const [routeData, setRouteData] = useState<RouteResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [specialInstructions, setSpecialInstructions] = useState('');
  const [deliveryAddress, setDeliveryAddress] = useState(user?.address || 'Apartment 101, Downtown Tower');
  const [deliveryNode, setDeliveryNode] = useState(user?.node_id || 'Node_C1');
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      const [restData, orderData] = await Promise.all([
        api.getRestaurants(),
        user ? api.getOrders() : Promise.resolve([]),
      ]);
      setRestaurants(restData);
      if (restData.length > 0 && !selectedRestaurant) {
        setSelectedRestaurant(restData[0]);
      }
      setOrders(orderData);
    } catch (err: any) {
      console.error(err);
      setMessage({ type: 'error', text: err.message || 'Failed to fetch restaurants' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInitialData();
  }, [user]);

  const addToCart = (item: MenuItem) => {
    // If selecting item from a different restaurant, clear cart
    if (selectedRestaurant && Object.keys(cart).length > 0) {
      const existingRestId = Object.values(cart)[0].item.restaurant_id;
      if (existingRestId !== selectedRestaurant.id) {
        if (!window.confirm('Adding items from a different restaurant will clear your current cart. Continue?')) {
          return;
        }
        setCart({ [item.id]: { item, quantity: 1 } });
        return;
      }
    }

    setCart((prev) => {
      const current = prev[item.id]?.quantity || 0;
      return {
        ...prev,
        [item.id]: { item, quantity: current + 1 },
      };
    });
  };

  const updateQuantity = (itemId: number, delta: number) => {
    setCart((prev) => {
      const current = prev[itemId]?.quantity || 0;
      const next = current + delta;
      if (next <= 0) {
        const copy = { ...prev };
        delete copy[itemId];
        return copy;
      }
      return {
        ...prev,
        [itemId]: { ...prev[itemId], quantity: next },
      };
    });
  };

  const clearCart = () => setCart({});

  // Subtotal & Estimated Total calculation
  const subtotal = Object.values(cart).reduce((sum, item) => sum + item.item.price * item.quantity, 0);
  const tax = subtotal * 0.05;
  const deliveryFee = subtotal > 0 ? 5.0 : 0;
  const grandTotal = subtotal + tax + deliveryFee;

  const handlePlaceOrder = async () => {
    if (!selectedRestaurant) return;
    if (Object.keys(cart).length === 0) {
      setMessage({ type: 'error', text: 'Please add items to your cart.' });
      return;
    }

    try {
      setSubmitting(true);
      setMessage(null);

      const itemsPayload = Object.values(cart).map((ci) => ({
        menu_item_id: ci.item.id,
        quantity: ci.quantity,
      }));

      const newOrder = await api.createOrder({
        restaurant_id: selectedRestaurant.id,
        delivery_address: deliveryAddress,
        delivery_node: deliveryNode,
        special_instructions: specialInstructions,
        items: itemsPayload,
      });

      setMessage({ type: 'success', text: `Order #${newOrder.id} placed successfully! Backend verified prices.` });
      clearCart();
      const updatedOrders = await api.getOrders();
      setOrders(updatedOrders);
      viewOrderRoute(newOrder);
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to create order.' });
    } finally {
      setSubmitting(false);
    }
  };

  const viewOrderRoute = async (order: Order) => {
    setActiveRouteOrder(order);
    try {
      const route = await api.getOrderRoute(order.id);
      setRouteData(route);
    } catch (err: any) {
      console.error(err);
      setRouteData(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'PENDING':
        return <span className="badge badge-blue">Pending</span>;
      case 'PREPARING':
        return <span className="badge badge-purple">Preparing Kitchen</span>;
      case 'READY_FOR_PICKUP':
        return <span className="badge badge-amber">Ready for Pickup</span>;
      case 'DELIVERING':
        return <span className="badge badge-emerald">Out for Delivery</span>;
      case 'DELIVERED':
        return <span className="badge badge-emerald">Delivered</span>;
      case 'CANCELLED':
        return <span className="badge badge-rose">Cancelled</span>;
      default:
        return <span className="badge">{status}</span>;
    }
  };

  return (
    <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '24px' }}>
      
      {/* Notifications */}
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

      {/* Hero Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 800, letterSpacing: '-0.02em', background: 'linear-gradient(90deg, #60a5fa, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            Customer Gourmet Portal
          </h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '4px' }}>
            Select restaurants, customize meals, place backend-validated orders, and observe dynamic Dijkstra courier routes.
          </p>
        </div>

        <button onClick={fetchInitialData} className="btn btn-outline btn-sm">
          <RefreshCw size={14} /> Refresh Catalog
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '24px' }}>
        
        {/* Left Column: Restaurants & Menu Items */}
        <div style={{ gridColumn: 'span 2' }}>
          
          {/* Restaurant Selector Pills */}
          <div style={{ marginBottom: '20px' }}>
            <div style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: '10px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Available Restaurants
            </div>
            <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
              {restaurants.map((rest) => {
                const isSelected = selectedRestaurant?.id === rest.id;
                return (
                  <div
                    key={rest.id}
                    onClick={() => setSelectedRestaurant(rest)}
                    className="glass-panel glass-panel-interactive"
                    style={{
                      padding: '12px 18px',
                      cursor: 'pointer',
                      border: isSelected ? '1px solid #3b82f6' : '1px solid var(--border-color)',
                      background: isSelected ? 'rgba(59, 130, 246, 0.12)' : 'var(--bg-card)',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '12px',
                    }}
                  >
                    <div style={{ width: '36px', height: '36px', borderRadius: '10px', background: 'linear-gradient(135deg, #f59e0b, #d97706)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <Utensils size={18} color="#fff" />
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: '0.95rem' }}>{rest.name}</div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.76rem', color: 'var(--text-secondary)' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '3px', color: '#fbbf24' }}>
                          <Star size={12} fill="#fbbf24" /> {rest.rating}
                        </span>
                        <span>•</span>
                        <span>{rest.cuisine_type}</span>
                        <span>•</span>
                        <span className="badge badge-blue" style={{ fontSize: '0.65rem' }}>{rest.node_id}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Menu Catalog */}
          {selectedRestaurant && (
            <div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
                <div>
                  <h3 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{selectedRestaurant.name} Catalog</h3>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)' }}>{selectedRestaurant.description}</p>
                </div>
                <span className="badge badge-emerald">Verified DB Pricing</span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: '16px' }}>
                {selectedRestaurant.menu_items.map((item) => (
                  <div key={item.id} className="glass-panel" style={{ padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                    <div>
                      {item.image_url && (
                        <div style={{ width: '100%', height: '120px', borderRadius: '8px', overflow: 'hidden', marginBottom: '10px' }}>
                          <img src={item.image_url} alt={item.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                        </div>
                      )}
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                        <h4 style={{ fontWeight: 700, fontSize: '0.98rem' }}>{item.name}</h4>
                        <span style={{ fontWeight: 800, color: '#38bdf8', fontSize: '1rem' }}>${item.price.toFixed(2)}</span>
                      </div>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '4px', minHeight: '38px' }}>
                        {item.description || 'Artisanal recipe prepared with organic ingredients.'}
                      </p>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px', fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                        <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                          <Clock size={12} /> {item.preparation_time_mins} mins prep
                        </span>
                        <span>•</span>
                        <span className="badge badge-purple" style={{ fontSize: '0.65rem' }}>{item.category}</span>
                      </div>
                    </div>

                    <div style={{ marginTop: '14px' }}>
                      <button onClick={() => addToCart(item)} className="btn btn-sm btn-primary" style={{ width: '100%' }}>
                        <Plus size={14} /> Add to Cart
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

        </div>

        {/* Right Column: Checkout Cart & Active Orders */}
        <div>
          
          {/* Shopping Cart */}
          <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <ShoppingBag size={18} color="#38bdf8" />
                <h3 style={{ fontWeight: 700, fontSize: '1.05rem' }}>Order Basket</h3>
              </div>
              {Object.keys(cart).length > 0 && (
                <button onClick={clearCart} className="btn btn-sm btn-outline" style={{ padding: '4px 8px', color: '#f43f5e' }}>
                  <Trash2 size={13} />
                </button>
              )}
            </div>

            {Object.keys(cart).length === 0 ? (
              <div style={{ padding: '24px 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                Your basket is empty. Select culinary delicacies from the menu!
              </div>
            ) : (
              <div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
                  {Object.values(cart).map(({ item, quantity }) => (
                    <div key={item.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '8px', borderBottom: '1px solid var(--border-color)' }}>
                      <div>
                        <div style={{ fontWeight: 600, fontSize: '0.88rem' }}>{item.name}</div>
                        <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                          ${item.price.toFixed(2)} × {quantity} = ${(item.price * quantity).toFixed(2)}
                        </div>
                      </div>

                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <button onClick={() => updateQuantity(item.id, -1)} className="btn btn-sm btn-outline" style={{ padding: '2px 6px' }}>
                          <Minus size={12} />
                        </button>
                        <span style={{ fontWeight: 700, fontSize: '0.88rem', minWidth: '16px', textAlign: 'center' }}>{quantity}</span>
                        <button onClick={() => updateQuantity(item.id, 1)} className="btn btn-sm btn-outline" style={{ padding: '2px 6px' }}>
                          <Plus size={12} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Delivery Form inputs */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '16px' }}>
                  <div>
                    <label style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Delivery Street Address</label>
                    <input
                      type="text"
                      className="input-field"
                      value={deliveryAddress}
                      onChange={(e) => setDeliveryAddress(e.target.value)}
                    />
                  </div>

                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                    <div>
                      <label style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Dropoff Node</label>
                      <select
                        className="input-field"
                        value={deliveryNode}
                        onChange={(e) => setDeliveryNode(e.target.value)}
                      >
                        <option value="Node_C1">Node_C1 (Downtown Apt 101)</option>
                        <option value="Node_C2">Node_C2 (Green Park Villa 202)</option>
                        <option value="Node_C3">Node_C3 (Tech Park 303)</option>
                        <option value="Node_C4">Node_C4 (Residency 404)</option>
                      </select>
                    </div>

                    <div>
                      <label style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Special Note</label>
                      <input
                        type="text"
                        placeholder="Leave at lobby..."
                        className="input-field"
                        value={specialInstructions}
                        onChange={(e) => setSpecialInstructions(e.target.value)}
                      />
                    </div>
                  </div>
                </div>

                {/* Price Breakdown */}
                <div style={{ background: 'rgba(15, 23, 42, 0.6)', padding: '12px', borderRadius: '8px', fontSize: '0.84rem', display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '16px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                    <span>Subtotal:</span>
                    <span>${subtotal.toFixed(2)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                    <span>Estimated Tax (5%):</span>
                    <span>${tax.toFixed(2)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
                    <span>Delivery Fee:</span>
                    <span>${deliveryFee.toFixed(2)}</span>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 800, fontSize: '0.98rem', paddingTop: '6px', borderTop: '1px solid var(--border-color)', color: '#38bdf8' }}>
                    <span>Grand Total:</span>
                    <span>${grandTotal.toFixed(2)}</span>
                  </div>
                </div>

                <button
                  onClick={handlePlaceOrder}
                  disabled={submitting}
                  className="btn btn-primary"
                  style={{ width: '100%', padding: '12px' }}
                >
                  {submitting ? 'Verifying & Placing...' : `Confirm Order • $${grandTotal.toFixed(2)}`}
                </button>
              </div>
            )}
          </div>

          {/* Active Order History & Live Tracking */}
          <div className="glass-panel" style={{ padding: '20px' }}>
            <h3 style={{ fontWeight: 700, fontSize: '1.05rem', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Truck size={18} color="#10b981" /> Order History & Live Track
            </h3>

            {orders.length === 0 ? (
              <div style={{ color: 'var(--text-muted)', fontSize: '0.84rem', textAlign: 'center', padding: '12px 0' }}>
                No past orders found. Place your first order!
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '420px', overflowY: 'auto' }}>
                {orders.map((ord) => (
                  <div
                    key={ord.id}
                    className="glass-panel"
                    style={{
                      padding: '12px',
                      cursor: 'pointer',
                      border: activeRouteOrder?.id === ord.id ? '1px solid #06b6d4' : '1px solid var(--border-color)',
                    }}
                    onClick={() => viewOrderRoute(ord)}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '6px' }}>
                      <div style={{ fontWeight: 700, fontSize: '0.9rem' }}>Order #{ord.id}</div>
                      {getStatusBadge(ord.status)}
                    </div>

                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                      Total: <strong>${ord.total_amount.toFixed(2)}</strong> • {ord.items.length} items
                    </div>

                    <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                      To: {ord.delivery_node} ({ord.delivery_address})
                    </div>

                    {ord.delivery_assignment && (
                      <div style={{ marginTop: '6px', fontSize: '0.74rem', color: '#34d399', display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <Zap size={12} /> Courier assigned via {ord.delivery_assignment.algorithm_used} (~{ord.delivery_assignment.total_distance} km)
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

      </div>

      {/* Live Route Visualizer Section */}
      {activeRouteOrder && (
        <div style={{ marginTop: '28px' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px' }}>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 800 }}>Live Dijkstra Route Telemetry for Order #{activeRouteOrder.id}</h2>
            {getStatusBadge(activeRouteOrder.status)}
          </div>
          <RouteMapVisualizer routeData={routeData} height={380} />
        </div>
      )}

    </div>
  );
};
