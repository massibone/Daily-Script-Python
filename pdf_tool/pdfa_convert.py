import sys
import fitz

def convert_to_pdfa(input_pdf: str, output_pdfa: str, level: str = "1"):
    level = str(level).strip()
    if level not in {"1", "2", "3"}:
        raise ValueError("level deve essere '1', '2' o '3' (per PDF/A-1..3).")

    doc = fitz.open(input_pdf)
    try:
        # PyMuPDF salva in PDF/A usando il flag pdfa= "PDF/A-<n>"
        doc.save(
            output_pdfa,
            pdfa=f"PDF/A-{level}",
            garbage=4
        )
    finally:
        doc.close()

def main():
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("Uso: python pdfa_convert.py input.pdf output.pdfa [1|2|3]")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdfa = sys.argv[2]
    level = sys.argv[3] if len(sys.argv) == 4 else "1"

    convert_to_pdfa(input_pdf, output_pdfa, level)
    print(f"Convertito in PDF/A-{level}: {output_pdfa}")

if __name__ == "__main__":
    main()
