---
name: deploy
description: CI/CD pipeline setup and execution guide for the government subsidy crawler
triggers:
  - deploy
  - cicd
  - github actions
  - pipeline
  - secrets
argument-hint: ""
---

# Government Subsidy Crawler CI/CD Deployment Guide

Guide for setting up and running the CI/CD pipeline.

---

## Architecture Overview

```
GitHub Actions (Cron: Tue/Fri 10:00 KST)
  1. Download DB from S3
  2. Crawl → Match → Send Email
  3. Upload DB to S3
```

---

## Prerequisites

Obtain the following values from the dev team:

| Secret Name | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS IAM Access Key |
| `AWS_SECRET_ACCESS_KEY` | AWS IAM Secret Key |
| `BIZINFO_API_KEY` | BizInfo API Key |
| `SMTP_SERVER` | Email SMTP server address |
| `SMTP_PORT` | Email SMTP port |
| `SENDER_EMAIL` | Sender email address |
| `SENDER_PASSWORD` | Sender email password |
| `EMAIL_RECIPIENTS` | Recipient email list |
| `ANTHROPIC_API_KEY` | Claude API Key |
| `LLM_MATCHING` | Enable LLM matching (default: "false") |
| `MATCH_SCORE_THRESHOLD` | Match score threshold (default: "40") |

---

## Deployment Steps

Proceed step by step. Confirm the result with the user at each step.

### Step 1: Register GitHub Secrets

Register the values provided by the dev team as GitHub Secrets.
Using `gh` CLI:

```bash
gh secret set AWS_ACCESS_KEY_ID --body "<provided value>"
gh secret set AWS_SECRET_ACCESS_KEY --body "<provided value>"
gh secret set BIZINFO_API_KEY --body "<provided value>"
gh secret set SMTP_SERVER --body "<provided value>"
gh secret set SMTP_PORT --body "<provided value>"
gh secret set SENDER_EMAIL --body "<provided value>"
gh secret set SENDER_PASSWORD --body "<provided value>"
gh secret set EMAIL_RECIPIENTS --body "<provided value>"
gh secret set ANTHROPIC_API_KEY --body "<provided value>"
gh secret set LLM_MATCHING --body "<provided value>"
gh secret set MATCH_SCORE_THRESHOLD --body "<provided value>"
```

Ask the user for each value one at a time before registering.

### Step 2: Verify with Manual Run

```bash
gh workflow run crawler.yml
```

Or go to GitHub repo > Actions tab > "정부 지원사업 자동 크롤링 및 이메일 발송" > "Run workflow" button.

### Verification Checklist

- [ ] AWS credentials configured successfully in Actions log
- [ ] S3 download/upload confirmed in log
- [ ] Crawl → Match → Email completed successfully

---

## Common Tasks

### Trigger a Manual Crawl
```bash
gh workflow run crawler.yml
```

### Check Run Logs
```bash
gh run list --workflow=crawler.yml --limit 5
gh run view <run-id> --log
```

### Change Crawl Schedule
Edit the `cron` value in `.github/workflows/crawler.yml`.
Current: `0 1 * * 2,5` (Tue/Fri 10:00 KST)
Format: `min hour(UTC) * * day-of-week` (0=Sun, 1=Mon, ..., 6=Sat)
