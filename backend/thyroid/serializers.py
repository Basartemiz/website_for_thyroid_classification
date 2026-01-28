"""
Serializers for the Thyroid Nodule Evaluation API.
"""

from rest_framework import serializers


class SizeInputSerializer(serializers.Serializer):
    """Serializer for nodule size input."""
    mode = serializers.ChoiceField(
        choices=['2d', '3d'],
        default='2d'
    )
    a_mm = serializers.FloatField(min_value=0, required=True)
    b_mm = serializers.FloatField(min_value=0, required=False, allow_null=True)
    c_mm = serializers.FloatField(min_value=0, required=False, allow_null=True)


class ClinicalInputSerializer(serializers.Serializer):
    """Serializer for clinical information."""
    age = serializers.IntegerField(min_value=0, max_value=150, required=False)
    sex = serializers.ChoiceField(
        choices=['male', 'female', 'other'],
        required=False
    )
    family_history = serializers.BooleanField(default=False, required=False)
    family_history_detail = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        allow_null=True
    )
    radiation_history = serializers.BooleanField(default=False, required=False)
    radiation_history_detail = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        allow_null=True
    )


class NoduleEvaluationRequestSerializer(serializers.Serializer):
    """Serializer for nodule evaluation request."""
    # Composition
    composition = serializers.ChoiceField(
        choices=[
            'cystic',
            'spongiform',
            'mixed_cystic_solid',
            'solid',
            'almost_solid'
        ],
        default='solid'
    )

    # Echogenicity
    echogenicity = serializers.ChoiceField(
        choices=[
            'anechoic',
            'hyperechoic',
            'isoechoic',
            'hypoechoic',
            'very_hypoechoic',
            'moderately_hypoechoic',
            'markedly_hypoechoic'
        ],
        default='isoechoic'
    )

    # Shape
    shape = serializers.ChoiceField(
        choices=['wider_than_tall', 'taller_than_wide'],
        default='wider_than_tall'
    )

    # Margin
    margin = serializers.ChoiceField(
        choices=[
            'smooth',
            'ill_defined',
            'lobulated',
            'irregular',
            'microlobulated',
            'extrathyroidal_extension'
        ],
        default='smooth'
    )

    # Echogenic Foci
    echogenic_foci = serializers.ChoiceField(
        choices=[
            'none',
            'large_comet_tail',
            'macrocalcifications',
            'peripheral_calcifications',
            'punctate_echogenic_foci',
            'microcalcifications'
        ],
        default='none'
    )

    # Size
    size = SizeInputSerializer(required=True)

    # Clinical info
    clinical = ClinicalInputSerializer(required=False)


class SourceSerializer(serializers.Serializer):
    """Serializer for RAG source citations."""
    doc_id = serializers.CharField()
    page = serializers.IntegerField()
    chunk_id = serializers.CharField()
    excerpt = serializers.CharField()


class ACRResultSerializer(serializers.Serializer):
    """Serializer for ACR TI-RADS result."""
    points = serializers.IntegerField()
    tr_level = serializers.CharField()
    description = serializers.CharField()
    point_breakdown = serializers.DictField(required=False)


class EUResultSerializer(serializers.Serializer):
    """Serializer for EU-TIRADS result."""
    eu_level = serializers.CharField()
    risk_category = serializers.CharField()
    malignancy_risk = serializers.CharField()
    high_suspicious_features = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )


class SizeResultSerializer(serializers.Serializer):
    """Serializer for size calculation result."""
    mode = serializers.CharField()
    a_mm = serializers.FloatField()
    b_mm = serializers.FloatField(allow_null=True)
    c_mm = serializers.FloatField(allow_null=True)
    volume_mm3 = serializers.FloatField(allow_null=True)
    max_dimension_mm = serializers.FloatField()


class RecommendationSerializer(serializers.Serializer):
    """Serializer for management recommendation."""
    action = serializers.CharField()
    label_tr = serializers.CharField()
    label_en = serializers.CharField()
    rationale = serializers.CharField()
    rationale_tr = serializers.CharField()


class TreatmentOptionsSerializer(serializers.Serializer):
    """Serializer for treatment options."""
    surgical = serializers.ListField(child=serializers.CharField())
    non_surgical = serializers.ListField(child=serializers.CharField())


class LLMExplanationSerializer(serializers.Serializer):
    """Serializer for guideline-specific LLM explanations."""
    tr = serializers.CharField()
    us = serializers.CharField()
    eu = serializers.CharField()


class NoduleEvaluationResponseSerializer(serializers.Serializer):
    """Serializer for complete evaluation response."""
    input_echo = serializers.DictField()
    acr = ACRResultSerializer()
    eu = EUResultSerializer()
    tr_guideline = serializers.DictField()
    size = SizeResultSerializer()
    recommendation = RecommendationSerializer()
    treatment_options = TreatmentOptionsSerializer()
    llm_explanation = LLMExplanationSerializer()
    sources = SourceSerializer(many=True)


class HealthCheckResponseSerializer(serializers.Serializer):
    """Serializer for health check response."""
    status = serializers.CharField()
    vectorstore_ready = serializers.BooleanField()
    vectorstore_count = serializers.IntegerField(required=False)
