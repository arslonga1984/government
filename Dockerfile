FROM python:3.11-slim

WORKDIR /app

# 시스템 의존성
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    sqlite3 \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Playwright (선택 — JS 렌더링 사이트용)
RUN pip install --no-cache-dir playwright && \
    playwright install chromium && \
    playwright install-deps

# 소스 복사
COPY . .

# 데이터 디렉토리
RUN mkdir -p data

# 크론 설정: 매주 월/목 오전 9시
RUN echo "0 1 * * 2,5 cd /app && python main.py run >> /app/crawler.log 2>&1" | crontab -

# 크론 + 컨테이너 유지
CMD ["sh", "-c", "cron && tail -f /app/crawler.log"]
