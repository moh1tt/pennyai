"use client";
import { useEffect, useState } from "react";
import {
  fetchPennySummary,
  fetchPennyDetails,
  PennySummaryResponse,
  PennyDetailsRow,
} from "../lib/fetchData";

export default function DashboardPage() {
  const [summary, setSummary] = useState<PennySummaryResponse | null>(null);
  const [details, setDetails] = useState<PennyDetailsRow[]>([]);
  const [page, setPage] = useState(1);
  const [selectedTicker, setSelectedTicker] = useState<PennyDetailsRow | null>(null);

  const pageSize = 15;

  useEffect(() => {
    const loadData = async () => {
      try {
        const summaryData = await fetchPennySummary();
        setSummary(summaryData);

        const detailsData = await fetchPennyDetails(100, false); // fetch enough for pagination
        const offset = (page - 1) * pageSize;
        setDetails(detailsData.data.slice(offset, offset + pageSize));
      } catch (err) {
        console.error(err);
      }
    };
    loadData();
  }, [page]);

  const handleTickerClick = (ticker: string) => {
    const tickerData = details.find((d) => d.reddit_ticker === ticker);
    if (tickerData) setSelectedTicker(tickerData);
  };

  if (!summary) return <div className="flex justify-center items-center h-screen">Loading...</div>;

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 via-white to-gray-100 p-8 font-sans">
      {/* Header and Summary Cards */}
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Penny Stocks Dashboard</h1>
        <p className="text-gray-600">Real-time insights and trends on trending penny stocks</p>
      </header>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white shadow-lg rounded-xl p-6">
          <h2 className="text-gray-500 font-semibold">Total Stocks</h2>
          <p className="text-3xl font-bold text-gray-900">{summary.totalStocks}</p>
        </div>
        <div className="bg-white shadow-lg rounded-xl p-6">
          <h2 className="text-gray-500 font-semibold">New Stocks Today</h2>
          <p className="text-3xl font-bold text-gray-900">{summary.newStocksToday}</p>
        </div>
        <div className="bg-white shadow-lg rounded-xl p-6">
          <h2 className="text-gray-500 font-semibold">Top Gainer</h2>
          <p className="text-2xl font-bold text-green-600">
            {summary.topGainers[0]?.reddit_ticker} ({summary.topGainers[0]?.change_pct?.toFixed(2)}%)
          </p>
        </div>
        <div className="bg-white shadow-lg rounded-xl p-6">
          <h2 className="text-gray-500 font-semibold">Tracked Trends</h2>
          <p className="text-3xl font-bold text-gray-900">{Object.keys(summary.trends).length}</p>
        </div>
      </div>

      {/* Details Table */}
      <div className="bg-white shadow-lg rounded-xl p-6 overflow-x-auto">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Stock Details</h2>
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Ticker</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Name</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Price</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Previous Close</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Market Cap</th>
              <th className="px-4 py-2 text-left text-sm font-medium text-gray-500">Sector</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {details.map((stock) => (
              <tr
                key={stock.row_id}
                className="cursor-pointer hover:bg-gray-100"
                onClick={() => handleTickerClick(stock.reddit_ticker)}
              >
                <td className="px-4 py-2 text-gray-900 font-medium">{stock.reddit_ticker}</td>
                <td className="px-4 py-2 text-gray-700">{stock.long_name || stock.short_name}</td>
                <td className="px-4 py-2 text-gray-700">{stock.current_price ?? "—"}</td>
                <td className="px-4 py-2 text-gray-700">{stock.previous_close ?? "—"}</td>
                <td className="px-4 py-2 text-gray-700">{stock.market_cap ?? "—"}</td>
                <td className="px-4 py-2 text-gray-700">{stock.sector ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Pagination */}
        <div className="flex justify-center mt-4 space-x-2">
          <button
            className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 disabled:cursor-not-allowed transition"
            disabled={page === 1}
            onClick={() => setPage((p) => Math.max(1, p - 1))}
          >
            Prev
          </button>
          <span className="px-3 py-1 text-gray-700 font-medium">Page {page}</span>
          <button
            className="px-3 py-1 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition"
            onClick={() => setPage((p) => p + 1)}
          >
            Next
          </button>
        </div>
      </div>

      {/* Modal for Selected Ticker */}
      {selectedTicker && (
        <>
          {/* Overlay */}
          <div className="fixed inset-0 z-40">
            <div className="absolute inset-0 bg-gray-100 opacity-40"></div>
          </div>

          {/* Modal content */}
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <div className="bg-white rounded-2xl p-6 shadow-lg max-w-lg w-full overflow-y-auto max-h-[90vh] border border-gray-200 relative">
              <button
                className="absolute top-3 right-3 text-gray-400 hover:text-gray-700"
                onClick={() => setSelectedTicker(null)}
              >
                ✕
              </button>
              <h2 className="text-2xl font-bold mb-3 text-gray-900">
                {selectedTicker.reddit_ticker} - {selectedTicker.long_name}
              </h2>

              <div className="space-y-2 text-gray-700">
                <p><strong>Verdict:</strong> {selectedTicker.verdict ?? "—"}</p>
                <p><strong>Price:</strong> {selectedTicker.current_price ?? "—"}</p>
                <p><strong>Previous Close:</strong> {selectedTicker.previous_close ?? "—"}</p>
                <p><strong>Market Cap:</strong> {selectedTicker.market_cap ?? "—"}</p>
                <p><strong>Sector:</strong> {selectedTicker.sector ?? "—"}</p>
                <p><strong>Industry:</strong> {selectedTicker.industry ?? "—"}</p>
                <p><strong>Founded:</strong> {selectedTicker.founded ?? "—"}</p>
                <p><strong>Employees:</strong> {selectedTicker.employees ?? "—"}</p>
                <p><strong>Country:</strong> {selectedTicker.country ?? "—"}</p>
                <p><strong>Currency:</strong> {selectedTicker.currency ?? "—"}</p>
                <p><strong>Website:</strong> <a href={selectedTicker.website} target="_blank" className="text-blue-600 underline">{selectedTicker.website}</a></p>
                <p><strong>Summary:</strong> {selectedTicker.summarized_content ?? selectedTicker.about ?? "—"}</p>
                <p><strong>Comments Summary:</strong> {selectedTicker.summarized_comments ?? "—"}</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
