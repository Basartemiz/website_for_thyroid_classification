import type { FormOption } from '../types';

interface CriteriaSelectProps {
  label: string;
  name: string;
  options: FormOption[];
  value: string;
  onChange: (name: string, value: string) => void;
}

export function CriteriaSelect({
  label,
  name,
  options,
  value,
  onChange,
}: CriteriaSelectProps) {
  return (
    <div className="criteria-select">
      <label htmlFor={name}>{label}</label>
      <select
        id={name}
        name={name}
        value={value}
        onChange={(e) => onChange(name, e.target.value)}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label_tr} ({option.label})
          </option>
        ))}
      </select>
    </div>
  );
}
