type StatusBadgeProps = {
  status: string;
};

const labels: Record<string, string> = {
  draft: "草稿",
  materials_ready: "素材已就绪",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className="inline-flex items-center rounded border border-teal-200 bg-teal-50 px-2 py-1 text-xs font-medium text-teal-800">
      {labels[status] ?? status}
    </span>
  );
}
