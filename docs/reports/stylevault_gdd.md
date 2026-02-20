# StyleVault — Service Design Document (GDD)

> **문서 버전:** v1.0  
> **작성일:** 2026-02-20  
> **관련 문서:**  
> - [아이디어 리포트](./ideas_ai_style_marketplace_2026-02-20.md)  
> - [리뷰 기사](./stylevault_review_article.md)  
> - [엔지니어링 Q&A](./stylevault_engineering_qa.md)  
> - [사용자 시나리오](./stylevault_scenario_creator_journey.md)  
> - [페르소나 바이블](./stylevault_character_bible.md)  
> - [서비스 설계 & 밸런싱](./stylevault_level_design.md)

---

## 1. 제품 비전

### 1.1 한 줄 정의
> **"작가가 자기 스타일로 LoRA를 만들고, 저작권이 추적된 상태로 게임 회사에 스타일 라이선스를 판매하는 인증 마켓플레이스"**

### 1.2 핵심 차별점

| 기존 솔루션 | StyleVault |
|-----------|-----------|
| Civitai: 무료 공유 위주, 저작권 추적 없음 | 저작권 체인 완전 추적, 상업 라이선스 보장 |
| exactly.ai: 큐레이션 모델, 게임 특화 없음 | 게임 엔진 플러그인 + 대량 생성 최적화 |
| Hugging Face: 기술 장벽 높음, 법적 보장 없음 | 비기술자 작가도 원클릭 LoRA 생성 |
| 전통 아웃소싱: 비용 $60K+, 기간 3~6개월 | 비용 $1.5K~$3K, 기간 수일, 스타일 완벽 일관성 |

### 1.3 타겟 유저

| 페르소나 | 설명 | 비율 |
|---------|------|------|
| **프로 일러스트레이터** | 자기 스타일로 AI 수익화를 원하는 작가 | 40% |
| **인디 게임 개발자** | 적은 예산으로 일관된 아트 에셋이 필요한 소규모 팀 | 30% |
| **중소 게임 스튜디오** | AI 에셋의 법적 리스크를 제거하고 싶은 기업 | 20% |
| **미디어/광고 제작사** | 특정 스타일의 비주얼 에셋을 빠르게 대량 생산 | 10% |

---

## 2. 핵심 루프

```
┌──────────────────────────────────────────────────────────────┐
│                    ◤ 작가 루프 ◥                              │
│                                                              │
│  [작품 업로드] → [스타일 분석] → [LoRA 학습] → [QA 검증]      │
│       ↑                                           │          │
│       │              ┌────────────────────────────┘          │
│       │              ▼                                       │
│  [수익 수령] ← [로열티 정산] ← [스토어 등록 & 라이선스 설정]  │
│                      ↑                                       │
└──────────────────────┼───────────────────────────────────────┘
                       │
┌──────────────────────┼───────────────────────────────────────┐
│                    ◤ 기업 루프 ◥                              │
│                      │                                       │
│  [스타일 검색] → [데모 비교] → [라이선스 구매]                │
│       ↑                                           │          │
│       │              ┌────────────────────────────┘          │
│       │              ▼                                       │
│  [게임 출시] ← [에셋 적용] ← [API/플러그인으로 에셋 생성]    │
└──────────────────────────────────────────────────────────────┘
```

### 2.1 세션 설계

| 항목 | 작가 | 기업 |
|------|------|------|
| 1세션 길이 | 30~60분 (초기 설정), 10분 (모니터링) | 5~10분 (생성 작업), 1분 (API 호출) |
| 이상적 이용 빈도 | 주 1회 (대시보드 확인) | 일 3~5회 (에셋 생성) |
| 핵심 가치 순간 | 첫 정산 수령 | 첫 에셋 생성 & 게임 적용 |

---

## 3. 코어 시스템

### 3.1 작가 인증 시스템 (Artist Verification)

작가의 신원과 작품 소유권을 검증하여 LoRA 학습 데이터의 합법성을 보장합니다.

```yaml
verification_pipeline:
  step_1_identity:
    methods:
      - social_oauth: ["artstation", "pixiv", "instagram", "twitter"]
      - email_verification: true
    passing_criteria: "1개 이상 소셜 계정 + 이메일 인증"
    
  step_2_portfolio:
    methods:
      - cross_platform_check:
          description: "연동 플랫폼에서 동일 작품 업로드 이력 확인"
          api: ["artstation_api", "pixiv_api"]
          threshold: "업로드 작품의 70% 이상 매칭"
      - reverse_image_search:
          description: "Google Vision + TinEye로 원작자 확인"
          flag_threshold: "다른 계정에서 먼저 발견 시"
      - style_clustering:
          description: "CLIP 벡터 클러스터링으로 스타일 일관성 검증"
          threshold: "산포도 < 0.3 (동일 작가 기준)"
    passing_criteria: "3개 방법 중 2개 이상 통과"
    
  step_3_live_drawing:  # 선택적 프리미엄 인증
    description: "지정 포즈 30초 드로잉 타임랩스 제출"
    ai_check: "결과물과 포트폴리오 스타일 매칭 검증"
    badge: "✅ Live Verified"
    
  result:
    verified: "일반 인증 배지"
    premium_verified: "라이브 드로잉 포함 프리미엄 배지"
    failed: "수동 리뷰 에스컬레이션"
```

### 3.2 LoRA 학습 & QA 시스템 (Training Pipeline)

```yaml
training_pipeline:
  input:
    min_images: 10
    max_images: 100
    recommended: 20-30
    supported_formats: ["png", "jpg", "webp"]
    min_resolution: 512x512
    
  preprocessing:
    auto_tagging:
      model: "WD 1.4 Tagger + BLIP-2"
      outputs: ["style_tags", "subject_tags", "quality_score"]
    diversity_check:
      metric: "CLIP 벡터 분산"
      threshold: 0.68  # 최소 다양성 점수
      recommendation: "부족 시 구체적 추천 이미지 유형 안내"
    copyright_declaration:
      - "모든 이미지 본인 창작 확인"
      - "제3자 IP 미포함 확인"
      - "외부 플랫폼 타임스탬프 교차 검증"
      
  training:
    base_model: "SDXL 1.0 / Flux.1 (선택)"
    method: "LoRA (rank 32, alpha 16)"
    epochs: "auto (early stopping)"
    hardware: "A10G 24GB (g5.xlarge)"
    estimated_time: "10-20분"
    cost: "$0.25/건"
    
  qa_pipeline:
    step_1_reference_generation:
      standard_prompts: 20  # 표준 프롬프트 세트
      per_prompt_images: 4
    step_2_metrics:
      style_fidelity:  # 학습 데이터와의 스타일 유사도
        method: "CLIP embedding cosine similarity"
        pass_threshold: 0.85
      prompt_responsiveness:  # 다양한 프롬프트에 대한 반응
        method: "CLIP text-image alignment"
        pass_threshold: 0.80
      overfit_risk:  # 학습 데이터 암기 정도
        method: "학습데이터 vs 생성물 pixel-level similarity"
        warn_threshold: 0.25
      copyright_conflict:
        method: "Pinecone ANN search vs 기존 LoRA 레퍼런스"
        flag_threshold: 0.92
    step_3_ip_check:
      model: "커스텀 IP 캐릭터 분류기"
      database: "알려진 IP 캐릭터 10,000+ 엔트리"
```

### 3.3 라이선스 관리 시스템 (License Engine)

```yaml
license_system:
  tier_templates:
    indie:
      price_range: "$19-$49/month"
      max_generations: 500
      commercial_use: true
      credit_required: true
      exclusive: false
      
    studio:
      price_range: "$99-$249/month"
      max_generations: 5000
      commercial_use: true
      credit_required: false
      exclusive: false
      
    exclusive:
      price_range: "$1,000+/month (negotiable)"
      max_generations: unlimited
      commercial_use: true
      credit_required: false
      exclusive: true  # 한 기업 독점
      
  royalty_distribution:
    platform_share: 15%
    creator_share: 85%
    blending_policy: "가중치 비례 분배"
    settlement_cycle: "월 1회 (말일 마감 → 익월 15일 지급)"
    min_payout: "$20"
    reserve_pool: "미사용 생성 건수 대응분 → 분기 보너스"
    
  usage_tracking:
    method: "API 호출 로그 + 이벤트 소싱"
    realtime_dashboard: true
    export: "CSV / API endpoint"
    
  restrictions_default:
    - no_nft_minting
    - no_lora_resale
    - no_sublicensing
    - artist_can_add_custom_restrictions
```

### 3.4 저작권 체인 시스템 (Copyright Chain)

```yaml
copyright_chain:
  architecture: "Event Sourcing (append-only)"
  storage: "PostgreSQL + S3 archive"
  
  tracked_events:
    - ARTIST_VERIFIED
    - TRAINING_DATA_UPLOADED (with image hashes)
    - COPYRIGHT_DECLARED
    - LORA_TRAINED (with model hash)
    - QA_PASSED
    - STORE_LISTED
    - LICENSE_PURCHASED
    - IMAGE_GENERATED (with output hash + license_id)
    - LICENSE_RENEWED / EXPIRED / REVOKED
    
  certificate:
    format: "JSON metadata embedded in image EXIF"
    fields:
      - generation_id
      - lora_id
      - artist_id
      - license_id
      - timestamp
      - copyright_chain_url  # 검증 페이지 링크
      
  legal_export:
    format: "PDF report"
    contents:
      - full_event_timeline
      - image_hashes
      - license_terms
      - artist_verification_status
    use_case: "법적 분쟁 시 증거 자료"
```

---

## 4. UI/UX 설계

### 4.1 핵심 화면 구성

```
[랜딩 페이지]
├── 히어로: "당신의 스타일, 당신의 자산"
├── 인기 작가 쇼케이스 (수익 데이터 포함)
├── 검색 바: 스타일/장르/용도별 검색
└── CTA: "작가로 시작하기" / "에셋 찾기"

[작가 대시보드]
├── 내 LoRA 목록 (상태: 학습중/검증중/판매중)
├── 수익 현황 (일별/월별 그래프)
├── 사용 분석 (어떤 기업이 어떤 프롬프트로 사용)
└── 알림: 신규 구매, QA 결과, 정산 완료

[기업 대시보드]
├── 구독 중인 LoRA 목록
├── 월간 사용량 / 잔여 생성 건수
├── API 키 관리
├── 생성 이력 + 라이선스 인증서 다운로드
└── Unity/Unreal 플러그인 다운로드

[마켓플레이스]
├── 카테고리: 캐릭터 / 배경 / UI / 텍스처 / 이펙트
├── 필터: 스타일(수채화/셀셰이딩/리얼리즘/...) / 가격 / QA점수
├── LoRA 상세 페이지:
│   ├── 데모 갤러리 (6~12장)
│   ├── QA 리포트 요약
│   ├── 작가 프로필 + 인증 배지
│   ├── 가격/라이선스 옵션 탭
│   ├── "저작권 체인 보기" 버튼
│   └── "실시간 데모" (프롬프트 입력 → 즉시 생성)
└── 블렌딩 모드: LoRA 2~3개 선택 → 혼합 결과 미리보기
```

### 4.2 대시보드 (작가 수익 화면)

```
┌──────────────────────────────────────────────────────────┐
│  📊 이번 달 수익                          2026년 2월     │
│  ┌────────────────────────────────────────────────────┐  │
│  │  $2,340.00                    ▲ 23% vs 지난달     │  │
│  │  ████████████████████░░░░░░░░  $3,000 목표의 78%  │  │
│  └────────────────────────────────────────────────────┘  │
│                                                          │
│  LoRA별 수익                                              │
│  ┌─────────────────────────────┬────────┬──────────────┐ │
│  │ Warm Fantasy Style v1       │ $1,450 │ ████████     │ │
│  │ Watercolor Landscape v2     │  $620  │ ████         │ │
│  │ Chibi Character Pack        │  $270  │ ██           │ │
│  └─────────────────────────────┴────────┴──────────────┘ │
│                                                          │
│  최근 구매                                                │
│  ┌──────────────────────────┬──────────┬────────────┐    │
│  │ Studio GreenPixel        │ Studio   │ 2시간 전   │    │
│  │ IndieDevKim              │ Indie    │ 어제       │    │
│  │ MegaGame Corp            │ Exclusive│ 3일 전     │    │
│  └──────────────────────────┴──────────┴────────────┘    │
└──────────────────────────────────────────────────────────┘
```

### 4.3 알림 시스템

| 이벤트 | 채널 | 내용 |
|--------|------|------|
| 신규 라이선스 구매 | 이메일 + 인앱 | "[기업명]이 [LoRA명]을 [티어]로 구매" |
| LoRA QA 완료 | 인앱 + 푸시 | "QA 통과! 스토어에 등록하세요" |
| 월간 정산 | 이메일 | "2월 정산 $2,340 → 2/15 지급 예정" |
| 사용량 경고 (기업) | 인앱 | "이번 달 생성 430/500건 사용. 업그레이드 권장" |
| 저작권 알림 | 이메일 + 인앱 | "외부에서 유사 LoRA 탐지됨. 확인 필요" |

---

## 5. 수익 모델

### 5.1 구독 티어 (기업용)

| 티어 | 가격 | 포함 내용 |
|------|------|----------|
| **Free Trial** | $0 (7일) | LoRA 3개 데모 생성 각 10건, 워터마크 포함 |
| **Indie** | $49/월 | 생성 500건/월, LoRA 5개까지, 크레딧 표기 필수 |
| **Studio** | $199/월 | 생성 5,000건/월, LoRA 무제한, 크레딧 선택 |
| **Enterprise** | 협의 | 무제한, 온프레미스 옵션, 전담 지원, SLA |

### 5.2 추가 수익원

| 수익원 | 설명 | 예상 비중 |
|--------|------|----------|
| 거래 수수료 | 작가 직판 수익의 15% | 35% |
| LoRA 학습 서비스 | 작가 무료, 프리미엄 학습(고급 최적화) $10/건 | 5% |
| 프리미엄 노출 | 마켓플레이스 상단 노출 광고 | 10% |
| 기업 구독 | Indie~Enterprise 정기 구독 | 45% |
| API 초과 과금 | 월정액 초과 생성 시 $0.03/건 | 5% |

---

## 6. 기술 아키텍처

> 상세 내용은 [엔지니어링 Q&A](./stylevault_engineering_qa.md) Round 6 참조

```
┌───────────┐   ┌───────────┐   ┌───────────┐
│  Next.js  │   │  Unity    │   │  Unreal   │
│  Web App  │   │  Plugin   │   │  Plugin   │
└─────┬─────┘   └─────┬─────┘   └─────┬─────┘
      │               │               │
      └───────────────┼───────────────┘
                      │
              ┌───────▼───────┐
              │  API Gateway  │  (Rate Limit + Auth)
              └───────┬───────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
  ┌───────────┐ ┌───────────┐ ┌───────────┐
  │   Auth    │ │   Asset   │ │  License  │
  │  Service  │ │  Service  │ │  Service  │
  └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
        ▼             ▼             ▼
  ┌───────────┐ ┌───────────┐ ┌───────────┐
  │PostgreSQL │ │GPU Cluster│ │PostgreSQL │
  │ (Users)   │ │ + SQS     │ │ (Events)  │
  └───────────┘ └─────┬─────┘ └───────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
     ┌────────┐  ┌────────┐  ┌────────┐
     │  S3    │  │Pinecone│  │ Redis  │
     │(Storage│  │(Vector)│  │(Cache) │
     └────────┘  └────────┘  └────────┘
```

### 6.1 핵심 기술 스택

| 영역 | 기술 | 선정 이유 |
|------|------|----------|
| 프론트엔드 | Next.js + TypeScript | SEO + SSR, React 생태계 |
| 게임 플러그인 | C# (Unity), C++ (Unreal) | 네이티브 API 바인딩 |
| 백엔드 | FastAPI (Python) | AI/ML 라이브러리, 비동기 |
| AI 엔진 | ComfyUI (headless) | LoRA 로딩/블렌딩 유연성 |
| 베이스 모델 | SDXL / Flux.1 | 업계 표준, LoRA 호환 |
| DB | PostgreSQL 16 | 이벤트 소싱, JSONB |
| 벡터 DB | Pinecone | ANN 검색 < 50ms |
| 캐시 | Redis Cluster | 생성 결과 캐싱 |
| 결제 | Stripe Connect | 마켓플레이스 정산 |
| 인프라 | AWS EKS + Terraform | IaC, 컨테이너 오케스트레이션 |

---

## 7. 런칭 로드맵

### Phase 0: 프로토타입 (8주)
- 핵심 LoRA 학습 파이프라인 구축
- 기본 마켓플레이스 UI (Next.js)
- 작가 인증 시스템 MVP (소셜 OAuth + 역이미지 검색)
- 저작권 체인 이벤트 로그 시스템
- **마일스톤:** 내부 팀원 5명이 LoRA 생성 → 판매 프로세스 완주

### Phase 1: 클로즈드 베타 (6주)
- 앰버서더 작가 20명 초대 (팔로워 10K+ 인증 작가)
- 인디 게임 개발사 10개 초대
- QA 파이프라인 + 저작권 충돌 검사 도입
- 결제/정산 시스템 연동 (Stripe Connect)
- **마일스톤:** 50개 인증 LoRA + 첫 유료 거래 발생

### Phase 2: 퍼블릭 런칭 (4주)
- 오픈 가입 (작가 + 기업)
- Unity 플러그인 v1 출시
- 실시간 데모 생성 기능
- 마케팅: 게임 개발 컨퍼런스 + 아트 커뮤니티 PR
- **마일스톤:** 작가 500명, 기업 30개, LoRA 200개

### Phase 3: 성장 (지속)
- Unreal 플러그인 출시
- LoRA 블렌딩 기능
- Enterprise 온프레미스 배포
- 다국어 (일본어, 중국어) 지원
- 모바일 대시보드 앱
- **목표:** 14개월 BEP 달성 (작가 7,000명, 기업 280개)

---

## 8. 핵심 리스크 & 대응

| 리스크 | 심각도 | 대응 전략 |
|--------|:------:|----------|
| **저작권 법률 변경** — AI 생성물 관련 법률이 급변하여 사업 모델 자체가 위협받을 수 있음 | 🔴 | 법무팀 확보 + EU/US 규제 변화를 분기별 모니터링. 최악의 경우 라이선스 모델을 "에셋 마켓플레이스"(완성 에셋 판매)로 피봇 가능 |
| **작가 초기 확보 실패** — 콜드 스타트 문제. 작가가 없으면 기업이 안 오고 그 반대도 마찬가지 | 🔴 | 앰버서더 프로그램 (초기 20명에게 보장 수익 $500/월 6개월). "이 유명 작가의 스타일을 합법적으로 사용 가능"이라는 마케팅 |
| **Civitai의 저작권 기능 추가** — 기존 대형 플랫폼이 유사 기능을 출시할 수 있음 | 🟡 | 인증 시스템의 깊이 + 게임 엔진 통합이 진입장벽. 먼저 기업 고객과 장기 계약 확보하여 전환 비용 상승 |
| **LoRA 품질 편차** — 작가마다 LoRA 품질이 달라 마켓플레이스 신뢰도 하락 | 🟡 | QA 시스템의 최소 기준을 높게 설정. 미달 시 "학습 데이터 개선 가이드" 제공 후 재학습 무료 |
| **GPU 비용 급증** — 사용자 증가 시 GPU 비용이 수익을 초과할 수 있음 | 🟡 | 캐싱 레이어 (히트율 30~40%), 배치 처리, 스팟 인스턴스 활용으로 건당 비용 $0.04→$0.025 |
| **스타일 도용 탐지 오류** — 유사 스타일이 무단 도용으로 오탐(False Positive) | 🟢 | 임계값 보수적 설정(0.92) + 자동 탐지 후 반드시 수동 리뷰 단계 포함 |

---

*다음 문서: [사용자 시나리오](./stylevault_scenario_creator_journey.md) →*
