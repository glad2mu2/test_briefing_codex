"""PPTX builder for briefing slides."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from urllib.request import urlopen

from src.schemas import ArticleSummary, SlidePlan


class PPTXBuildError(RuntimeError):
    """Raised when PPTX output cannot be created."""


def build_briefing_pptx(
    summaries: tuple[ArticleSummary, ...],
    slide_plans: tuple[SlidePlan, ...],
    output_path: Path,
) -> Path:
    """Build a simple PPTX briefing deck and return the output path."""
    _validate_output_path(output_path)
    if not summaries:
        raise PPTXBuildError("at least one article summary is required")
    for summary in summaries:
        _validate_summary(summary)
    try:
        from pptx import Presentation
        from pptx.util import Inches, Pt
    except ImportError as exc:
        raise PPTXBuildError("python-pptx package is not installed") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    presentation = Presentation()
    plan_by_article = {plan.article_id: plan for plan in slide_plans}

    for summary in summaries:
        slide = presentation.slides.add_slide(presentation.slide_layouts[6])
        title_box = slide.shapes.add_textbox(
            Inches(0.45),
            Inches(0.35),
            Inches(12.4),
            Inches(0.8),
        )
        title_frame = title_box.text_frame
        title_frame.text = summary.title
        title_frame.paragraphs[0].font.size = Pt(24)
        title_frame.paragraphs[0].font.bold = True

        topic_box = slide.shapes.add_textbox(Inches(0.65), Inches(1.1), Inches(8.2), Inches(0.35))
        topic_frame = topic_box.text_frame
        topic_frame.text = f"주제: {summary.topic or summary.issue_id}"
        topic_frame.paragraphs[0].font.size = Pt(10)

        body_box = slide.shapes.add_textbox(Inches(0.65), Inches(1.55), Inches(8.0), Inches(2.2))
        body_frame = body_box.text_frame
        body_frame.word_wrap = True
        body_frame.text = f"기사 내용 정리\n{summary.summary}"
        body_frame.paragraphs[0].font.size = Pt(11)
        body_frame.paragraphs[0].font.bold = True
        if len(body_frame.paragraphs) > 1:
            body_frame.paragraphs[1].font.size = Pt(16)

        conclusion_box = slide.shapes.add_textbox(
            Inches(0.65),
            Inches(4.05),
            Inches(8.0),
            Inches(1.6),
        )
        conclusion_frame = conclusion_box.text_frame
        conclusion_frame.word_wrap = True
        conclusion_frame.text = f"결론 및 시사점\n{summary.conclusion}"
        conclusion_frame.paragraphs[0].font.size = Pt(11)
        conclusion_frame.paragraphs[0].font.bold = True
        if len(conclusion_frame.paragraphs) > 1:
            conclusion_frame.paragraphs[1].font.size = Pt(14)

        meta_box = slide.shapes.add_textbox(
            Inches(0.65),
            Inches(6.65),
            Inches(12.0),
            Inches(0.35),
        )
        meta_frame = meta_box.text_frame
        meta_frame.text = (
            f"PDF: {summary.pdf_source} | 기사 출처: {summary.source} | URL: {summary.url}"
        )
        meta_frame.paragraphs[0].font.size = Pt(8)

        plan = plan_by_article.get(summary.article_id)
        if not _try_add_article_image(slide, summary, Inches(9.05), Inches(1.45), Inches(3.6)):
            visual_text = _visual_label(summary, plan)
            visual_box = slide.shapes.add_textbox(
                Inches(9.1),
                Inches(1.4),
                Inches(3.4),
                Inches(3.2),
            )
            visual_frame = visual_box.text_frame
            visual_frame.text = visual_text
            visual_frame.paragraphs[0].font.size = Pt(13)

    presentation.save(output_path)
    return output_path


def _validate_output_path(output_path: Path) -> None:
    normalized = output_path.as_posix()
    if "/data/output/" not in f"/{normalized}":
        raise PPTXBuildError("PPTX output must be written under data/output")


def _validate_summary(summary: ArticleSummary) -> None:
    if not summary.source or not summary.url:
        raise PPTXBuildError(
            f"slide metadata missing for article {summary.article_id}: source and url required"
        )
    if (
        not summary.pdf_source
        or not summary.topic
        or not summary.pdf_summary
        or not summary.conclusion
    ):
        raise PPTXBuildError(
            f"slide metadata missing for article {summary.article_id}: "
            "pdf_source, topic, pdf_summary, and conclusion required"
        )


def _visual_label(summary: ArticleSummary, plan: SlidePlan | None) -> str:
    if summary.image_url:
        return f"Article image unavailable:\n{summary.image_url}"
    if plan is not None and plan.visual_type:
        return f"Visual plan:\n{plan.visual_type}"
    return "Visual plan:\nsource thumbnail or generated chart"


def _try_add_article_image(
    slide: object,
    summary: ArticleSummary,
    left: object,
    top: object,
    width: object,
) -> bool:
    if not summary.image_url:
        return False
    try:
        image_data = _image_bytes(summary.image_url)
        slide.shapes.add_picture(image_data, left, top, width=width)
    except Exception:
        return False
    return True


def _image_bytes(image_url: str) -> BytesIO | str:
    if image_url.startswith(("http://", "https://")):
        with urlopen(image_url, timeout=10) as response:
            return BytesIO(response.read())
    path = Path(image_url)
    if not path.exists():
        raise FileNotFoundError(image_url)
    return str(path)
