'''
Text-Utils CLI - Sistema di utilità testo con architettura a plugin

Questo è un tool da riga di comando estendibile che supporta diversi comandi
per manipolare testo. Utilizza un pattern Registry per permettere l'aggiunta
dinamica di nuovi comandi senza modificare il codice principale.

Architettura:
- Registry Pattern: I comandi si auto-registrano usando un decoratore
- Plugin System: Nuovi comandi possono essere aggiunti nella cartella plugins/
- Estendibilità: Il main script rimane invariato quando si aggiungono comandi

Struttura del progetto:
text-utils/
├── text_utils.py          # Script principale (questo file)
├── registry.py            # Sistema di registrazione comandi
├── commands/              # Comandi built-in
│   ├── __init__.py
│   ├── count.py
│   ├── reverse.py
│   ├── shout.py
│   └── whisper.py
└── plugins/               # Comandi custom (plugin utente)
    ├── __init__.py
    └── summarize.py       # Esempio plugin

Uso:
    python text_utils.py count "hello world"
    python text_utils.py reverse "hello"
    python text_utils.py shout "hello world"
    python text_utils.py whisper "HELLO WORLD"
    python text_utils.py list  # Lista tutti i comandi disponibili

Aggiungere un nuovo comando:
    1. Crea un file in commands/ o plugins/
    2. Usa il decoratore @register_command
    3. Il comando sarà automaticamente disponibile!
'''

# ============================================================================
# FILE: registry.py
# Sistema di registrazione comandi
# ============================================================================

class CommandRegistry:
    """Registry per gestire dinamicamente i comandi disponibili"""
    
    def __init__(self):
        self._commands = {}
    
    def register(self, name, description=""):
        """
        Decoratore per registrare un comando
        
        Uso:
            @register_command('count', 'Conta caratteri in un testo')
            def count_command(text):
                return len(text)
        """
        def decorator(func):
            self._commands[name] = {
                'function': func,
                'description': description or func.__doc__ or "Nessuna descrizione"
            }
            return func
        return decorator
    
    def get_command(self, name):
        """Ottiene una funzione comando dal registro"""
        if name in self._commands:
            return self._commands[name]['function']
        return None
    
    def list_commands(self):
        """Restituisce tutti i comandi registrati"""
        return self._commands
    
    def exists(self, name):
        """Verifica se un comando esiste"""
        return name in self._commands


# Istanza globale del registry
_registry = CommandRegistry()

def register_command(name, description=""):
    """Funzione helper per registrare comandi"""
    return _registry.register(name, description)

def get_registry():
    """Ottiene l'istanza del registry"""
    return _registry


# ============================================================================
# FILE: commands/count.py
# Comando per contare caratteri/parole
# ============================================================================

@register_command('count', 'Conta caratteri e parole nel testo')
def count_command(text):
    """Conta caratteri e parole nel testo fornito"""
    chars = len(text)
    words = len(text.split())
    lines = len(text.split('\n'))
    
    return f"""
📊 Statistiche Testo:
  • Caratteri: {chars}
  • Parole: {words}
  • Righe: {lines}
"""


# ============================================================================
# FILE: commands/reverse.py
# Comando per invertire testo
# ============================================================================

@register_command('reverse', 'Inverte il testo fornito')
def reverse_command(text):
    """Inverte l'ordine dei caratteri nel testo"""
    return text[::-1]


# ============================================================================
# FILE: commands/shout.py
# Comando per convertire in maiuscolo
# ============================================================================

@register_command('shout', 'Converte il testo in MAIUSCOLO')
def shout_command(text):
    """Converte il testo in maiuscolo (SHOUT)"""
    return text.upper() + "!"


# ============================================================================
# FILE: commands/whisper.py
# Comando per convertire in minuscolo
# ============================================================================

@register_command('whisper', 'Converte il testo in minuscolo')
def whisper_command(text):
    """Converte il testo in minuscolo (whisper)"""
    return text.lower() + "..."


# ============================================================================
# FILE: plugins/summarize.py
# Esempio di plugin custom
# ============================================================================

@register_command('summarize', 'Riassume il testo (prime 50 caratteri)')
def summarize_command(text):
    """Restituisce un riassunto del testo (primi 50 caratteri)"""
    if len(text) <= 50:
        return text
    return text[:50] + "..."


# ============================================================================
# FILE: plugins/uppercase_words.py
# Altro esempio di plugin
# ============================================================================

@register_command('capitalize', 'Mette in maiuscolo ogni parola')
def capitalize_command(text):
    """Mette in maiuscolo la prima lettera di ogni parola"""
    return text.title()


# ============================================================================
# FILE: plugins/remove_spaces.py
# Altro esempio di plugin
# ============================================================================

@register_command('compact', 'Rimuove spazi multipli')
def compact_command(text):
    """Rimuove spazi multipli lasciandone solo uno"""
    import re
    return re.sub(r'\s+', ' ', text).strip()


# ============================================================================
# FILE: text_utils.py (MAIN)
# Script principale - Non richiede modifiche per nuovi comandi!
# ============================================================================

import sys


def load_plugins():
    """
    Carica automaticamente tutti i plugin disponibili.
    In un progetto reale, questa funzione scansionerebbe le cartelle
    commands/ e plugins/ e importerebbe dinamicamente i moduli.
    
    Per questo esempio, tutti i comandi sono già definiti sopra.
    """
    # In produzione:
    # import importlib
    # import os
    # import pkgutil
    # 
    # for folder in ['commands', 'plugins']:
    #     if os.path.exists(folder):
    #         for (_, name, _) in pkgutil.iter_modules([folder]):
    #             importlib.import_module(f'{folder}.{name}')
    
    pass  # Tutti i comandi sono già registrati in questo esempio


def print_help():
    """Mostra l'help generale"""
    registry = get_registry()
    commands = registry.list_commands()
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              TEXT-UTILS CLI - Sistema a Plugin                ║
╚═══════════════════════════════════════════════════════════════╝

Uso: python text_utils.py <comando> <testo>

Comandi disponibili:
""")
    
    for name, info in sorted(commands.items()):
        desc = info['description']
        print(f"  • {name:12} - {desc}")
    
    print("""
Esempi:
  python text_utils.py count "hello world"
  python text_utils.py reverse "hello"
  python text_utils.py shout "ciao mondo"
  python text_utils.py list
  
Per aggiungere un nuovo comando:
  1. Crea un file nella cartella plugins/
  2. Usa @register_command('nome', 'descrizione')
  3. Il comando sarà automaticamente disponibile!
""")


def list_commands():
    """Lista tutti i comandi disponibili con dettagli"""
    registry = get_registry()
    commands = registry.list_commands()
    
    print("\n🔧 Comandi Registrati nel Sistema:\n")
    for name, info in sorted(commands.items()):
        print(f"  [{name}]")
        print(f"    Descrizione: {info['description']}")
        print(f"    Funzione: {info['function'].__name__}")
        print()


def main():
    """Funzione principale - gestisce input e dispatch comandi"""
    
    # Carica tutti i plugin disponibili
    load_plugins()
    
    # Ottieni registry
    registry = get_registry()
    
    # Parse argomenti
    if len(sys.argv) < 2:
        print_help()
        sys.exit(1)
    
    command_name = sys.argv[1].lower()
    
    # Comandi speciali
    if command_name in ['help', '--help', '-h']:
        print_help()
        sys.exit(0)
    
    if command_name == 'list':
        list_commands()
        sys.exit(0)
    
    # Verifica se il comando esiste
    if not registry.exists(command_name):
        print(f"❌ Errore: Comando '{command_name}' non trovato")
        print(f"\n💡 Usa 'python text_utils.py list' per vedere tutti i comandi disponibili")
        sys.exit(1)
    
    # Verifica se c'è il testo da processare
    if len(sys.argv) < 3:
        print(f"❌ Errore: Manca il testo da processare")
        print(f"\nUso: python text_utils.py {command_name} <testo>")
        sys.exit(1)
    
    # Ottieni il testo (tutti gli argomenti dopo il comando)
    text = ' '.join(sys.argv[2:])
    
    # Esegui il comando
    try:
        command_func = registry.get_command(command_name)
        result = command_func(text)
        
        print(f"\n✅ Risultato comando '{command_name}':")
        print(f"\n{result}\n")
        
    except Exception as e:
        print(f"❌ Errore durante l'esecuzione del comando: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
