"""
Views for the Thyroid Nodule Evaluation API.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    NoduleEvaluationRequestSerializer,
    NoduleEvaluationResponseSerializer,
    HealthCheckResponseSerializer
)
from .rules import (
    calculate_acr_tirads,
    classify_eu_tirads,
    calculate_size,
    get_recommendation
)
from .rules.recommendations import get_treatment_options
from .rag.vectorstore import get_vectorstore
from .rag.llm_response import generate_llm_response, generate_tr_guideline_summary


class HealthCheckView(APIView):
    """API health check endpoint."""

    def get(self, request):
        """
        GET /api/health/

        Returns system health status. Lightweight — does not
        initialize heavy dependencies like ChromaDB.
        """
        response_data = {
            'status': 'healthy',
            'vectorstore_ready': False,
            'vectorstore_count': 0
        }

        # Only check vectorstore if already initialized (avoid cold start)
        from .rag.vectorstore import _vectorstore_instance
        if _vectorstore_instance is not None:
            try:
                response_data['vectorstore_ready'] = _vectorstore_instance.is_ready()
                response_data['vectorstore_count'] = _vectorstore_instance.count()
            except Exception:
                pass

        serializer = HealthCheckResponseSerializer(data=response_data)
        serializer.is_valid()

        return Response(serializer.data, status=status.HTTP_200_OK)


class NoduleEvaluationView(APIView):
    """Thyroid nodule evaluation endpoint."""

    def post(self, request):
        """
        POST /api/nodule/evaluate/

        Evaluate a thyroid nodule using ACR TI-RADS and EU-TIRADS.
        Returns classification, recommendations, and RAG-based explanation.
        """
        # Validate input
        serializer = NoduleEvaluationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

        validated_data = serializer.validated_data

        # Extract nodule characteristics
        nodule_characteristics = {
            'composition': validated_data['composition'],
            'echogenicity': validated_data['echogenicity'],
            'shape': validated_data['shape'],
            'margin': validated_data['margin'],
            'echogenic_foci': validated_data['echogenic_foci'],
        }

        # Calculate size
        size_input = validated_data['size']
        size_result = calculate_size(size_input)

        # Calculate ACR TI-RADS
        acr_result = calculate_acr_tirads(nodule_characteristics)

        # Classify EU-TIRADS
        # Add additional fields for EU-TIRADS
        eu_input = nodule_characteristics.copy()
        eu_input['is_simple_cyst'] = (
            validated_data['composition'] == 'cystic' and
            validated_data['echogenicity'] == 'anechoic'
        )
        eu_input['is_spongiform'] = validated_data['composition'] == 'spongiform'
        eu_result = classify_eu_tirads(eu_input)

        # Get recommendation
        clinical_data = validated_data.get('clinical', {})
        clinical_risk_factors = []
        if clinical_data.get('family_history'):
            clinical_risk_factors.append('family_history')
        if clinical_data.get('radiation_history'):
            clinical_risk_factors.append('radiation_history')

        recommendation_input = {
            'tr_level': acr_result['tr_level'],
            'max_dimension_mm': size_result['max_dimension_mm'],
            'clinical_risk_factors': clinical_risk_factors if clinical_risk_factors else None
        }
        recommendation = get_recommendation(recommendation_input)

        # Get treatment options
        treatment_options = get_treatment_options(
            acr_result['tr_level'],
            recommendation['action']
        )

        # Generate TR guideline summary
        tr_guideline_summary = generate_tr_guideline_summary(
            acr_result['tr_level'],
            recommendation['action']
        )

        # Generate LLM explanation
        llm_response = generate_llm_response(
            tr_level=acr_result['tr_level'],
            eu_level=eu_result['eu_level'],
            action=recommendation['action'],
            nodule_characteristics=nodule_characteristics,
            size_info=size_result,
            clinical_info=clinical_data if clinical_data else None
        )

        # Build response
        response_data = {
            'input_echo': validated_data,
            'acr': acr_result,
            'eu': eu_result,
            'tr_guideline': {
                'summary': tr_guideline_summary
            },
            'size': size_result,
            'recommendation': recommendation,
            'treatment_options': treatment_options,
            'llm_explanation': llm_response['llm_explanation'],
            'sources': llm_response['sources']
        }

        return Response(response_data, status=status.HTTP_200_OK)
