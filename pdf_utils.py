# pdf_utils.py
from fpdf import FPDF
import os

# ✅ NanumGothic 폰트는 fonts/ 폴더에 위치해야 함
FONT_PATH = "fonts/NanumGothic.ttf"

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.add_font("Nanum", "", FONT_PATH, uni=True)
        self.set_font("Nanum", size=12)
        self.add_page()

def save_to_pdf(summary_text, filename="summary.pdf"):
    pdf = PDF()

    lines = summary_text.split("\n")
    for line in lines:
        # ⚠️ 이모지 및 특수문자로 인한 cmap 오류 방지
        safe_line = line.encode("utf-16", "ignore").decode("utf-16", "ignore")
        pdf.multi_cell(0, 10, safe_line)

    os.makedirs("outputs", exist_ok=True)
    filepath = os.path.join("outputs", filename)
    pdf.output(filepath)
    return filepath  # PDF 파일 경로 반환
