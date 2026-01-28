"""
Tests for the Thyroid API endpoints.
"""

import pytest
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status


class TestHealthEndpoint(TestCase):
    """Test the health check endpoint."""

    def setUp(self):
        self.client = APIClient()

    def test_health_endpoint_returns_200(self):
        """Test GET /api/health/ returns 200 OK."""
        response = self.client.get('/api/health/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'healthy'
        assert 'vectorstore_ready' in response.data


class TestNoduleEvaluationEndpoint(TestCase):
    """Test the nodule evaluation endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'composition': 'solid',
            'echogenicity': 'hypoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
            'size': {
                'mode': '3d',
                'a_mm': 12,
                'b_mm': 10,
                'c_mm': 9,
            },
        }

    def test_evaluate_endpoint_returns_200(self):
        """Test POST /api/nodule/evaluate/ returns 200 OK."""
        response = self.client.post(
            '/api/nodule/evaluate/',
            self.valid_payload,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK

    def test_evaluate_returns_acr_result(self):
        """Test evaluate endpoint returns ACR TI-RADS result."""
        response = self.client.post(
            '/api/nodule/evaluate/',
            self.valid_payload,
            format='json'
        )

        assert 'acr' in response.data
        assert 'points' in response.data['acr']
        assert 'tr_level' in response.data['acr']
        assert 'description' in response.data['acr']

    def test_evaluate_returns_eu_result(self):
        """Test evaluate endpoint returns EU-TIRADS result."""
        response = self.client.post(
            '/api/nodule/evaluate/',
            self.valid_payload,
            format='json'
        )

        assert 'eu' in response.data
        assert 'eu_level' in response.data['eu']
        assert 'risk_category' in response.data['eu']

    def test_evaluate_returns_size_result(self):
        """Test evaluate endpoint returns size calculations."""
        response = self.client.post(
            '/api/nodule/evaluate/',
            self.valid_payload,
            format='json'
        )

        assert 'size' in response.data
        assert response.data['size']['max_dimension_mm'] == 12
        assert response.data['size']['volume_mm3'] is not None

    def test_evaluate_returns_recommendation(self):
        """Test evaluate endpoint returns recommendation."""
        response = self.client.post(
            '/api/nodule/evaluate/',
            self.valid_payload,
            format='json'
        )

        assert 'recommendation' in response.data
        assert 'action' in response.data['recommendation']
        assert 'label_tr' in response.data['recommendation']

    def test_evaluate_tr4_12mm_fna_recommendation(self):
        """Test TR4 nodule with 12mm size gets FNA recommendation."""
        # solid=2 + hypoechoic=2 = 4 points = TR4
        # TR4 FNA threshold is 15mm, so 12mm should be follow-up
        payload = {
            'composition': 'solid',
            'echogenicity': 'hypoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
            'size': {
                'mode': '2d',
                'a_mm': 12,
            },
        }
        response = self.client.post(
            '/api/nodule/evaluate/',
            payload,
            format='json'
        )

        assert response.data['acr']['tr_level'] == 'TR4'
        assert response.data['recommendation']['action'] == 'follow_up'

    def test_evaluate_tr4_15mm_fna_recommendation(self):
        """Test TR4 nodule with 15mm size gets FNA recommendation."""
        payload = {
            'composition': 'solid',
            'echogenicity': 'hypoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
            'size': {
                'mode': '2d',
                'a_mm': 15,
            },
        }
        response = self.client.post(
            '/api/nodule/evaluate/',
            payload,
            format='json'
        )

        assert response.data['acr']['tr_level'] == 'TR4'
        assert response.data['recommendation']['action'] == 'fna'

    def test_evaluate_tr4_8mm_no_action(self):
        """Test TR4 nodule with 8mm size gets no action recommendation."""
        payload = {
            'composition': 'solid',
            'echogenicity': 'hypoechoic',
            'shape': 'wider_than_tall',
            'margin': 'smooth',
            'echogenic_foci': 'none',
            'size': {
                'mode': '2d',
                'a_mm': 8,
            },
        }
        response = self.client.post(
            '/api/nodule/evaluate/',
            payload,
            format='json'
        )

        assert response.data['acr']['tr_level'] == 'TR4'
        assert response.data['recommendation']['action'] == 'no_action'

    def test_evaluate_returns_treatment_options(self):
        """Test evaluate endpoint returns treatment options."""
        response = self.client.post(
            '/api/nodule/evaluate/',
            self.valid_payload,
            format='json'
        )

        assert 'treatment_options' in response.data
        assert 'surgical' in response.data['treatment_options']
        assert 'non_surgical' in response.data['treatment_options']

    def test_evaluate_with_clinical_info(self):
        """Test evaluate endpoint with clinical information."""
        payload = self.valid_payload.copy()
        payload['clinical'] = {
            'age': 45,
            'sex': 'female',
            'family_history': True,
            'radiation_history': False,
        }

        response = self.client.post(
            '/api/nodule/evaluate/',
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK
        assert 'input_echo' in response.data
        assert response.data['input_echo']['clinical']['family_history'] is True

    def test_evaluate_missing_required_field(self):
        """Test evaluate endpoint with missing required field returns 400."""
        payload = self.valid_payload.copy()
        del payload['size']

        response = self.client.post(
            '/api/nodule/evaluate/',
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_evaluate_invalid_composition(self):
        """Test evaluate endpoint with invalid composition returns 400."""
        payload = self.valid_payload.copy()
        payload['composition'] = 'invalid_value'

        response = self.client.post(
            '/api/nodule/evaluate/',
            payload,
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_evaluate_returns_sources(self):
        """Test evaluate endpoint returns sources list."""
        response = self.client.post(
            '/api/nodule/evaluate/',
            self.valid_payload,
            format='json'
        )

        assert 'sources' in response.data
        assert isinstance(response.data['sources'], list)
