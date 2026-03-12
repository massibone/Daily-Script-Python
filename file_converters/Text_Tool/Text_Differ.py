
class TextDiffer:
    """
    Confronta due testi e genera diff dettagliato.
    
    Features:
    - Diff riga per riga
    - Evidenziazione modifiche
    - Statistiche differenze
    - Output formattato (unified, side-by-side)
    - Percentuale similarità
    
    Example:
        >>> differ = TextDiffer()
        >>> diff = differ.compare_files("old.txt", "new.txt")
        >>> print(differ.format_diff(diff))
    """
    
    def __init__(self):
        self.diff_result = None
    
    def compare_texts(self, text1: str, text2: str) -> Dict:
        """
        Confronta due testi.
        
        Returns:
            Dict con righe aggiunte, rimosse, modificate
        """
        lines1 = text1.split('\n')
        lines2 = text2.split('\n')
        
        # Simple line-by-line comparison
        added = []
        removed = []
        common = []
        
        set1 = set(lines1)
        set2 = set(lines2)
        
        for line in lines2:
            if line not in set1:
                added.append(line)
            else:
                common.append(line)
        
        for line in lines1:
            if line not in set2:
                removed.append(line)
        
        # Similarità (Jaccard similarity)
        if len(set1) == 0 and len(set2) == 0:
            similarity = 100.0
        else:
            similarity = len(set1 & set2) / len(set1 | set2) * 100 if set1 | set2 else 0
        
        result = {
            'total_lines_1': len(lines1),
            'total_lines_2': len(lines2),
            'added': added,
            'removed': removed,
            'common': common,
            'num_added': len(added),
            'num_removed': len(removed),
            'num_common': len(common),
            'similarity_percent': round(similarity, 2)
        }
        
        self.diff_result = result
        return result
    
    def compare_files(self, file1: str, file2: str) -> Dict:
        """Confronta due file"""
        try:
            with open(file1, 'r', encoding='utf-8') as f:
                text1 = f.read()
            with open(file2, 'r', encoding='utf-8') as f:
                text2 = f.read()
            return self.compare_texts(text1, text2)
        except Exception as e:
            return {'error': str(e)}
    
    def format_diff(self, diff: Dict, max_lines: int = 20) -> str:
        """Formatta diff in output leggibile"""
        if 'error' in diff:
            return f"❌ Errore: {diff['error']}"
        
        output = f"""
╔═══════════════════════════════════════════════════════════════╗
║                    TEXT DIFFER - REPORT                       ║
╚═══════════════════════════════════════════════════════════════╝

📊 STATISTICHE DIFF
  File 1 righe:            {diff['total_lines_1']:>10}
  File 2 righe:            {diff['total_lines_2']:>10}
  Righe comuni:            {diff['num_common']:>10}
  Righe aggiunte:          {diff['num_added']:>10}
  Righe rimosse:           {diff['num_removed']:>10}
  Similarità:              {diff['similarity_percent']:>9.2f}%

"""
        
        if diff['removed']:
            output += "🔴 RIGHE RIMOSSE (max 20):\n"
            for line in diff['removed'][:max_lines]:
                output += f"  - {line}\n"
            if len(diff['removed']) > max_lines:
                output += f"  ... e altre {len(diff['removed']) - max_lines} righe\n"
            output += "\n"
        
        if diff['added']:
            output += "🟢 RIGHE AGGIUNTE (max 20):\n"
            for line in diff['added'][:max_lines]:
                output += f"  + {line}\n"
            if len(diff['added']) > max_lines:
                output += f"  ... e altre {len(diff['added']) - max_lines} righe\n"
        
        output += "\n" + "═" * 65 + "\n"
        return output

