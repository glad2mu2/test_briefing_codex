# CODEX_WORKFLOW.md

This is the primary no-API workflow for creating briefing PPTs inside the Codex app.

## Concept

The user asks Codex to prepare a weekly construction briefing. Codex reads the uploaded PDFs and any user-provided source files, organizes PDF issues by topic, collects related recent domestic articles with web tools, then writes a local briefing manifest. The project code turns that manifest into both an XLSX research table and a PPTX deck.

This avoids putting `OPENAI_API_KEY` into the project and avoids automatic API billing from the local app.

## User Request Pattern

Ask Codex something like:

```text
uploads 폴더의 PDF를 읽고 건설업 주간 브리핑 PPT를 만들어줘.
경영진 보고용으로 10장 이내, 각 슬라이드에는 제목/출처/URL/200자 요약을 넣어줘.
API 자동 실행 말고 Codex-assisted 방식으로 진행해줘.
```

## Codex Steps

1. Inspect `uploads/` and any user-mentioned files.
2. Extract key construction issues and organize them by topic.
3. Collect recent related Korean domestic articles for each topic/issue with web tools.
4. Keep article summaries at 200 Korean characters or fewer.
5. Include article title, source, original URL, article summary, conclusion/implication, and image URL when available.
6. Write a manifest JSON under `data/articles/codex_briefing_manifest.json`.
7. Run:

```powershell
.\.venv\Scripts\python.exe -m src.main `
  --mode codex_assisted `
  --manifest .\data\articles\codex_briefing_manifest.json
```

8. Return both generated files to the user:
   - `data/output/briefing_YYYYMMDD_v{version}.xlsx`
   - `data/output/briefing_YYYYMMDD_v{version}.pptx`

## XLSX Columns

The generated XLSX must use these exact columns:

```text
PDF Source
주제
내용 요약
기사 제목
기사 원본URL
기사 출처
기사 내용 정리
결론 및 시사점
```

## Domestic Article Source Priority

Related article collection must use domestic articles and follow this order:

1. 대한경제: `https://www.dnews.co.kr/`
2. 한국경제 부동산 RSS: `https://www.hankyung.com/feed/realestate`
3. 한국경제 경제 RSS: `https://www.hankyung.com/feed/economy`
4. 서울경제 부동산 RSS: `https://www.sedaily.com/rss/realestate`
5. 서울경제 경제 RSS: `https://www.sedaily.com/rss/economy`
6. 연합뉴스 최신기사 RSS: `https://www.yna.co.kr/rss/news.xml`
7. 국토일보 RSS: `http://www.ikld.kr/rss/allArticle.xml`
8. 네이버 뉴스: `https://news.naver.com/`

Use lower-priority sources only when higher-priority sources do not have a relevant article.
Use Naver News as a fallback discovery surface; prefer the original press URL when available.

## Runtime Notes

- Prefer `.\.venv\Scripts\python.exe` for this workspace.
- Do not assume `python`, `py`, `uv`, or `pip` are on PATH.
- If setup is broken, consult `python_setup_guide.md`; the safest Windows fix is official Python with `Add python.exe to PATH`.
- Do not use a WSL-created `.venv` from PowerShell, or a Windows-created `.venv` from WSL.

## Manifest Format

```json
{
  "title": "건설업 주간 브리핑",
  "articles": [
    {
      "article_id": "article-1",
      "issue_id": "issue-1",
      "pdf_source": "PDF 출처명",
      "topic": "주제",
      "pdf_summary": "PDF 주요 내용 요약",
      "article_title": "기사 제목",
      "article_url": "https://www.dnews.co.kr/",
      "article_source": "대한경제",
      "article_summary": "200자 이내 기사 내용 정리",
      "conclusion": "결론 및 시사점",
      "image_url": null
    }
  ]
}
```

## API Mode

`api_auto` remains optional for future automation. It requires `OPENAI_API_KEY` and may incur API charges.
