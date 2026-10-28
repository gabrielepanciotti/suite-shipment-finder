export interface Party {
  postal_code: string;
  city: string;
  country: string;
}

export interface Parcel {
  length_cm: number;
  width_cm: number;
  height_cm: number;
  weight_kg: number;
  count: number;
}

export interface QuoteRequest {
  sender: Party;
  recipient: Party;
  parcel: Parcel;
}

export interface Offer {
  source: string;
  carrier: string;
  service: string;
  price_eur: number;
  delivery_days_min: number | null;
  delivery_days_max: number | null;
  url: string;
}

export type SourceStatus =
  "ok" | "empty" | "blocked" | "changed" | "timeout" | "error";

export interface SourceOutcome {
  source: string;
  status: SourceStatus;
  detail: string;
  offers: Offer[];
  elapsed_s: number;
}

export interface Comparison {
  request: QuoteRequest;
  offers: Offer[];
  outcomes: SourceOutcome[];
  best: Offer | null;
  degraded: string[];
}

export interface SavedOffer {
  id: string;
  offer: Offer;
  savedAt: string;
}
