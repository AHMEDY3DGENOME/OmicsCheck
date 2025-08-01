from fpdf import FPDF
from pathlib import Path
from datetime import datetime

class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 16)
        self.cell(0, 10, "OmicsCheck Report", ln=True, align="C")
        self.set_font("Arial", "", 12)
        self.cell(0, 10, f"Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align="C")
        self.ln(10)

    def section_title(self, title):
        self.set_font("Arial", "B", 14)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, title, ln=True)
        self.set_text_color(0, 0, 0)
        self.ln(5)

    def add_key_value(self, key, value):
        self.set_font("Arial", "", 12)
        self.cell(50, 10, f"{key}:", ln=False)
        self.set_font("Arial", "B", 12)
        self.cell(0, 10, str(value), ln=True)

def generate_pdf_report(gse_id: str, analysis: dict, output_dir: Path, orientation_note: str = "", log2_note: str = ""):
    pdf = PDF()
    pdf.add_page()

    # Section 1: Overview
    pdf.section_title(f"GEO Series ID: {gse_id}")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 10, f"This report summarizes the gene expression matrix and visual analyses performed for GEO dataset {gse_id} using OmicsCheck.")

    if orientation_note:
        pdf.section_title("Orientation Note")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, orientation_note)

    if log2_note:
        pdf.section_title("Log2 Transformation Suggestion")
        pdf.set_font("Arial", "", 12)
        pdf.multi_cell(0, 10, log2_note)

    # Section 2: Summary Stats
    pdf.section_title("Summary Statistics")
    for key, value in analysis.items():
        pdf.add_key_value(key.replace('_', ' ').capitalize(), value)

    # Section 3: Plots
    for img_title, img_file in [("Boxplot", "boxplot.png"), ("Heatmap (Top 30 variable genes)", "heatmap.png")]:
        img_path = output_dir / img_file
        if img_path.exists():
            pdf.add_page()
            pdf.section_title(img_title)
            pdf.image(str(img_path), x=10, y=30, w=180)

    report_path = output_dir / "report.pdf"
    pdf.output(str(report_path))

