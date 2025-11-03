// frontend/lib/fetchPennyData.ts

export interface PennySummary {
  reddit_ticker: string;
  current_price: number | null;
  change_pct: number | null;
}

export interface PennyTrends {
  [ticker: string]: { last_updated: string; current_price: number | null }[];
}

export interface PennySummaryResponse {
  totalStocks: number;
  newStocksToday: number;
  topGainers: PennySummary[];
  trends: PennyTrends;
}

export interface PennyDetailsRow {
  row_id: number;
  reddit_ticker: string;
  yfinance_symbol: string;
  long_name: string;
  short_name: string;
  sector: string;
  industry: string;
  market_cap: number | null;
  employees: number | null;
  founded: number | null;
  country: string;
  currency: string;
  current_price: number | null;
  previous_close: number | null;
  open: number | null;
  day_high: number | null;
  day_low: number | null;
  volume: number | null;
  website: string;
  about: string;
  score: number | null;
  num_comments: number | null;
  content?: string;
  created_utc: string;
  error?: string;
  last_updated: string;
  summarized_content?: string;
  summarized_comments?: string;
  verdict?: string;
}

export interface PennyDetailsResponse {
  totalStocks: number;
  data: PennyDetailsRow[];
}

// ---------------- Fetch summary ----------------
export async function fetchPennySummary(): Promise<PennySummaryResponse> {
  const res = await fetch("http://localhost:8000/api/pennystocks/summary");
  if (!res.ok) throw new Error("Failed to fetch summary data");
  return res.json();
}

// ---------------- Fetch details ----------------
export async function fetchPennyDetails(
  limit?: number,
  include_comments: boolean = true
): Promise<PennyDetailsResponse> {
  const url = new URL("http://localhost:8000/api/pennystocks/details");
  if (limit) url.searchParams.append("limit", limit.toString());
  url.searchParams.append("include_comments", include_comments.toString());

  const res = await fetch(url.toString());
  if (!res.ok) throw new Error("Failed to fetch details data");
  return res.json();
}
