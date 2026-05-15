import re
import sys
from typing import Dict, Tuple
from collections import Counter
from text_utils import register_command, get_registry

# ============================================================================
# Text Analyzer Functions
# ============================================================================

def count_syllables(word: str) -> int:
    """
    Approssima il conteggio delle sillabe in una parola (per l'italiano).
    Regole semplificate:
    - Ogni vocale (a, e, i, o, u) conta come una sillaba.
    - Le vocali consecutive contano come una sola sillaba.
    - Le vocali finali "e" e "i" non contano come sillabe (es. "cane" -> 2 sillabe).
    """
    word = word.lower()
    vowels = "aeiou"
    syllable_count = 0
    prev_char_was_vowel = False

    for char in word:
        if char in vowels:
            if not prev_char_was_vowel:
                syllable_count += 1
            prev_char_was_vowel = True
        else:
            prev_char_was_vowel = False

    # Regola per le vocali finali "e" e "i"
    if len(word) > 1 and word[-1] in "ei":
        syllable_count -= 1

    return max(1, syllable_count)  # Ogni parola ha almeno una sillaba

def calculate_flesch_reading_ease(text: str) -> float:
    """
    Calcola l'indice di leggibilità Flesch (per l'inglese).
    Formula: 206.835 - 1.015 * (parole/totale_frasi) - 84.6 * (sillabe/parole)
    Risultato:
    - 90-100: Molto facile (es. fumetti)
    - 60-70: Facile (es. romanzi)
    - 30-50: Difficile (es. articoli accademici)
    - 0-30: Molto difficile (es. documenti legali)
    """
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return 0.0

    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0

    total_words = len(words)
    total_sentences = len(sentences)
    total_syllables = sum(count_syllables(word) for word in words)

    if total_sentences == 0:
        return 0.0

    asl = total_words / total_sentences  # Average sentence length
    asw = total_syllables / total_words  # Average syllables per word

    flesch_score = 206.835 - (1.015 * asl) - (84.6 * asw)
    return round(flesch_score, 2)

def calculate_gulpease_index(text: str) -> float:
    """
    Calcola l'indice di leggibilità Gulpease (per l'italiano).
    Formula: 89 + (300 * numero_frasi - 10 * numero_lettere) / numero_parole
    Risultato:
    - > 80: Molto facile
    - 60-80: Facile
    - 40-60: Medio
    - < 40: Difficile
    """
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return 0.0

    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0

    total_words = len(words)
    total_sentences = len(sentences)
    total_letters = sum(len(word) for word in words)

    if total_words == 0:
        return 0.0

    gulpease_score = 89 + (300 * total_sentences - 10 * total_letters) / total_words
    return round(gulpease_score, 2)

def calculate_lexical_diversity(text: str) -> float:
    """
    Calcola la complessità lessicale (rapporto parole uniche/totale parole).
    Risultato:
    - 0.0: Tutte le parole sono ripetute (bassa diversità)
    - 1.0: Tutte le parole sono uniche (alta diversità)
    """
    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return 0.0
    unique_words = set(words)
    return round(len(unique_words) / len(words), 2)

def analyze_text(text: str) -> Dict:
    """
    Analizza il testo e restituisce un dizionario con tutte le metriche.
    """
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    words = re.findall(r'\b\w+\b', text.lower())
    if not words:
        return {
            "error": "Nessun testo valido trovato."
        }

    total_words = len(words)
    total_sentences = len(sentences)
    total_chars = len(text)
    total_syllables = sum(count_syllables(word) for word in words)
    avg_word_length = sum(len(word) for word in words) / total_words
    avg_sentence_length = total_words / total_sentences if total_sentences > 0 else 0
    lexical_diversity = calculate_lexical_diversity(text)
    flesch_score = calculate_flesch_reading_ease(text)
    gulpease_score = calculate_gulpease_index(text)

    return {
        "statistiche": {
            "caratteri": total_chars,
            "parole": total_words,
            "frasi": total_sentences,
            "sillabe": total_syllables,
        },
        "metriche": {
            "lunghezza_media_parole": round(avg_word_length, 2),
            "lunghezza_media_frasi": round(avg_sentence_length, 2),
            "complessita_lessicale": lexical_diversity,
        },
        "indici_leggibilita": {
            "flesch": flesch_score,
            "gulpease": gulpease_score,
        },
        "interpretazione": {
            "flesch": (
                "Molto facile (90-100)" if flesch_score >= 90 else
                "Facile (60-89)" if flesch_score >= 60 else
                "Difficile (30-59)" if flesch_score >= 30 else
                "Molto difficile (0-29)"
            ),
            "gulpease": (
                "Molto facile (>80)" if gulpease_score > 80 else
                "Facile (60-80)" if gulpease_score >= 60 else
                "Medio (40-59)" if gulpease_score >= 40 else
                "Difficile (<40)"
            ),
        },
    }

@register_command('analyze', 'Analizza leggibilità e complessità del testo (Flesch, Gulpease, ecc.)')
def analyze_command(text: str) -> str:
    """
    Analizza il testo e restituisce un report dettagliato su leggibilità e complessità.
    """
    if not text.strip():
        return "❌ Errore: Testo vuoto."

    analysis = analyze_text(text)

    if "error" in analysis:
        return f"❌ {analysis['error']}"

    stats = analysis["statistiche"]
    metrics = analysis["metriche"]
    readability = analysis["indici_leggibilita"]
    interpretation = analysis["interpretazione"]

    report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                  📊 ANALISI TESTO - TEXT ANALYZER               ║
╚══════════════════════════════════════════════════════════════════════╝

📌 **Statistiche di base:**
  • Caratteri:       {stats['caratteri']:,}
  • Parole:          {stats['parole']:,}
  • Frasi:           {stats['frasi']:,}
  • Sillabe:         {stats['sillabe']:,}

---
📈 **Metriche avanzate:**
  • Lunghezza media parole:    {metrics['lunghezza_media_parole']} caratteri
  • Lunghezza media frasi:     {metrics['lunghezza_media_frasi']} parole
  • Complessità lessicale:     {metrics['complessita_lessicale']*100:.1f}% (unicità parole)

---
🔍 **Indici di leggibilità:**
  • **Flesch (EN):**  {readability['flesch']} → {interpretation['flesch']}
  • **Gulpease (IT):** {readability['gulpease']} → {interpretation['gulpease']}

---
💡 **Suggerimenti:**
  • Se il punteggio **Flesch** è < 60, il testo potrebbe essere difficile per un pubblico generale.
  • Se il punteggio **Gulpease** è < 40, il testo è complesso (adatto a lettori esperti).
  • Una **complessità lessicale** > 0.7 indica un testo vario e ricco di vocaboli.
"""

    return report

# ============================================================================
# Integration with text_utils.py
# ============================================================================

# Assicurati che il comando sia registrato nel registry globale
_registry = get_registry()
if not _registry.exists('analyze'):
    _registry.register('analyze', 'Analizza leggibilità e complessità del testo')('analyze_command')
