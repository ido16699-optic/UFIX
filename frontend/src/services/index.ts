import api from './api';
import {
  LoginCredentials,
  RegisterData,
  AuthToken,
  User,
  CustomerProfile,
  HandymanProfile,
  JobRequest,
  CreateJobRequest,
  Offer,
  CreateOffer,
  Order,
  PaymentIntent,
  ChatThread,
  ChatMessage,
  Review,
  CreateReview,
  PaginatedResponse,
  ServiceCategory,
  JobRequestStatus,
  OfferStatus,
  OrderStatus,
} from '../types';

// ============ Auth Services ============

export const authService = {
  async register(data: RegisterData): Promise<User> {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  async login(credentials: LoginCredentials): Promise<AuthToken> {
    const response = await api.post<AuthToken>('/auth/login', credentials);
    return response.data;
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// ============ Profile Services ============

export const profileService = {
  // Customer
  async getCustomerProfile(): Promise<CustomerProfile> {
    const response = await api.get<CustomerProfile>('/profiles/customer/me');
    return response.data;
  },

  async updateCustomerProfile(data: Partial<CustomerProfile>): Promise<CustomerProfile> {
    const response = await api.patch<CustomerProfile>('/profiles/customer/me', data);
    return response.data;
  },

  // Handyman
  async getHandymanProfile(): Promise<HandymanProfile> {
    const response = await api.get<HandymanProfile>('/profiles/handyman/me');
    return response.data;
  },

  async updateHandymanProfile(data: Partial<HandymanProfile>): Promise<HandymanProfile> {
    const response = await api.patch<HandymanProfile>('/profiles/handyman/me', data);
    return response.data;
  },

  async updateLocation(latitude: number, longitude: number): Promise<HandymanProfile> {
    const response = await api.post<HandymanProfile>('/profiles/handyman/me/location', {
      latitude,
      longitude,
    });
    return response.data;
  },

  async uploadVerification(file: File, fileType: string): Promise<void> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('file_type', fileType);
    await api.post('/profiles/handyman/me/verification', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  async getPublicHandymanProfile(handymanId: number): Promise<HandymanProfile> {
    const response = await api.get<HandymanProfile>(`/profiles/handyman/${handymanId}`);
    return response.data;
  },
};

// ============ Job Services ============

export const jobService = {
  async createJobRequest(data: CreateJobRequest): Promise<JobRequest> {
    const response = await api.post<JobRequest>('/jobs', data);
    return response.data;
  },

  async getMyJobRequests(
    page = 1,
    pageSize = 20,
    status?: JobRequestStatus
  ): Promise<PaginatedResponse<JobRequest>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (status) params.append('status_filter', status);

    const response = await api.get<PaginatedResponse<JobRequest>>(`/jobs/my-requests?${params}`);
    return response.data;
  },

  async getJobRequest(jobId: number): Promise<JobRequest> {
    const response = await api.get<JobRequest>(`/jobs/${jobId}`);
    return response.data;
  },

  async getAvailableJobs(
    page = 1,
    pageSize = 20,
    category?: ServiceCategory
  ): Promise<PaginatedResponse<JobRequest>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (category) params.append('category', category);

    const response = await api.get<PaginatedResponse<JobRequest>>(`/jobs/available?${params}`);
    return response.data;
  },
};

// ============ Offer Services ============

export const offerService = {
  async createOffer(data: CreateOffer): Promise<Offer> {
    const response = await api.post<Offer>('/offers', data);
    return response.data;
  },

  async getOffersForJob(jobId: number): Promise<{ items: Offer[]; total: number }> {
    const response = await api.get<{ items: Offer[]; total: number }>(`/offers/job/${jobId}`);
    return response.data;
  },

  async acceptOffer(offerId: number): Promise<Offer> {
    const response = await api.post<Offer>(`/offers/${offerId}/accept`);
    return response.data;
  },

  async rejectOffer(offerId: number): Promise<Offer> {
    const response = await api.post<Offer>(`/offers/${offerId}/reject`);
    return response.data;
  },

  async getMyOffers(status?: OfferStatus): Promise<{ items: Offer[]; total: number }> {
    const params = status ? `?status_filter=${status}` : '';
    const response = await api.get<{ items: Offer[]; total: number }>(`/offers/my-offers${params}`);
    return response.data;
  },
};

// ============ Order Services ============

export const orderService = {
  async getMyOrders(
    page = 1,
    pageSize = 20,
    status?: OrderStatus
  ): Promise<PaginatedResponse<Order>> {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
    });
    if (status) params.append('status_filter', status);

    const response = await api.get<PaginatedResponse<Order>>(`/orders?${params}`);
    return response.data;
  },

  async getOrder(orderId: number): Promise<Order> {
    const response = await api.get<Order>(`/orders/${orderId}`);
    return response.data;
  },

  async updateOrderStatus(orderId: number, status: OrderStatus): Promise<Order> {
    const response = await api.patch<Order>(`/orders/${orderId}/status`, { status });
    return response.data;
  },

  async createPaymentIntent(orderId: number): Promise<PaymentIntent> {
    const response = await api.post<PaymentIntent>('/payments/create-intent', { order_id: orderId });
    return response.data;
  },

  async confirmPayment(paymentIntentId: string): Promise<void> {
    await api.post('/payments/confirm', { payment_intent_id: paymentIntentId });
  },
};

// ============ Chat Services ============

export const chatService = {
  async getMyThreads(): Promise<{ items: ChatThread[]; total: number }> {
    const response = await api.get<{ items: ChatThread[]; total: number }>('/chat/threads');
    return response.data;
  },

  async getThread(threadId: number): Promise<ChatThread> {
    const response = await api.get<ChatThread>(`/chat/threads/${threadId}`);
    return response.data;
  },

  async sendMessage(threadId: number, content: string): Promise<ChatMessage> {
    const response = await api.post<ChatMessage>(`/chat/threads/${threadId}/messages`, { content });
    return response.data;
  },
};

// ============ Review Services ============

export const reviewService = {
  async createReview(data: CreateReview): Promise<Review> {
    const response = await api.post<Review>('/reviews', data);
    return response.data;
  },

  async getUserReviews(userId: number): Promise<{ items: Review[]; total: number; average_rating: number }> {
    const response = await api.get<{ items: Review[]; total: number; average_rating: number }>(
      `/reviews/user/${userId}`
    );
    return response.data;
  },
};
