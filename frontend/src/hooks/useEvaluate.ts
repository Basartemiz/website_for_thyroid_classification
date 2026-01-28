import { useState, useCallback } from 'react';
import { evaluateNodule } from '../api/client';
import type { NoduleEvaluationRequest, NoduleEvaluationResponse } from '../types';

interface UseEvaluateReturn {
  evaluate: (data: NoduleEvaluationRequest) => Promise<void>;
  result: NoduleEvaluationResponse | null;
  loading: boolean;
  error: string | null;
  reset: () => void;
}

export function useEvaluate(): UseEvaluateReturn {
  const [result, setResult] = useState<NoduleEvaluationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const evaluate = useCallback(async (data: NoduleEvaluationRequest) => {
    setLoading(true);
    setError(null);

    try {
      const response = await evaluateNodule(data);
      setResult(response);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Değerlendirme sırasında bir hata oluştu.');
      }
      setResult(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const reset = useCallback(() => {
    setResult(null);
    setError(null);
  }, []);

  return { evaluate, result, loading, error, reset };
}
