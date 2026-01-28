import type { SizeInput as SizeInputType } from '../types';

interface SizeInputProps {
  value: SizeInputType;
  onChange: (size: SizeInputType) => void;
}

export function SizeInput({ value, onChange }: SizeInputProps) {
  const handleModeChange = (mode: '2d' | '3d') => {
    onChange({
      ...value,
      mode,
      c_mm: mode === '2d' ? null : value.c_mm,
    });
  };

  const handleDimensionChange = (dimension: 'a_mm' | 'b_mm' | 'c_mm', val: string) => {
    const numVal = val === '' ? (dimension === 'a_mm' ? 0 : null) : parseFloat(val);
    onChange({
      ...value,
      [dimension]: numVal,
    });
  };

  return (
    <div className="size-input">
      <div className="size-header">
        <label>Boyut (Size)</label>
        <div className="mode-toggle">
          <button
            type="button"
            className={value.mode === '2d' ? 'active' : ''}
            onClick={() => handleModeChange('2d')}
          >
            2D
          </button>
          <button
            type="button"
            className={value.mode === '3d' ? 'active' : ''}
            onClick={() => handleModeChange('3d')}
          >
            3D
          </button>
        </div>
      </div>

      <div className="dimensions">
        <div className="dimension">
          <label htmlFor="a_mm">A (mm)</label>
          <input
            type="number"
            id="a_mm"
            min="0"
            step="0.1"
            value={value.a_mm || ''}
            onChange={(e) => handleDimensionChange('a_mm', e.target.value)}
            placeholder="0"
          />
        </div>

        <div className="dimension">
          <label htmlFor="b_mm">B (mm)</label>
          <input
            type="number"
            id="b_mm"
            min="0"
            step="0.1"
            value={value.b_mm ?? ''}
            onChange={(e) => handleDimensionChange('b_mm', e.target.value)}
            placeholder="0"
          />
        </div>

        {value.mode === '3d' && (
          <div className="dimension">
            <label htmlFor="c_mm">C (mm)</label>
            <input
              type="number"
              id="c_mm"
              min="0"
              step="0.1"
              value={value.c_mm ?? ''}
              onChange={(e) => handleDimensionChange('c_mm', e.target.value)}
              placeholder="0"
            />
          </div>
        )}
      </div>
    </div>
  );
}
