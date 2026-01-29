import { useState, useEffect } from 'react';

const DURATION_MS = 60_000;
const INTERVAL_MS = 100;
const MAX_PERCENT = 95;

export function ProgressBar() {
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsed((prev) => Math.min(prev + INTERVAL_MS, DURATION_MS));
    }, INTERVAL_MS);

    return () => clearInterval(timer);
  }, []);

  // Quadratic ease-out: 1 - (1-t)²
  const t = Math.min(elapsed / DURATION_MS, 1);
  const eased = 1 - (1 - t) * (1 - t);
  const percent = Math.min(eased * 100, MAX_PERCENT);

  const remainingSeconds = Math.max(0, Math.ceil((DURATION_MS - elapsed) / 1000));

  return (
    <div className="progress-bar-wrapper">
      <div className="progress-bar-header">
        <span>Nodül değerlendiriliyor...</span>
        <span className="progress-bar-percent">{Math.round(percent)}%</span>
      </div>
      <div className="progress-bar-track">
        <div
          className="progress-bar-fill"
          style={{ width: `${percent}%` }}
        />
      </div>
      <p className="progress-bar-text">
        Tahmini kalan süre: ~{remainingSeconds} saniye
      </p>
    </div>
  );
}
