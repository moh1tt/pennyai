interface SummaryCardProps {
  title: string;
  value: number | string;
}

export default function SummaryCard({ title, value }: SummaryCardProps) {
  return (
    <div className="p-6 bg-white rounded-lg shadow text-center">
      <p className="text-gray-500">{title}</p>
      <p className="text-3xl font-bold">{value}</p>
    </div>
  );
}
