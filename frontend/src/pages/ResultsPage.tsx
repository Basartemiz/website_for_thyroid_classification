import { useNavigate, Navigate } from 'react-router-dom';
import { ResultsPanel } from '../components/ResultsPanel';
import { ProgressBar } from '../components/ProgressBar';
import { useEvaluationContext } from '../context/EvaluationContext';

export function ResultsPage() {
  const { result, loading, error, reset } = useEvaluationContext();
  const navigate = useNavigate();

  // Guard: if there's nothing to show, redirect to form
  if (!loading && !result && !error) {
    return <Navigate to="/" replace />;
  }

  const handleNewEvaluation = () => {
    reset();
    navigate('/');
  };

  return (
    <div className="results-page">
      {loading && <ProgressBar />}

      {error && !loading && (
        <div className="results-container">
          <div className="error-message">
            <p>{error}</p>
            <button onClick={handleNewEvaluation}>Yeni Değerlendirme</button>
          </div>
        </div>
      )}

      {result && !loading && (
        <div className="results-container">
          <ResultsPanel result={result} />
          <button className="new-evaluation-button" onClick={handleNewEvaluation}>
            Yeni Değerlendirme
          </button>
        </div>
      )}
    </div>
  );
}
