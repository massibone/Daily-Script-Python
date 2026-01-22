class WordCounter:
    """
    Contatore parole avanzato con statistiche dettagliate.
    
    Features:
    - Conteggio caratteri, parole, frasi, paragrafi
    - Parole più frequenti
    - Lunghezza media parole
    - Distribuzione lunghezza parole
    - Tempo lettura stimato
    - Export statistiche JSON/CSV
    
    Example:
        >>> counter = WordCounter()
        >>> stats = counter.analyze_file("document.txt")
        >>> print(counter.format_report(stats))
    """
    
    def __init__(self):
        self.stats = {}
    
    def analyze_text(self, text: str) -> Dict:
        """
        Analizza testo e genera statistiche complete.
        
        Args:
            text: Testo da analizzare
        
        Returns:
            Dizionario con statistiche
        """
        # Basic counts
        chars = len(text)
        chars_no_spaces = len(text.replace(' ', '').replace('\n', ''))
        
        # Words
        words = text.split()
        word_count = len(words)
        
        # Sentences (approssimato)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        # Paragraphs
        paragraphs = text.split('\n\n')
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        # Word analysis
        word_lengths = [len(w) for w in words]
        avg_word_length = sum(word_lengths) / len(word_lengths) if word_lengths else 0
        
        # Word frequency (case insensitive)
        word_freq = Counter(word.lower().strip('.,!?;:') for word in words)
        most_common = word_freq.most_common(10)
        
        # Unique words
        unique_words = len(set(word.lower() for word in words))
        
        # Reading time (assume 200 words per minute)
        reading_time_minutes = word_count / 200
        
        # Lexical diversity (unique/total words)
        lexical_diversity = (unique_words / word_count * 100) if word_count > 0 else 0
        
        stats = {
            'characters': chars,
            'characters_no_spaces': chars_no_spaces,
            'words': word_count,
            'sentences': sentence_count,
            'paragraphs': paragraph_count,
            'unique_words': unique_words,
            'avg_word_length': round(avg_word_length, 2),
            'reading_time_minutes': round(reading_time_minutes, 2),
            'lexical_diversity': round(lexical_diversity, 2),
            'most_common_words': most_common,
            'word_length_distribution': Counter(word_lengths)
        }
        
        self.stats = stats
        return stats
    
    def analyze_file(self, filepath: str) -> Dict:
        """Analizza file di testo"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
            return self.analyze_text(text)
        except Exception as e:
            return {'error': str(e)}
    
    def format_report(self, stats: Dict) -> str:
        """Formatta statistiche in report leggibile"""
        if 'error' in stats:
            return f"❌ Errore: {stats['error']}"
        
        report = f"""
╔═══════════════════════════════════════════════════════════════╗
║                   WORD COUNTER - REPORT                       ║
╚═══════════════════════════════════════════════════════════════╝

📊 CONTEGGI BASE
  Caratteri totali:        {stats['characters']:>10,}
  Caratteri (no spazi):    {stats['characters_no_spaces']:>10,}
  Parole:                  {stats['words']:>10,}
  Frasi:                   {stats['sentences']:>10,}
  Paragrafi:               {stats['paragraphs']:>10,}

📖 ANALISI PAROLE
  Parole unique:           {stats['unique_words']:>10,}
  Lunghezza media parola:  {stats['avg_word_length']:>10.2f} caratteri
  Diversità lessicale:     {stats['lexical_diversity']:>10.2f}%

⏱️  TEMPO LETTURA
  Tempo stimato:           {stats['reading_time_minutes']:>10.2f} minuti
  (basato su 200 parole/min)

🔝 TOP 10 PAROLE PIÙ FREQUENTI
"""
        for word, count in stats['most_common_words']:
            report += f"  {word:<20} {count:>5} volte\n"
        
        report += "\n" + "═" * 65 + "\n"
        return report
    
    def export_json(self, filepath: str) -> bool:
        """Esporta statistiche in JSON"""
        try:
            # Converti Counter in dict per JSON
            exportable = self.stats.copy()
            exportable['word_length_distribution'] = dict(exportable['word_length_distribution'])
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(exportable, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False


""")
    
    sample_text = """
# Python Programming

Python is a **powerful** and *easy-to-learn* programming language.
It has efficient high-level data structures and a simple but effective
approach to object-oriented programming.

Python's elegant syntax and dynamic typing, together with its interpreted
nature, make it an ideal language for scripting and rapid application
development in many areas on most platforms.

## Features

* Easy to learn
* Free and open source
* Portable
* Rich library support
"""
    
    print("\n1  WORD COUNTER")
    print("─" * 65)
    counter = WordCounter()
    stats = counter.analyze_text(sample_text)
    print(counter.format_report(stats)) 
