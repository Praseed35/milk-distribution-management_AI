export interface RouteBase {
  route_code: string;
  route_name: string;
  description?: string | null;
}

export interface RouteCreate extends RouteBase {}

export interface RouteUpdate extends RouteBase {}

export interface RouteResponse extends RouteBase {
  id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
