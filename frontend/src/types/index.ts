export type UserRole = 'CUSTOMER' | 'RESTAURANT' | 'DELIVERY_AGENT' | 'ADMIN';

export type OrderStatus =
  | 'PENDING'
  | 'PREPARING'
  | 'READY_FOR_PICKUP'
  | 'DELIVERING'
  | 'DELIVERED'
  | 'CANCELLED';

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  role: UserRole;
  phone?: string;
  address?: string;
  node_id: string;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface MenuItem {
  id: number;
  restaurant_id: number;
  name: string;
  description?: string;
  price: number;
  category: string;
  is_available: boolean;
  preparation_time_mins: number;
  image_url?: string;
  created_at: string;
  updated_at: string;
}

export interface Restaurant {
  id: number;
  name: string;
  description?: string;
  cuisine_type: string;
  address: string;
  node_id: string;
  latitude: number;
  longitude: number;
  rating: number;
  is_active: boolean;
  owner_id: number;
  created_at: string;
  updated_at: string;
  menu_items: MenuItem[];
}

export interface OrderItem {
  id: number;
  menu_item_id: number;
  item_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

export interface DeliveryAssignmentBrief {
  id: number;
  agent_id: number;
  algorithm_used: string;
  assignment_score: number;
  route_path?: string[];
  total_distance: number;
  estimated_time_mins: number;
  assigned_at: string;
  picked_up_at?: string;
  delivered_at?: string;
}

export interface Order {
  id: number;
  customer_id: number;
  restaurant_id: number;
  status: OrderStatus;
  total_amount: number;
  delivery_fee: number;
  tax_amount: number;
  special_instructions?: string;
  delivery_address: string;
  delivery_node: string;
  created_at: string;
  updated_at: string;
  items: OrderItem[];
  delivery_assignment?: DeliveryAssignmentBrief;
}

export interface DeliveryAgent {
  id: number;
  user_id: number;
  is_available: boolean;
  current_node: string;
  vehicle_type: string;
  rating: number;
  current_workload: number;
  max_capacity: number;
  total_deliveries: number;
  created_at: string;
  updated_at: string;
  user?: User;
}

export interface RouteStep {
  step_index: number;
  node_id: string;
  label: string;
  type: string;
  lat: number;
  lon: number;
}

export interface GraphNode {
  id: string;
  label: string;
  node_type: string;
  latitude: number;
  longitude: number;
}

export interface GraphEdge {
  u: string;
  v: string;
  w: number;
}

export interface RouteResponse {
  order_id: number;
  source_node: string;
  destination_node: string;
  agent_node?: string;
  path: string[];
  distance_km: number;
  estimated_time_mins: number;
  steps: RouteStep[];
  graph_visual: {
    nodes: GraphNode[];
    edges: GraphEdge[];
  };
}

export interface AlgorithmBenchmarkItem {
  algorithm: string;
  category: string;
  input_size: string;
  time_complexity: string;
  space_complexity: string;
  execution_time_ms: number;
  result_summary: string;
}

export interface AlgorithmBenchmarkComparison {
  algorithms: AlgorithmBenchmarkItem[];
  system_specs: {
    python_version: string;
    os: string;
    processor: string;
  };
  timestamp: string;
}

export interface ConcurrencyTaskResult {
  task_id: number;
  task_name: string;
  result: any;
  duration_ms: number;
  thread_or_process_id: string;
}

export interface ConcurrencyBenchmarkResponse {
  mechanism: string;
  workload_type: string;
  task_count: number;
  total_elapsed_time_ms: number;
  sequential_baseline_ms: number;
  speedup_ratio: number;
  detailed_tasks: ConcurrencyTaskResult[];
  explanation: string;
  gil_impact_analysis: string;
}
