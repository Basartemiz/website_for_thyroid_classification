import { useState } from 'react';
import type { NoduleEvaluationResponse } from '../types';
import { ActionBadge } from './ActionBadge';
import { SourcesList } from './SourcesList';

interface ResultsPanelProps {
  result: NoduleEvaluationResponse;
}

type GuidelineTab = 'tr' | 'us' | 'eu';

export function ResultsPanel({ result }: ResultsPanelProps) {
  const [activeTab, setActiveTab] = useState<GuidelineTab>('tr');

  const renderGuidelineExplanation = (content: string) => {
    if (!content) return <p>Bu kılavuz için açıklama bulunamadı.</p>;
    return content.split('\n').map((paragraph, index) => (
      <p key={index}>{paragraph}</p>
    ));
  };

  return (
    <div className="results-panel">
      <h2>Değerlendirme Sonuçları</h2>

      {/* Classification Results */}
      <div className="results-section classification">
        <h3>Sınıflandırma</h3>
        <div className="classification-grid">
          <div className="classification-item acr">
            <span className="label">ACR TI-RADS</span>
            <span className="value">{result.acr.tr_level}</span>
            <span className="points">{result.acr.points} puan</span>
            <span className="description">{result.acr.description}</span>
          </div>
          <div className="classification-item eu">
            <span className="label">EU-TIRADS</span>
            <span className="value">{result.eu.eu_level}</span>
            <span className="risk">{result.eu.risk_category}</span>
            <span className="malignancy">Malignite riski: {result.eu.malignancy_risk}</span>
          </div>
        </div>
      </div>

      {/* Size Information */}
      <div className="results-section size">
        <h3>Boyut Bilgileri</h3>
        <div className="size-info">
          <p>
            <strong>Maksimum boyut:</strong> {result.size.max_dimension_mm} mm
          </p>
          {result.size.volume_mm3 && (
            <p>
              <strong>Hacim:</strong> {result.size.volume_mm3} mm³
            </p>
          )}
          <p>
            <strong>Boyutlar:</strong> {result.size.a_mm}
            {result.size.b_mm && ` x ${result.size.b_mm}`}
            {result.size.c_mm && ` x ${result.size.c_mm}`} mm
          </p>
        </div>
      </div>

      {/* Recommendation */}
      <div className="results-section recommendation">
        <h3>Öneri</h3>
        <div className="recommendation-content">
          <ActionBadge
            action={result.recommendation.action}
            label={result.recommendation.label_tr}
          />
          <p className="rationale">{result.recommendation.rationale_tr}</p>
        </div>
      </div>

      {/* Treatment Options */}
      <div className="results-section treatment">
        <h3>Tedavi Seçenekleri</h3>
        <div className="treatment-options">
          {result.treatment_options.surgical.length > 0 && (
            <div className="option-group">
              <h4>Cerrahi Seçenekler</h4>
              <ul>
                {result.treatment_options.surgical.map((option, index) => (
                  <li key={index}>{option}</li>
                ))}
              </ul>
            </div>
          )}
          {result.treatment_options.non_surgical.length > 0 && (
            <div className="option-group">
              <h4>Non-Cerrahi Seçenekler</h4>
              <ul>
                {result.treatment_options.non_surgical.map((option, index) => (
                  <li key={index}>{option}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Guideline-Specific LLM Explanations */}
      <div className="results-section explanation">
        <h3>Kılavuz Tabanlı Açıklamalar</h3>

        <div className="guideline-tabs">
          <button
            type="button"
            className={`guideline-tab ${activeTab === 'tr' ? 'active' : ''}`}
            onClick={() => setActiveTab('tr')}
          >
            TR Kılavuzu
          </button>
          <button
            type="button"
            className={`guideline-tab ${activeTab === 'us' ? 'active' : ''}`}
            onClick={() => setActiveTab('us')}
          >
            US (ACR) Kılavuzu
          </button>
          <button
            type="button"
            className={`guideline-tab ${activeTab === 'eu' ? 'active' : ''}`}
            onClick={() => setActiveTab('eu')}
          >
            EU Kılavuzu
          </button>
        </div>

        <div className="guideline-content">
          {activeTab === 'tr' && (
            <div className="guideline-section tr-guideline-section">
              <h4>Türkiye Kılavuzuna Göre</h4>
              <div className="llm-explanation">
                {renderGuidelineExplanation(result.llm_explanation.tr)}
              </div>
            </div>
          )}

          {activeTab === 'us' && (
            <div className="guideline-section us-guideline-section">
              <h4>US (ACR TI-RADS) Kılavuzuna Göre</h4>
              <div className="llm-explanation">
                {renderGuidelineExplanation(result.llm_explanation.us)}
              </div>
            </div>
          )}

          {activeTab === 'eu' && (
            <div className="guideline-section eu-guideline-section">
              <h4>EU-TIRADS Kılavuzuna Göre</h4>
              <div className="llm-explanation">
                {renderGuidelineExplanation(result.llm_explanation.eu)}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Sources */}
      <SourcesList sources={result.sources} />
    </div>
  );
}
