import {
  AlgorithmBenchmarkComparison,
  AuthResponse,
  ConcurrencyBenchmarkResponse,
  DeliveryAgent,
  DeliveryAssignmentBrief,
  MenuItem,
  Order,
  OrderStatus,
  Restaurant,
  RouteResponse,
  User,
} from '../types';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

class ApiClient {
  private token: string | null = localStorage.getItem('token');

  setToken(token: string | null) {
    this.token = token;
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
  }

  getToken(): string | null {
    return this.token;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    if (!response.ok) {
      let errorMsg = `Error ${response.status}: ${response.statusText}`;
      try {
        const errorData = await response.json();
        errorMsg = errorData.detail || errorMsg;
      } catch {
        // use statusText
      }
      throw new Error(errorMsg);
    }

    return response.json();
  }

  // Auth
  async login(username_or_email: string, password: string): Promise<AuthResponse> {
    const data = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ username_or_email, password }),
    });
    this.setToken(data.access_token);
    return data;
  }

  async register(user: {
    email: string;
    username: string;
    password: string;
    full_name: string;
    role: string;
    phone?: string;
    address?: string;
    node_id?: string;
  }): Promise<User> {
    return this.request<User>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(user),
    });
  }

  async getMe(): Promise<User> {
    return this.request<User>('/auth/me');
  }

  // Restaurants
  async getRestaurants(): Promise<Restaurant[]> {
    return this.request<Restaurant[]>('/restaurants/');
  }

  async getRestaurant(id: number): Promise<Restaurant> {
    return this.request<Restaurant>(`/restaurants/${id}`);
  }

  async addMenuItem(
    restaurantId: number,
    item: {
      name: string;
      description?: string;
      price: number;
      category: string;
      is_available: boolean;
      preparation_time_mins: number;
    }
  ): Promise<MenuItem> {
    return this.request<MenuItem>(`/restaurants/${restaurantId}/items`, {
      method: 'POST',
      body: JSON.stringify(item),
    });
  }

  // Orders
  async createOrder(order: {
    restaurant_id: number;
    delivery_address: string;
    delivery_node: string;
    special_instructions?: string;
    items: { menu_item_id: number; quantity: number }[];
  }): Promise<Order> {
    return this.request<Order>('/orders/', {
      method: 'POST',
      body: JSON.stringify(order),
    });
  }

  async getOrders(): Promise<Order[]> {
    return this.request<Order[]>('/orders/');
  }

  async getOrder(orderId: number): Promise<Order> {
    return this.request<Order>(`/orders/${orderId}`);
  }

  async updateOrderStatus(orderId: number, status: OrderStatus): Promise<Order> {
    return this.request<Order>(`/orders/${orderId}/status`, {
      method: 'PATCH',
      body: JSON.stringify({ status }),
    });
  }

  async getOrderRoute(orderId: number): Promise<RouteResponse> {
    return this.request<RouteResponse>(`/orders/${orderId}/route`);
  }

  // Delivery
  async getDeliveryAgents(): Promise<DeliveryAgent[]> {
    return this.request<DeliveryAgent[]>('/deliveries/agents');
  }

  async getMyAgentProfile(): Promise<DeliveryAgent> {
    return this.request<DeliveryAgent>('/deliveries/agents/me');
  }

  async updateAgentStatus(status: { is_available?: boolean; current_node?: string }): Promise<DeliveryAgent> {
    return this.request<DeliveryAgent>('/deliveries/agents/me/status', {
      method: 'PATCH',
      body: JSON.stringify(status),
    });
  }

  async calculateRoute(start_node: string, end_node: string): Promise<RouteResponse> {
    return this.request<RouteResponse>(`/deliveries/route?start_node=${start_node}&end_node=${end_node}`);
  }

  // Algorithms
  async runDijkstra(start_node: string, end_node: string): Promise<any> {
    return this.request('/algorithms/dijkstra', {
      method: 'POST',
      body: JSON.stringify({ start_node, end_node }),
    });
  }

  async runDPSchedule(max_time_window: number, orders?: any[]): Promise<any> {
    return this.request('/algorithms/dp-schedule', {
      method: 'POST',
      body: JSON.stringify({ max_time_window, orders }),
    });
  }

  async runBacktracking(delivery_nodes: string[], start_node = 'Node_R1', max_total_distance_km = 35.0): Promise<any> {
    return this.request('/algorithms/backtracking-route', {
      method: 'POST',
      body: JSON.stringify({ delivery_nodes, start_node, max_total_distance_km }),
    });
  }

  async runBranchAndBound(locations: string[]): Promise<any> {
    return this.request('/algorithms/branch-and-bound', {
      method: 'POST',
      body: JSON.stringify({ locations }),
    });
  }

  async runDivideAndConquer(sample_size = 100): Promise<any> {
    return this.request('/algorithms/divide-and-conquer', {
      method: 'POST',
      body: JSON.stringify({ sample_size }),
    });
  }

  async benchmarkAllAlgorithms(): Promise<AlgorithmBenchmarkComparison> {
    return this.request<AlgorithmBenchmarkComparison>('/algorithms/benchmark-all');
  }

  // Concurrency
  async benchmarkAsyncio(task_count = 10): Promise<ConcurrencyBenchmarkResponse> {
    return this.request<ConcurrencyBenchmarkResponse>(`/concurrency/asyncio?task_count=${task_count}`);
  }

  async benchmarkThreading(task_count = 8, max_workers = 4): Promise<ConcurrencyBenchmarkResponse> {
    return this.request<ConcurrencyBenchmarkResponse>(
      `/concurrency/threading?task_count=${task_count}&max_workers=${max_workers}`
    );
  }

  async benchmarkMultiprocessing(task_count = 4, max_workers = 4): Promise<ConcurrencyBenchmarkResponse> {
    return this.request<ConcurrencyBenchmarkResponse>(
      `/concurrency/multiprocessing?task_count=${task_count}&max_workers=${max_workers}`
    );
  }

  // Admin
  async getAdminSummary(): Promise<any> {
    return this.request('/admin/summary');
  }

  async resetSeedData(): Promise<any> {
    return this.request('/admin/seed-reset', { method: 'POST' });
  }
}

export const api = new ApiClient();
