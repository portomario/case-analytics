# -*- coding: utf-8 -*-
"""Gera um PPT com os principais gráficos do case em output/case_turnover_apresentacao.pptx"""
from pathlib import Path

def main():
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
    except Exception as e:
        raise SystemExit(
            "Biblioteca 'python-pptx' não encontrada. Instale com:\n"
            "  pip install python-pptx\n"
            f"Erro original: {e}"
        )

    base = Path(__file__).resolve().parent.parent
    out = base / "output"
    out.mkdir(parents=True, exist_ok=True)

    prs = Presentation()

    # Slide 1 — Capa
    slide = prs.slides.add_slide(prs.slide_layouts[5])
    title = slide.shapes.title if slide.shapes and hasattr(slide.shapes, 'title') else None
    if title:
        title.text = "Case — People Analytics (Turnover)"
    else:
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(9), Inches(1.5))
        tf = txBox.text_frame
        tf.text = "Case — People Analytics (Turnover)"

    # Lista de imagens (se existirem)
    charts = [
        ("Taxa de desligamento (%)", out / "taxa_desligamento.png"),
        ("Turnover (rotatividade) (%)", out / "turnover_rotatividade.png"),
        ("Turnover voluntário (%)", out / "turnover_voluntario.png"),
        ("Turnover involuntário (%)", out / "turnover_involuntario.png"),
        ("Sazonalidade — desligamento (%) por mês", out / "seasonality_desligamento.png"),
        ("Desligamento (%) — MM3", out / "desligamento_ma3.png"),
        ("Turnover (%) — MM3", out / "turnover_ma3.png"),
    ]

    for title, img_path in charts:
        if not img_path.exists():
            # pula imagens ausentes
            continue
        slide = prs.slides.add_slide(prs.slide_layouts[5])
        txBox = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(9), Inches(1))
        tf = txBox.text_frame
        tf.text = title
        slide.shapes.add_picture(str(img_path), Inches(0.5), Inches(1.1), width=Inches(9))

    ppt_path = out / "case_turnover_apresentacao.pptx"
    prs.save(str(ppt_path))
    print(f"✅ PPT gerado: {ppt_path}")

if __name__ == "__main__":
    main()
