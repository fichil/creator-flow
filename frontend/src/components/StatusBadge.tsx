type StatusBadgeProps = {
  status: string;
};

const labels: Record<string, string> = {
  draft: "草稿",
  materials_ready: "素材已就绪",
  archived: "已归档",
};

const styles: Record<string, string> = {
  archived: "border-stone-300 bg-stone-100 text-stone-700",
  default: "border-teal-200 bg-teal-50 text-teal-800",
};

export function StatusBadge({ status }: StatusBadgeProps) {
  return (
    <span className={`inline-flex items-center rounded border px-2 py-1 text-xs font-medium ${styles[status] ?? styles.default}`}>
      {labels[status] ?? status}
    </span>
  );
}
