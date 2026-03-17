import hashlib
import logging
import re
import signal
import time

import requests
from bs4 import BeautifulSoup

from config.settings import BIZINFO_API_KEY, CRAWL_SITES
from database import log_crawl_start, log_crawl_finish, upsert_announcement
from utils import now_iso

logger = logging.getLogger(__name__)

PAGE_SIZE = 100
SITE_TIMEOUT_SEC = 120  # 사이트당 최대 2분

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# 사이트별 Playwright 목록 셀렉터 매핑
LIST_SELECTORS = {
    "kstartup": {
        "container": ".bizpbanc-list li, .list-wrap li, ul.biz-list li, .card-list li",
        "title": ".tit, .title, strong, h3, h4, .subject",
        "link": "a",
        "deadline": ".date, .deadline, .period, .end-date",
    },
    "iitp": {
        "container": ".board-list li, .list_area li, table tbody tr",
        "title": ".tit, .title, a, td:nth-child(2)",
        "link": "a",
        "deadline": ".date, td:last-child",
    },
    "kisa": {
        "container": "table tbody tr, .board-list li",
        "title": ".tit, .title, a, td:nth-child(2)",
        "link": "a",
        "deadline": "td:last-child, .date",
    },
}


def _make_hash(title: str, source_site: str) -> str:
    raw = f"{source_site}::{title}".encode("utf-8")
    return hashlib.md5(raw).hexdigest()


def _abs_url(href: str, base_url: str) -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href
    base = base_url.rstrip("/")
    path = href if href.startswith("/") else "/" + href
    return base + path


def _build_item(title: str, site: dict, href: str, deadline: str,
                org: str, summary: str) -> dict:
    return {
        "content_hash": _make_hash(title, site["id"]),
        "title": title,
        "source_site": site["id"],
        "url": href,
        "deadline": deadline,
        "org": org,
        "summary": summary,
        "crawled_at": now_iso(),
    }


def is_actual_support_program(title: str) -> bool:
    """
    제목 기반으로 실제 지원사업 여부 판단

    정보성 콘텐츠(동향, 리포트, 가이드 등)는 제외하고
    실제 지원금을 받을 수 있는 사업 공고만 True 반환

    Args:
        title: 공고 제목

    Returns:
        True: 실제 지원사업 공고
        False: 정보성 콘텐츠 (제외 대상)
    """
    # 제외할 키워드 (정보성 콘텐츠)
    exclude_keywords = [
        '동향', '보고서', 'report', '리포트',
        'lens', '가이드', '원칙', '분석',
        '뉴스', '소식', '이슈', '트렌드', '해외', '현황',
    ]

    # 포함해야 할 키워드 (실제 지원사업)
    include_keywords = [
        '지원사업', '공모', '신청', '모집',
        '접수', '지원금', '사업자', '참여기업',
        '수요기업', '공급기업', '선정', '바우처',
        '지원대상', '사업공고',
    ]

    title_lower = title.lower()

    # 1차: 제외 키워드 체크 (하나라도 있으면 제외)
    for keyword in exclude_keywords:
        if keyword in title_lower:
            logger.debug("[필터] 정보성 콘텐츠 제외: %s", title)
            return False

    # 2차: 포함 키워드 체크 (하나라도 있으면 포함)
    for keyword in include_keywords:
        if keyword in title_lower:
            return True

    # 3차: 제목이 너무 짧으면 제외 (의미 있는 공고는 보통 10자 이상)
    if len(title) < 10:
        logger.debug("[필터] 제목이 너무 짧아 제외: %s", title)
        return False

    # 키워드가 없지만 충분한 길이면 일단 포함 (보수적 접근)
    return True


# ─── 기업마당 API 크롤러 ──────────────────────────────────────

def crawl_bizinfo_api(site: dict) -> list[dict]:
    items = []
    page = 1
    while True:
        params = {
            "crtfcKey": BIZINFO_API_KEY,
            "dataType": "json",
            "pageUnit": PAGE_SIZE,
            "pageIndex": page,
        }
        try:
            resp = requests.get(site["api_url"], params=params, headers=HEADERS,
                                timeout=30, verify=False)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            logger.warning("[bizinfo] API 호출 실패: %s", e)
            break

        results = data.get("jsonArray") or data.get("result") or []
        if not results:
            break

        logger.info("[bizinfo] API 호출 — 페이지 %d, %d건", page, len(results))
        for row in results:
            title = (row.get("pblancNm") or row.get("PBANC_NM") or "").strip()
            href = row.get("pblancUrl") or row.get("DETL_PG_URL") or ""
            url = _abs_url(href, site["url"])
            # reqstBeginEndDe 형식: "2026-03-03 ~ 2026-04-05" → 마감일만 추출
            date_range = row.get("reqstBeginEndDe") or row.get("RCRIT_PD_END_DE") or ""
            deadline = date_range.split("~")[-1].strip() if "~" in date_range else date_range
            org = row.get("jrsdInsttNm") or row.get("ENTRPS_NM") or site.get("org", "")
            # bsnsSumryCn은 HTML 포함 가능 → 태그 제거
            raw_summary = row.get("bsnsSumryCn") or row.get("BSNS_SUMRY_CN") or ""
            summary = re.sub(r"<[^>]+>", " ", raw_summary).strip()

            if not title:
                continue

            # 실제 지원사업 공고만 필터링 (정보성 콘텐츠 제외)
            if not is_actual_support_program(title):
                continue

            items.append(_build_item(title, site, url, deadline, org, summary[:500]))

        if len(results) < PAGE_SIZE:
            break
        page += 1
        time.sleep(0.5)

    return items


def crawl_bizinfo_html(site: dict) -> list[dict]:
    """API 실패 시 HTML 폴백."""
    items = []
    try:
        resp = requests.get(site["list_url"], headers=HEADERS, timeout=30, verify=False)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        for row in soup.select("table tbody tr"):
            cells = row.find_all("td")
            if len(cells) < 3:
                continue
            a_tag = row.find("a")
            title = a_tag.get_text(strip=True) if a_tag else cells[1].get_text(strip=True)
            href = _abs_url(a_tag.get("href", "") if a_tag else "", site["url"])
            deadline = cells[-1].get_text(strip=True) if cells else ""

            if not title:
                continue

            # 실제 지원사업 공고만 필터링 (정보성 콘텐츠 제외)
            if not is_actual_support_program(title):
                continue

            items.append(_build_item(title, site, href, deadline, site.get("org", ""), ""))
    except Exception as e:
        logger.error("[bizinfo] HTML 폴백 실패: %s", e)
    return items


# ─── 기본 HTML 크롤러 ─────────────────────────────────────────

def crawl_html(site: dict) -> list[dict]:
    items = []
    try:
        resp = requests.get(site["list_url"], headers=HEADERS, timeout=30, verify=False)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        selectors = [
            "table tbody tr",
            ".board-list li",
            ".list-wrap li",
            "ul.notice-list li",
        ]
        rows = []
        for sel in selectors:
            rows = soup.select(sel)
            if rows:
                break

        for row in rows:
            a_tag = row.find("a")
            if not a_tag:
                continue
            title = a_tag.get_text(strip=True)
            href = _abs_url(a_tag.get("href", ""), site["url"])

            cells = row.find_all("td")
            deadline = cells[-1].get_text(strip=True) if len(cells) > 2 else ""

            if not title:
                continue

            # 실제 지원사업 공고만 필터링 (정보성 콘텐츠 제외)
            if not is_actual_support_program(title):
                continue

            items.append(_build_item(title, site, href, deadline, site.get("org", ""), ""))
    except Exception as e:
        logger.error("[%s] HTML 크롤링 실패: %s", site["id"], e)
    return items


# ─── Playwright 크롤러 ────────────────────────────────────────

def crawl_playwright(site: dict) -> list[dict]:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.warning("[%s] playwright 미설치. HTML 폴백 사용.", site["id"])
        return crawl_html(site)

    items = []
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(user_agent=HEADERS["User-Agent"])
        # 모든 작업에 기본 타임아웃 15초 적용 (hang 방지)
        page.set_default_timeout(15000)
        try:
            page.goto(site["list_url"], timeout=60000, wait_until="domcontentloaded")
            try:
                page.wait_for_load_state("networkidle", timeout=20000)
            except Exception:
                page.wait_for_timeout(3000)

            sel_cfg = LIST_SELECTORS.get(site["id"])
            if sel_cfg:
                rows = page.query_selector_all(sel_cfg["container"])
                for row in rows:
                    a_el = row.query_selector(sel_cfg["link"])
                    tit_el = row.query_selector(sel_cfg["title"])

                    title = ""
                    if tit_el:
                        title = (tit_el.inner_text() or "").strip()
                    elif a_el:
                        title = (a_el.inner_text() or "").strip()

                    href = _abs_url(a_el.get_attribute("href") or "" if a_el else "", site["url"])

                    dl_el = row.query_selector(sel_cfg["deadline"])
                    deadline = (dl_el.inner_text() or "").strip() if dl_el else ""

                    # 내용 전체 텍스트를 summary로 활용
                    summary = (row.inner_text() or "").strip()[:300]

                    if not title or len(title) < 4:
                        continue

                    # 실제 지원사업 공고만 필터링 (정보성 콘텐츠 제외)
                    if not is_actual_support_program(title):
                        continue

                    items.append(_build_item(title, site, href, deadline, site.get("org", ""), summary))
            else:
                # 범용 폴백
                links = page.query_selector_all("a")
                seen = set()
                for link in links:
                    title = (link.inner_text() or "").strip()
                    href = _abs_url(link.get_attribute("href") or "", site["url"])
                    if not title or len(title) < 10 or title in seen:
                        continue

                    # 실제 지원사업 공고만 필터링 (정보성 콘텐츠 제외)
                    if not is_actual_support_program(title):
                        continue

                    seen.add(title)
                    items.append(_build_item(title, site, href, "", site.get("org", ""), ""))

        except Exception as e:
            logger.error("[%s] Playwright 크롤링 실패: %s", site["id"], e)
        finally:
            browser.close()

    return items


# ─── 메인 크롤링 실행 ─────────────────────────────────────────

def run_crawl(site_filter: str = None):
    sites = CRAWL_SITES
    if site_filter:
        sites = [s for s in sites if s["id"] == site_filter]
        if not sites:
            logger.error("사이트 '%s'를 찾을 수 없습니다.", site_filter)
            return

    for site in sites:
        started_at = now_iso()
        log_id = log_crawl_start(site["id"], started_at)
        logger.info("[%s] 크롤링 시작", site["id"])

        def _timeout_handler(signum, frame):
            raise TimeoutError(f"[{site['id']}] {SITE_TIMEOUT_SEC}초 초과")

        try:
            # Unix 환경에서만 SIGALRM 사용 (Linux/macOS GitHub Actions)
            use_signal = hasattr(signal, "SIGALRM")
            if use_signal:
                signal.signal(signal.SIGALRM, _timeout_handler)
                signal.alarm(SITE_TIMEOUT_SEC)

            crawler_type = site.get("crawler_type", "html")
            if crawler_type == "api":
                items = crawl_bizinfo_api(site)
                if not items:
                    logger.info("[%s] API 결과 없음 — HTML 폴백", site["id"])
                    items = crawl_bizinfo_html(site)
            elif crawler_type == "playwright":
                items = crawl_playwright(site)
            else:
                items = crawl_html(site)

            if use_signal:
                signal.alarm(0)  # 타이머 해제

            new_count = 0
            for item in items:
                if upsert_announcement(item):
                    new_count += 1

            logger.info("[%s] 완료 - %d건 수집, %d건 신규", site["id"], len(items), new_count)
            log_crawl_finish(log_id, "success", len(items), new_count, now_iso())

        except TimeoutError as e:
            logger.warning("%s — 다음 사이트로 건너뜀", e)
            log_crawl_finish(log_id, "timeout", 0, 0, now_iso(), str(e))
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
        except Exception as e:
            logger.error("[%s] 오류: %s", site["id"], e)
            log_crawl_finish(log_id, "error", 0, 0, now_iso(), str(e))
            if hasattr(signal, "SIGALRM"):
                signal.alarm(0)
