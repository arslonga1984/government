import { useState, useEffect } from "react";

const SITES = [
  { id: 1, name: "기업마당 (Bizinfo)", url: "https://www.bizinfo.go.kr", org: "중소벤처기업부", category: "통합", desc: "중소기업 지원사업 통합 포털 — AI, 클라우드, DX, 수출, 금융 등 전 분야", priority: "★★★", crawlable: "RSS/API 가능", keywords: ["AI", "클라우드", "DX", "SaaS", "보안"] },
  { id: 2, name: "클라우드서비스 지원포털", url: "https://www.cloudsup.or.kr", org: "과기정통부 / NIPA", category: "클라우드", desc: "클라우드 바우처, AI 통합 바우처 전담 사이트", priority: "★★★", crawlable: "HTML 크롤링", keywords: ["클라우드 바우처", "AI 통합 바우처", "SaaS"] },
  { id: 3, name: "K-Startup 창업지원포털", url: "https://www.k-startup.go.kr", org: "중소벤처기업부", category: "창업/스타트업", desc: "창업 관련 정부사업 공고 포털", priority: "★★☆", crawlable: "HTML 크롤링", keywords: ["창업", "스타트업", "기술사업화"] },
  { id: 4, name: "중소기업기술정보진흥원 (TIPA)", url: "https://www.smtech.go.kr", org: "중소벤처기업부", category: "R&D", desc: "중소기업 R&D 지원사업 — 창업성장기술개발, 기술혁신 등", priority: "★★★", crawlable: "HTML 크롤링", keywords: ["R&D", "기술개발", "AI", "SW"] },
  { id: 5, name: "중소기업기술개발사업 종합관리시스템 (SMIV)", url: "https://www.mssmiv.com/portal/Main", org: "중소벤처기업부", category: "R&D", desc: "중소기업 기술개발 사업공고 통합 관리", priority: "★★★", crawlable: "HTML 크롤링", keywords: ["기술개발", "R&D"] },
  { id: 6, name: "정보통신산업진흥원 (NIPA)", url: "https://www.nipa.kr", org: "과기정통부", category: "ICT/AI", desc: "AI 바우처, SW 성장지원, 클라우드 SaaS 개발 역량지원 등", priority: "★★★", crawlable: "HTML 크롤링", keywords: ["AI 바우처", "SW", "SaaS", "클라우드", "디지털전환"] },
  { id: 7, name: "정보통신기획평가원 (IITP)", url: "https://www.iitp.kr", org: "과기정통부", category: "ICT R&D", desc: "ICT·AI R&D 과제 사업공고", priority: "★★☆", crawlable: "HTML 크롤링", keywords: ["ICT R&D", "AI", "정보보안"] },
  { id: 8, name: "한국지능정보사회진흥원 (NIA)", url: "https://www.nia.or.kr", org: "과기정통부", category: "AI/데이터", desc: "데이터바우처, AI 학습데이터, 디지털 전환 사업", priority: "★★★", crawlable: "HTML 크롤링", keywords: ["데이터바우처", "AI", "디지털전환"] },
  { id: 9, name: "한국데이터산업진흥원 (K-DATA)", url: "https://www.kdata.or.kr", org: "과기정통부", category: "데이터", desc: "데이터바우처 지원사업 (공급기업/수요기업)", priority: "★★★", crawlable: "HTML 크롤링", keywords: ["데이터바우처", "데이터 가공", "AI 학습데이터"] },
  { id: 10, name: "나라장터 (KONEPS)", url: "https://www.g2b.go.kr", org: "조달청", category: "조달", desc: "공공조달 입찰 공고 — AI/SW/보안 관련 조달 정보", priority: "★★☆", crawlable: "API 제공", keywords: ["조달", "SW", "보안", "AI"] },
  { id: 11, name: "한국산업기술진흥원 (KIAT)", url: "https://www.kiat.or.kr", org: "산업통상자원부", category: "산업기술", desc: "산업AI 혁신, 산업 DX 관련 R&D 사업", priority: "★★☆", crawlable: "HTML 크롤링", keywords: ["산업AI", "DX", "제조혁신"] },
  { id: 12, name: "한국인터넷진흥원 (KISA)", url: "https://www.kisa.or.kr", org: "과기정통부", category: "보안/인터넷", desc: "정보보호, 개인정보보호, 보안 관련 지원사업", priority: "★★☆", crawlable: "HTML 크롤링", keywords: ["정보보호", "보안", "DLP", "개인정보"] },
  { id: 13, name: "IRIS (국가연구개발사업 통합관리시스템)", url: "https://www.iris.go.kr", org: "과기정통부", category: "R&D 통합", desc: "정부 R&D 과제 통합 공고 (AI, ICT 포함)", priority: "★★☆", crawlable: "HTML 크롤링", keywords: ["R&D", "AI", "ICT"] },
  { id: 14, name: "소상공인시장진흥공단", url: "https://www.semas.or.kr", org: "중소벤처기업부", category: "소상공인", desc: "소상공인 디지털전환, 스마트상점 지원사업", priority: "★☆☆", crawlable: "HTML 크롤링", keywords: ["소상공인", "디지털전환", "스마트상점"] },
  { id: 15, name: "스마트공장 사업관리시스템", url: "https://www.smart-factory.kr", org: "중소벤처기업부", category: "제조 DX", desc: "스마트공장 구축, 클라우드 제조솔루션 등", priority: "★★☆", crawlable: "HTML 크롤링", keywords: ["스마트공장", "제조DX", "클라우드"] },
];

const PRODUCTS = [
  { name: "오피스에이전트", tags: ["AI", "RAG", "문서검색", "챗봇", "에이전트", "LLM", "SaaS", "클라우드", "DX", "디지털전환", "업무자동화"], color: "#3B82F6" },
  { name: "오피스키퍼", tags: ["DLP", "정보유출방지", "보안", "PC보안", "정보보호", "개인정보"], color: "#EF4444" },
  { name: "오피스넥스트", tags: ["협업", "메신저", "그룹웨어", "SaaS", "클라우드", "업무환경"], color: "#10B981" },
  { name: "나모에디터", tags: ["웹에디터", "HTML5", "콘텐츠", "웹표준", "공공기관"], color: "#F59E0B" },
  { name: "오피스밸런스", tags: ["근로시간", "52시간", "업무관리"], color: "#8B5CF6" },
];

const SAMPLE_ANNOUNCEMENTS = [
  {
    id: 1,
    title: "2026년도 AI 통합 바우처(클라우드 바우처) 지원 사업",
    source: "클라우드서비스 지원포털",
    org: "과기정통부 / NIPA",
    deadline: "2026-04-15",
    budget: "최대 2,400만원",
    summary: "중소기업 대상 AI·클라우드 서비스 도입 바우처 지원. SaaS형 AI 솔루션 구매 가능.",
    requirements: "중소기업 기본법 상 중소기업, 3년 이상 사업영위",
    matchProducts: ["오피스에이전트", "오피스키퍼", "오피스넥스트"],
    matchScore: 95,
    matchReasons: ["AI SaaS 솔루션 공급기업 등록 가능", "RAG 기반 문서검색 AI 서비스 해당", "클라우드 DLP 솔루션 해당"],
  },
  {
    id: 2,
    title: "2026년 AI 바우처 지원사업",
    source: "NIPA",
    org: "과기정통부",
    deadline: "2026-05-10",
    budget: "최대 2억원",
    summary: "AI 솔루션 도입 필요 수요기업에 바우처 지급, 공급기업은 AI 솔루션 대금 수령",
    requirements: "자체 AI 솔루션 보유 공급기업 등록 필요",
    matchProducts: ["오피스에이전트"],
    matchScore: 92,
    matchReasons: ["RAG 기반 AI 에이전트 솔루션 직접 해당", "기업용 AI 챗봇·문서검색 수요 매칭", "공급기업 Pool 등록으로 매출 파이프라인 확대"],
  },
  {
    id: 3,
    title: "2026년 데이터바우처 지원사업 (수요기업 모집)",
    source: "K-DATA",
    org: "과기정통부",
    deadline: "2026-03-30",
    budget: "최대 5,000만원",
    summary: "데이터 기반 서비스 개발에 필요한 데이터 구매·가공 바우처 지원",
    requirements: "중소기업, 소상공인, 예비창업자",
    matchProducts: ["오피스에이전트"],
    matchScore: 78,
    matchReasons: ["AI 학습 데이터 구축에 오피스에이전트 RAG 활용 가능", "데이터 가공 서비스 공급기업 등록 가능성"],
  },
  {
    id: 4,
    title: "2026년 중소기업 클라우드 서비스 보급·확산 사업",
    source: "클라우드서비스 지원포털",
    org: "과기정통부",
    deadline: "2026-04-20",
    budget: "최대 400만원",
    summary: "클라우드 전환 비용 지원. SaaS 도입 바우처 형태.",
    requirements: "중소기업, 클라우드 서비스 미도입 기업 우선",
    matchProducts: ["오피스키퍼", "오피스넥스트", "오피스에이전트"],
    matchScore: 88,
    matchReasons: ["클라우드형 DLP 솔루션 공급기업 적합", "협업 SaaS 공급기업 등록 가능", "수요기업 고객에게 바우처 활용 안내 가능"],
  },
  {
    id: 5,
    title: "2026년 스마트 제조혁신 지원사업 (디지털·AI 전환)",
    source: "기업마당",
    org: "중소벤처기업부",
    deadline: "2026-03-31",
    budget: "총사업비 30~100% 지원",
    summary: "중소·중견 제조기업 디지털·AI 전환 지원. 스마트공장 구축 포함.",
    requirements: "국내 중소·중견 제조기업",
    matchProducts: ["오피스에이전트", "오피스키퍼"],
    matchScore: 65,
    matchReasons: ["제조현장 문서 AI 검색·관리 솔루션으로 활용", "제조 데이터 보안(DLP) 솔루션 연계"],
  },
  {
    id: 6,
    title: "2026년 정보보호 산업 기반조성 지원사업",
    source: "KISA",
    org: "과기정통부",
    deadline: "2026-04-05",
    budget: "과제당 1~3억원",
    summary: "정보보호 제품·서비스 개발 및 사업화 지원",
    requirements: "정보보호 분야 중소기업",
    matchProducts: ["오피스키퍼"],
    matchScore: 82,
    matchReasons: ["DLP 솔루션 고도화 R&D 지원 가능", "클라우드 보안 기능 개발 연계"],
  },
];

function getScoreColor(score) {
  if (score >= 90) return "#16A34A";
  if (score >= 75) return "#2563EB";
  if (score >= 60) return "#D97706";
  return "#9CA3AF";
}

function getScoreBg(score) {
  if (score >= 90) return "rgba(22,163,74,0.08)";
  if (score >= 75) return "rgba(37,99,235,0.06)";
  if (score >= 60) return "rgba(217,119,6,0.05)";
  return "rgba(156,163,175,0.05)";
}

export default function SubsidyMonitor() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [selectedProduct, setSelectedProduct] = useState("전체");
  const [sortBy, setSortBy] = useState("score");

  const filtered = SAMPLE_ANNOUNCEMENTS
    .filter(a => selectedProduct === "전체" || a.matchProducts.includes(selectedProduct))
    .sort((a, b) => sortBy === "score" ? b.matchScore - a.matchScore : new Date(a.deadline) - new Date(b.deadline));

  const tabs = [
    { id: "dashboard", label: "대시보드", icon: "📊" },
    { id: "announcements", label: "매칭 공고", icon: "📋" },
    { id: "sites", label: "크롤링 사이트", icon: "🌐" },
    { id: "architecture", label: "시스템 설계", icon: "⚙️" },
    { id: "email", label: "이메일 미리보기", icon: "✉️" },
  ];

  return (
    <div style={{ fontFamily: "'Pretendard', 'Noto Sans KR', -apple-system, sans-serif", background: "#F8FAFC", minHeight: "100vh", color: "#1E293B" }}>
      {/* Header */}
      <div style={{ background: "linear-gradient(135deg, #0F172A 0%, #1E3A5F 50%, #0F172A 100%)", color: "white", padding: "32px 24px 20px" }}>
        <div style={{ maxWidth: 1100, margin: "0 auto" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
            <span style={{ fontSize: 28 }}>🏛️</span>
            <h1 style={{ fontSize: 22, fontWeight: 700, margin: 0, letterSpacing: "-0.3px" }}>정부 지원사업 자동 매칭 서비스</h1>
          </div>
          <p style={{ fontSize: 13, color: "#94A3B8", margin: "4px 0 0 40px" }}>
            지란지교소프트 제품군 × 정부 지원사업 공고 자동 크롤링 & 매칭
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ background: "white", borderBottom: "1px solid #E2E8F0", position: "sticky", top: 0, zIndex: 10 }}>
        <div style={{ maxWidth: 1100, margin: "0 auto", display: "flex", gap: 0, overflowX: "auto" }}>
          {tabs.map(t => (
            <button
              key={t.id}
              onClick={() => setActiveTab(t.id)}
              style={{
                padding: "14px 20px",
                border: "none",
                borderBottom: activeTab === t.id ? "2px solid #2563EB" : "2px solid transparent",
                background: "none",
                color: activeTab === t.id ? "#2563EB" : "#64748B",
                fontWeight: activeTab === t.id ? 600 : 400,
                fontSize: 13,
                cursor: "pointer",
                whiteSpace: "nowrap",
                transition: "all 0.15s",
              }}
            >
              {t.icon} {t.label}
            </button>
          ))}
        </div>
      </div>

      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "24px 16px" }}>
        {/* Dashboard Tab */}
        {activeTab === "dashboard" && (
          <div>
            {/* Stats */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 16, marginBottom: 28 }}>
              {[
                { label: "모니터링 사이트", value: "15개", icon: "🌐", color: "#3B82F6" },
                { label: "매칭 제품군", value: "5개", icon: "📦", color: "#10B981" },
                { label: "현재 매칭 공고", value: `${SAMPLE_ANNOUNCEMENTS.length}건`, icon: "📋", color: "#F59E0B" },
                { label: "크롤링 주기", value: "3일", icon: "🔄", color: "#8B5CF6" },
              ].map((s, i) => (
                <div key={i} style={{ background: "white", borderRadius: 12, padding: "20px 18px", border: "1px solid #E2E8F0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <div style={{ fontSize: 12, color: "#64748B", marginBottom: 6 }}>{s.label}</div>
                      <div style={{ fontSize: 24, fontWeight: 700, color: s.color }}>{s.value}</div>
                    </div>
                    <span style={{ fontSize: 32, opacity: 0.7 }}>{s.icon}</span>
                  </div>
                </div>
              ))}
            </div>

            {/* Product Cards */}
            <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: "#334155" }}>제품별 매칭 현황</h3>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 12, marginBottom: 28 }}>
              {PRODUCTS.map(p => {
                const count = SAMPLE_ANNOUNCEMENTS.filter(a => a.matchProducts.includes(p.name)).length;
                const avgScore = count > 0 ? Math.round(SAMPLE_ANNOUNCEMENTS.filter(a => a.matchProducts.includes(p.name)).reduce((s, a) => s + a.matchScore, 0) / count) : 0;
                return (
                  <div key={p.name} style={{ background: "white", borderRadius: 10, padding: "16px", border: `1px solid ${p.color}22`, borderLeft: `4px solid ${p.color}` }}>
                    <div style={{ fontSize: 14, fontWeight: 600, color: p.color, marginBottom: 8 }}>{p.name}</div>
                    <div style={{ fontSize: 12, color: "#64748B" }}>매칭 공고 <span style={{ fontWeight: 700, color: "#1E293B" }}>{count}건</span></div>
                    <div style={{ fontSize: 12, color: "#64748B", marginTop: 2 }}>평균 매칭률 <span style={{ fontWeight: 700, color: getScoreColor(avgScore) }}>{avgScore}%</span></div>
                  </div>
                );
              })}
            </div>

            {/* Top Matches */}
            <h3 style={{ fontSize: 15, fontWeight: 600, marginBottom: 12, color: "#334155" }}>매칭률 TOP 3 공고</h3>
            {SAMPLE_ANNOUNCEMENTS.sort((a,b) => b.matchScore - a.matchScore).slice(0, 3).map((a, i) => (
              <div key={a.id} style={{ background: "white", borderRadius: 10, padding: "16px 18px", marginBottom: 10, border: "1px solid #E2E8F0", display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{ width: 44, height: 44, borderRadius: "50%", background: getScoreBg(a.matchScore), display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16, fontWeight: 800, color: getScoreColor(a.matchScore), flexShrink: 0 }}>
                  {a.matchScore}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14, fontWeight: 600, color: "#1E293B", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{a.title}</div>
                  <div style={{ fontSize: 12, color: "#64748B", marginTop: 2 }}>{a.source} · 마감 {a.deadline} · {a.budget}</div>
                </div>
                <div style={{ display: "flex", gap: 4, flexShrink: 0, flexWrap: "wrap", justifyContent: "flex-end" }}>
                  {a.matchProducts.map(mp => {
                    const prod = PRODUCTS.find(p => p.name === mp);
                    return <span key={mp} style={{ fontSize: 10, padding: "2px 8px", borderRadius: 99, background: `${prod?.color || "#999"}15`, color: prod?.color || "#999", fontWeight: 500 }}>{mp}</span>;
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Announcements Tab */}
        {activeTab === "announcements" && (
          <div>
            {/* Filters */}
            <div style={{ display: "flex", gap: 12, marginBottom: 20, flexWrap: "wrap", alignItems: "center" }}>
              <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                {["전체", ...PRODUCTS.map(p => p.name)].map(p => (
                  <button
                    key={p}
                    onClick={() => setSelectedProduct(p)}
                    style={{
                      padding: "6px 14px", borderRadius: 99, border: "1px solid",
                      borderColor: selectedProduct === p ? "#2563EB" : "#E2E8F0",
                      background: selectedProduct === p ? "#2563EB" : "white",
                      color: selectedProduct === p ? "white" : "#64748B",
                      fontSize: 12, fontWeight: 500, cursor: "pointer",
                    }}
                  >{p}</button>
                ))}
              </div>
              <select
                value={sortBy}
                onChange={e => setSortBy(e.target.value)}
                style={{ marginLeft: "auto", padding: "6px 12px", borderRadius: 8, border: "1px solid #E2E8F0", fontSize: 12, color: "#475569", background: "white" }}
              >
                <option value="score">매칭률순</option>
                <option value="deadline">마감일순</option>
              </select>
            </div>

            {/* Announcement Cards */}
            {filtered.map(a => (
              <div key={a.id} style={{ background: "white", borderRadius: 12, padding: "20px", marginBottom: 14, border: "1px solid #E2E8F0", borderLeft: `4px solid ${getScoreColor(a.matchScore)}` }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 15, fontWeight: 700, color: "#0F172A", marginBottom: 4 }}>{a.title}</div>
                    <div style={{ fontSize: 12, color: "#64748B" }}>{a.source} ({a.org})</div>
                  </div>
                  <div style={{ textAlign: "center", padding: "8px 16px", borderRadius: 10, background: getScoreBg(a.matchScore), flexShrink: 0, marginLeft: 12 }}>
                    <div style={{ fontSize: 22, fontWeight: 800, color: getScoreColor(a.matchScore) }}>{a.matchScore}%</div>
                    <div style={{ fontSize: 10, color: "#64748B" }}>매칭률</div>
                  </div>
                </div>

                <p style={{ fontSize: 13, color: "#475569", lineHeight: 1.6, margin: "0 0 12px" }}>{a.summary}</p>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, fontSize: 12, marginBottom: 12 }}>
                  <div><span style={{ color: "#94A3B8" }}>마감일:</span> <span style={{ fontWeight: 600 }}>{a.deadline}</span></div>
                  <div><span style={{ color: "#94A3B8" }}>지원규모:</span> <span style={{ fontWeight: 600 }}>{a.budget}</span></div>
                  <div style={{ gridColumn: "1 / -1" }}><span style={{ color: "#94A3B8" }}>신청자격:</span> <span style={{ fontWeight: 500 }}>{a.requirements}</span></div>
                </div>

                <div style={{ marginBottom: 10 }}>
                  <div style={{ fontSize: 11, color: "#94A3B8", marginBottom: 6, fontWeight: 500 }}>매칭 제품</div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {a.matchProducts.map(mp => {
                      const prod = PRODUCTS.find(p => p.name === mp);
                      return <span key={mp} style={{ fontSize: 11, padding: "3px 10px", borderRadius: 99, background: `${prod?.color || "#999"}12`, color: prod?.color || "#999", fontWeight: 600 }}>{mp}</span>;
                    })}
                  </div>
                </div>

                <div style={{ background: "#F8FAFC", borderRadius: 8, padding: "10px 14px" }}>
                  <div style={{ fontSize: 11, color: "#64748B", fontWeight: 600, marginBottom: 6 }}>매칭 근거</div>
                  {a.matchReasons.map((r, i) => (
                    <div key={i} style={{ fontSize: 12, color: "#475569", lineHeight: 1.7 }}>• {r}</div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Sites Tab */}
        {activeTab === "sites" && (
          <div>
            <p style={{ fontSize: 13, color: "#64748B", marginBottom: 20, lineHeight: 1.6 }}>
              총 <strong>{SITES.length}개</strong> 사이트를 3일 주기로 크롤링합니다. 우선순위가 높은 사이트부터 AI, 클라우드, DX, 보안 관련 공고를 수집합니다.
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {SITES.map(s => (
                <div key={s.id} style={{ background: "white", borderRadius: 10, padding: "16px 18px", border: "1px solid #E2E8F0" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                    <div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: "#0F172A" }}>{s.name}</div>
                      <div style={{ fontSize: 11, color: "#94A3B8", marginTop: 2 }}>{s.url}</div>
                    </div>
                    <span style={{ fontSize: 13, letterSpacing: 1 }}>{s.priority}</span>
                  </div>
                  <div style={{ fontSize: 12, color: "#475569", lineHeight: 1.5, marginBottom: 8 }}>{s.desc}</div>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap", alignItems: "center" }}>
                    <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 4, background: "#EFF6FF", color: "#2563EB", fontWeight: 500 }}>{s.org}</span>
                    <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 4, background: "#F0FDF4", color: "#16A34A", fontWeight: 500 }}>{s.category}</span>
                    <span style={{ fontSize: 10, padding: "2px 8px", borderRadius: 4, background: "#FFF7ED", color: "#EA580C", fontWeight: 500 }}>{s.crawlable}</span>
                    {s.keywords.slice(0, 3).map(k => (
                      <span key={k} style={{ fontSize: 10, padding: "2px 6px", borderRadius: 4, background: "#F1F5F9", color: "#64748B" }}>{k}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Architecture Tab */}
        {activeTab === "architecture" && (
          <div>
            <div style={{ background: "white", borderRadius: 12, padding: "24px", border: "1px solid #E2E8F0", marginBottom: 20 }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: "#0F172A", marginTop: 0, marginBottom: 16 }}>시스템 아키텍처</h3>
              
              {/* Architecture Diagram */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: 16 }}>
                {/* Layer 1: Data Sources */}
                <div style={{ background: "#EFF6FF", borderRadius: 10, padding: "16px" }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: "#1D4ED8", marginBottom: 10 }}>① 데이터 수집 레이어 (3일 주기 크롤링)</div>
                  <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                    {["Bizinfo API", "NIPA", "IITP", "NIA", "K-DATA", "CloudSup", "K-Startup", "SMIV", "TIPA", "KISA", "나라장터 API", "KIAT", "IRIS", "SEMAS", "스마트공장"].map(s => (
                      <span key={s} style={{ fontSize: 10, padding: "4px 10px", background: "white", borderRadius: 6, border: "1px solid #BFDBFE", color: "#1E40AF", fontWeight: 500 }}>{s}</span>
                    ))}
                  </div>
                </div>

                <div style={{ textAlign: "center", color: "#94A3B8", fontSize: 18 }}>▼</div>

                {/* Layer 2: Processing */}
                <div style={{ background: "#F0FDF4", borderRadius: 10, padding: "16px" }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: "#15803D", marginBottom: 10 }}>② 처리 & 매칭 레이어</div>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 10 }}>
                    {[
                      { title: "크롤러 엔진", desc: "Playwright/Selenium + BeautifulSoup" },
                      { title: "데이터 정규화", desc: "공고 제목, 기간, 조건, 내용 파싱" },
                      { title: "키워드 매칭", desc: "제품 태그 ↔ 공고 키워드 유사도" },
                      { title: "LLM 매칭 (선택)", desc: "GPT/Claude API로 정밀 매칭 판단" },
                    ].map(item => (
                      <div key={item.title} style={{ background: "white", borderRadius: 8, padding: "10px 12px", border: "1px solid #BBF7D0" }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: "#166534" }}>{item.title}</div>
                        <div style={{ fontSize: 11, color: "#64748B", marginTop: 2 }}>{item.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div style={{ textAlign: "center", color: "#94A3B8", fontSize: 18 }}>▼</div>

                {/* Layer 3: Storage */}
                <div style={{ background: "#FFF7ED", borderRadius: 10, padding: "16px" }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: "#C2410C", marginBottom: 10 }}>③ 저장 & 관리 레이어</div>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 10 }}>
                    {[
                      { title: "PostgreSQL DB", desc: "공고 데이터, 매칭 결과, 이력 저장" },
                      { title: "중복 제거", desc: "해시 기반 중복 공고 필터링" },
                      { title: "변경 감지", desc: "마감일·내용 변경 시 알림 트리거" },
                    ].map(item => (
                      <div key={item.title} style={{ background: "white", borderRadius: 8, padding: "10px 12px", border: "1px solid #FED7AA" }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: "#9A3412" }}>{item.title}</div>
                        <div style={{ fontSize: 11, color: "#64748B", marginTop: 2 }}>{item.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <div style={{ textAlign: "center", color: "#94A3B8", fontSize: 18 }}>▼</div>

                {/* Layer 4: Output */}
                <div style={{ background: "#FAF5FF", borderRadius: 10, padding: "16px" }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: "#7C3AED", marginBottom: 10 }}>④ 알림 & 리포트 레이어</div>
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))", gap: 10 }}>
                    {[
                      { title: "이메일 발송", desc: "3일 주기 HTML 리포트 메일 (SMTP)" },
                      { title: "Slack 알림 (선택)", desc: "긴급 공고 실시간 웹훅 알림" },
                      { title: "대시보드", desc: "웹 대시보드에서 전체 현황 조회" },
                    ].map(item => (
                      <div key={item.title} style={{ background: "white", borderRadius: 8, padding: "10px 12px", border: "1px solid #DDD6FE" }}>
                        <div style={{ fontSize: 12, fontWeight: 600, color: "#5B21B6" }}>{item.title}</div>
                        <div style={{ fontSize: 11, color: "#64748B", marginTop: 2 }}>{item.desc}</div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Tech Stack */}
            <div style={{ background: "white", borderRadius: 12, padding: "24px", border: "1px solid #E2E8F0", marginBottom: 20 }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: "#0F172A", marginTop: 0, marginBottom: 16 }}>기술 스택 제안</h3>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))", gap: 16 }}>
                {[
                  { title: "백엔드", items: ["Python 3.11+", "FastAPI (API 서버)", "Celery + Redis (스케줄러)", "Playwright (JS 렌더링 크롤링)", "BeautifulSoup4 (HTML 파싱)"] },
                  { title: "데이터베이스", items: ["PostgreSQL (메인 DB)", "Redis (캐시/큐)", "SQLAlchemy (ORM)"] },
                  { title: "AI 매칭 (선택)", items: ["Claude API (공고 분석/매칭)", "키워드 TF-IDF 기반 매칭", "코사인 유사도 점수화"] },
                  { title: "인프라", items: ["Docker Compose", "GitHub Actions (CI/CD)", "AWS EC2 or 가비아 VPS", "Crontab (3일 주기 실행)"] },
                  { title: "이메일", items: ["SMTP (네이버/Gmail)", "Jinja2 HTML 템플릿", "인라인 CSS 이메일 스타일"] },
                  { title: "모니터링", items: ["Sentry (에러 추적)", "로그 파일 관리", "크롤링 성공/실패 대시보드"] },
                ].map(s => (
                  <div key={s.title} style={{ background: "#F8FAFC", borderRadius: 8, padding: "14px" }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: "#1E293B", marginBottom: 8 }}>{s.title}</div>
                    {s.items.map(item => (
                      <div key={item} style={{ fontSize: 12, color: "#475569", lineHeight: 1.8 }}>• {item}</div>
                    ))}
                  </div>
                ))}
              </div>
            </div>

            {/* Implementation Steps */}
            <div style={{ background: "white", borderRadius: 12, padding: "24px", border: "1px solid #E2E8F0" }}>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: "#0F172A", marginTop: 0, marginBottom: 16 }}>구현 로드맵 (4주)</h3>
              {[
                { week: "Week 1", title: "크롤러 개발", tasks: ["15개 사이트 크롤러 모듈 개발", "데이터 정규화 파이프라인 구축", "PostgreSQL 스키마 설계"] },
                { week: "Week 2", title: "매칭 엔진", tasks: ["제품-공고 키워드 매칭 로직 구현", "매칭 점수 알고리즘 (TF-IDF + 규칙 기반)", "LLM 매칭 옵션 (Claude API 연동)"] },
                { week: "Week 3", title: "알림 시스템", tasks: ["HTML 이메일 템플릿 제작", "3일 주기 스케줄러 (Celery Beat)", "수신자 관리 기능"] },
                { week: "Week 4", title: "배포 & 안정화", tasks: ["Docker 컨테이너화", "모니터링 & 로깅 설정", "테스트 운영 & 피드백 반영"] },
              ].map((w, i) => (
                <div key={w.week} style={{ display: "flex", gap: 16, marginBottom: i < 3 ? 16 : 0, paddingBottom: i < 3 ? 16 : 0, borderBottom: i < 3 ? "1px solid #F1F5F9" : "none" }}>
                  <div style={{ width: 80, flexShrink: 0 }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: "#2563EB", background: "#EFF6FF", borderRadius: 6, padding: "4px 10px", textAlign: "center" }}>{w.week}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: 13, fontWeight: 600, color: "#1E293B", marginBottom: 4 }}>{w.title}</div>
                    {w.tasks.map(t => (
                      <div key={t} style={{ fontSize: 12, color: "#64748B", lineHeight: 1.7 }}>• {t}</div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Email Preview Tab */}
        {activeTab === "email" && (
          <div>
            <p style={{ fontSize: 13, color: "#64748B", marginBottom: 16, lineHeight: 1.6 }}>
              3일마다 담당자에게 발송되는 이메일의 미리보기입니다. 매칭률이 높은 순으로 정렬되며, 공고 요약/일정/요건/매칭 근거가 포함됩니다.
            </p>
            
            {/* Email Mock */}
            <div style={{ background: "white", borderRadius: 12, border: "1px solid #D1D5DB", overflow: "hidden", maxWidth: 680 }}>
              {/* Email Header */}
              <div style={{ background: "#F3F4F6", padding: "12px 20px", borderBottom: "1px solid #E5E7EB", fontSize: 12, color: "#6B7280" }}>
                <div><strong>From:</strong> 지원사업 알리미 &lt;subsidy-alert@jiransoft.co.kr&gt;</div>
                <div><strong>To:</strong> 옥윤혜 &lt;yh.ok@jiransoft.co.kr&gt;, 고민호 &lt;mh.ko@jiransoft.co.kr&gt;</div>
                <div><strong>Subject:</strong> [지원사업 매칭] 2026.03.06 — 신규 6건 매칭 (최고 매칭률 95%)</div>
              </div>

              {/* Email Body */}
              <div style={{ padding: "24px 20px" }}>
                <div style={{ textAlign: "center", marginBottom: 24 }}>
                  <div style={{ fontSize: 18, fontWeight: 700, color: "#111827", marginBottom: 4 }}>🏛️ 정부 지원사업 매칭 리포트</div>
                  <div style={{ fontSize: 12, color: "#6B7280" }}>2026.03.04 ~ 2026.03.06 수집 · 지란지교소프트 제품군 기준</div>
                </div>

                <div style={{ background: "#EFF6FF", borderRadius: 8, padding: "12px 16px", marginBottom: 20, textAlign: "center" }}>
                  <span style={{ fontSize: 13, color: "#1D4ED8", fontWeight: 600 }}>
                    이번 주기: 신규 공고 <strong>6건</strong> 매칭 · 최고 매칭률 <strong style={{ color: "#16A34A" }}>95%</strong>
                  </span>
                </div>

                {SAMPLE_ANNOUNCEMENTS.sort((a, b) => b.matchScore - a.matchScore).map((a, i) => (
                  <div key={a.id} style={{ borderLeft: `3px solid ${getScoreColor(a.matchScore)}`, padding: "12px 16px", marginBottom: 14, background: "#FAFAFA", borderRadius: "0 8px 8px 0" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                      <div style={{ fontSize: 14, fontWeight: 700, color: "#111827" }}>{i + 1}. {a.title}</div>
                      <span style={{ fontSize: 14, fontWeight: 800, color: getScoreColor(a.matchScore), flexShrink: 0, marginLeft: 8 }}>{a.matchScore}%</span>
                    </div>
                    <div style={{ fontSize: 12, color: "#6B7280", marginBottom: 8 }}>{a.source} · {a.org}</div>
                    <div style={{ fontSize: 12, color: "#374151", lineHeight: 1.6, marginBottom: 8 }}>{a.summary}</div>
                    <div style={{ fontSize: 12, marginBottom: 6 }}>
                      <span style={{ color: "#9CA3AF" }}>📅 마감:</span> <strong>{a.deadline}</strong>&nbsp;&nbsp;
                      <span style={{ color: "#9CA3AF" }}>💰 규모:</span> <strong>{a.budget}</strong>
                    </div>
                    <div style={{ fontSize: 12, marginBottom: 6 }}>
                      <span style={{ color: "#9CA3AF" }}>✅ 자격:</span> {a.requirements}
                    </div>
                    <div style={{ fontSize: 12 }}>
                      <span style={{ color: "#9CA3AF" }}>🎯 매칭 제품:</span>{" "}
                      {a.matchProducts.map(mp => (
                        <span key={mp} style={{ display: "inline-block", fontSize: 11, padding: "1px 8px", borderRadius: 99, background: `${PRODUCTS.find(p => p.name === mp)?.color || "#999"}15`, color: PRODUCTS.find(p => p.name === mp)?.color || "#999", fontWeight: 600, marginRight: 4 }}>{mp}</span>
                      ))}
                    </div>
                    <div style={{ fontSize: 11, color: "#6B7280", marginTop: 6, fontStyle: "italic" }}>
                      매칭 근거: {a.matchReasons[0]}
                    </div>
                  </div>
                ))}

                <div style={{ textAlign: "center", marginTop: 20, padding: "16px", background: "#F9FAFB", borderRadius: 8, fontSize: 11, color: "#9CA3AF" }}>
                  이 메일은 지란지교소프트 정부 지원사업 자동 매칭 시스템에서 3일 주기로 발송됩니다.<br/>
                  수신 설정 변경: subsidy-admin@jiransoft.co.kr
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
