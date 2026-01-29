import { createContext, useContext } from 'react';
import type { NoduleEvaluationRequest, NoduleEvaluationResponse } from '../types';

export interface EvaluationContextType {
  evaluate: (data: NoduleEvaluationRequest) => Promise<void>;
  result: NoduleEvaluationResponse | null;
  loading: boolean;
  error: string | null;
  reset: () => void;
}

export const EvaluationContext = createContext<EvaluationContextType | null>(null);

export function useEvaluationContext(): EvaluationContextType {
  const ctx = useContext(EvaluationContext);
  if (!ctx) {
    throw new Error('useEvaluationContext must be used within an EvaluationContext.Provider');
  }
  return ctx;
}
