const statusLabels: Record<string, string> = {
  candidate: "候选",
  draft: "草稿",
  selected: "已选择",
  dismissed: "已忽略",
  queued: "排队中",
  running: "运行中",
  succeeded: "成功",
  failed: "失败",
  pending_review: "待审核",
  approved: "已通过",
  rejected: "已拒绝",
};

export function formatStatus(status: string) {
  return statusLabels[status] ?? status;
}
