"""
정부 지원사업 자동 매칭 크롤러

사용법:
  python main.py init       # DB 초기화 (최초 1회)
  python main.py run        # 전체 파이프라인 (크롤링→매칭→이메일)
  python main.py crawl      # 크롤링만
  python main.py crawl --site bizinfo  # 특정 사이트만
  python main.py match      # 매칭만
  python main.py notify     # 이메일 발송만
  python main.py preview    # 이메일 미리보기 (HTML 파일 저장)
"""

import argparse
import io
import logging
import sys

from dotenv import load_dotenv

load_dotenv()

# Windows에서 UTF-8 출력을 보장
if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("crawler.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("main")


def _ensure_db():
    from database import init_db
    init_db()


def cmd_init(_args):
    _ensure_db()
    print("DB 초기화 완료")


def cmd_crawl(args):
    _ensure_db()
    from crawler import run_crawl
    run_crawl(site_filter=getattr(args, "site", None))


def cmd_match(_args):
    from matcher import run_match
    run_match()


def cmd_notify(_args):
    from notifier import run_notify
    run_notify()


def cmd_preview(_args):
    from notifier import run_preview
    run_preview()


def cmd_run(_args):
    _ensure_db()
    from crawler import run_crawl
    from matcher import run_match
    from notifier import run_notify

    logger.info("=== 전체 파이프라인 시작 ===")
    run_crawl()
    run_match()
    run_notify()
    logger.info("=== 전체 파이프라인 완료 ===")


def main():
    parser = argparse.ArgumentParser(
        description="정부 지원사업 자동 매칭 크롤러",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")
    subparsers.required = True

    subparsers.add_parser("init", help="DB 초기화 (최초 1회)").set_defaults(func=cmd_init)
    subparsers.add_parser("run", help="전체 파이프라인 실행").set_defaults(func=cmd_run)

    crawl_p = subparsers.add_parser("crawl", help="크롤링만 실행")
    crawl_p.add_argument("--site", help="특정 사이트 ID만 크롤링")
    crawl_p.set_defaults(func=cmd_crawl)

    subparsers.add_parser("match", help="매칭만 실행").set_defaults(func=cmd_match)
    subparsers.add_parser("notify", help="이메일 발송만").set_defaults(func=cmd_notify)
    subparsers.add_parser("preview", help="이메일 미리보기 (HTML 저장)").set_defaults(func=cmd_preview)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
