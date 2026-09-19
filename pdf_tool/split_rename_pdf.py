from __future__ import annotations

import argparse
import re
from pathlib import Path
import fitz  # PyMuPDF


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "document"


def build_name(pattern: str, source_pdf: Path, page_number: int, total_pages: int) -> str:
    name = pattern.format(
        stem=slugify(source_pdf.stem),
        original=source_pdf.stem,
        page=page_number,
        total=total_pages,
    )
    return f"{slugify(name)}.pdf"


def split_pdf(input_pdf: Path, output_dir: Path, pattern: str) -> list[Path]:
    doc = fitz.open(input_pdf)
    created_files: list[Path] = []
    try:
        total_pages = doc.page_count
        if total_pages == 0:
            return created_files

        for page_index in range(total_pages):
            new_doc = fitz.open()
            try:
                new_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)
                file_name = build_name(pattern, input_pdf, page_index + 1, total_pages)
                output_path = output_dir / file_name
                counter = 1
                while output_path.exists():
                    output_path = output_dir / file_name.replace(".pdf", f"-{counter}.pdf")
                    counter += 1
                new_doc.save(output_path)
                created_files.append(output_path)
            finally:
                new_doc.close()
    finally:
        doc.close()
    return created_files

def batch_split(input_dir: Path, output_dir: Path, pattern: str) -> dict[str, list[str]]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Input path is not a directory: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, list[str]] = {}

    for pdf_path in sorted(input_dir.glob("*.pdf")):
        created = split_pdf(pdf_path, output_dir, pattern)
        results[pdf_path.name] = [str(path) for path in created]

    return results


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Split multipage PDFs into single-page files and rename them in batch."
    )
    parser.add_argument("input_dir", type=Path, help="Folder containing source PDF files")
    parser.add_argument(
        "-o", "--output-dir",
        type=Path,
        default=Path("split_output"),
        help="Folder where split PDF files will be saved"
    )
    parser.add_argument(
        "-p", "--pattern",
        default="{stem}-page-{page}",
        help="Output naming pattern using {stem}, {original}, {page}, {total}"
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    results = batch_split(args.input_dir, args.output_dir, args.pattern)
    for source, files in results.items():
        print(f"{source}: {len(files)} files created")
        for file_path in files:
            print(f"  - {file_path}")


if __name__ == "__main__":
    main()
  
