# 정부 지원사업 자동 매칭 크롤러

지란소프트 제품과 연관된 정부 지원사업 공고를 자동으로 수집·분석하여, 담당자에게 이메일로 알려주는 내부 자동화 도구입니다.

---

## 목차

1. [개요](#개요)
2. [크롤링 대상 사이트](#크롤링-대상-사이트)
3. [매칭 기준](#매칭-기준)
4. [이메일 알림](#이메일-알림)
5. [설치 방법](#설치-방법)
6. [사용 방법](#사용-방법)
7. [설정 변경](#설정-변경)
8. [자동 실행 스케줄](#자동-실행-스케줄)

---

## 개요

```
크롤링 → 매칭 → 이메일 발송
   ↓         ↓          ↓
공고 수집   제품 연관성  담당자에게
(DB 저장)   점수 계산    HTML 메일
```

- 수집한 공고를 SQLite DB에 저장하고 중복 제거
- 제품별 키워드로 연관 점수 계산 (기본 임계값: 40점)
- 신규 매칭 공고만 선별하여 이메일 발송 (중복 발송 없음)

---

## 크롤링 대상 사이트

총 **15개** 사이트를 크롤링합니다.

### ★★★ 1순위 — 통합 포털 / 직접 지원사업

| 사이트 | 기관 | 특징 | 크롤링 방식 |
|--------|------|------|------------|
| **기업마당** (bizinfo.go.kr) | 중소벤처기업부 | 전 분야 지원사업 통합 포털, 공식 REST API 제공 | REST API → HTML 폴백 |
| **클라우드서비스 지원포털** (cloudsup.or.kr) | 과기정통부/NIPA | 클라우드 바우처, AI 통합 바우처 전담 | HTML 파싱 |
| **NIPA** (nipa.kr) | 과기정통부 | AI 바우처, SW 성장지원, 클라우드 SaaS 개발 역량지원 | Playwright |
| **NIA** (nia.or.kr) | 과기정통부 | 데이터바우처, AI 학습데이터, 디지털 전환 사업 | Playwright |
| **K-DATA** (kdata.or.kr) | 과기정통부 | 데이터바우처 지원사업 (공급기업/수요기업) | Playwright |

### ★★★ 2순위 — R&D / 기술개발

| 사이트 | 기관 | 특징 | 크롤링 방식 |
|--------|------|------|------------|
| **TIPA** (smtech.go.kr) | 중소벤처기업부 | 중소기업 R&D, 창업성장기술개발, 기술혁신 | HTML 파싱 |
| **SMIV** (mssmiv.com) | 중소벤처기업부 | 중소기업 기술개발 사업공고 통합 관리 | HTML 파싱 |
| **IITP** (iitp.kr) | 과기정통부 | ICT·AI R&D 과제 사업공고 | HTML 파싱 |
| **KISA** (kisa.or.kr) | 과기정통부 | 정보보호, 개인정보보호, 보안 지원사업 | HTML 파싱 |
| **KIAT** (kiat.or.kr) | 산업통상자원부 | 산업AI 혁신, 산업 DX 관련 R&D | Playwright |
| **IRIS** (iris.go.kr) | 과기정통부 | 국가 R&D 과제 통합 공고 (AI, ICT 포함) | HTML 파싱 |

### ★★☆ 3순위 — 조달 / 특화 지원

| 사이트 | 기관 | 특징 | 크롤링 방식 |
|--------|------|------|------------|
| **K-Startup** (k-startup.go.kr) | 중소벤처기업부 | 창업 관련 정부사업 공고 포털 (SPA) | Playwright |
| **나라장터** (g2b.go.kr) | 조달청 | 공공조달 입찰 공고 (AI/SW/보안) | Playwright |
| **소상공인시장진흥공단** (semas.or.kr) | 중소벤처기업부 | 소상공인 디지털전환, 스마트상점 지원 | Playwright |
| **스마트공장** (smart-factory.kr) | 중소벤처기업부 | 스마트공장 구축, 클라우드 제조솔루션 | Playwright |

### 수집 항목

각 공고에서 다음 정보를 수집합니다:

| 항목 | 설명 |
|------|------|
| 공고명 | 지원사업 제목 |
| 출처 사이트 | 수집 사이트 ID |
| 공고 URL | 원문 링크 |
| 마감일 | 접수 마감 날짜 |
| 주관 기관 | 사업 주관 부처/기관명 |
| 사업 요약 | 공고 내용 요약 (최대 500자) |
| 수집 일시 | 크롤링 시각 (UTC) |

### 기업마당 API vs HTML 폴백

기업마당은 공식 REST API를 우선 사용합니다.

```
API 키 유효 → REST API 사용 (정형 데이터, 요약 포함)
API 키 없음 → HTML 파싱 폴백 (제목·링크·마감일만 수집)
```

API 키는 [bizinfo.go.kr](https://www.bizinfo.go.kr) 에서 신청 (승인 1~3 영업일 소요).

---

## 매칭 기준

### 대상 제품 및 키워드

`config/settings.py`의 `PRODUCTS`에 정의된 제품별 키워드로 매칭합니다.

| 제품 | 주요 키워드 | 가중치 |
|------|------------|--------|
| **오피스에이전트** | AI, RAG, LLM, 챗봇, 에이전트, 문서검색, 업무자동화, 생성형AI, GPT, SaaS, DX, AI바우처 | 1.5× |
| **오피스키퍼** | DLP, 정보유출방지, 보안, PC보안, 정보보호, 개인정보, 엔드포인트, 데이터보안 | 1.2× |
| **오피스넥스트** | 협업, 메신저, 그룹웨어, SaaS, 클라우드, 스마트워크, 재택근무, 디지털전환 | 1.0× |
| **나모에디터** | 웹에디터, HTML5, 콘텐츠, 웹표준, 공공기관, 전자정부, 웹접근성, CMS | 1.0× |

### 점수 계산 방식

```
매칭 점수 = (제목 키워드 점수 × 2) + (요약 키워드 점수 × 1)

키워드 점수 = 매칭된 키워드 수 × 10 × 제품 가중치
```

- **제목 가중치 2배**: 제목에 키워드가 있으면 더 높은 점수
- **동의어 확장**: 예) `AI` → `인공지능`, `머신러닝`, `딥러닝` 자동 포함
- **기본 임계값**: 40점 이상인 공고만 알림 발송 (`MATCH_SCORE_THRESHOLD`)

### 점수 예시

| 공고명 | 매칭 키워드 | 점수 |
|--------|------------|------|
| **AI**모델개발사업 공고 | AI (제목) | 30점 |
| **AI·LLM** 기반 스타트업 지원 | AI, LLM (제목) | 60점 |
| 기업 **보안** 솔루션 R&D 지원 | 보안 (제목) | 20점 |

### 선택: LLM 기반 정밀 매칭

`.env`에서 `LLM_MATCHING=true` 설정 시 Claude AI가 공고 내용을 읽고 연관성을 추가로 판단합니다.

```
최종 점수 = (키워드 점수 × 0.5) + (LLM 판단 점수 × 0.5)
```

---

## 이메일 알림

### 발송 조건

- 임계값(기본 40점) 이상 매칭된 신규 공고만 발송
- 이미 발송된 공고는 재발송하지 않음

### 이메일 형식

HTML 카드 형식으로 발송됩니다. 점수 높은 순으로 정렬되며 각 공고는 카드로 표시됩니다.

```
[지란소프트] 정부 지원사업 매칭 리포트 (2026-03-06) — N건

┌─ 다크 헤더 ─────────────────────────────────────┐
│  정부 지원사업 매칭 리포트                         │
│  2026년 03월 06일 수집 기준                        │
├─ 파란 요약 배너 ────────────────────────────────┤
│  이번 주기 신규 공고  N건 매칭 · 최고 점수  85점   │
│  [오피스에이전트 3건] [오피스키퍼 1건]             │
├─ 공고 카드 (점수 높은 순) ──────────────────────┤
│  1. AI·LLM 기반 스타트업 지원    ●85             │
│     smtech · 마감 2026-04-01    (매칭점수)        │
│     [오피스에이전트]  #ai  #llm                   │
│  2. 기업 보안 솔루션 R&D 지원    ●60             │
│     ...                                          │
└─────────────────────────────────────────────────┘
```

매칭 점수에 따라 색상이 달라집니다: **초록(90+)**, **파랑(75+)**, **주황(60+)**, **회색(60 미만)**

### 미리보기

발송 전에 HTML 파일로 미리 확인할 수 있습니다:

```bash
python main.py preview
# data/email_preview_YYYYMMDD_HHMMSS.html 생성
```

---

## 설치 방법

### 방법 A: 로컬 직접 실행 (개발/테스트)

```bash
# 1. 가상환경 생성
py -m venv venv
venv/Scripts/activate        # Windows
# source venv/bin/activate   # Linux/Mac

# 2. 의존성 설치
pip install requests beautifulsoup4 lxml python-dotenv

# 3. Playwright 설치 (K-Startup 크롤링용)
pip install playwright
playwright install chromium

# 4. 환경 변수 설정
cp .env.example .env
# .env 파일 편집 (아래 설정 항목 참고)

# 5. DB 초기화
python main.py init
```

### 방법 B: Docker (운영 서버 권장)

```bash
# Docker 설치 후
cp .env.example .env
# .env 편집

docker compose up -d --build

# 로그 확인
docker compose logs -f crawler
```

---

## 사용 방법

### CLI 명령어

```bash
python main.py init       # DB 초기화 (최초 1회 필수)
python main.py run        # 전체 파이프라인 (크롤링 → 매칭 → 이메일)
python main.py crawl      # 크롤링만 실행
python main.py crawl --site bizinfo    # 특정 사이트만 크롤링
python main.py crawl --site kstartup  # K-Startup만
python main.py crawl --site smtech    # 중소기업기술정보진흥원만
python main.py match      # 매칭만 실행 (크롤링 후 사용)
python main.py notify     # 이메일 발송만
python main.py preview    # 이메일 미리보기 (HTML 파일 저장)
```

### 처음 시작하는 경우

```bash
python main.py init        # DB 초기화
python main.py crawl       # 전체 사이트 크롤링
python main.py preview     # 이메일 미리보기로 매칭 결과 확인
python main.py notify      # 이메일 발송
```

### 특정 사이트만 테스트하는 경우

```bash
python main.py crawl --site smtech    # smtech 크롤링
python main.py match                  # 매칭
python main.py preview                # 미리보기
```

### DB 직접 조회

```bash
sqlite3 subsidy_crawler.db

-- 최근 수집 공고 10건
SELECT title, source_site, deadline FROM announcements
ORDER BY crawled_at DESC LIMIT 10;

-- 매칭 점수 높은 순
SELECT a.title, m.product_name, m.match_score
FROM match_results m
JOIN announcements a ON a.content_hash = m.announcement_hash
ORDER BY m.match_score DESC LIMIT 10;

-- 크롤링 이력
SELECT site_id, status, items_found, new_items, finished_at
FROM crawl_log ORDER BY finished_at DESC LIMIT 10;

.exit
```

---

## 설정 변경

모든 설정은 `config/settings.py`와 `.env`에서 관리합니다.

### .env 필수 항목

```ini
BIZINFO_API_KEY=발급받은_인증키        # 기업마당 API 키
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SENDER_EMAIL=발송계정@gmail.com
SENDER_PASSWORD=앱비밀번호16자리       # Gmail 앱 비밀번호
EMAIL_RECIPIENTS=담당자1@jiransoft.co.kr,담당자2@jiransoft.co.kr
```

### .env 선택 항목

```ini
LLM_MATCHING=false                    # true 시 Claude AI 정밀 매칭 사용
ANTHROPIC_API_KEY=                    # LLM_MATCHING=true 일 때 필요
MATCH_SCORE_THRESHOLD=40              # 매칭 임계값 (낮출수록 더 많은 공고 알림)
```

### 수신자 변경

`.env`의 `EMAIL_RECIPIENTS`를 수정합니다 (쉼표 구분, 공백 없이):

```ini
EMAIL_RECIPIENTS=yh.ok@jiransoft.co.kr,mh.ko@jiransoft.co.kr,신규담당자@jiransoft.co.kr
```

Docker 사용 시 `docker compose restart` 필요.

### 제품 키워드 추가

`config/settings.py`의 `PRODUCTS`에서 수정:

```python
"오피스에이전트": {
    "tags": [
        "AI", "RAG", "LLM",
        "새로운키워드",    # 여기에 추가
    ],
    "weight": 1.5,
},
```

### 새 크롤링 사이트 추가

`config/settings.py`의 `CRAWL_SITES`에 추가:

```python
{
    "id": "new_site",
    "name": "사이트 이름",
    "url": "https://www.example.go.kr",
    "list_url": "https://www.example.go.kr/board/list",
    "crawler_type": "html",   # html | api | playwright
    "org": "소관 기관명",
    "priority": 2,
},
```

---

## 자동 실행 스케줄

**매주 화요일, 금요일 오전 10시 (KST)** 자동 실행

```cron
0 1 * * 2,5  →  python main.py run  (UTC 기준, KST 오전 10시)
```

- Docker: 컨테이너 내부 cron으로 자동 설정됨
- 직접 설치: `bash setup_cron.sh` 실행하면 자동 등록

스케줄 변경은 `Dockerfile` 또는 `setup_cron.sh`에서 cron 표현식 수정.

---

## 파일 구조

```
.
├── main.py              # CLI 진입점
├── crawler.py           # 사이트별 크롤러
├── matcher.py           # 키워드 매칭 엔진
├── notifier.py          # 이메일 발송 및 미리보기
├── database.py          # SQLite DB 레이어
├── utils.py             # 공통 유틸리티 (now_iso 등)
├── config/
│   └── settings.py      # 전체 설정 (제품, 사이트, 키워드)
├── data/                # 이메일 미리보기 HTML 저장
├── subsidy_crawler.db   # SQLite DB (자동 생성)
├── crawler.log          # 실행 로그
├── .env                 # 환경 변수 (Git 제외)
├── .env.example         # 환경 변수 템플릿
├── Dockerfile
├── docker-compose.yml
└── setup_cron.sh        # 크론 자동 설정 스크립트
```
