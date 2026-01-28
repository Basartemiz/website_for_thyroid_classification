"""
Tests for ACR TI-RADS scoring engine.
"""

import pytest
from thyroid.rules.classification import calculate_acr_tirads, get_tr_level


class TestACRTiradsScoring:
    """Test ACR TI-RADS point calculation."""

    def test_tr1_benign_all_zero_points(self):
        """Test TR1: All benign features should result in 0 points."""
        findings = {
            'composition': 'cystic',
            'echogenicity': 'anechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
        }
        result = calculate_acr_tirads(findings)

        assert result['points'] == 0
        assert result['tr_level'] == 'TR1'
        assert result['description'] == 'Benign'

    def test_tr2_spongiform_nodule(self):
        """Test TR2: Spongiform nodule with 1 point for isoechoic."""
        findings = {
            'composition': 'spongiform',
            'echogenicity': 'isoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
        }
        result = calculate_acr_tirads(findings)

        assert result['points'] == 1  # 0 (spongiform) + 1 (isoechoic)
        assert result['tr_level'] == 'TR2'
        assert result['description'] == 'Not suspicious'

    def test_tr3_solid_hypoechoic(self):
        """Test TR3: Solid + hypoechoic = 4 points -> should be TR4."""
        findings = {
            'composition': 'solid',
            'echogenicity': 'hypoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
        }
        result = calculate_acr_tirads(findings)

        # solid=2, hypoechoic=2, rest=0
        assert result['points'] == 4
        assert result['tr_level'] == 'TR4'
        assert result['description'] == 'Moderately suspicious'

    def test_tr4_moderately_suspicious(self):
        """Test TR4: Moderately suspicious features (4-6 points)."""
        findings = {
            'composition': 'solid',  # 2 points
            'echogenicity': 'isoechoic',  # 1 point
            'shape': 'wider_than_tall',  # 0 points
            'margin': 'lobulated',  # 2 points
            'echogenic_foci': 'none',  # 0 points
        }
        result = calculate_acr_tirads(findings)

        assert result['points'] == 5
        assert result['tr_level'] == 'TR4'
        assert result['description'] == 'Moderately suspicious'

    def test_tr5_highly_suspicious(self):
        """Test TR5: Multiple suspicious features >= 7 points."""
        findings = {
            'composition': 'solid',  # 2 points
            'echogenicity': 'very_hypoechoic',  # 3 points
            'shape': 'taller_than_wide',  # 3 points
            'margin': 'smooth',  # 0 points
            'echogenic_foci': 'none',  # 0 points
        }
        result = calculate_acr_tirads(findings)

        assert result['points'] == 8
        assert result['tr_level'] == 'TR5'
        assert result['description'] == 'Highly suspicious'

    def test_tr5_with_microcalcifications(self):
        """Test TR5 with punctate echogenic foci (microcalcifications)."""
        findings = {
            'composition': 'solid',  # 2 points
            'echogenicity': 'hypoechoic',  # 2 points
            'shape': 'wider_than_tall',  # 0 points
            'margin': 'smooth',  # 0 points
            'echogenic_foci': 'punctate_echogenic_foci',  # 3 points
        }
        result = calculate_acr_tirads(findings)

        assert result['points'] == 7
        assert result['tr_level'] == 'TR5'

    def test_point_breakdown_included(self):
        """Test that point breakdown is included in result."""
        findings = {
            'composition': 'mixed_cystic_solid',
            'echogenicity': 'hyperechoic',
            'shape': 'wider_than_tall',
            'margin': 'ill_defined',
            'echogenic_foci': 'macrocalcifications',
        }
        result = calculate_acr_tirads(findings)

        assert 'point_breakdown' in result
        assert result['point_breakdown']['composition']['points'] == 1
        assert result['point_breakdown']['echogenicity']['points'] == 1
        assert result['point_breakdown']['shape']['points'] == 0
        assert result['point_breakdown']['margin']['points'] == 0
        assert result['point_breakdown']['echogenic_foci']['points'] == 1

    def test_extrathyroidal_extension(self):
        """Test extrathyroidal extension margin (3 points)."""
        findings = {
            'composition': 'solid',  # 2 points
            'echogenicity': 'hypoechoic',  # 2 points
            'shape': 'wider_than_tall',  # 0 points
            'margin': 'extrathyroidal_extension',  # 3 points
            'echogenic_foci': 'none',  # 0 points
        }
        result = calculate_acr_tirads(findings)

        assert result['points'] == 7
        assert result['tr_level'] == 'TR5'


class TestTRLevelMapping:
    """Test TR level mapping function."""

    def test_tr1_zero_points(self):
        assert get_tr_level(0) == 'TR1'

    def test_tr2_one_point(self):
        assert get_tr_level(1) == 'TR2'

    def test_tr2_two_points(self):
        assert get_tr_level(2) == 'TR2'

    def test_tr3_three_points(self):
        assert get_tr_level(3) == 'TR3'

    def test_tr4_four_points(self):
        assert get_tr_level(4) == 'TR4'

    def test_tr4_six_points(self):
        assert get_tr_level(6) == 'TR4'

    def test_tr5_seven_points(self):
        assert get_tr_level(7) == 'TR5'

    def test_tr5_high_points(self):
        assert get_tr_level(10) == 'TR5'
