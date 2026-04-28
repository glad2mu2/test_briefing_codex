# Python 환경 설정 가이드

작성일: 2026-04-28
대상: `python, py, uv, pip, conda, winget 모두 PATH에 없음` 오류로 막힌 사용자

---

## 1. 결론 먼저

| 환경 | Python 상태 | 설명 |
|------|-------------|------|
| **WSL (Ubuntu)** | ✅ 설치됨 (`/usr/bin/python3`, 3.12.3) | 이 뉴스레터 프로젝트가 사용 중 |
| **Windows (PowerShell/CMD)** | ❌ 미설치 | MS Store placeholder만 존재 → 다른 프로젝트가 막히는 원인 |

→ **이 프로젝트는 WSL 안에서 돌아가고 있어서 문제가 없는 것**이고,
   Windows에서 새 Python 프로젝트를 시작하려면 **Windows에 Python을 따로 설치**해야 합니다.

---

## 2. 이 프로젝트(newsletter_team_agent)는 어떻게 Python을 쓰는가

### 2.1 WSL의 시스템 Python 사용

```bash
# WSL 터미널에서 확인
$ which python3
/usr/bin/python3

$ python3 --version
Python 3.12.3
```

### 2.2 가상환경(`.venv/`)

프로젝트 루트의 `.venv/`는 WSL 시스템 Python으로 만든 venv입니다.

```
.venv/pyvenv.cfg 내용:
  home = /usr/bin
  version = 3.12.3
  executable = /usr/bin/python3.12
  command = /usr/bin/python3 -m venv .../.venv
```

여기에 `requirements.txt`의 패키지(anthropic, openpyxl, weasyprint, flask, pytest …)가
설치돼 있고, `orchestrator.py`·`agents/*.py`가 이걸 사용합니다.

### 2.3 실제 사용 흐름

```bash
# WSL 터미널을 켜고 프로젝트 폴더로 이동
cd /mnt/c/Users/cmuser/Desktop/test_heewoo/newsletter_team_agent-main

# 가상환경 활성화 (선택 — 안 해도 동작은 함)
source .venv/bin/activate

# 파이프라인 실행
python orchestrator.py --step 1
```

> ⚠️ **PowerShell/CMD에서 이 프로젝트를 직접 돌리지 마세요.**
> WSL 안에서 만든 venv고, 의존성(WeasyPrint의 GTK3 등)도 Linux 라이브러리에 묶여 있습니다.

---

## 3. 다른 프로젝트(Windows)에서 Python 쓰려면

선택지 3가지. 가장 추천하는 순서로 정렬했습니다.

### 옵션 A. 공식 Python 설치 (가장 안정적, 추천)

1. https://www.python.org/downloads/windows/ 접속
2. 최신 안정판(예: Python 3.12.x) **Windows installer (64-bit)** 다운로드
3. 설치 마법사 실행 시 **반드시 체크**:
   - ✅ **Add python.exe to PATH** (맨 아래 체크박스, 기본 해제돼 있음 — 꼭 켜기)
   - ✅ Install for all users (선택)
4. 설치 완료 후 **새 PowerShell 창**을 열고 검증:
   ```powershell
   python --version
   pip --version
   py --version          # Windows 런처
   ```
5. MS Store placeholder가 우선순위를 빼앗는 경우:
   - `설정 → 앱 → 고급 앱 설정 → 앱 실행 별칭` 에서
     **App Installer / Python 3, Python (Windows)** 두 항목을 **OFF**

### 옵션 B. winget 으로 설치 (winget이 있다면)

> 현재는 winget도 PATH에 없다고 하니 사실상 옵션 A로 가는 게 빠릅니다.
> 그래도 winget이 살아 있다면:
```powershell
winget install Python.Python.3.12
```
설치 후 새 터미널 창을 여세요.

`winget`이 정말 없다면 → MS Store에서 **App Installer**를 검색해 설치하면 winget이 같이 들어옵니다.

### 옵션 C. uv 사용 (모던 Python 매니저, 빠름)

uv는 Python 자체도 설치해주는 도구입니다.

```powershell
# PowerShell에서 (관리자 권한 X)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 새 터미널 열고
uv --version
uv python install 3.12        # Python 3.12 자동 설치
uv venv                        # 현재 폴더에 .venv 만들기
uv pip install <패키지명>
```

### 옵션 D. Anaconda / Miniconda (데이터 분석용)

머신러닝/데이터 분석 비중이 크다면:
- Miniconda: https://docs.conda.io/en/latest/miniconda.html
- 설치 후 `Anaconda Prompt` 사용

---

## 4. 설치 후 새 프로젝트 시작하는 표준 절차 (Windows)

```powershell
# 1) 프로젝트 폴더로 이동
cd C:\Users\cmuser\Desktop\새프로젝트

# 2) 가상환경 만들기
python -m venv .venv

# 3) 활성화
.\.venv\Scripts\Activate.ps1
# (만약 실행 정책 오류 나면 한 번만:)
# Set-ExecutionPolicy -Scope CurrentUser RemoteSigned

# 4) 패키지 설치
pip install --upgrade pip
pip install <필요한 패키지>

# 5) requirements 저장
pip freeze > requirements.txt

# 6) 비활성화
deactivate
```

---

## 5. 자주 겪는 문제 & 해결

| 증상 | 원인 | 해결 |
|------|------|------|
| `python` 입력 시 MS Store가 열림 | WindowsApps placeholder가 진짜 Python보다 PATH 우선순위 높음 | 설정 → 앱 실행 별칭에서 Python 항목 OFF |
| `python --version`은 되는데 `pip` 안 됨 | 설치 시 pip 옵션 누락 | 설치 마법사 다시 실행 → Modify → ensure pip 체크 |
| 설치는 했는데 PATH에 없음 | 설치 시 "Add to PATH" 체크 누락 | 인스톨러 다시 실행 → Modify → Add to PATH 체크 |
| `Activate.ps1` 실행 정책 오류 | PowerShell 기본 정책이 Restricted | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| WSL과 Windows의 Python을 혼동 | venv는 만든 OS에서만 동작 | WSL `.venv`는 WSL에서, Windows `.venv`는 Windows에서 |

---

## 6. 빠른 의사결정 트리

```
새 프로젝트가 어디서 돌아가나?
├─ WSL/Linux 안에서 → 이 프로젝트와 동일한 방식 (apt python3 + venv)
└─ Windows PowerShell/CMD에서 →
    ├─ 단순 스크립트/웹 → 옵션 A (공식 인스톨러)  ← 가장 추천
    ├─ 패키지 관리 자동화 원함 → 옵션 C (uv)
    └─ 데이터 분석/머신러닝 → 옵션 D (Miniconda)
```

---

## 7. 참고

- 이 프로젝트의 WSL 셋업 스크립트: `setup.sh` (WeasyPrint용 GTK3 등 시스템 의존성 포함)
- 이 프로젝트의 Python 패키지 목록: `requirements.txt`
- 이 프로젝트가 다른 OS로 이식이 필요하다면 별도 검토 필요 (WeasyPrint의 Windows 설치는 까다로움)
