import { useState } from 'react';
import type { NoduleEvaluationRequest, SizeInput as SizeInputType, ClinicalInput } from '../types';
import {
  compositionOptions,
  echogenicityOptions,
  shapeOptions,
  marginOptions,
  echogenicFociOptions,
} from '../types';
import { CriteriaSelect } from './CriteriaSelect';
import { SizeInput } from './SizeInput';

interface NoduleFormProps {
  onSubmit: (data: NoduleEvaluationRequest) => void;
  loading: boolean;
}

const STEP_TITLES = [
  'Ultrason Bulguları',
  'Boyut Ölçümleri',
  'Klinik Bilgiler',
  'Özet & Değerlendir',
];

const defaultSize: SizeInputType = {
  mode: '2d',
  a_mm: 10,
  b_mm: null,
  c_mm: null,
};

const defaultClinical: ClinicalInput = {
  age: undefined,
  sex: undefined,
  family_history: false,
  family_history_detail: '',
  radiation_history: false,
  radiation_history_detail: '',
};

export function NoduleForm({ onSubmit, loading }: NoduleFormProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [composition, setComposition] = useState('solid');
  const [echogenicity, setEchogenicity] = useState('isoechoic');
  const [shape, setShape] = useState('wider_than_tall');
  const [margin, setMargin] = useState('smooth');
  const [echogenicFoci, setEchogenicFoci] = useState('none');
  const [size, setSize] = useState<SizeInputType>(defaultSize);
  const [clinical, setClinical] = useState<ClinicalInput>(defaultClinical);

  const handleCriteriaChange = (name: string, value: string) => {
    switch (name) {
      case 'composition':
        setComposition(value);
        break;
      case 'echogenicity':
        setEchogenicity(value);
        break;
      case 'shape':
        setShape(value);
        break;
      case 'margin':
        setMargin(value);
        break;
      case 'echogenic_foci':
        setEchogenicFoci(value);
        break;
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const data: NoduleEvaluationRequest = {
      composition: composition as NoduleEvaluationRequest['composition'],
      echogenicity: echogenicity as NoduleEvaluationRequest['echogenicity'],
      shape: shape as NoduleEvaluationRequest['shape'],
      margin: margin as NoduleEvaluationRequest['margin'],
      echogenic_foci: echogenicFoci as NoduleEvaluationRequest['echogenic_foci'],
      size,
      clinical: clinical,
    };

    onSubmit(data);
  };

  const goToNextStep = () => {
    if (currentStep < 4) {
      setCurrentStep(currentStep + 1);
    }
  };

  const goToPrevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const getOptionLabel = (options: typeof compositionOptions, value: string) => {
    const option = options.find((o) => o.value === value);
    return option ? option.label_tr : value;
  };

  const renderStepIndicator = () => (
    <div className="step-indicator">
      {STEP_TITLES.map((title, index) => {
        const stepNumber = index + 1;
        const isActive = stepNumber === currentStep;
        const isCompleted = stepNumber < currentStep;

        return (
          <div
            key={stepNumber}
            className={`step-indicator-item ${isActive ? 'active' : ''} ${isCompleted ? 'completed' : ''}`}
          >
            <div className="step-circle">
              {isCompleted ? (
                <span className="step-check">&#10003;</span>
              ) : (
                stepNumber
              )}
            </div>
            <span className="step-title">{title}</span>
          </div>
        );
      })}
      <div className="step-progress-bar">
        <div
          className="step-progress-fill"
          style={{ width: `${((currentStep - 1) / 3) * 100}%` }}
        />
      </div>
    </div>
  );

  const renderStep1 = () => (
    <div className="step-content">
      <h3>Ultrason Bulguları</h3>
      <p className="step-description">Nodülün ultrason görüntüleme özelliklerini seçin.</p>

      <CriteriaSelect
        label="Kompozisyon (Composition)"
        name="composition"
        options={compositionOptions}
        value={composition}
        onChange={handleCriteriaChange}
      />

      <CriteriaSelect
        label="Ekojenite (Echogenicity)"
        name="echogenicity"
        options={echogenicityOptions}
        value={echogenicity}
        onChange={handleCriteriaChange}
      />

      <CriteriaSelect
        label="Şekil (Shape)"
        name="shape"
        options={shapeOptions}
        value={shape}
        onChange={handleCriteriaChange}
      />

      <CriteriaSelect
        label="Kenar (Margin)"
        name="margin"
        options={marginOptions}
        value={margin}
        onChange={handleCriteriaChange}
      />

      <CriteriaSelect
        label="Ekojenik Odaklar (Echogenic Foci)"
        name="echogenic_foci"
        options={echogenicFociOptions}
        value={echogenicFoci}
        onChange={handleCriteriaChange}
      />
    </div>
  );

  const renderStep2 = () => (
    <div className="step-content">
      <h3>Boyut Ölçümleri</h3>
      <p className="step-description">Nodülün boyut ölçümlerini girin.</p>

      <SizeInput value={size} onChange={setSize} />
    </div>
  );

  const renderStep3 = () => (
    <div className="step-content">
      <h3>Klinik Bilgiler</h3>
      <p className="step-description">Hasta bilgilerini girin (opsiyonel).</p>

      <div className="clinical-info">
        <div className="clinical-field">
          <label htmlFor="age">Yaş (Age)</label>
          <input
            type="number"
            id="age"
            min="0"
            max="150"
            value={clinical.age ?? ''}
            onChange={(e) =>
              setClinical({
                ...clinical,
                age: e.target.value ? parseInt(e.target.value) : undefined,
              })
            }
          />
        </div>

        <div className="clinical-field">
          <label htmlFor="sex">Cinsiyet (Sex)</label>
          <select
            id="sex"
            value={clinical.sex ?? ''}
            onChange={(e) =>
              setClinical({
                ...clinical,
                sex: (e.target.value as ClinicalInput['sex']) || undefined,
              })
            }
          >
            <option value="">Seçiniz</option>
            <option value="female">Kadın (Female)</option>
            <option value="male">Erkek (Male)</option>
            <option value="other">Diğer (Other)</option>
          </select>
        </div>

        <div className="clinical-field checkbox">
          <label>
            <input
              type="checkbox"
              checked={clinical.family_history ?? false}
              onChange={(e) =>
                setClinical({
                  ...clinical,
                  family_history: e.target.checked,
                  family_history_detail: e.target.checked ? clinical.family_history_detail : '',
                })
              }
            />
            Aile Öyküsü (Family History)
          </label>
        </div>

        {clinical.family_history && (
          <div className="clinical-field detail-textarea">
            <label htmlFor="family_history_detail">Aile Öyküsü Detayı</label>
            <textarea
              id="family_history_detail"
              placeholder="Aile öyküsü hakkında detaylı bilgi girin..."
              value={clinical.family_history_detail ?? ''}
              onChange={(e) =>
                setClinical({
                  ...clinical,
                  family_history_detail: e.target.value,
                })
              }
              rows={3}
            />
          </div>
        )}

        <div className="clinical-field checkbox">
          <label>
            <input
              type="checkbox"
              checked={clinical.radiation_history ?? false}
              onChange={(e) =>
                setClinical({
                  ...clinical,
                  radiation_history: e.target.checked,
                  radiation_history_detail: e.target.checked ? clinical.radiation_history_detail : '',
                })
              }
            />
            Radyasyon Öyküsü (Radiation History)
          </label>
        </div>

        {clinical.radiation_history && (
          <div className="clinical-field detail-textarea">
            <label htmlFor="radiation_history_detail">Radyasyon Öyküsü Detayı</label>
            <textarea
              id="radiation_history_detail"
              placeholder="Radyasyon öyküsü hakkında detaylı bilgi girin..."
              value={clinical.radiation_history_detail ?? ''}
              onChange={(e) =>
                setClinical({
                  ...clinical,
                  radiation_history_detail: e.target.value,
                })
              }
              rows={3}
            />
          </div>
        )}
      </div>
    </div>
  );

  const renderStep4 = () => (
    <div className="step-content">
      <h3>Özet & Değerlendir</h3>
      <p className="step-description">Girilen bilgileri kontrol edin ve değerlendirmeyi başlatın.</p>

      <div className="step-summary">
        <div className="summary-section">
          <h4>Ultrason Bulguları</h4>
          <table className="summary-table">
            <tbody>
              <tr>
                <td>Kompozisyon</td>
                <td>{getOptionLabel(compositionOptions, composition)}</td>
              </tr>
              <tr>
                <td>Ekojenite</td>
                <td>{getOptionLabel(echogenicityOptions, echogenicity)}</td>
              </tr>
              <tr>
                <td>Şekil</td>
                <td>{getOptionLabel(shapeOptions, shape)}</td>
              </tr>
              <tr>
                <td>Kenar</td>
                <td>{getOptionLabel(marginOptions, margin)}</td>
              </tr>
              <tr>
                <td>Ekojenik Odaklar</td>
                <td>{getOptionLabel(echogenicFociOptions, echogenicFoci)}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <div className="summary-section">
          <h4>Boyut Ölçümleri</h4>
          <table className="summary-table">
            <tbody>
              <tr>
                <td>Ölçüm Modu</td>
                <td>{size.mode === '2d' ? '2D' : '3D'}</td>
              </tr>
              <tr>
                <td>A Boyutu</td>
                <td>{size.a_mm} mm</td>
              </tr>
              {size.mode === '3d' && size.b_mm && (
                <tr>
                  <td>B Boyutu</td>
                  <td>{size.b_mm} mm</td>
                </tr>
              )}
              {size.mode === '3d' && size.c_mm && (
                <tr>
                  <td>C Boyutu</td>
                  <td>{size.c_mm} mm</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        <div className="summary-section">
          <h4>Klinik Bilgiler</h4>
          <table className="summary-table">
            <tbody>
              <tr>
                <td>Yaş</td>
                <td>{clinical.age ?? 'Belirtilmemiş'}</td>
              </tr>
              <tr>
                <td>Cinsiyet</td>
                <td>
                  {clinical.sex === 'female'
                    ? 'Kadın'
                    : clinical.sex === 'male'
                      ? 'Erkek'
                      : clinical.sex === 'other'
                        ? 'Diğer'
                        : 'Belirtilmemiş'}
                </td>
              </tr>
              <tr>
                <td>Aile Öyküsü</td>
                <td>
                  {clinical.family_history
                    ? clinical.family_history_detail
                      ? `Var - ${clinical.family_history_detail}`
                      : 'Var'
                    : 'Yok'}
                </td>
              </tr>
              <tr>
                <td>Radyasyon Öyküsü</td>
                <td>
                  {clinical.radiation_history
                    ? clinical.radiation_history_detail
                      ? `Var - ${clinical.radiation_history_detail}`
                      : 'Var'
                    : 'Yok'}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );

  const renderCurrentStep = () => {
    switch (currentStep) {
      case 1:
        return renderStep1();
      case 2:
        return renderStep2();
      case 3:
        return renderStep3();
      case 4:
        return renderStep4();
      default:
        return null;
    }
  };

  return (
    <form className="nodule-form wizard-form" onSubmit={handleSubmit}>
      <h2>Tiroid Nodülü Değerlendirmesi</h2>

      {renderStepIndicator()}

      <div className="wizard-step-container">
        {renderCurrentStep()}
      </div>

      <div className="step-navigation">
        {currentStep > 1 && (
          <button
            type="button"
            className="nav-button prev-button"
            onClick={goToPrevStep}
          >
            Geri
          </button>
        )}

        {currentStep < 4 ? (
          <button
            type="button"
            className="nav-button next-button"
            onClick={goToNextStep}
          >
            İleri
          </button>
        ) : (
          <button type="submit" className="submit-button" disabled={loading}>
            {loading ? 'Değerlendiriliyor...' : 'Değerlendir'}
          </button>
        )}
      </div>
    </form>
  );
}
