#!/bin/bash
# 정부 지원사업 크롤러 크론 자동 설정 스크립트

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="$SCRIPT_DIR/venv/bin/python"
CRON_JOB="0 1 * * 2,5 cd $SCRIPT_DIR && $PYTHON main.py run >> $SCRIPT_DIR/crawler.log 2>&1"

# 기존 크론에 없으면 추가
( crontab -l 2>/dev/null | grep -v "subsidy-crawler\|main.py run"; echo "# 정부 지원사업 크롤러: 매주 월/목 오전 9시"; echo "$CRON_JOB" ) | crontab -

echo "크론 설정 완료:"
crontab -l | grep "main.py"
