import os

# ─── API / 인증 ───────────────────────────────────────────────
BIZINFO_API_KEY = os.getenv("BIZINFO_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
LLM_MATCHING = os.getenv("LLM_MATCHING", "false").lower() == "true"

# ─── 이메일 ──────────────────────────────────────────────────
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
EMAIL_RECIPIENTS = [
    r.strip()
    for r in os.getenv("EMAIL_RECIPIENTS", "").split(",")
    if r.strip()
]

# ─── DB ──────────────────────────────────────────────────────
DB_PATH = os.getenv("DB_PATH", "subsidy_crawler.db")
DATA_DIR = os.getenv("DATA_DIR", "data")

# ─── 매칭 ────────────────────────────────────────────────────
MATCH_SCORE_THRESHOLD = int(os.getenv("MATCH_SCORE_THRESHOLD", "50"))

# ─── 크롤링 사이트 (15개) ────────────────────────────────────
CRAWL_SITES = [
    # ★★★ 1순위 — 통합 포털 / 직접 지원사업
    {
        "id": "bizinfo",
        "name": "기업마당",
        "url": "https://www.bizinfo.go.kr",
        "list_url": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/list.do",
        "api_url": "https://www.bizinfo.go.kr/uss/rss/bizinfoApi.do",
        "crawler_type": "api",
        "org": "중소벤처기업부",
        "priority": 1,
    },
    {
        "id": "cloudsup",
        "name": "클라우드서비스 지원포털",
        "url": "https://www.cloudsup.or.kr",
        "list_url": "https://www.cloudsup.or.kr/information/notice",
        "crawler_type": "html",
        "org": "과기정통부 / NIPA",
        "priority": 1,
    },
    {
        "id": "nipa",
        "name": "정보통신산업진흥원 (NIPA)",
        "url": "https://www.nipa.kr",
        "list_url": "https://www.nipa.kr/biz/listBiz.do",
        "crawler_type": "playwright",
        "org": "과기정통부",
        "priority": 1,
    },
    {
        "id": "nia",
        "name": "한국지능정보사회진흥원 (NIA)",
        "url": "https://www.nia.or.kr",
        "list_url": "https://www.nia.or.kr/site/nia_kor/ex/bbs/ListBusiness.do?businessMnCd=23000200",
        "crawler_type": "playwright",
        "org": "과기정통부",
        "priority": 1,
    },
    {
        "id": "kdata",
        "name": "한국데이터산업진흥원 (K-DATA)",
        "url": "https://www.kdata.or.kr",
        "list_url": "https://www.kdata.or.kr/kr/board/notice_01/boardList.do",
        "crawler_type": "html",
        "org": "과기정통부",
        "priority": 1,
    },

    # ★★★ 2순위 — R&D / 기술개발
    {
        "id": "smtech",
        "name": "중소기업기술정보진흥원 (TIPA)",
        "url": "https://www.smtech.go.kr",
        "list_url": "https://www.smtech.go.kr/front/ifg/no/notice01_list.do",
        "crawler_type": "html",
        "org": "중소벤처기업부",
        "priority": 2,
    },
    {
        "id": "mssmiv",
        "name": "중소기업기술개발사업 종합관리시스템 (SMIV)",
        "url": "https://www.mssmiv.com",
        "list_url": "https://www.mssmiv.com/portal/board/BoardList?bbsId=1",
        "crawler_type": "html",
        "org": "중소벤처기업부",
        "priority": 2,
    },
    {
        "id": "iitp",
        "name": "정보통신기획평가원 (IITP)",
        "url": "https://www.iitp.kr",
        "list_url": "https://www.iitp.kr/kr/1/business/list.it",
        "crawler_type": "playwright",
        "org": "과기정통부",
        "priority": 2,
    },
    {
        "id": "kisa",
        "name": "한국인터넷진흥원 (KISA)",
        "url": "https://www.kisa.or.kr",
        "list_url": "https://www.kisa.or.kr/401",
        "crawler_type": "playwright",
        "org": "과기정통부",
        "priority": 2,
    },
    {
        "id": "kiat",
        "name": "한국산업기술진흥원 (KIAT)",
        "url": "https://www.kiat.or.kr",
        "list_url": "https://www.kiat.or.kr/front/board/boardContentsListPage.do?board_id=90",
        "crawler_type": "playwright",
        "org": "산업통상자원부",
        "priority": 2,
    },
    # ★★☆ 3순위 — 창업 / 소상공인 지원
    {
        "id": "kstartup",
        "name": "K-Startup 창업지원포털",
        "url": "https://www.k-startup.go.kr",
        "list_url": "https://www.k-startup.go.kr/web/contents/bizpbanc-ongoing.do",
        "crawler_type": "playwright",
        "org": "중소벤처기업부",
        "priority": 3,
    },
    {
        "id": "semas",
        "name": "소상공인시장진흥공단",
        "url": "https://www.semas.or.kr",
        "list_url": "https://www.semas.or.kr/web/board/webBoardList.kmdc?bCd=2001&pNm=BOA0101",
        "crawler_type": "playwright",
        "org": "중소벤처기업부",
        "priority": 3,
    },
    # 제거된 사이트:
    # - iris: 로그인 필수 (인증 불가)
    # - koneps: SSO 인증 필수 (공개 접근 불가)
    # - smartfactory: 완전 SPA (URL 없음)
]

# ─── 제품 & 키워드 (5개 제품) ────────────────────────────────
PRODUCTS = {
    "오피스에이전트": {
        "tags": [
            "AI", "인공지능", "RAG", "LLM", "대화형", "챗봇", "에이전트",
            "문서검색", "업무자동화", "자동화", "지식관리", "생성형AI", "GPT",
            "자연어처리", "NLP", "SaaS", "클라우드", "디지털전환", "DX",
            "AI바우처", "AI통합바우처",
        ],
        "weight": 1.5,
    },
    "오피스키퍼": {
        "tags": [
            "DLP", "정보유출방지", "내부정보유출방지", "보안", "PC보안",
            "정보보호", "개인정보", "엔드포인트", "보안관제", "데이터보안",
        ],
        "weight": 1.2,
    },
    "오피스넥스트": {
        "tags": [
            "협업", "메신저", "그룹웨어", "SaaS", "클라우드", "업무환경",
            "스마트워크", "재택근무", "원격근무", "디지털전환",
        ],
        "weight": 1.0,
    },
    "나모에디터": {
        "tags": [
            "웹에디터", "HTML5", "콘텐츠", "웹표준", "공공기관",
            "전자정부", "웹접근성", "CMS",
        ],
        "weight": 1.0,
    },
}

# ─── 동의어 사전 ──────────────────────────────────────────────
KEYWORD_SYNONYMS = {
    "AI": ["인공지능", "머신러닝", "딥러닝", "생성형AI"],
    "인공지능": ["AI", "머신러닝", "딥러닝", "생성형AI"],
    "LLM": ["GPT", "생성형AI", "언어모델"],
    "보안": ["정보보호", "사이버보안", "보안솔루션"],
    "DLP": ["정보유출방지", "내부정보유출방지", "문서보안"],
    "자동화": ["업무자동화", "RPA", "디지털전환"],
    "DX": ["디지털전환", "디지털혁신", "스마트화"],
    "SaaS": ["클라우드", "구독형", "서비스형소프트웨어"],
    "클라우드": ["SaaS", "PaaS", "IaaS"],
    "협업": ["그룹웨어", "메신저", "협업툴"],
    "공공기관": ["전자정부", "행정기관", "지자체"],
}
