import sys
import re
from typing import Dict, Callable, List


# ============================================================================
# Registry System
# ============================================================================

class CommandRegistry:
    """Registry per gestire dinamicamente i comandi disponibili"""
    
    def __init__(self):
        self._commands: Dict[str, Dict] = {}
    
    def register(self, name: str, description: str = ""):
        """
        Decoratore per registrare un comando.
        
        Args:
            name: Nome del comando
            description: Descrizione del comando
        
        Usage:
            @register_command('count', 'Conta caratteri in un testo')
            def count_command(text):
                return len(text)
        """
        def decorator(func: Callable):
            self._commands[name] = {
                'function': func,
                'description': description or func.__doc__ or "Nessuna descrizione"
            }
            return func
        return decorator
    
    def get_command(self, name: str) -> Callable:
        """
        Ottiene una funzione comando dal registro.
        
        Args:
            name: Nome del comando
        
        Returns:
            Funzione comando o None
        """
        if name in self._commands:
            return self._commands[name]['function']
        return None
    
    def list_commands(self) -> Dict:
        """Restituisce tutti i comandi registrati"""
        return self._commands.copy()
    
    def exists(self, name: str) -> bool:
        """Verifica se un comando esiste"""
        return name in self._commands


# Istanza globale del registry
_registry = CommandRegistry()


def register_command(name: str, description: str = ""):
    """Funzione helper per registrare comandi"""
    return _registry.register(name, description)


def get_registry() -> CommandRegistry:
    """Ottiene l'istanza del registry"""
    return _registry


# ============================================================================
# Built-in Commands
# ============================================================================

@register_command('count', 'Conta caratteri, parole e righe nel testo')
def count_command(text: str) -> str:
    """Conta caratteri e parole nel testo fornito"""
    chars = len(text)
    words = len(text.split())
    lines = len(text.split('\n'))
    
    return f"""
╔═══════════════════════════════════════════════════════════════╗
║                    Statistiche Testo                          ║
╚═══════════════════════════════════════════════════════════════╝

  📊 Caratteri:     {chars:>10}
  📝 Parole:        {words:>10}
  📄 Righe:         {lines:>10}
"""


@register_command('reverse', 'Inverte il testo fornito')
def reverse_command(text: str) -> str:
    """Inverte l'ordine dei caratteri nel testo"""
    return text[::-1]


@register_command('shout', 'Converte il testo in MAIUSCOLO')
def shout_command(text: str) -> str:
    """Converte il testo in maiuscolo (SHOUT)"""
    return text.upper() + "!"


@register_command('whisper', 'Converte il testo in minuscolo')
def whisper_command(text: str) -> str:
    """Converte il testo in minuscolo (whisper)"""
    return text.lower() + "..."


@register_command('capitalize', 'Mette in maiuscolo ogni parola')
def capitalize_command(text: str) -> str:
    """Mette in maiuscolo la prima lettera di ogni parola"""
    return text.title()


@register_command('summarize', 'Riassume il testo (prime 50 caratteri)')
def summarize_command(text: str) -> str:
    """Restituisce un riassunto del testo (primi 50 caratteri)"""
    if len(text) <= 50:
        return text
    return text[:50] + "..."


@register_command('compact', 'Rimuove spazi multipli')
def compact_command(text: str) -> str:
    """Rimuove spazi multipli lasciandone solo uno"""
    return re.sub(r'\s+', ' ', text).strip()


@register_command('length', 'Restituisce la lunghezza del testo')
def length_command(text: str) -> str:
    """Restituisce il numero di caratteri"""
    return f"Lunghezza: {len(text)} caratteri"


@register_command('words', 'Conta solo le parole')
def words_command(text: str) -> str:
    """Conta il numero di parole"""
    word_count = len(text.split())
    return f"Numero parole: {word_count}"


@register_command('lines', 'Conta solo le righe')
def lines_command(text: str) -> str:
    """Conta il numero di righe"""
    line_count = len(text.split('\n'))
    return f"Numero righe: {line_count}"


@register_command('snake_case', 'Converte in snake_case')
def snake_case_command(text: str) -> str:
    """Converte il testo in snake_case"""
    # Sostituisci spazi con underscore
    text = re.sub(r'\s+', '_', text)
    # Inserisci underscore prima delle maiuscole
    text = re.sub(r'([a-z])([A-Z])', r'\1_\2', text)
    return text.lower()


@register_command('kebab_case', 'Converte in kebab-case')
def kebab_case_command(text: str) -> str:
    """Converte il testo in kebab-case"""
    text = re.sub(r'\s+', '-', text)
    text = re.sub(r'([a-z])([A-Z])', r'\1-\2', text)
    return text.lower()


@register_command('camel_case', 'Converte in camelCase')
def camel_case_command(text: str) -> str:
    """Converte il testo in camelCase"""
    words = text.split()
    if not words:
        return text
    return words[0].lower() + ''.join(word.capitalize() for word in words[1:])


@register_command('pascal_case', 'Converte in PascalCase')
def pascal_case_command(text: str) -> str:
    """Converte il testo in PascalCase"""
    words = text.split()
    return ''.join(word.capitalize() for word in words)


@register_command('remove_vowels', 'Rimuove tutte le vocali')
def remove_vowels_command(text: str) -> str:
    """Rimuove tutte le vocali dal testo"""
    return re.sub(r'[aeiouAEIOU]', '', text)


@register_command('only_vowels', 'Mantiene solo le vocali')
def only_vowels_command(text: str) -> str:
    """Mantiene solo le vocali nel testo"""
    return re.sub(r'[^aeiouAEIOU]', '', text)


@register_command('rot13', 'Applica cifratura ROT13')
def rot13_command(text: str) -> str:
    """Applica cifratura ROT13 al testo"""
    import codecs
    return codecs.encode(text, 'rot13')


@register_command('strip', 'Rimuove spazi all\'inizio e alla fine')
def strip_command(text: str) -> str:
    """Rimuove spazi bianchi all'inizio e alla fine"""
    return text.strip()


# ============================================================================
# Main CLI Interface
# ============================================================================

def print_help():
    """Mostra l'help generale"""
    registry = get_registry()
    commands = registry.list_commands()
    
    print("""
╔═══════════════════════════════════════════════════════════════╗
║              TEXT-UTILS CLI - Sistema a Plugin                ║
╚═══════════════════════════════════════════════════════════════╝

Uso: python text_utils.py <comando> <testo>

📚 Comandi disponibili:
""")
    
    # Organizza comandi per categoria
    categories = {
        'Statistiche': ['count', 'length', 'words', 'lines'],
        'Trasformazioni Base': ['reverse', 'shout', 'whisper', 'capitalize', 'strip'],
        'Naming Conventions': ['snake_case', 'kebab_case', 'camel_case', 'pascal_case'],
        'Editing': ['summarize', 'compact', 'remove_vowels', 'only_vowels'],
        'Encoding': ['rot13']
    }
    
    for category, cmd_list in categories.items():
        print(f"\n  🔹 {category}:")
        for cmd_name in cmd_list:
            if cmd_name in commands:
                desc = commands[cmd_name]['description']
                print(f"    • {cmd_name:15} - {desc}")
    
    # Comandi non categorizzati
    categorized = set(sum(categories.values(), []))
    other_commands = [cmd for cmd in commands.keys() if cmd not in categorized]
    
    if other_commands:
        print(f"\n  🔹 Altri comandi:")
        for cmd_name in other_commands:
            desc = commands[cmd_name]['description']
            print(f"    • {cmd_name:15} - {desc}")
    
    print("""
💡 Esempi:
  python text_utils.py count "hello world"
  python text_utils.py reverse "hello"
  python text_utils.py shout "ciao mondo"
  python text_utils.py snake_case "Hello World Example"
  python text_utils.py list
  
🔧 Per aggiungere un nuovo comando:
  1. Usa il decoratore @register_command('nome', 'descrizione')
  2. Il comando sarà automaticamente disponibile!
  
📋 Altri comandi:
  python text_utils.py list              - Lista comandi con dettagli
  python text_utils.py help              - Mostra questo messaggio
""")


def list_commands():
    """Lista tutti i comandi disponibili con dettagli"""
    registry = get_registry()
    commands = registry.list_commands()
    
    print("\n🔧 Comandi Registrati nel Sistema:\n")
    print(f"{'Comando':<20} {'Funzione':<25} {'Descrizione'}")
    print("=" * 80)
    
    for name, info in sorted(commands.items()):
        func_name = info['function'].__name__
        desc = info['description'][:40] + "..." if len(info['description']) > 40 else info['description']
        print(f"{name:<20} {func_name:<25} {desc}")
    
    print(f"\n✅ Totale: {len(commands)} comandi disponibili\n")


def print_banner():
    """Stampa banner iniziale"""
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                     TEXT-UTILS CLI v1.0                       ║
║              Sistema a Plugin per Manipolazione Testo         ║
╚═══════════════════════════════════════════════════════════════╝
""")


def main():
    """Funzione principale - gestisce input e dispatch comandi"""
    
    # Parse argomenti
    if len(sys.argv) < 2:
        print_banner()
        print_help()
        sys.exit(1)
    
    command_name = sys.argv[1].lower()
    
    # Comandi speciali
    if command_name in ['help', '--help', '-h']:
        print_banner()
        print_help()
        sys.exit(0)
    
    if command_name == 'list':
        print_banner()
        list_commands()
        sys.exit(0)
    
    # Ottieni registry
    registry = get_registry()
    
    # Verifica se il comando esiste
    if not registry.exists(command_name):
        print(f"\n❌ Errore: Comando '{command_name}' non trovato\n")
        print(f"💡 Usa 'python text_utils.py list' per vedere tutti i comandi disponibili")
        print(f"💡 Usa 'python text_utils.py help' per la guida completa\n")
        sys.exit(1)
    
    # Verifica se c'è il testo da processare
    if len(sys.argv) < 3:
        print(f"\n❌ Errore: Manca il testo da processare\n")
        print(f"Uso: python text_utils.py {command_name} <testo>\n")
        sys.exit(1)
    
    # Ottieni il testo (tutti gli argomenti dopo il comando)
    text = ' '.join(sys.argv[2:])
    
    # Esegui il comando
    try:
        print_banner()
        command_func = registry.get_command(command_name)
        result = command_func(text)
        
        print(f"✅ Risultato comando '{command_name}':\n")
        print(f"{'─' * 65}")
        print(result)
        print(f"{'─' * 65}\n")
        
    except Exception as e:
        print(f"\n❌ Errore durante l'esecuzione del comando: {e}\n")
        sys.exit(1)


# ============================================================================
# Plugin Loader (Opzionale - per caricare plugin esterni)
# ============================================================================

def load_plugins_from_file(plugin_file: str):
    """
    Carica plugin da file esterno.
    
    Args:
        plugin_file: Path al file Python con plugin
    
    Example plugin file content:
        from text_utils import register_command
        
        @register_command('my_command', 'My custom command')
        def my_command(text):
            return text.upper()
    """
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("plugins", plugin_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            print(f"✅ Plugin caricati da: {plugin_file}")
    except Exception as e:
        print(f"⚠️  Errore caricamento plugin: {e}")


# ============================================================================
# Entry Point
# ============================================================================

if __name__ == '__main__':
    # Opzionale: carica plugin esterni
    # load_plugins_from_file('my_plugins.py')
    
    main()
