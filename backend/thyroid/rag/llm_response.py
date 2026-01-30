"""
LLM response generation for RAG pipeline.
"""

from typing import Dict, Any, List, Optional
import openai
from django.conf import settings

from .retriever import retrieve_chunks, format_chunks_for_context


SYSTEM_PROMPT_TR = """Sen tiroid nodüllerini değerlendiren uzman bir endokrinoloji ve radyoloji asistanısın.
Kılavuzlara dayalı, bilimsel ve profesyonel bir şekilde yanıt vermelisin.

Yanıtlarında:
1. Türkçe tıbbi terminoloji kullan
2. Kılavuz referanslarına atıfta bulun
3. Klinik karar vermeye yardımcı ol
4. Açık ve anlaşılır ol
5. Kısa ve öz yanıtlar ver, gereksiz detaylardan kaçın
6. Sadece verilen nodülün değerlendirmesiyle doğrudan ilgili bilgileri sun

Verilen bağlam bilgilerini kullanarak soruları yanıtla.
Bağlamda olmayan bilgiler için "Bu konuda kılavuzlarda yeterli bilgi bulunmamaktadır" de.
Her kılavuz bölümünü en fazla 3-4 cümle ile sınırla. Genel tiroid bilgisi değil, spesifik olarak bu nodüle özgü değerlendirme yap."""


def retrieve_guideline_chunks(
    query: str,
    tr_level: str,
    action: str,
    nodule_characteristics: Dict[str, Any],
    guideline_filter: str,
    top_k: int = 3
) -> List[Dict[str, Any]]:
    """
    Retrieve chunks filtered by guideline type.

    Args:
        query: Base query string
        tr_level: TI-RADS classification level
        action: Recommended action
        nodule_characteristics: Nodule features
        guideline_filter: Filter keyword ('turkey', 'acr'/'american', 'eu'/'european')
        top_k: Number of chunks to retrieve

    Returns:
        List of filtered chunks
    """
    chunks = retrieve_chunks(
        query=query,
        tr_level=tr_level,
        action=action,
        nodule_characteristics=nodule_characteristics,
        top_k=top_k * 2  # Retrieve more to allow filtering
    )

    # Filter by guideline
    if guideline_filter == 'turkey':
        filtered = [c for c in chunks if 'turkey' in c['doc_id'].lower()]
    elif guideline_filter in ['acr', 'american']:
        filtered = [c for c in chunks if 'acr' in c['doc_id'].lower() or 'america' in c['doc_id'].lower()]
    elif guideline_filter in ['eu', 'european']:
        filtered = [c for c in chunks if 'eu' in c['doc_id'].lower() or 'europe' in c['doc_id'].lower()]
    else:
        filtered = chunks

    return filtered[:top_k]


def generate_llm_response(
    tr_level: str,
    eu_level: str,
    action: str,
    nodule_characteristics: Dict[str, Any],
    size_info: Dict[str, Any],
    clinical_info: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Generate LLM explanations based on the evaluation results.

    Produces 3 separate guideline-specific answers (TR, US/ACR, EU).

    Args:
        tr_level: ACR TI-RADS level
        eu_level: EU-TIRADS level
        action: Recommended action
        nodule_characteristics: Ultrasound findings
        size_info: Size measurements
        clinical_info: Clinical information (age, sex, history)

    Returns:
        Dictionary with 'llm_explanation' containing tr/us/eu keys and 'sources' list
    """
    if not settings.OPENAI_API_KEY:
        return {
            'llm_explanation': {
                'tr': 'OpenAI API anahtarı yapılandırılmamış.',
                'us': 'OpenAI API anahtarı yapılandırılmamış.',
                'eu': 'OpenAI API anahtarı yapılandırılmamış.',
            },
            'sources': []
        }

    # Build base query for retrieval
    base_query = f"""
    Tiroid nodülü değerlendirmesi:
    - ACR TI-RADS: {tr_level}
    - EU-TIRADS: {eu_level}
    - Önerilen eylem: {action}
    - Nodül özellikleri: {nodule_characteristics}
    - Boyut: {size_info}
    """

    # Retrieve chunks for each guideline
    tr_chunks = retrieve_guideline_chunks(
        query=base_query,
        tr_level=tr_level,
        action=action,
        nodule_characteristics=nodule_characteristics,
        guideline_filter='turkey',
        top_k=5
    )

    us_chunks = retrieve_guideline_chunks(
        query=base_query,
        tr_level=tr_level,
        action=action,
        nodule_characteristics=nodule_characteristics,
        guideline_filter='acr',
        top_k=3
    )

    eu_chunks = retrieve_guideline_chunks(
        query=base_query,
        tr_level=tr_level,
        action=action,
        nodule_characteristics=nodule_characteristics,
        guideline_filter='eu',
        top_k=3
    )

    # Format context for each guideline
    tr_context = format_chunks_for_context(tr_chunks)
    us_context = format_chunks_for_context(us_chunks)
    eu_context = format_chunks_for_context(eu_chunks)

    # Build clinical info string
    clinical_str = ""
    if clinical_info:
        clinical_parts = []
        if clinical_info.get('age'):
            clinical_parts.append(f"Yaş: {clinical_info['age']}")
        if clinical_info.get('sex'):
            sex_map = {'male': 'Erkek', 'female': 'Kadın', 'other': 'Diğer'}
            clinical_parts.append(f"Cinsiyet: {sex_map.get(clinical_info['sex'], clinical_info['sex'])}")
        if clinical_info.get('family_history'):
            detail = clinical_info.get('family_history_detail', '')
            if detail:
                clinical_parts.append(f"Aile öyküsü: Var - {detail}")
            else:
                clinical_parts.append("Aile öyküsü: Var")
        if clinical_info.get('radiation_history'):
            detail = clinical_info.get('radiation_history_detail', '')
            if detail:
                clinical_parts.append(f"Radyasyon öyküsü: Var - {detail}")
            else:
                clinical_parts.append("Radyasyon öyküsü: Var")
        if clinical_parts:
            clinical_str = "\n**Klinik Bilgiler:**\n" + "\n".join(f"- {p}" for p in clinical_parts)

    # Build user prompt
    user_prompt = f"""Aşağıdaki tiroid nodülü değerlendirmesi için 3 farklı kılavuza dayalı ayrı ayrı açıklamalar yap:

**Nodül Bilgileri:**
- ACR TI-RADS: {tr_level}
- EU-TIRADS: {eu_level}
- Kompozisyon: {nodule_characteristics.get('composition', 'Belirtilmemiş')}
- Ekojenite: {nodule_characteristics.get('echogenicity', 'Belirtilmemiş')}
- Şekil: {nodule_characteristics.get('shape', 'Belirtilmemiş')}
- Kenar: {nodule_characteristics.get('margin', 'Belirtilmemiş')}
- Ekojenik odaklar: {nodule_characteristics.get('echogenic_foci', 'Belirtilmemiş')}
- Maksimum boyut: {size_info.get('max_dimension_mm', 'Belirtilmemiş')} mm
- Önerilen Eylem: {action}
{clinical_str}

**Kılavuz Bilgileri:**

TR Kılavuzu:
{tr_context if tr_context else "Türkiye kılavuzundan ilgili bilgi bulunamadı."}

US (ACR) Kılavuzu:
{us_context if us_context else "ACR kılavuzundan ilgili bilgi bulunamadı."}

EU Kılavuzu:
{eu_context if eu_context else "EU kılavuzundan ilgili bilgi bulunamadı."}

Lütfen her kılavuz için AYRI bir değerlendirme yap. Her bölüm en fazla 3-4 cümle olsun.
Genel bilgi verme, sadece bu nodülün değerlendirilmesiyle ilgili spesifik bilgileri yaz.
Yanıtını şu formatta ver:

### TR Kılavuzuna Göre:
[Türkiye kılavuzuna dayalı açıklama]

### US (ACR TI-RADS) Kılavuzuna Göre:
[ACR TI-RADS kılavuzuna dayalı açıklama]

### EU-TIRADS Kılavuzuna Göre:
[EU-TIRADS kılavuzuna dayalı açıklama]"""

    try:
        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        response = client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_TR},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_completion_tokens=1200
        )

        full_explanation = response.choices[0].message.content

        # Parse the response into 3 sections
        llm_explanation = parse_guideline_sections(full_explanation)

        # Combine all sources
        all_chunks = tr_chunks + us_chunks + eu_chunks
        sources = [
            {
                'doc_id': chunk['doc_id'],
                'page': chunk['page'],
                'chunk_id': chunk['chunk_id'],
                'excerpt': chunk['excerpt']
            }
            for chunk in all_chunks
        ]

        return {
            'llm_explanation': llm_explanation,
            'sources': sources
        }

    except Exception as e:
        error_msg = f'LLM yanıtı oluşturulurken hata: {str(e)}'
        return {
            'llm_explanation': {
                'tr': error_msg,
                'us': error_msg,
                'eu': error_msg,
            },
            'sources': []
        }


def parse_guideline_sections(full_text: str) -> Dict[str, str]:
    """
    Parse the LLM response into TR, US, and EU sections.

    Args:
        full_text: Full LLM response text

    Returns:
        Dictionary with 'tr', 'us', 'eu' keys
    """
    result = {
        'tr': '',
        'us': '',
        'eu': ''
    }

    # Define section markers
    tr_markers = ['### TR Kılavuzuna Göre:', '### TR Kılavuzu:', '**TR Kılavuzuna Göre:**']
    us_markers = ['### US (ACR TI-RADS) Kılavuzuna Göre:', '### US (ACR) Kılavuzu:', '### ACR TI-RADS', '**US (ACR TI-RADS) Kılavuzuna Göre:**']
    eu_markers = ['### EU-TIRADS Kılavuzuna Göre:', '### EU-TIRADS:', '### EU Kılavuzu:', '**EU-TIRADS Kılavuzuna Göre:**']

    text = full_text

    # Find TR section
    tr_start = -1
    for marker in tr_markers:
        idx = text.find(marker)
        if idx != -1:
            tr_start = idx + len(marker)
            break

    # Find US section
    us_start = -1
    for marker in us_markers:
        idx = text.find(marker)
        if idx != -1:
            us_start = idx + len(marker)
            break

    # Find EU section
    eu_start = -1
    for marker in eu_markers:
        idx = text.find(marker)
        if idx != -1:
            eu_start = idx + len(marker)
            break

    # Extract sections based on positions
    positions = []
    if tr_start != -1:
        positions.append(('tr', tr_start))
    if us_start != -1:
        positions.append(('us', us_start))
    if eu_start != -1:
        positions.append(('eu', eu_start))

    # Sort by position
    positions.sort(key=lambda x: x[1])

    # Extract text for each section
    for i, (key, start) in enumerate(positions):
        if i + 1 < len(positions):
            # Find end (start of next section minus the marker)
            next_key, next_start = positions[i + 1]
            # Find where the next marker actually starts (before the header)
            end = next_start
            # Look backwards to find "###" or "**"
            for j in range(next_start - 1, max(start, next_start - 100), -1):
                if text[j:j+3] == '###' or text[j:j+2] == '**':
                    end = j
                    break
            result[key] = text[start:end].strip()
        else:
            result[key] = text[start:].strip()

    # If parsing failed, put full text in all sections
    if not any(result.values()):
        result = {
            'tr': full_text,
            'us': full_text,
            'eu': full_text
        }

    return result


def generate_tr_guideline_summary(tr_level: str, action: str) -> str:
    """
    Generate a summary from Turkish guidelines (turkey.pdf).

    Args:
        tr_level: TI-RADS level
        action: Recommended action

    Returns:
        Summary string
    """
    if not settings.OPENAI_API_KEY:
        return "RAG sistemi yapılandırılmamış (API anahtarı eksik)."

    try:
        query = f"Türkiye kılavuzu tiroid nodülü {tr_level} {action} yönetim öneri"

        chunks = retrieve_chunks(
            query=query,
            tr_level=tr_level,
            action=action,
            top_k=3
        )

        # Filter for turkey.pdf
        turkey_chunks = [c for c in chunks if 'turkey' in c['doc_id'].lower()]

        if turkey_chunks:
            return " ".join([c['excerpt'] for c in turkey_chunks[:2]])

        return "Türkiye kılavuzundan ilgili bilgi bulunamadı."

    except Exception as e:
        return f"Kılavuz özeti oluşturulurken hata: {str(e)}"
