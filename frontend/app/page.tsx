"use client";
import useSWR from "swr";
import { fetchPennyData } from "@/lib/fetchData";
import SummaryCard from "@/components/SummaryCard";

export default function Dashboard() {
  const { data, error, isValidating, mutate } = useSWR("pennystocks", fetchPennyData, {
    refreshInterval: 60000, // auto-refresh every 60s
  });

  if (error) return <div className="p-6 text-red-500">Error loading data</div>;
  if (!data) return <div className="p-6">Loading...</div>;

  return (
    <div className="p-6 max-w-md mx-auto space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">📊 Penny Stocks Dashboard</h1>
        <button
          onClick={() => mutate()}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          {isValidating ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      <SummaryCard title="Total Stocks" value={data.totalStocks} />
    </div>
  );
}
