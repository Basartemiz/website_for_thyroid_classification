// Request types
export interface SizeInput {
  mode: '2d' | '3d';
  a_mm: number;
  b_mm?: number | null;
  c_mm?: number | null;
}

export interface ClinicalInput {
  age?: number;
  sex?: 'male' | 'female' | 'other';
  family_history?: boolean;
  family_history_detail?: string;
  radiation_history?: boolean;
  radiation_history_detail?: string;
}

export interface NoduleEvaluationRequest {
  composition: 'cystic' | 'spongiform' | 'mixed_cystic_solid' | 'solid' | 'almost_solid';
  echogenicity: 'anechoic' | 'hyperechoic' | 'isoechoic' | 'hypoechoic' | 'very_hypoechoic' | 'moderately_hypoechoic' | 'markedly_hypoechoic';
  shape: 'wider_than_tall' | 'taller_than_wide';
  margin: 'smooth' | 'ill_defined' | 'lobulated' | 'irregular' | 'microlobulated' | 'extrathyroidal_extension';
  echogenic_foci: 'none' | 'large_comet_tail' | 'macrocalcifications' | 'peripheral_calcifications' | 'punctate_echogenic_foci' | 'microcalcifications';
  size: SizeInput;
  clinical?: ClinicalInput;
}

// Response types
export interface ACRResult {
  points: number;
  tr_level: string;
  description: string;
  point_breakdown?: Record<string, { value: string; points: number }>;
}

export interface EUResult {
  eu_level: string;
  risk_category: string;
  malignancy_risk: string;
  high_suspicious_features?: string[];
}

export interface SizeResult {
  mode: string;
  a_mm: number;
  b_mm: number | null;
  c_mm: number | null;
  volume_mm3: number | null;
  max_dimension_mm: number;
}

export interface Recommendation {
  action: 'no_action' | 'follow_up' | 'fna';
  label_tr: string;
  label_en: string;
  rationale: string;
  rationale_tr: string;
}

export interface TreatmentOptions {
  surgical: string[];
  non_surgical: string[];
}

export interface Source {
  doc_id: string;
  page: number;
  chunk_id: string;
  excerpt: string;
}

export interface LLMExplanation {
  tr: string;
  us: string;
  eu: string;
}

export interface NoduleEvaluationResponse {
  input_echo: NoduleEvaluationRequest;
  acr: ACRResult;
  eu: EUResult;
  tr_guideline: {
    summary: string;
  };
  size: SizeResult;
  recommendation: Recommendation;
  treatment_options: TreatmentOptions;
  llm_explanation: LLMExplanation;
  sources: Source[];
}

export interface HealthCheckResponse {
  status: string;
  vectorstore_ready: boolean;
  vectorstore_count?: number;
}

// Form option types
export interface FormOption<T = string> {
  value: T;
  label: string;
  label_tr: string;
}

// Form options
export const compositionOptions: FormOption[] = [
  { value: 'cystic', label: 'Cystic', label_tr: 'Kistik' },
  { value: 'spongiform', label: 'Spongiform', label_tr: 'Spongiform' },
  { value: 'mixed_cystic_solid', label: 'Mixed Cystic-Solid', label_tr: 'Mikst Kistik-Solid' },
  { value: 'solid', label: 'Solid', label_tr: 'Solid' },
  { value: 'almost_solid', label: 'Almost Solid', label_tr: 'Hemen Hemen Solid' },
];

export const echogenicityOptions: FormOption[] = [
  { value: 'anechoic', label: 'Anechoic', label_tr: 'Anekoik' },
  { value: 'hyperechoic', label: 'Hyperechoic', label_tr: 'Hiperekoik' },
  { value: 'isoechoic', label: 'Isoechoic', label_tr: 'İzoekoik' },
  { value: 'hypoechoic', label: 'Hypoechoic', label_tr: 'Hipoekoik' },
  { value: 'very_hypoechoic', label: 'Very Hypoechoic', label_tr: 'Çok Hipoekoik' },
];

export const shapeOptions: FormOption[] = [
  { value: 'wider_than_tall', label: 'Wider than Tall', label_tr: 'Yatay (Enine Daha Geniş)' },
  { value: 'taller_than_wide', label: 'Taller than Wide', label_tr: 'Dikey (Boyuna Daha Uzun)' },
];

export const marginOptions: FormOption[] = [
  { value: 'smooth', label: 'Smooth', label_tr: 'Düzgün' },
  { value: 'ill_defined', label: 'Ill-defined', label_tr: 'Belirsiz' },
  { value: 'lobulated', label: 'Lobulated', label_tr: 'Lobüle' },
  { value: 'irregular', label: 'Irregular', label_tr: 'Düzensiz' },
  { value: 'extrathyroidal_extension', label: 'Extrathyroidal Extension', label_tr: 'Ekstratiroidal Uzanım' },
];

export const echogenicFociOptions: FormOption[] = [
  { value: 'none', label: 'None', label_tr: 'Yok' },
  { value: 'large_comet_tail', label: 'Large Comet-tail', label_tr: 'Büyük Kuyruklu Yıldız Artefaktı' },
  { value: 'macrocalcifications', label: 'Macrocalcifications', label_tr: 'Makrokalsifikasyon' },
  { value: 'peripheral_calcifications', label: 'Peripheral Calcifications', label_tr: 'Periferik Kalsifikasyon' },
  { value: 'punctate_echogenic_foci', label: 'Punctate Echogenic Foci', label_tr: 'Punktat Ekojenik Odaklar' },
];
