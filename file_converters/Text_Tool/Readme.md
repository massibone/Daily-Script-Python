# 📝 Text Tools

Text-Utils CLI - Sistema di utilità testo con architettura a plugin

## 🔧 text_utils.py

Tool CLI con sistema a plugin per manipolare testo.
Questo è un tool da riga di comando estendibile che supporta diversi comandi
per manipolare testo. Utilizza un pattern Registry per permettere l'aggiunta
dinamica di nuovi comandi senza modificare il codice principale.

### Comandi Disponibili

**Statistiche:**
- `count` - Conta caratteri, parole, righe
- `length` - Lunghezza testo
- `words` - Conta parole
- `lines` - Conta righe

**Trasformazioni:**
- `reverse` - Inverte testo
- `shout` - MAIUSCOLO
- `whisper` - minuscolo
- `capitalize` - Prima Lettera Maiuscola

**Naming Conventions:**
- `snake_case` - hello_world
- `kebab-case` - hello-world
- `camelCase` - helloWorld
- `PascalCase` - HelloWorld

**Editing:**
- `summarize` - Primi 50 caratteri
- `compact` - Rimuovi spazi multipli
- `strip` - Rimuovi spazi inizio/fine
- `remove_vowels` - Rimuovi vocali
- `only_vowels` - Solo vocali

**Encoding:**
- `rot13` - Cifratura ROT13

### Uso

```bash
# Statistiche
python text_utils.py count "Hello World"

# Trasformazioni
python text_utils.py shout "hello world"
python text_utils.py reverse "hello"

# Naming conventions
python text_utils.py snake_case "Hello World Example"
python text_utils.py camel_case "hello world example"

# Lista comandi
python text_utils.py list

# Help
python text_utils.py help
```

### Output Esempio

```bash
$ python text_utils.py count "Hello World"

╔═══════════════════════════════════════════════════════════════╗
║                    Statistiche Testo                          ║
╚═══════════════════════════════════════════════════════════════╝

  📊 Caratteri:             11
  📝 Parole:                 2
  📄 Righe:                  1
```

### Aggiungere Plugin Custom

Crea `plugins/my_plugin.py`:

```python
from text_utils import register_command

@register_command('my_command', 'Il mio comando custom')
def my_command(text):
    # La tua logica
    return text.replace('a', '@')
```


### Architettura

**Registry Pattern:**
- I comandi si auto-registrano
- Nessuna modifica al main necessaria
- Facile aggiungere nuovi comandi

**Vantaggi:**
- ✅ Estendibile senza modificare core
- ✅ Plugin system modulare
- ✅ CLI user-friendly
- ✅ Zero dipendenze esterne

## 📦 Dipendenze

Nessuna! Solo Python 3.6+ standard library.







Esempio nuovo comando:
    @register_command('uppercase_words', 'Rende maiuscola ogni parola')
    def uppercase_words(text):
        return text.upper()
