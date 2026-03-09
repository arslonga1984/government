import json
import logging

from config.settings import (
    KEYWORD_SYNONYMS,
    LLM_MATCHING,
    MATCH_SCORE_THRESHOLD,
    PRODUCTS,
    ANTHROPIC_API_KEY,
)
from database import get_unmatched_announcements, save_match_results
from utils import now_iso

logger = logging.getLogger(__name__)


def _expand_keywords(tags: list[str]) -> set[str]:
    expanded = set(t.lower() for t in tags)
    for tag in tags:
        for synonym in KEYWORD_SYNONYMS.get(tag, []):
            expanded.add(synonym.lower())
    return expanded


def _keyword_score(text: str, keywords: set[str], weight: float) -> tuple[float, list[str]]:
    text_lower = text.lower()
    matched = [kw for kw in keywords if kw in text_lower]
    score = len(matched) * 10 * weight
    return score, matched


_anthropic_client = None


def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None:
        import anthropic
        _anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _anthropic_client


def _llm_score(title: str, summary: str, product_name: str, tags: list[str]) -> float:
    if not ANTHROPIC_API_KEY:
        return 0.0
    try:
        client = _get_anthropic_client()
        prompt = (
            f"정부 지원사업 공고와 소프트웨어 제품의 연관성을 0-100점으로 평가하세요.\n\n"
            f"공고 제목: {title}\n"
            f"공고 내용: {summary[:300]}\n\n"
            f"제품명: {product_name}\n"
            f"제품 키워드: {', '.join(tags)}\n\n"
            f"숫자만 답하세요 (예: 75)."
        )
        msg = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{"role": "user", "content": prompt}],
        )
        return float(msg.content[0].text.strip())
    except Exception as e:
        logger.warning("LLM 매칭 실패: %s", e)
        return 0.0


# 확장 키워드를 모듈 로드 시 한 번만 계산
_EXPANDED_KEYWORDS: dict[str, set[str]] = {
    name: _expand_keywords(product["tags"])
    for name, product in PRODUCTS.items()
}


def match_announcement(announcement: dict) -> list[dict]:
    title = announcement.get("title", "")
    summary = announcement.get("summary", "")

    results = []
    for product_name, product in PRODUCTS.items():
        tags = product["tags"]
        weight = product.get("weight", 1.0)
        keywords = _EXPANDED_KEYWORDS[product_name]

        # 제목 가중치 2배, 요약 1배
        title_score, title_matched = _keyword_score(title, keywords, weight * 2)
        body_score, body_matched = _keyword_score(summary, keywords, weight)
        matched = list(set(title_matched + body_matched))
        score = title_score + body_score

        if LLM_MATCHING and summary:
            llm = _llm_score(title, summary, product_name, tags)
            score = score * 0.5 + llm * 0.5

        if score >= MATCH_SCORE_THRESHOLD:
            results.append({
                "announcement_hash": announcement["content_hash"],
                "product_name": product_name,
                "match_score": round(score, 2),
                "matched_keywords": json.dumps(matched, ensure_ascii=False),
                "created_at": now_iso(),
            })

    return results


def run_match():
    announcements = get_unmatched_announcements()
    logger.info("매칭 대상 공고: %d건", len(announcements))

    all_results = []
    for ann in announcements:
        results = match_announcement(ann)
        all_results.extend(results)
        if results:
            names = [r["product_name"] for r in results]
            logger.info("[매칭] %s → %s", ann["title"][:30], names)

    if all_results:
        save_match_results(all_results)
        logger.info("매칭 결과 %d건 저장 완료", len(all_results))
    else:
        logger.info("임계값(%d) 이상 매칭 없음", MATCH_SCORE_THRESHOLD)
