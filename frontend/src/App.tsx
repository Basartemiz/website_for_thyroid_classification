import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { useEvaluate } from './hooks/useEvaluate';
import { EvaluationContext } from './context/EvaluationContext';
import { FormPage } from './pages/FormPage';
import { ResultsPage } from './pages/ResultsPage';
import './App.css';

function App() {
  const evaluation = useEvaluate();

  return (
    <EvaluationContext.Provider value={evaluation}>
      <BrowserRouter>
        <div className="app">
          <header className="app-header">
            <h1>Tiroid Nodülü Değerlendirme Sistemi</h1>
            <p>TI-RADS Kılavuz Tabanlı Klinik Karar Destek Sistemi</p>
          </header>

          <main className="app-main">
            <Routes>
              <Route path="/" element={<FormPage />} />
              <Route path="/results" element={<ResultsPage />} />
            </Routes>
          </main>

          <footer className="app-footer">
            <p>
              Bu sistem klinik karar destek amaçlıdır. Nihai tanı ve tedavi kararları
              uzman hekim tarafından verilmelidir.
            </p>
          </footer>
        </div>
      </BrowserRouter>
    </EvaluationContext.Provider>
  );
}

export default App;
