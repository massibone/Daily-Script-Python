'''
Base64 to File Converter
Converte codice Base64 in file PDF, JPEG, PNG, TXT

Questo programma:
1. Legge codice Base64 da file .txt o JSON
2. Decodifica automaticamente
3. Salva come PDF, JPEG, PNG o altri formati
4. Include GUI (tkinter) e modalità CLI
5. Logging completo delle operazioni
6. Validazione e gestione errori

Formati supportati:
  • PDF (application/pdf)
  • JPEG/JPG (image/jpeg)
  • PNG (image/png)
  • GIF (image/gif)
  • TXT (text/plain)

Uso CLI:
    python base64_converter.py input.txt output.pdf
    python base64_converter.py --json data.json --key "documento" --output doc.pdf

Uso GUI:
    python base64_converter.py --gui

Uso come libreria:
    from base64_converter import Base64Converter
    
    converter = Base64Converter()
    converter.decode_from_file("codice-base64.txt", "output.pdf")

Autore: File Converter Tools
License: MIT
'''

import base64
import json
import os
import sys
import logging
from pathlib import Path
from typing import Optional, Dict, Tuple
from datetime import datetime
import argparse


# ============================================================================
# Setup Logging
# ============================================================================

def setup_logging(log_file: str = "converter.log"):
    """Configura sistema di logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


# ============================================================================
# Base64 Converter Core
# ============================================================================

class Base64Converter:
    """
    Classe per conversione Base64 in file.
    
    Supporta PDF, immagini (JPEG, PNG, GIF), testo e altri formati binari.
    """
    
    # Mapping MIME types per riconoscimento automatico
    MIME_TYPES = {
        'JVBERi0': 'pdf',           # PDF magic number
        '/9j/': 'jpg',              # JPEG magic number
        'iVBORw0KGgo': 'png',       # PNG magic number
        'R0lGOD': 'gif',            # GIF magic number
        'UEsDB': 'zip',             # ZIP magic number
    }
    
    def __init__(self):
        self.stats = {
            'conversions': 0,
            'errors': 0,
            'total_bytes': 0
        }
    
    def detect_file_type(self, base64_str: str) -> str:
        """
        Rileva automaticamente il tipo di file dal Base64.
        
        Args:
            base64_str: Stringa Base64
        
        Returns:
            str: Estensione file (pdf, jpg, png, ecc.)
        """
        # Pulisci la stringa
        clean_str = base64_str.strip()
        
        # Controlla magic numbers
        for magic, ext in self.MIME_TYPES.items():
            if clean_str.startswith(magic):
                logger.info(f"Tipo file rilevato: {ext.upper()}")
                return ext
        
        logger.warning("Tipo file non rilevato, assumo PDF")
        return 'pdf'
    
    def validate_base64(self, base64_str: str) -> bool:
        """
        Valida stringa Base64.
        
        Args:
            base64_str: Stringa da validare
        
        Returns:
            bool: True se valida
        """
        try:
            # Rimuovi whitespace
            clean_str = base64_str.strip().replace('\n', '').replace('\r', '')
            
            # Verifica lunghezza multipla di 4
            if len(clean_str) % 4 != 0:
                logger.error("Lunghezza Base64 non valida (deve essere multiplo di 4)")
                return False
            
            # Verifica caratteri validi
            import string
            valid_chars = string.ascii_letters + string.digits + '+/='
            if not all(c in valid_chars for c in clean_str):
                logger.error("Caratteri non validi nella stringa Base64")
                return False
            
            # Prova a decodificare
            base64.b64decode(clean_str, validate=True)
            return True
            
        except Exception as e:
            logger.error(f"Validazione Base64 fallita: {e}")
            return False
    
    def decode_base64(self, base64_str: str) -> bytes:
        """
        Decodifica stringa Base64 in bytes.
        
        Args:
            base64_str: Stringa Base64
        
        Returns:
            bytes: Dati decodificati
        
        Raises:
            ValueError: Se decodifica fallisce
        """
        try:
            # Pulisci stringa
            clean_str = base64_str.strip().replace('\n', '').replace('\r', '')
            
            # Decodifica
            decoded_bytes = base64.b64decode(clean_str)
            
            logger.info(f"Decodificati {len(decoded_bytes)} bytes")
            self.stats['total_bytes'] += len(decoded_bytes)
            
            return decoded_bytes
            
        except Exception as e:
            logger.error(f"Errore decodifica Base64: {e}")
            self.stats['errors'] += 1
            raise ValueError(f"Decodifica fallita: {e}")
    
    def save_file(self, data: bytes, output_path: str) -> bool:
        """
        Salva bytes su file.
        
        Args:
            data: Dati binari
            output_path: Percorso file output
        
        Returns:
            bool: True se salvataggio riuscito
        """
        try:
            # Crea directory se non esiste
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Scrivi file
            with open(output_file, 'wb') as f:
                f.write(data)
            
            file_size = output_file.stat().st_size
            logger.info(f"✅ File salvato: {output_path} ({file_size} bytes)")
            self.stats['conversions'] += 1
            
            return True
            
        except Exception as e:
            logger.error(f"Errore salvataggio file: {e}")
            self.stats['errors'] += 1
            return False
    
    def decode_from_file(self, input_file: str, output_file: str,
                        auto_detect: bool = True) -> bool:
        """
        Legge Base64 da file e converte.
        
        Args:
            input_file: File contenente Base64
            output_file: File output
            auto_detect: Rileva automaticamente tipo file
        
        Returns:
            bool: True se conversione riuscita
        """
        try:
            logger.info(f"Lettura file: {input_file}")
            
            # Leggi file
            with open(input_file, 'r', encoding='utf-8') as f:
                base64_str = f.read()
            
            # Valida
            if not self.validate_base64(base64_str):
                logger.error("Base64 non valido")
                return False
            
            # Auto-detect tipo file
            if auto_detect:
                detected_type = self.detect_file_type(base64_str)
                
                # Aggiorna estensione output se necessario
                output_path = Path(output_file)
                if output_path.suffix[1:].lower() != detected_type:
                    output_file = str(output_path.with_suffix(f'.{detected_type}'))
                    logger.info(f"Estensione aggiornata a: {detected_type}")
            
            # Decodifica
            decoded_data = self.decode_base64(base64_str)
            
            # Salva
            return self.save_file(decoded_data, output_file)
            
        except FileNotFoundError:
            logger.error(f"File non trovato: {input_file}")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            logger.error(f"Errore conversione: {e}")
            self.stats['errors'] += 1
            return False
    
    def decode_from_json(self, json_file: str, json_key: str,
                        output_file: str) -> bool:
        """
        Legge Base64 da JSON e converte.
        
        Args:
            json_file: File JSON
            json_key: Chiave contenente Base64
            output_file: File output
        
        Returns:
            bool: True se conversione riuscita
        
        Example JSON:
            {
                "documento": "JVBERi0xLjQK...",
                "tipo": "pdf",
                "nome": "fattura.pdf"
            }
        """
        try:
            logger.info(f"Lettura JSON: {json_file}")
            
            # Leggi JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Estrai Base64
            if json_key not in data:
                logger.error(f"Chiave '{json_key}' non trovata nel JSON")
                return False
            
            base64_str = data[json_key]
            
            # Valida e converte
            if not self.validate_base64(base64_str):
                return False
            
            decoded_data = self.decode_base64(base64_str)
            return self.save_file(decoded_data, output_file)
            
        except json.JSONDecodeError as e:
            logger.error(f"Errore parsing JSON: {e}")
            self.stats['errors'] += 1
            return False
        except Exception as e:
            logger.error(f"Errore: {e}")
            self.stats['errors'] += 1
            return False
    
    def encode_to_base64(self, input_file: str, output_file: str = None,
                        include_json: bool = False) -> str:
        """
        Converte file in Base64 (operazione inversa).
        
        Args:
            input_file: File da convertire
            output_file: File output (opzionale)
            include_json: Crea JSON con metadati
        
        Returns:
            str: Stringa Base64
        """
        try:
            # Leggi file
            with open(input_file, 'rb') as f:
                file_data = f.read()
            
            # Codifica
            base64_str = base64.b64encode(file_data).decode('utf-8')
            
            logger.info(f"File codificato: {len(base64_str)} caratteri")
            
            # Salva se richiesto
            if output_file:
                if include_json:
                    # Crea JSON con metadati
                    file_path = Path(input_file)
                    metadata = {
                        'file_name': file_path.name,
                        'file_type': file_path.suffix[1:],
                        'size_bytes': len(file_data),
                        'encoded_at': datetime.now().isoformat(),
                        'base64_data': base64_str
                    }
                    
                    with open(output_file, 'w', encoding='utf-8') as f:
                        json.dump(metadata, f, indent=2)
                else:
                    # Salva solo Base64
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(base64_str)
                
                logger.info(f"✅ Base64 salvato: {output_file}")
            
            return base64_str
            
        except Exception as e:
            logger.error(f"Errore encoding: {e}")
            return ""
    
    def get_stats(self) -> Dict:
        """Ottieni statistiche conversioni"""
        return self.stats.copy()
    
    def reset_stats(self):
        """Resetta statistiche"""
        self.stats = {'conversions': 0, 'errors': 0, 'total_bytes': 0}


# ============================================================================
# GUI con tkinter
# ============================================================================

def create_gui():
    """Crea interfaccia grafica"""
    try:
        import tkinter as tk
        from tkinter import ttk, filedialog, messagebox, scrolledtext
    except ImportError:
        print("❌ tkinter non disponibile. Usa modalità CLI.")
        return
    
    class ConverterGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("Base64 ↔ File Converter")
            self.root.geometry("700x600")
            
            self.converter = Base64Converter()
            self.create_widgets()
        
        def create_widgets(self):
            # Frame principale
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Titolo
            title = ttk.Label(main_frame, text="Base64 ↔ File Converter",
                            font=('Arial', 16, 'bold'))
            title.grid(row=0, column=0, columnspan=3, pady=10)
            
            # Notebook per tab
            notebook = ttk.Notebook(main_frame)
            notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Tab 1: Base64 → File
            decode_frame = ttk.Frame(notebook, padding="10")
            notebook.add(decode_frame, text="Base64 → File")
            self.create_decode_tab(decode_frame)
            
            # Tab 2: File → Base64
            encode_frame = ttk.Frame(notebook, padding="10")
            notebook.add(encode_frame, text="File → Base64")
            self.create_encode_tab(encode_frame)
            
            # Log area
            log_label = ttk.Label(main_frame, text="Log:")
            log_label.grid(row=2, column=0, sticky=tk.W, pady=(10, 0))
            
            self.log_text = scrolledtext.ScrolledText(main_frame, height=8)
            self.log_text.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=5)
            
            # Statistiche
            self.stats_label = ttk.Label(main_frame, text="Conversioni: 0 | Errori: 0")
            self.stats_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        def create_decode_tab(self, parent):
            # Input file
            ttk.Label(parent, text="File Base64:").grid(row=0, column=0, sticky=tk.W)
            self.input_entry = ttk.Entry(parent, width=50)
            self.input_entry.grid(row=0, column=1, padx=5)
            ttk.Button(parent, text="Sfoglia", command=self.browse_input).grid(row=0, column=2)
            
            # Output file
            ttk.Label(parent, text="File Output:").grid(row=1, column=0, sticky=tk.W, pady=10)
            self.output_entry = ttk.Entry(parent, width=50)
            self.output_entry.grid(row=1, column=1, padx=5, pady=10)
            ttk.Button(parent, text="Sfoglia", command=self.browse_output).grid(row=1, column=2, pady=10)
            
            # Auto-detect
            self.auto_detect_var = tk.BooleanVar(value=True)
            ttk.Checkbutton(parent, text="Auto-rileva tipo file",
                          variable=self.auto_detect_var).grid(row=2, column=1, sticky=tk.W)
            
            # Converti button
            ttk.Button(parent, text="Converti Base64 → File",
                      command=self.convert_decode,
                      style='Accent.TButton').grid(row=3, column=1, pady=20)
        
        def create_encode_tab(self, parent):
            # Input file
            ttk.Label(parent, text="File Input:").grid(row=0, column=0, sticky=tk.W)
            self.encode_input = ttk.Entry(parent, width=50)
            self.encode_input.grid(row=0, column=1, padx=5)
            ttk.Button(parent, text="Sfoglia", command=self.browse_encode_input).grid(row=0, column=2)
            
            # Output file
            ttk.Label(parent, text="File Base64:").grid(row=1, column=0, sticky=tk.W, pady=10)
            self.encode_output = ttk.Entry(parent, width=50)
            self.encode_output.grid(row=1, column=1, padx=5, pady=10)
            ttk.Button(parent, text="Sfoglia", command=self.browse_encode_output).grid(row=1, column=2, pady=10)
            
            # JSON option
            self.json_var = tk.BooleanVar(value=False)
            ttk.Checkbutton(parent, text="Includi metadati JSON",
                          variable=self.json_var).grid(row=2, column=1, sticky=tk.W)
            
            # Converti button
            ttk.Button(parent, text="Converti File → Base64",
                      command=self.convert_encode).grid(row=3, column=1, pady=20)
        
        def browse_input(self):
            file = filedialog.askopenfilename(
                title="Seleziona file Base64",
                filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
            )
            if file:
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, file)
        
        def browse_output(self):
            file = filedialog.asksaveasfilename(
                title="Salva file come",
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf"), ("JPEG", "*.jpg"), ("PNG", "*.png"), ("All files", "*.*")]
            )
            if file:
                self.output_entry.delete(0, tk.END)
                self.output_entry.insert(0, file)
        
        def browse_encode_input(self):
            file = filedialog.askopenfilename(title="Seleziona file da convertire")
            if file:
                self.encode_input.delete(0, tk.END)
                self.encode_input.insert(0, file)
        
        def browse_encode_output(self):
            file = filedialog.asksaveasfilename(
                title="Salva Base64 come",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")]
            )
            if file:
                self.encode_output.delete(0, tk.END)
                self.encode_output.insert(0, file)
        
        def log(self, message):
            self.log_text.insert(tk.END, f"{datetime.now().strftime('%H:%M:%S')} - {message}\n")
            self.log_text.see(tk.END)
        
        def update_stats(self):
            stats = self.converter.get_stats()
            self.stats_label.config(
                text=f"Conversioni: {stats['conversions']} | Errori: {stats['errors']} | "
                     f"Bytes: {stats['total_bytes']:,}"
            )
        
        def convert_decode(self):
            input_file = self.input_entry.get()
            output_file = self.output_entry.get()
            
            if not input_file or not output_file:
                messagebox.showerror("Errore", "Seleziona file input e output")
                return
            
            self.log(f"Inizio conversione: {input_file}")
            
            success = self.converter.decode_from_file(
                input_file, output_file,
                auto_detect=self.auto_detect_var.get()
            )
            
            if success:
                self.log(f"✅ Conversione completata: {output_file}")
                messagebox.showinfo("Successo", f"File salvato:\n{output_file}")
            else:
                self.log("❌ Conversione fallita")
                messagebox.showerror("Errore", "Conversione fallita. Controlla il log.")
            
            self.update_stats()
        
        def convert_encode(self):
            input_file = self.encode_input.get()
            output_file = self.encode_output.get()
            
            if not input_file or not output_file:
                messagebox.showerror("Errore", "Seleziona file input e output")
                return
            
            self.log(f"Inizio encoding: {input_file}")
            
            result = self.converter.encode_to_base64(
                input_file, output_file,
                include_json=self.json_var.get()
            )
            
            if result:
                self.log(f"✅ Encoding completato: {output_file}")
                messagebox.showinfo("Successo", f"Base64 salvato:\n{output_file}")
            else:
                self.log("❌ Encoding fallito")
                messagebox.showerror("Errore", "Encoding fallito. Controlla il log.")
    
    root = tk.Tk()
    app = ConverterGUI(root)
    root.mainloop()


# ============================================================================
# CLI Interface
# ============================================================================

def main_cli():
    """Interfaccia command line"""
    parser = argparse.ArgumentParser(
        description="Base64 to File Converter - Converti Base64 in PDF/immagini e viceversa"
    )
    
    parser.add_argument('input', nargs='?', help='File input (Base64 o file da convertire)')
    parser.add_argument('output', nargs='?', help='File output')
    parser.add_argument('--gui', action='store_true', help='Avvia interfaccia grafica')
    parser.add_argument('--json', help='File JSON contenente Base64')
    parser.add_argument('--key', default='documento', help='Chiave JSON (default: documento)')
    parser.add_argument('--encode', action='store_true', help='Modalità encoding (File → Base64)')
    parser.add_argument('--include-json', action='store_true', help='Includi metadati JSON nell\'encoding')
    parser.add_argument('--no-auto-detect', action='store_true', help='Disabilita auto-rilevamento tipo file')
    
    args = parser.parse_args()
    
    # GUI mode
    if args.gui:
        create_gui()
        return
    
    # CLI mode
    converter = Base64Converter()
    
    if args.encode:
        # File → Base64
        if not args.input or not args.output:
            print("❌ Specifica file input e output")
            parser.print_help()
            return
        
        print(f"🔄 Encoding: {args.input} → {args.output}")
        result = converter.encode_to_base64(args.input, args.output, args.include_json)
        
        if result:
            print(f"✅ Encoding completato!")
        else:
            print("❌ Encoding fallito")
    
    elif args.json:
        # JSON → File
        if not args.output:
            print("❌ Specifica file output")
            return
        
        print(f"🔄 Conversione JSON: {args.json} [{args.key}] → {args.output}")
        success = converter.decode_from_json(args.json, args.key, args.output)
        
        if success:
            print(f"✅ Conversione completata!")
        else:
            print("❌ Conversione fallita")
    
    elif args.input and args.output:
        # Base64 → File
        print(f"🔄 Conversione: {args.input} → {args.output}")
        success = converter.decode_from_file(
            args.input, args.output,
            auto_detect=not args.no_auto_detect
        )
        
        if success:
            print(f"✅ Conversione completata!")
        else:
            print("❌ Conversione fallita")
    
    else:
        parser.print_help()
        return
    
    # Mostra statistiche
    stats = converter.get_stats()
    print(f"\n📊 Statistiche:")
    print(f"   Conversioni: {stats['conversions']}")
    print(f"   Errori: {stats['errors']}")
    print(f"   Bytes totali: {stats['total_bytes']:,}")


if __name__ == '__main__':
    main_cli()