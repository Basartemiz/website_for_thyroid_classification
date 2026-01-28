"""
Thyroid Nodule Classification Engines.

Contains both ACR TI-RADS and EU-TIRADS classification systems.
References: america.pdf, classification.pdf, europe.pdf
"""

from typing import TypedDict, Literal, Optional


# =============================================================================
# ACR TI-RADS (American College of Radiology)
# =============================================================================

# Point values for each category
COMPOSITION_POINTS = {
    'cystic': 0,
    'spongiform': 0,
    'mixed_cystic_solid': 1,
    'solid': 2,
    'almost_solid': 2,
}

ECHOGENICITY_POINTS = {
    'anechoic': 0,
    'hyperechoic': 1,
    'isoechoic': 1,
    'hypoechoic': 2,
    'very_hypoechoic': 3,
}

SHAPE_POINTS = {
    'wider_than_tall': 0,
    'taller_than_wide': 3,
}

MARGIN_POINTS = {
    'smooth': 0,
    'ill_defined': 0,
    'lobulated': 2,
    'irregular': 2,
    'extrathyroidal_extension': 3,
}

ECHOGENIC_FOCI_POINTS = {
    'none': 0,
    'large_comet_tail': 0,
    'macrocalcifications': 1,
    'peripheral_calcifications': 2,
    'punctate_echogenic_foci': 3,
}


class ACRTiradsInput(TypedDict, total=False):
    composition: Literal[
        'cystic', 'spongiform', 'mixed_cystic_solid', 'solid', 'almost_solid'
    ]
    echogenicity: Literal[
        'anechoic', 'hyperechoic', 'isoechoic', 'hypoechoic', 'very_hypoechoic'
    ]
    shape: Literal['wider_than_tall', 'taller_than_wide']
    margin: Literal[
        'smooth', 'ill_defined', 'lobulated', 'irregular', 'extrathyroidal_extension'
    ]
    echogenic_foci: Literal[
        'none', 'large_comet_tail', 'macrocalcifications',
        'peripheral_calcifications', 'punctate_echogenic_foci'
    ]


class ACRTiradsResult(TypedDict):
    points: int
    tr_level: str
    description: str
    point_breakdown: dict


TR_LEVEL_DESCRIPTIONS = {
    'TR1': 'Benign',
    'TR2': 'Not suspicious',
    'TR3': 'Mildly suspicious',
    'TR4': 'Moderately suspicious',
    'TR5': 'Highly suspicious',
}


def get_tr_level(points: int) -> str:
    """
    Map total points to TR level.

    TR1: 0 points (Benign)
    TR2: 2 points (Not suspicious)
    TR3: 3 points (Mildly suspicious)
    TR4: 4-6 points (Moderately suspicious)
    TR5: >=7 points (Highly suspicious)
    """
    if points == 0:
        return 'TR1'
    elif points <= 2:
        return 'TR2'
    elif points == 3:
        return 'TR3'
    elif points <= 6:
        return 'TR4'
    else:
        return 'TR5'


def calculate_acr_tirads(findings: ACRTiradsInput) -> ACRTiradsResult:
    """
    Calculate ACR TI-RADS score based on ultrasound findings.

    Args:
        findings: Dictionary containing ultrasound characteristics

    Returns:
        ACRTiradsResult with points, TR level, description, and breakdown
    """
    point_breakdown = {}

    # Calculate points for each category
    composition = findings.get('composition', 'solid')
    composition_pts = COMPOSITION_POINTS.get(composition, 0)
    point_breakdown['composition'] = {
        'value': composition,
        'points': composition_pts
    }

    echogenicity = findings.get('echogenicity', 'isoechoic')
    echogenicity_pts = ECHOGENICITY_POINTS.get(echogenicity, 0)
    point_breakdown['echogenicity'] = {
        'value': echogenicity,
        'points': echogenicity_pts
    }

    shape = findings.get('shape', 'wider_than_tall')
    shape_pts = SHAPE_POINTS.get(shape, 0)
    point_breakdown['shape'] = {
        'value': shape,
        'points': shape_pts
    }

    margin = findings.get('margin', 'smooth')
    margin_pts = MARGIN_POINTS.get(margin, 0)
    point_breakdown['margin'] = {
        'value': margin,
        'points': margin_pts
    }

    echogenic_foci = findings.get('echogenic_foci', 'none')
    echogenic_foci_pts = ECHOGENIC_FOCI_POINTS.get(echogenic_foci, 0)
    point_breakdown['echogenic_foci'] = {
        'value': echogenic_foci,
        'points': echogenic_foci_pts
    }

    # Calculate total points
    total_points = (
        composition_pts +
        echogenicity_pts +
        shape_pts +
        margin_pts +
        echogenic_foci_pts
    )

    tr_level = get_tr_level(total_points)

    return {
        'points': total_points,
        'tr_level': tr_level,
        'description': TR_LEVEL_DESCRIPTIONS[tr_level],
        'point_breakdown': point_breakdown,
    }


# =============================================================================
# EU-TIRADS (European Thyroid Association)
# =============================================================================

class EUTiradsInput(TypedDict, total=False):
    composition: Literal[
        'cystic', 'spongiform', 'mixed_cystic_solid', 'solid', 'almost_solid'
    ]
    echogenicity: Literal[
        'anechoic', 'hyperechoic', 'isoechoic', 'hypoechoic', 'very_hypoechoic',
        'moderately_hypoechoic', 'markedly_hypoechoic'
    ]
    shape: Literal['wider_than_tall', 'taller_than_wide']
    margin: Literal[
        'smooth', 'ill_defined', 'lobulated', 'irregular', 'microlobulated',
        'extrathyroidal_extension'
    ]
    echogenic_foci: Literal[
        'none', 'large_comet_tail', 'macrocalcifications',
        'peripheral_calcifications', 'punctate_echogenic_foci', 'microcalcifications'
    ]
    is_simple_cyst: Optional[bool]
    is_spongiform: Optional[bool]
    has_adenopathy: Optional[bool]


class EUTiradsResult(TypedDict):
    eu_level: str
    risk_category: str
    malignancy_risk: str
    high_suspicious_features: list


EU_LEVEL_INFO = {
    'EU-TIRADS 1': {
        'risk_category': 'Normal',
        'malignancy_risk': 'N/A',
    },
    'EU-TIRADS 2': {
        'risk_category': 'Benign',
        'malignancy_risk': '~0%',
    },
    'EU-TIRADS 3': {
        'risk_category': 'Low risk',
        'malignancy_risk': '2-4%',
    },
    'EU-TIRADS 4': {
        'risk_category': 'Intermediate risk',
        'malignancy_risk': '6-17%',
    },
    'EU-TIRADS 5': {
        'risk_category': 'High risk',
        'malignancy_risk': '26-87%',
    },
}


def classify_eu_tirads(findings: EUTiradsInput) -> EUTiradsResult:
    """
    Classify nodule according to EU-TIRADS guidelines.

    EU-TIRADS 2 (Benign): Simple cyst, spongiform nodule
    EU-TIRADS 3 (Low risk): Isoechoic or hyperechoic, oval shape, smooth margins
    EU-TIRADS 4 (Intermediate risk): Mildly hypoechoic, oval, smooth margins
    EU-TIRADS 5 (High risk): At least one high-risk feature

    High-risk features:
    - Taller-than-wide shape
    - Irregular/microlobulated margins
    - Microcalcifications
    - Marked hypoechogenicity

    Args:
        findings: Dictionary containing ultrasound characteristics

    Returns:
        EUTiradsResult with EU level and risk assessment
    """
    high_suspicious_features = []

    # Check for high suspicious aspects
    shape = findings.get('shape', 'wider_than_tall')
    if shape == 'taller_than_wide':
        high_suspicious_features.append('Taller-than-wide shape')

    margin = findings.get('margin', 'smooth')
    if margin in ['irregular', 'microlobulated']:
        high_suspicious_features.append(f'{margin.capitalize()} margin')

    echogenic_foci = findings.get('echogenic_foci', 'none')
    if echogenic_foci in ['microcalcifications', 'punctate_echogenic_foci']:
        high_suspicious_features.append('Microcalcifications')

    echogenicity = findings.get('echogenicity', 'isoechoic')
    if echogenicity in ['very_hypoechoic', 'markedly_hypoechoic']:
        high_suspicious_features.append('Marked hypoechogenicity')

    suspicious_count = len(high_suspicious_features)

    # Check for benign patterns first
    is_simple_cyst = findings.get('is_simple_cyst', False)
    is_spongiform = findings.get('is_spongiform', False)
    composition = findings.get('composition', 'solid')

    # If purely cystic or spongiform -> EU-TIRADS 2
    if is_simple_cyst or is_spongiform or composition in ['cystic', 'spongiform']:
        eu_level = 'EU-TIRADS 2'
    # Check for high-risk features
    elif findings.get('has_adenopathy', False):
        eu_level = 'EU-TIRADS 5'
        high_suspicious_features.append('Suspicious lymphadenopathy')
    elif suspicious_count >= 1:
        # Any high-risk feature -> EU-TIRADS 5
        eu_level = 'EU-TIRADS 5'
    elif echogenicity in ['hypoechoic', 'moderately_hypoechoic']:
        # Mildly hypoechoic without high-risk features -> EU-TIRADS 4
        eu_level = 'EU-TIRADS 4'
    elif echogenicity in ['isoechoic', 'hyperechoic']:
        # Iso/hyperechoic without high-risk features -> EU-TIRADS 3
        eu_level = 'EU-TIRADS 3'
    else:
        # Default to EU-TIRADS 3
        eu_level = 'EU-TIRADS 3'

    level_info = EU_LEVEL_INFO[eu_level]

    return {
        'eu_level': eu_level,
        'risk_category': level_info['risk_category'],
        'malignancy_risk': level_info['malignancy_risk'],
        'high_suspicious_features': high_suspicious_features,
    }
