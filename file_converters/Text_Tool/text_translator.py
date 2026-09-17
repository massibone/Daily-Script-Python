#!/usr/bin/env python3
"""
Text Translator - Rilevamento lingua e traduzione
====================================================
Tool CLI con architettura a plugin (Registry Pattern), coerente con
text_utils.py: i comandi si auto-registrano, il core non va mai
modificato per aggiungerne di nuovi.

Dipendenze:
    pip install langdetect deep-translator

Uso:
    python text_translator.py detect "Ciao, come stai?"
    python text_translator.py translate "Ciao, come stai?" --to en
    python text_translator.py translate "Hello" --from en --to it
    python text_translator.py languages
    python text_translator.py list
    python text_translator.py help
"""

import sys
import argparse

try:
    from langdetect import detect, detect_langs, DetectorFactory
    from langdetect.lang_detect_exception import LangDetectException
    DetectorFactory.seed = 0  # risultati deterministici
    _HAS_LANGDETECT = True
except ImportError:
    _HAS_LANGDETECT = False

try:
    from deep_translator import GoogleTranslator
    _HAS_TRANSLATOR = True
except ImportError:
    _HAS_TRANSLATOR = False


# ---------------------------------------------------------------------------
# Registry Pattern (stesso approccio di text_utils.py)
# ---------------------------------------------------------------------------
COMMANDS = {}


def register_command(name, description):
    """Decorator per auto-registrare un comando nel registry."""
    def wrapper(func):
        COMMANDS[name] = {"func": func, "description": description}
        return func
    return wrapper


# Nomi leggibili per i codici lingua più comuni (ISO 639-1)
LANGUAGE_NAMES = {
    "it": "Italiano", "en": "Inglese", "fr": "Francese", "de": "Tedesco",
    "es": "Spagnolo", "pt": "Portoghese", "nl": "Olandese", "ru": "Russo",
    "zh-cn": "Cinese (semplificato)", "ja": "Giapponese", "ko": "Coreano",
    "ar": "Arabo", "pl": "Polacco", "tr": "Turco", "sv": "Svedese",
    "el": "Greco", "ro": "Rumeno", "cs": "Ceco", "hu": "Ungherese",
    "da": "Danese", "fi": "Finlandese", "no": "Norvegese", "uk": "Ucraino",
    "hi": "Hindi", "bg": "Bulgaro",
}


def _box(title):
    line = "═" * 65
    print(f"\n╔{line}╗")
    print(f"║{title.center(65)}║")
    print(f"╚{line}╝\n")


def _require(flag, package_name):
    if not flag:
        print(f"⚠️  Libreria mancante. Installa con:\n    pip install {package_name}")
        sys.exit(1)


# ---------------------------------------------------------------------------
# Comandi
# ---------------------------------------------------------------------------
@register_command("detect", "Rileva la lingua di un testo")
def cmd_detect(text, **_):
    _require(_HAS_LANGDETECT, "langdetect")
    _box("Rilevamento Lingua")
    try:
        primary = detect(text)
        candidates = detect_langs(text)
    except LangDetectException:
        print("❌ Impossibile rilevare la lingua (testo troppo corto o ambiguo).")
        return

    name = LANGUAGE_NAMES.get(primary, primary)
    print(f"  🌍 Lingua rilevata:   {name} ({primary})")
    print(f"  📊 Affidabilità:")
    for c in candidates[:3]:
        bar = "█" * int(c.prob * 20)
        print(f"       {c.lang:6s} {bar:<20s} {c.prob * 100:5.1f}%")
    print()


@register_command("translate", "Traduce un testo in un'altra lingua")
def cmd_translate(text, source="auto", target="en", **_):
    _require(_HAS_TRANSLATOR, "deep-translator")
    _box("Traduzione")

    detected_note = ""
    if source == "auto" and _HAS_LANGDETECT:
        try:
            src_code = detect(text)
            detected_note = f" (rilevata: {LANGUAGE_NAMES.get(src_code, src_code)})"
        except LangDetectException:
            pass

    try:
        result = GoogleTranslator(source=source, target=target).translate(text)
    except Exception as e:
        print(f"❌ Errore durante la traduzione: {e}")
        print("   Verifica la connessione internet e i codici lingua usati.")
        return

    src_name = LANGUAGE_NAMES.get(source, source) if source != "auto" else f"auto{detected_note}"
    tgt_name = LANGUAGE_NAMES.get(target, target)

    print(f"  📥 Originale [{src_name}]:")
    print(f"     {text}")
    print(f"  📤 Tradotto  [{tgt_name}]:")
    print(f"     {result}")
    print()


@register_command("languages", "Elenca i codici lingua supportati")
def cmd_languages(**_):
    _box("Lingue Supportate")
    for code, name in sorted(LANGUAGE_NAMES.items(), key=lambda x: x[1]):
        print(f"  {code:8s} → {name}")
    print("\n  ℹ️  deep-translator supporta molte altre lingue: usa il codice")
    print("     ISO 639-1 anche se non è in questa lista abbreviata.\n")


@register_command("list", "Elenca tutti i comandi disponibili")
def cmd_list(**_):
    _box("Comandi Disponibili")
    for name, info in COMMANDS.items():
        print(f"  🔧 {name:<12s} - {info['description']}")
    print()


@register_command("help", "Mostra la guida d'uso")
def cmd_help(**_):
    print(__doc__)


# ---------------------------------------------------------------------------
# Entry point CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Text Translator - Rilevamento lingua e traduzione",
        add_help=False,
    )
    parser.add_argument("command", nargs="?", default="help", choices=list(COMMANDS.keys()) + ["help"])
    parser.add_argument("text", nargs="?", default=None, help="Testo da analizzare/tradurre")
    parser.add_argument("--from", dest="source", default="auto", help="Codice lingua sorgente (default: auto)")
    parser.add_argument("--to", dest="target", default="en", help="Codice lingua destinazione (default: en)")

    args = parser.parse_args()

    if args.command in ("help", "list", "languages"):
        COMMANDS[args.command]["func"]()
        return

    if not args.text:
        print(f"❌ Il comando '{args.command}' richiede un testo. Esempio:")
        print(f'   python text_translator.py {args.command} "il tuo testo"')
        sys.exit(1)

    COMMANDS[args.command]["func"](text=args.text, source=args.source, target=args.target)


if __name__ == "__main__":
    main()
