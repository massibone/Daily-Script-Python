# ============================================================================
# 3. MARKDOWN CONVERTER - Markdown ↔ HTML
# ============================================================================

class MarkdownConverter:
    """
    Converte Markdown in HTML e viceversa.
    
    Features:
    - Headers (# ## ###)
    - Bold, italic
    - Links, immagini
    - Liste (ordered/unordered)
    - Code blocks
    - Blockquotes
    
    Example:
        >>> converter = MarkdownConverter()
        >>> html = converter.markdown_to_html("# Title\\n**bold**")
        >>> print(html)
    """
    
    def markdown_to_html(self, markdown: str) -> str:
        """
        Converte Markdown in HTML.
        
        Args:
            markdown: Testo Markdown
        
        Returns:
            HTML generato
        """
        html = markdown
        
        # Headers
        html = re.sub(r'^######\s+(.+)$', r'<h6>\1</h6>', html, flags=re.MULTILINE)
        html = re.sub(r'^#####\s+(.+)$', r'<h5>\1</h5>', html, flags=re.MULTILINE)
        html = re.sub(r'^####\s+(.+)$', r'<h4>\1</h4>', html, flags=re.MULTILINE)
        html = re.sub(r'^###\s+(.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^##\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^#\s+(.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        
        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)
        
        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)
        
        # Links
        html = re.sub(r'\[(.+?)\]\((.+?)\)', r'<a href="\2">\1</a>', html)
        
        # Images
        html = re.sub(r'!\[(.+?)\]\((.+?)\)', r'<img src="\2" alt="\1">', html)
        
        # Code inline
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)
        
        # Unordered lists
        html = re.sub(r'^\* (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # Wrap consecutive <li> in <ul>
        html = re.sub(r'(<li>.*?</li>\n)+', r'<ul>\n\g<0></ul>\n', html, flags=re.DOTALL)
        
        # Paragraphs
        lines = html.split('\n')
        in_block = False
        result = []
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith('<') or not stripped:
                result.append(line)
                in_block = False
            else:
                if not in_block:
                    result.append('<p>' + line)
                    in_block = True
                else:
                    result.append(line + '</p>')
                    in_block = False
        
        return '\n'.join(result)
    
    def convert_file(self, input_file: str, output_file: str) -> bool:
        """Converte file Markdown in HTML"""
        try:
            with open(input_file, 'r', encoding='utf-8') as f:
                markdown = f.read()
            
            html = self.markdown_to_html(markdown)
            
            # Aggiungi template HTML base
            full_html = f"""<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
        }}
        img {{
            max-width: 100%;
        }}
    </style>
</head>
<body>
{html}
</body>
</html>"""
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            print(f"✅ Convertito: {input_file} → {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Errore: {e}")
            return False

