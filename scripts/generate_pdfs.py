"""Generate the project's PDF documents from the checked-in text sources."""

from pathlib import Path
import re
import textwrap

from fpdf import FPDF
from fpdf.enums import XPos, YPos


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def _pdf_text(value: str) -> str:
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "-",
        "\u2192": "->",
        "\u2713": "[OK]",
    }
    for source, target in replacements.items():
        value = value.replace(source, target)
    return value.encode("latin-1", "replace").decode("latin-1")


def _clean_line(line: str) -> str:
    line = line.rstrip()
    line = re.sub(r"^\s*\.\.\s+\w+::.*$", "", line)
    line = re.sub(r":(?:ref|class|func|meth|mod):`([^`]+)`", r"\1", line)
    line = re.sub(r"`([^`]+)`_", r"\1", line)
    line = re.sub(r"\*\*([^*]+)\*\*", r"\1", line)
    line = re.sub(r"``([^`]+)``", r"\1", line)
    line = line.replace("```", "")
    return _pdf_text(line)


class DocumentPDF(FPDF):
    def __init__(self, title: str):
        super().__init__()
        self.document_title = _pdf_text(title)
        self.set_auto_page_break(auto=True, margin=15)
        self.set_title(self.document_title)
        self.set_author("PyReact")

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(80, 80, 80)
        self.cell(
            0, 6, self.document_title, align="R",
            new_x=XPos.LMARGIN, new_y=YPos.NEXT,
        )
        self.ln(2)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(
            0, 6, f"Pagina {self.page_no()}", align="C",
            new_x=XPos.RIGHT, new_y=YPos.TOP,
        )


def _write_line(pdf: DocumentPDF, line: str) -> None:
    stripped = line.strip()
    if not stripped:
        pdf.ln(3)
        return

    is_markdown_heading = stripped.startswith("#")
    is_rst_heading = bool(re.fullmatch(r"[=\-~^]{3,}", stripped))
    if is_rst_heading:
        return

    if is_markdown_heading:
        level = len(stripped) - len(stripped.lstrip("#"))
        text = stripped.lstrip("#").strip()
        pdf.set_font("Helvetica", "B", 16 if level == 1 else 13 if level == 2 else 11)
        pdf.set_text_color(24, 71, 120)
        pdf.ln(2)
    else:
        text = stripped
        pdf.set_font(
            "Courier" if line.startswith("    ") else "Helvetica",
            "",
            8 if line.startswith("    ") else 9,
        )
        pdf.set_text_color(30, 30, 30)

    for wrapped in textwrap.wrap(
        text, width=105, break_long_words=True, break_on_hyphens=True
    ) or [""]:
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 5, wrapped)


def build_pdf(title: str, sources: list[Path], destination: Path) -> None:
    pdf = DocumentPDF(title)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(24, 71, 120)
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, 10, _pdf_text(title), align="C")
    pdf.ln(5)

    for source in sources:
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(24, 71, 120)
        pdf.set_x(pdf.l_margin)
        pdf.multi_cell(0, 8, _pdf_text(source.relative_to(ROOT).as_posix()))
        pdf.ln(1)
        for raw_line in source.read_text(encoding="utf-8").splitlines():
            _write_line(pdf, _clean_line(raw_line))
        pdf.ln(5)

    pdf.output(str(destination))


def main() -> None:
    manual_sources = [ROOT / "README.md"]
    manual_sources.extend(
        path
        for path in sorted(DOCS.rglob("*.rst"))
        if "_build" not in path.parts
    )
    build_pdf("Manual PyReact", manual_sources, DOCS / "Manual_PyReact.pdf")
    build_pdf(
        "Relatorio de Correcoes e Testes",
        [DOCS / "RELATORIO_CORRECOES_E_TESTES.md"],
        DOCS / "Relatorio_Correcoes_e_Testes.pdf",
    )
    build_pdf(
        "Guia de Execucao e Testes",
        [DOCS / "GUIA_EXECUCAO_E_TESTES.md"],
        DOCS / "Guia_Execucao_e_Testes.pdf",
    )
    print("PDFs generated in docs/")


if __name__ == "__main__":
    main()
