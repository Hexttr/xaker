export interface Service {
  id: string;
  name: string;
  url: string;
  createdAt: string;
  updatedAt: string;
}

export interface CreateServiceRequest {
  name: string;
  url: string;
}

export interface UpdateServiceRequest {
  name?: string;
  url?: string;
}

