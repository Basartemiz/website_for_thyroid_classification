import { NoduleForm } from './components/NoduleForm';
import { ResultsPanel } from './components/ResultsPanel';
import { useEvaluate } from './hooks/useEvaluate';
import './App.css';

function App() {
  const { evaluate, result, loading, error, reset } = useEvaluate();

  return (
    <div className="app">
      <header className="app-header">
        <h1>Tiroid Nodülü Değerlendirme Sistemi</h1>
        <p>TI-RADS Kılavuz Tabanlı Klinik Karar Destek Sistemi</p>
      </header>

      <main className="app-main">
        <div className="form-container">
          <NoduleForm onSubmit={evaluate} loading={loading} />
        </div>

        <div className="results-container">
          {error && (
            <div className="error-message">
              <p>{error}</p>
              <button onClick={reset}>Kapat</button>
            </div>
          )}

          {loading && (
            <div className="loading">
              <div className="spinner"></div>
              <p>Nodül değerlendiriliyor...</p>
            </div>
          )}

          {result && !loading && <ResultsPanel result={result} />}

          {!result && !loading && !error && (
            <div className="placeholder">
              <p>
                Tiroid nodülü özelliklerini girerek ACR TI-RADS ve EU-TIRADS
                sınıflandırmasını alın.
              </p>
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>
          Bu sistem klinik karar destek amaçlıdır. Nihai tanı ve tedavi kararları
          uzman hekim tarafından verilmelidir.
        </p>
      </footer>
    </div>
  );
}

export default App;
