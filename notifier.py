import json
import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config.settings import (
    DATA_DIR,
    EMAIL_RECIPIENTS,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
)
from database import get_unnotified_matches, mark_notified

logger = logging.getLogger(__name__)

SITE_LABEL = {
    "bizinfo":      "기업마당",
    "cloudsup":     "클라우드서비스 지원포털",
    "nipa":         "NIPA",
    "nia":          "NIA",
    "kdata":        "K-DATA",
    "smtech":       "TIPA",
    "mssmiv":       "SMIV",
    "iitp":         "IITP",
    "kisa":         "KISA",
    "kiat":         "KIAT",
    "iris":         "IRIS",
    "kstartup":     "K-Startup",
    "koneps":       "나라장터",
    "semas":        "소상공인진흥공단",
    "smartfactory": "스마트공장",
    "mss":          "중소벤처기업부",
}

PRODUCT_COLOR = {
    "오피스에이전트": "#3B82F6",
    "오피스키퍼":    "#EF4444",
    "오피스넥스트":  "#10B981",
    "나모에디터":    "#F59E0B",
}


_SCORE_STYLES = [
    (90, "#16A34A", "#F0FDF4"),
    (75, "#2563EB", "#EFF6FF"),
    (60, "#D97706", "#FFFBEB"),
    (0,  "#6B7280", "#F9FAFB"),
]


def _score_style(score: float) -> tuple[str, str]:
    """Returns (color, background) for a given score."""
    for threshold, color, bg in _SCORE_STYLES:
        if score >= threshold:
            return color, bg
    return "#6B7280", "#F9FAFB"


def _pill_span(text: str, color: str, bg: str, radius: str = "99px",
               size: str = "11px", padding: str = "2px 10px",
               extra: str = "") -> str:
    return (
        f'<span style="display:inline-block;font-size:{size};padding:{padding};'
        f'border-radius:{radius};background:{bg};color:{color};'
        f'font-weight:600;margin-right:4px{extra}">{text}</span>'
    )


def _product_tags(product_name: str) -> str:
    color = PRODUCT_COLOR.get(product_name, "#6B7280")
    bg = f"{color}18"
    return _pill_span(product_name, color, bg)


def _keyword_chips(keywords: list[str]) -> str:
    chips = ""
    for kw in keywords:
        chips += _pill_span(kw, "#475569", "#F1F5F9", radius="4px",
                            padding="2px 8px", extra=";margin:2px 2px 0 0",
                            )
    return chips


def _build_html(matches: list[dict]) -> str:
    # 점수 내림차순 정렬
    sorted_matches = sorted(matches, key=lambda x: x["match_score"], reverse=True)
    top_score = int(sorted_matches[0]["match_score"]) if sorted_matches else 0

    # 제품별 통계
    product_counts: dict[str, int] = {}
    for m in matches:
        product_counts[m["product_name"]] = product_counts.get(m["product_name"], 0) + 1

    date_range = datetime.now().strftime("%Y년 %m월 %d일")

    # 제품 통계 칩
    product_stat_chips = ""
    for pname, cnt in product_counts.items():
        color = PRODUCT_COLOR.get(pname, "#6B7280")
        product_stat_chips += _pill_span(
            f"{pname} {cnt}건", color, f"{color}18",
            size="12px", padding="3px 12px", extra=";margin:3px 4px 3px 0",
        )

    # 공고 카드
    cards = ""
    for idx, m in enumerate(sorted_matches, 1):
        keywords = json.loads(m.get("matched_keywords") or "[]")
        site = SITE_LABEL.get(m["source_site"], m["source_site"])
        url = m.get("url", "")
        score = m["match_score"]
        sc, sb = _score_style(score)
        deadline = m.get("deadline", "")
        summary = m.get("summary", "")

        title_html = (
            f'<a href="{url}" style="color:#0F172A;text-decoration:none" target="_blank">{m["title"]}</a>'
            if url else m["title"]
        )

        deadline_html = (
            f'<span style="font-size:12px;color:#64748B">&#128197; 마감 '
            f'<strong style="color:#0F172A">{deadline}</strong></span>&nbsp;&nbsp;'
            if deadline else ""
        )

        summary_html = (
            f'<p style="margin:8px 0 10px;font-size:13px;color:#475569;line-height:1.65">{summary[:200]}</p>'
            if summary else ""
        )

        keyword_html = _keyword_chips(keywords) if keywords else ""
        product_tag = _product_tags(m["product_name"])

        cards += f"""
<div style="border-left:4px solid {sc};background:white;border-radius:0 10px 10px 0;
            padding:16px 18px;margin-bottom:12px;
            box-shadow:0 1px 3px rgba(0,0,0,0.06)">
  <table width="100%" cellpadding="0" cellspacing="0">
    <tr>
      <td style="vertical-align:top">
        <div style="font-size:15px;font-weight:700;color:#0F172A;line-height:1.4;margin-bottom:4px">
          {idx}. {title_html}
        </div>
        <div style="font-size:12px;color:#64748B;margin-bottom:6px">
          {site}
          {('&nbsp;·&nbsp;' + deadline_html) if deadline else ''}
        </div>
        {summary_html}
        <div style="margin-top:6px">
          {product_tag}
          {keyword_html}
        </div>
      </td>
      <td style="width:72px;text-align:center;vertical-align:top;padding-left:12px;flex-shrink:0">
        <div style="width:60px;height:60px;border-radius:50%;
                    background:{sb};border:2px solid {sc};
                    display:table-cell;vertical-align:middle;text-align:center;
                    font-size:20px;font-weight:800;color:{sc}">
          {int(score)}
        </div>
        <div style="font-size:10px;color:#94A3B8;margin-top:3px">매칭점수</div>
      </td>
    </tr>
  </table>
</div>"""

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#F1F5F9;font-family:'Malgun Gothic','Apple SD Gothic Neo',sans-serif">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F1F5F9;padding:24px 0">
  <tr><td align="center">
  <table width="640" cellpadding="0" cellspacing="0" style="max-width:640px;width:100%">

    <!-- 헤더 -->
    <tr><td>
      <div style="background:linear-gradient(135deg,#0F172A 0%,#1E3A5F 60%,#0F172A 100%);
                  border-radius:12px 12px 0 0;padding:28px 28px 20px">
        <div style="font-size:13px;color:#94A3B8;margin-bottom:6px">
          &#127963; 지란지교소프트 &nbsp;|&nbsp; 정부 지원사업 자동 매칭
        </div>
        <div style="font-size:22px;font-weight:700;color:white;margin-bottom:6px;letter-spacing:-0.3px">
          정부 지원사업 매칭 리포트
        </div>
        <div style="font-size:13px;color:#94A3B8">{date_range} 수집 기준</div>
      </div>
    </td></tr>

    <!-- 요약 배너 -->
    <tr><td>
      <div style="background:#2563EB;padding:14px 28px">
        <table width="100%" cellpadding="0" cellspacing="0">
          <tr>
            <td style="color:white;font-size:14px;font-weight:600">
              &#127919; 이번 주기 신규 공고
              <strong style="font-size:20px;margin:0 4px">{len(matches)}건</strong>
              매칭
              &nbsp;&#8226;&nbsp;
              최고 점수
              <strong style="font-size:20px;color:#86EFAC;margin:0 4px">{top_score}점</strong>
            </td>
          </tr>
          <tr><td style="padding-top:8px">{product_stat_chips}</td></tr>
        </table>
      </div>
    </td></tr>

    <!-- 본문 -->
    <tr><td style="background:white;padding:24px 24px 8px;border-left:1px solid #E2E8F0;border-right:1px solid #E2E8F0">
      <div style="font-size:13px;font-weight:600;color:#64748B;
                  text-transform:uppercase;letter-spacing:0.5px;
                  margin-bottom:14px;padding-bottom:10px;border-bottom:1px solid #F1F5F9">
        매칭 공고 목록 (점수 높은 순)
      </div>
      {cards}
    </td></tr>

    <!-- 푸터 -->
    <tr><td>
      <div style="background:#F8FAFC;border:1px solid #E2E8F0;border-top:none;
                  border-radius:0 0 12px 12px;padding:18px 24px;text-align:center">
        <div style="font-size:12px;color:#94A3B8;line-height:1.8">
          이 메일은 정부 지원사업 자동 매칭 크롤러에 의해 자동 발송됩니다.<br>
          매주 <strong>화요일 · 금요일 오전 10시</strong> 발송 &nbsp;|&nbsp;
          수신 설정: subsidy-admin@jiransoft.co.kr
        </div>
      </div>
    </td></tr>

  </table>
  </td></tr>
</table>
</body>
</html>"""


def _send_email(subject: str, html_body: str, recipients: list[str]):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, recipients, msg.as_string())


def run_notify():
    matches = get_unnotified_matches()
    if not matches:
        logger.info("발송할 새 매칭 결과가 없습니다.")
        return

    if not EMAIL_RECIPIENTS:
        logger.error("EMAIL_RECIPIENTS가 설정되지 않았습니다.")
        return

    html = _build_html(matches)
    today = datetime.now().strftime("%Y-%m-%d")
    subject = f"[지란소프트] 정부 지원사업 매칭 리포트 ({today}) — {len(matches)}건"

    try:
        _send_email(subject, html, EMAIL_RECIPIENTS)
        hashes = list({m["announcement_hash"] for m in matches if "announcement_hash" in m})
        mark_notified(hashes)
        logger.info("이메일 발송 완료 → %s", ", ".join(EMAIL_RECIPIENTS))
    except Exception as e:
        logger.error("이메일 발송 실패: %s", e)
        raise


def run_preview():
    os.makedirs(DATA_DIR, exist_ok=True)

    matches = get_unnotified_matches()
    if not matches:
        logger.info("미리보기할 매칭 결과가 없습니다.")
        return

    html = _build_html(matches)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(DATA_DIR, f"email_preview_{timestamp}.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    logger.info("미리보기 저장: %s", path)
    print(f"미리보기 파일: {path}")
