"""
Thyroid nodule management recommendations.

Based on ACR TI-RADS size-based recommendations for action.
"""

from typing import TypedDict, Literal, List, Optional


class RecommendationInput(TypedDict, total=False):
    tr_level: str  # TR1, TR2, TR3, TR4, TR5
    max_dimension_mm: float
    clinical_risk_factors: Optional[List[str]]


class RecommendationResult(TypedDict):
    action: Literal['no_action', 'follow_up', 'fna']
    label_tr: str  # Turkish label
    label_en: str  # English label
    rationale: str
    rationale_tr: str


# Size thresholds in mm for each TR level
# Format: (follow_up_threshold, fna_threshold)
# If max_dimension < follow_up_threshold: no action
# If follow_up_threshold <= max_dimension < fna_threshold: follow up
# If max_dimension >= fna_threshold: FNA
SIZE_THRESHOLDS = {
    'TR1': (None, None),  # No FNA or follow-up regardless of size
    'TR2': (None, None),  # No FNA or follow-up regardless of size
    'TR3': (15, 25),      # Follow-up >=15mm, FNA >=25mm
    'TR4': (10, 15),      # Follow-up >=10mm, FNA >=15mm
    'TR5': (5, 10),       # Follow-up >=5mm, FNA >=10mm
}

ACTION_LABELS = {
    'no_action': {
        'tr': 'Eylem Gerektirmez',
        'en': 'No Action Required'
    },
    'follow_up': {
        'tr': 'Takip Önerilir',
        'en': 'Follow-up Recommended'
    },
    'fna': {
        'tr': 'IİAB (ince iğne aspirasyon biyopsisi)',
        'en': 'FNA (Fine Needle Aspiration) Biopsy'
    },
}


def get_recommendation(input_data: RecommendationInput) -> RecommendationResult:
    """
    Determine management recommendation based on TR level and nodule size.

    Args:
        input_data: Dictionary containing TR level and max dimension

    Returns:
        RecommendationResult with action, labels, and rationale
    """
    tr_level = input_data.get('tr_level', 'TR3')
    max_dimension = input_data.get('max_dimension_mm', 0)
    clinical_risk_factors = input_data.get('clinical_risk_factors', [])

    thresholds = SIZE_THRESHOLDS.get(tr_level, (10, 15))
    follow_up_threshold, fna_threshold = thresholds

    # Determine action based on TR level and size
    if tr_level in ['TR1', 'TR2']:
        action = 'no_action'
        rationale_en = f'{tr_level} nodules are benign or not suspicious and do not require FNA or routine follow-up regardless of size.'
        rationale_tr = f'{tr_level} nodüller benign veya şüpheli değildir ve boyuttan bağımsız olarak İİAB veya rutin takip gerektirmez.'
    elif max_dimension >= fna_threshold:
        action = 'fna'
        rationale_en = f'{tr_level} nodule with maximum dimension {max_dimension}mm (>={fna_threshold}mm threshold) requires FNA.'
        rationale_tr = f'{tr_level} nodül, maksimum boyutu {max_dimension}mm (>={fna_threshold}mm eşiği) olduğundan İİAB gerektirir.'
    elif max_dimension >= follow_up_threshold:
        action = 'follow_up'
        rationale_en = f'{tr_level} nodule with maximum dimension {max_dimension}mm (>={follow_up_threshold}mm threshold) requires follow-up ultrasound.'
        rationale_tr = f'{tr_level} nodül, maksimum boyutu {max_dimension}mm (>={follow_up_threshold}mm eşiği) olduğundan takip ultrasonografisi gerektirir.'
    else:
        action = 'no_action'
        rationale_en = f'{tr_level} nodule with maximum dimension {max_dimension}mm (<{follow_up_threshold}mm threshold) does not require action.'
        rationale_tr = f'{tr_level} nodül, maksimum boyutu {max_dimension}mm (<{follow_up_threshold}mm eşiği) olduğundan eylem gerektirmez.'

    # Adjust for clinical risk factors
    if clinical_risk_factors and action != 'fna':
        risk_factor_note_en = ' Clinical risk factors present may warrant earlier intervention.'
        risk_factor_note_tr = ' Mevcut klinik risk faktörleri daha erken müdahale gerektirebilir.'
        rationale_en += risk_factor_note_en
        rationale_tr += risk_factor_note_tr

    labels = ACTION_LABELS[action]

    return {
        'action': action,
        'label_tr': labels['tr'],
        'label_en': labels['en'],
        'rationale': rationale_en,
        'rationale_tr': rationale_tr,
    }


def get_treatment_options(tr_level: str, action: str) -> dict:
    """
    Get treatment options based on TR level and recommended action.

    Returns:
        Dictionary with surgical and non-surgical options
    """
    surgical_options = []
    non_surgical_options = []

    if action == 'fna':
        # If FNA is recommended, provide treatment options based on potential findings
        surgical_options = [
            'Total tiroidektomi',
            'Lobektomi',
            'Hemitiroidektomi',
        ]
        non_surgical_options = [
            'Aktif izlem (biyopsi sonucuna göre)',
            'Radyofrekans ablasyon (RFA)',
            'Etanol ablasyonu',
            'Mikrodalga ablasyonu',
        ]
    elif action == 'follow_up':
        surgical_options = [
            'Biyopsi sonucuna göre değerlendirilecek',
        ]
        non_surgical_options = [
            'Aktif izlem',
            'Periyodik ultrasonografi',
            '6-12 ay sonra kontrol',
        ]
    else:  # no_action
        non_surgical_options = [
            'Rutin takip gerektirmez',
            'Klinik endikasyon varsa yeniden değerlendirme',
        ]

    return {
        'surgical': surgical_options,
        'non_surgical': non_surgical_options,
    }
