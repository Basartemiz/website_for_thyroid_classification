interface ActionBadgeProps {
  action: 'no_action' | 'follow_up' | 'fna';
  label: string;
}

export function ActionBadge({ action, label }: ActionBadgeProps) {
  const badgeClass = `action-badge action-${action}`;

  return (
    <span className={badgeClass}>
      {label}
    </span>
  );
}
