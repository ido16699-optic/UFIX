// API Types for UFIX Platform

// ============ User Types ============

export enum UserRole {
  CUSTOMER = 'customer',
  HANDYMAN = 'handyman',
  ADMIN = 'admin',
}

export interface User {
  id: number;
  email: string;
  name: string;
  phone?: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  name: string;
  phone?: string;
  role: UserRole;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

// ============ Profile Types ============

export interface Address {
  label: string;
  address: string;
  latitude: number;
  longitude: number;
}

export interface CustomerProfile {
  id: number;
  user_id: number;
  default_address?: string;
  default_latitude?: number;
  default_longitude?: number;
  saved_addresses: Address[];
  created_at: string;
  user?: User;
}

export enum ServiceCategory {
  PLUMBING = 'plumbing',
  ELECTRICAL = 'electrical',
  PAINTING = 'painting',
  FURNITURE_ASSEMBLY = 'furniture_assembly',
  GENERAL_HANDYMAN = 'general_handyman',
}

export enum VerificationStatus {
  PENDING = 'pending',
  APPROVED = 'approved',
  REJECTED = 'rejected',
}

export interface HandymanProfile {
  id: number;
  user_id: number;
  categories: ServiceCategory[];
  bio?: string;
  service_radius_km: number;
  current_latitude?: number;
  current_longitude?: number;
  verification_status: VerificationStatus;
  average_rating: number;
  total_reviews: number;
  total_completed_jobs: number;
  created_at: string;
  user?: User;
}

export interface HandymanPublicProfile {
  id: number;
  user_id: number;
  name: string;
  categories: ServiceCategory[];
  bio?: string;
  verification_status: VerificationStatus;
  average_rating: number;
  total_reviews: number;
  total_completed_jobs: number;
}

// ============ Job Types ============

export enum RequestType {
  ASAP = 'asap',
  SCHEDULED = 'scheduled',
}

export enum JobRequestStatus {
  OPEN = 'open',
  MATCHED = 'matched',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

export interface JobRequest {
  id: number;
  customer_id: number;
  category: ServiceCategory;
  title: string;
  description: string;
  address: string;
  latitude: number;
  longitude: number;
  request_type: RequestType;
  scheduled_date?: string;
  scheduled_time_window?: string;
  status: JobRequestStatus;
  images?: string[];
  created_at: string;
  updated_at: string;
  offer_count?: number;
}

export interface CreateJobRequest {
  category: ServiceCategory;
  title: string;
  description: string;
  address: string;
  latitude: number;
  longitude: number;
  request_type: RequestType;
  scheduled_date?: string;
  scheduled_time_window?: string;
  images?: string[];
}

// ============ Offer Types ============

export enum OfferStatus {
  PENDING = 'pending',
  ACCEPTED = 'accepted',
  REJECTED = 'rejected',
  EXPIRED = 'expired',
  WITHDRAWN = 'withdrawn',
}

export interface Offer {
  id: number;
  job_request_id: number;
  handyman_id: number;
  price: number;
  message?: string;
  estimated_arrival_minutes?: number;
  available_date?: string;
  available_time_window?: string;
  status: OfferStatus;
  created_at: string;
  handyman?: HandymanPublicProfile;
}

export interface CreateOffer {
  job_request_id: number;
  price: number;
  message?: string;
  estimated_arrival_minutes?: number;
  available_date?: string;
  available_time_window?: string;
}

// ============ Order Types ============

export enum OrderStatus {
  PENDING_PAYMENT = 'pending_payment',
  PAYMENT_AUTHORIZED = 'payment_authorized',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
  DISPUTED = 'disputed',
}

export interface Order {
  id: number;
  job_request_id: number;
  offer_id: number;
  status: OrderStatus;
  started_at?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  job_request?: JobRequest;
  offer?: Offer;
}

export enum PaymentStatus {
  PENDING = 'pending',
  AUTHORIZED = 'authorized',
  COMPLETED = 'completed',
  PAYOUT_READY = 'payout_ready',
  PAYOUT_COMPLETED = 'payout_completed',
  REFUNDED = 'refunded',
  FAILED = 'failed',
}

export interface Payment {
  id: number;
  order_id: number;
  provider: string;
  amount: number;
  commission: number;
  handyman_payout: number;
  status: PaymentStatus;
  created_at: string;
  updated_at: string;
}

export interface PaymentIntent {
  client_secret: string;
  payment_intent_id: string;
  amount: number;
  currency: string;
}

// ============ Chat Types ============

export interface ChatMessage {
  id: number;
  thread_id: number;
  sender_id: number;
  content: string;
  is_read: boolean;
  read_at?: string;
  created_at: string;
}

export interface ChatThread {
  id: number;
  job_request_id: number;
  customer_user_id: number;
  handyman_user_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  last_message?: ChatMessage;
  unread_count?: number;
  messages?: ChatMessage[];
}

// ============ Review Types ============

export interface Review {
  id: number;
  order_id: number;
  from_user_id: number;
  to_user_id: number;
  stars: number;
  text?: string;
  created_at: string;
  from_user_name?: string;
  to_user_name?: string;
}

export interface CreateReview {
  order_id: number;
  to_user_id: number;
  stars: number;
  text?: string;
}

export interface ReviewSummary {
  average_rating: number;
  total_reviews: number;
  rating_distribution: Record<number, number>;
}

// ============ Pagination Types ============

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}
