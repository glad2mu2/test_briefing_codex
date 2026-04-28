# CODEX_WORKFLOW.md

This is the primary no-API workflow for creating briefing PPTs inside the Codex app.

## Concept

The user asks Codex to prepare a weekly construction briefing. Codex reads the uploaded PDFs and any user-provided source files, researches or summarizes with the tools available in the Codex session, then writes a local briefing manifest. The project code only turns that manifest into a PPTX.

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
2. Extract key construction issues and related articles manually within the Codex session.
3. Keep news summaries at 200 Korean characters or fewer.
4. Include source name and original URL for every slide.
5. Write a manifest JSON under `data/articles/codex_briefing_manifest.json`.
6. Run:

```powershell
.\.venv\Scripts\python.exe -m src.main `
  --mode codex_assisted `
  --manifest .\data\articles\codex_briefing_manifest.json
```

7. Return the generated `data/output/briefing_YYYYMMDD_v{version}.pptx` path to the user.

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
      "title": "슬라이드 제목",
      "source": "출처명",
      "url": "https://example.com/or/source-file",
      "summary": "200자 이내 한국어 요약",
      "image_url": null
    }
  ]
}
```

## API Mode

`api_auto` remains optional for future automation. It requires `OPENAI_API_KEY` and may incur API charges.
