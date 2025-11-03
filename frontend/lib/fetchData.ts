export interface PennyDataResponse {
  totalStocks: number;
}

export async function fetchPennyData(): Promise<PennyDataResponse> {
  const res = await fetch("http://localhost:8000/api/pennystocks");
  if (!res.ok) throw new Error("Failed to fetch data");
  return res.json();
}
