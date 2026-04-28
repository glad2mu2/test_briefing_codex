# SCM-WCB 디자인 규칙 v8 (표준)

> 2026-04-24 영구 반영. 이후 모든 주간 브리핑 PPTX는 이 규칙을 준수한다.

---

## 1. 폰트

| 요소 | 폰트 | 크기 | 색상 | 정렬·기타 |
|------|------|------|------|----------|
| 본문 | **나눔스퀘어 Bold** | **14pt** | `#000000` | bold=False |
| 제목(헤더) | 나눔스퀘어 Bold | 20pt | `#000000` | 중앙 정렬 + MIDDLE anchor |
| 한줄 요약 | 나눔스퀘어 Bold | 14pt | **`#2212FF`** | **좌측 정렬** |
| 날짜·출처 | 나눔스퀘어 Bold | 13pt | `#77787B` | **우측 정렬** + BOTTOM anchor |
| 차트 텍스트 | 나눔스퀘어 Bold | 14pt | `#000000` | 제목·축·범례·데이터 라벨 |
| 표 헤더 | 나눔스퀘어 Bold | 14pt | `#FFFFFF` | 배경 `#7F7F7F` |
| 표 본문 | 나눔스퀘어 Bold | 14pt | `#000000` | 배경 `#FFFFFF` |

> ★ Bold 속성은 전체 False. 폰트 패밀리 자체가 Bold 웨이트.
> ★ 기존 `NanumSquare_acB` / `NanumSquare_ac Bold` 사용 금지.

---

## 2. 컬러

| 이름 | HEX | 용도 |
|------|-----|------|
| 네이비 | `#1F3864` | 차트 주색 |
| 골드 | `#BF9000` | 차트 보조색 |
| 연네이비 | `#4A6EA0` | 차트 3차색 |
| 진회색 | `#7F7F7F` | 표 헤더 배경, 다크 그레이 |
| 콘텐츠 배경 | `#F2F2F2` | 헤더/콘텐츠 박스 |
| 윤곽선 | `#AFABAB` | 박스 테두리 |
| 메타 회색 | `#77787B` | 날짜/출처 텍스트 |
| 강조 파랑 | `#2212FF` | 한줄 요약 (유일한 강조) |
| 표 셀 테두리 | `#000000` | 모든 셀 4변 0.25pt |

---

## 3. 헤더 박스 레이아웃 (필수)

```
┌─────────────────────────────────────────────┐ y=0.25"
│                                             │
│          [제목 20pt 가운데 정렬]             │ 제목 영역 y=0.25~0.95"
│                                             │
│                              [출처 13pt ▶]  │ 출처 영역 y=0.90~1.18" 우측정렬
└─────────────────────────────────────────────┘ y=1.20"
▶ [한줄 요약 14pt 파랑 좌측정렬]                y=1.28~1.68"
┌─────────────────────────────────────────────┐ y=1.75"
│                                             │
│            [콘텐츠 박스 #F2F2F2]              │
│                                             │
└─────────────────────────────────────────────┘ y=7.35"
```

- 헤더 박스: `(0.3", 0.25")` 크기 `12.73" × 0.95"`
- 콘텐츠 박스: `(0.35", 1.75")` 크기 `12.6" × 5.6"`
- 콘텐츠 영역 실제 사용: `y=1.95"~7.25"` (높이 5.30")

---

## 4. 이슈 슬라이드 섹션 구성 (번호형)

```
1. 배경 / 맥락          (서술형 3~5줄)
2. 핵심 팩트            (수치 포함 5~7개 불렛)
3. [당사 함의] So What  (수주 기회 / 리스크 / 대응)
4. 당사 Action Items    (3~5개 구체 과제)
```

---

## 5. 좌우 2단 레이아웃 기준

| 요소 | 좌측 | 우측 |
|------|------|------|
| 시작 x | `0.55"` | `7.00"` |
| 너비 | `6.30"` | `5.98"` |
| 여백 (PAD) | — | 좌측과 **0.15"** 간격 |

- 좌우 간 최소 0.15" 간격으로 차트·표와 텍스트가 간섭하지 않도록 배치
- 유동 배치(상/하/좌/우)로 슬라이드 간 단조로움 제거

---

## 6. 표(Table) 테두리 규정 ★ PowerPoint 호환

### 필수 작업 2단계

1. **tableStyleId 제거**
   ```python
   def remove_table_style(table):
       tbl = table._tbl
       tblPr = tbl.find(qn('a:tblPr'))
       if tblPr is not None:
           for sid in tblPr.findall(qn('a:tableStyleId')):
               tblPr.remove(sid)
           for attr in ('firstRow','firstCol','lastRow','lastCol','bandRow','bandCol'):
               if attr in tblPr.attrib: tblPr.attrib[attr] = '0'
   ```

2. **모든 셀 4변에 line element 삽입** (0.25pt = 3175 EMU)
   ```xml
   <a:tcPr>
     <a:lnL w="3175" cap="flat" cmpd="sng" algn="ctr">
       <a:solidFill><a:srgbClr val="000000"/></a:solidFill>
       <a:prstDash val="solid"/>
       <a:round/>
       <a:headEnd type="none" w="med" len="med"/>
       <a:tailEnd type="none" w="med" len="med"/>
     </a:lnL>
     <a:lnR .../>
     <a:lnT .../>
     <a:lnB .../>
     <a:solidFill>...</a:solidFill>
   </a:tcPr>
   ```

> 요소 순서: `lnL → lnR → lnT → lnB` (OOXML 스키마 순서 준수)
> `a:fill` 앞에 line 요소들 배치

---

## 7. 차트(Chart) 규정

- python-pptx **네이티브 차트** 우선 사용 (PNG 이미지 지양)
- 허용 타입: `COLUMN_CLUSTERED`, `BAR_CLUSTERED`, `DOUGHNUT`, `LINE`
- 텍스트(제목·축·범례·데이터 라벨) 모두 14pt 나눔스퀘어 Bold
- 데이터 라벨 위치: OUTSIDE_END
- 시리즈 색상: 고정 팔레트 사용
- 그림자·외부 효과 제거 (`effectLst` 빈 노드 삽입)

---

## 8. 보고용 브리핑 명시

- 표지 부제: `[보고용 주간 브리핑 자료]`
- 푸터: `삼우씨엠(SAMOO CM) 전략사업그룹 | 2026-WNN Weekly Construction Briefing | 보고용 브리핑 자료`

---

## 9. 품질 체크리스트

- [ ] 폰트 100% `나눔스퀘어 Bold` (bold=False)
- [ ] 본문 14pt 통일
- [ ] 한줄 요약 파랑 14pt 좌측 정렬
- [ ] 출처 헤더 박스 내 우측 하단 13pt
- [ ] 표 전 셀 검정 0.25pt 테두리 (tableStyleId 제거 확인)
- [ ] 차트·텍스트 최소 0.15" 여백
- [ ] 차트는 네이티브 python-pptx 차트 (PNG 이미지 지양)
- [ ] 그림자·외부 효과 없음
- [ ] 빈 공간 없음 (좌/우/상/하 유동 배치)
- [ ] 이슈 슬라이드 번호형 섹션 (1.배경 2.팩트 3.So What 4.Action)
- [ ] 15±2 슬라이드 구성 (표지 + Exec + 카테고리 + 이슈 N + 차주)

---

## 10. 표준 빌더 스크립트

- 경로: `03_Templates\visualization_scripts\build_pptx_standard.py`
- 실행: `WEEK_DIR=/path/to/이번주폴더 python3 build_pptx_standard.py`
- 출력: `{WEEK_DIR}/05_outputs/주간 뉴스 브리핑.pptx`
