"""
Tests for EU-TIRADS classification.
"""

import pytest
from thyroid.rules.classification import classify_eu_tirads


class TestEUTiradsClassification:
    """Test EU-TIRADS classification logic."""

    def test_eu_tirads_2_simple_cyst(self):
        """Test EU-TIRADS 2: Simple cyst -> Benign."""
        findings = {
            'composition': 'cystic',
            'echogenicity': 'anechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
            'is_simple_cyst': True,
        }
        result = classify_eu_tirads(findings)

        assert result['eu_level'] == 'EU-TIRADS 2'
        assert result['risk_category'] == 'Benign'

    def test_eu_tirads_2_spongiform(self):
        """Test EU-TIRADS 2: Spongiform nodule -> Benign."""
        findings = {
            'composition': 'spongiform',
            'echogenicity': 'isoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
            'is_spongiform': True,
        }
        result = classify_eu_tirads(findings)

        assert result['eu_level'] == 'EU-TIRADS 2'
        assert result['risk_category'] == 'Benign'

    def test_eu_tirads_3_isoechoic(self):
        """Test EU-TIRADS 3: Isoechoic without suspicious features."""
        findings = {
            'composition': 'solid',
            'echogenicity': 'isoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
        }
        result = classify_eu_tirads(findings)

        assert result['eu_level'] == 'EU-TIRADS 3'
        assert result['risk_category'] == 'Low risk'

    def test_eu_tirads_3_hyperechoic(self):
        """Test EU-TIRADS 3: Hyperechoic without suspicious features."""
        findings = {
            'composition': 'solid',
            'echogenicity': 'hyperechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
        }
        result = classify_eu_tirads(findings)

        assert result['eu_level'] == 'EU-TIRADS 3'
        assert result['risk_category'] == 'Low risk'

    def test_eu_tirads_4_hypoechoic(self):
        """Test EU-TIRADS 4: Hypoechoic without high-risk features."""
        findings = {
            'composition': 'solid',
            'echogenicity': 'hypoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
        }
        result = classify_eu_tirads(findings)

        assert result['eu_level'] == 'EU-TIRADS 4'
        assert result['risk_category'] == 'Intermediate risk'

    def test_eu_tirads_5_taller_than_wide(self):
        """Test EU-TIRADS 5: Taller-than-wide shape (high-risk feature)."""
        findings = {
            'composition': 'solid',
            'echogenicity': 'isoechoic',
            'shape': 'taller_than_wide',
            'margin': 'smooth',
            'echogenic_foci': 'none',
        }
        result = classify_eu_tirads(findings)

        assert result['eu_level'] == 'EU-TIRADS 5'
        assert result['risk_category'] == 'High risk'
        assert 'Taller-than-wide shape' in result['high_suspicious_features']

    def test_eu_tirads_5_irregular_margin(self):
        """Test EU-TIRADS 5: Irregular margin (high-risk feature)."""
        findings = {
            'composition': 'solid',
            'echogenicity': 'isoechoic',
            'shape': 'wider_than_tall',
            'margin': 'irregular',
            'echogenic_foci': 'none',
        }
        result = classify_eu_tirads(findings)

        assert result['eu_level'] == 'EU-TIRADS 5'
        assert result['risk_category'] == 'High risk'

    def test_eu_tirads_5_microcalcifications(self):
        """Test EU-TIRADS 5: Microcalcifications (high-risk feature)."""
        findings = {
            'composition': 'solid',
            'echogenicity': 'isoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'microcalcifications',
        }
        result = classify_eu_tirads(findings)

        assert result['eu_level'] == 'EU-TIRADS 5'
        assert result['risk_category'] == 'High risk'
        assert 'Microcalcifications' in result['high_suspicious_features']

    def test_eu_tirads_5_marked_hypoechoic(self):
        """Test EU-TIRADS 5: Marked hypoechogenicity (high-risk feature)."""
        findings = {
            'composition': 'solid',
            'echogenicity': 'markedly_hypoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
        }
        result = classify_eu_tirads(findings)

        assert result['eu_level'] == 'EU-TIRADS 5'
        assert result['risk_category'] == 'High risk'
        assert 'Marked hypoechogenicity' in result['high_suspicious_features']

    def test_eu_tirads_5_with_adenopathy(self):
        """Test EU-TIRADS 5: Suspicious lymphadenopathy."""
        findings = {
            'composition': 'solid',
            'echogenicity': 'isoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
            'has_adenopathy': True,
        }
        result = classify_eu_tirads(findings)

        assert result['eu_level'] == 'EU-TIRADS 5'
        assert 'Suspicious lymphadenopathy' in result['high_suspicious_features']

    def test_malignancy_risk_included(self):
        """Test that malignancy risk is included in result."""
        findings = {
            'composition': 'solid',
            'echogenicity': 'isoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
        }
        result = classify_eu_tirads(findings)

        assert 'malignancy_risk' in result
        assert result['malignancy_risk'] == '2-4%'  # EU-TIRADS 3
