Text-Utils CLI - Sistema di utilità testo con architettura a plugin

Questo è un tool da riga di comando estendibile che supporta diversi comandi
per manipolare testo. Utilizza un pattern Registry per permettere l'aggiunta
dinamica di nuovi comandi senza modificare il codice principale.

Architettura:
- Registry Pattern: I comandi si auto-registrano usando un decoratore
- Plugin System: Nuovi comandi possono essere aggiunti facilmente
- Estendibilità: Il main script rimane invariato quando si aggiungono comandi

Comandi built-in:
  • count      - Conta caratteri, parole e righe
  • reverse    - Inverte il testo
  • shout      - Converte in MAIUSCOLO
  • whisper    - Converte in minuscolo
  • capitalize - Prima lettera maiuscola di ogni parola
  • summarize  - Riassunto primi 50 caratteri
  • compact    - Rimuove spazi multipli

Uso:
    python text_utils.py count "hello world"
    python text_utils.py reverse "hello"
    python text_utils.py shout "hello world"
    python text_utils.py list

Aggiungere un nuovo comando:
    1. Usa il decoratore @register_command
    2. Il comando sarà automaticamente disponibile!

Esempio nuovo comando:
    @register_command('uppercase_words', 'Rende maiuscola ogni parola')
    def uppercase_words(text):
        return text.upper()
