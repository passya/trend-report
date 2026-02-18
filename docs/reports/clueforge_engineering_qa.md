# ClueForge 엔지니어링 Q&A

> SW 엔지니어 관점에서 ClueForge의 기술적 실현 가능성을 검증하는 핑퐁 대화입니다.

**관련 문서:**
- [아이디어 리포트](./ideas_llm_text_mystery_game_2026-02-18.md)
- [리뷰 기사](./clueforge_review_article.md)

---

## Round 1: 데이터/메모리 — 사건 상태 관리와 컨텍스트 한계

🧑‍💻 **엔지니어:** 리뷰를 보면 하나의 사건에서 6개 장소, 6명의 NPC, 10개 이상의 단서가 등장합니다. NPC 심문은 자유 텍스트 입력이고 감정 상태도 추적합니다. 이 모든 **사건 상태(Game State)**를 어떻게 관리하나요? LLM 컨텍스트 윈도우에 다 넣으면 토큰 비용이 폭발할 텐데요.

🏗️ **아키텍트:** 좋은 지적입니다. ClueForge는 **이중 레이어 상태 관리** 구조를 씁니다.

```
┌──────────────────────────────────────┐
│  Layer 1: Structured State (DB/JSON) │
│  - 사건 정의 (범인, 동기, 타임라인)  │
│  - 단서 목록 (발견 여부, 분석 상태)  │
│  - NPC 프로필 (페르소나, 비밀, 감정)  │
│  - 가설 그래프 (정합성 점수)          │
│  - 플레이어 행동 로그                 │
└──────────────┬───────────────────────┘
               │ 필요한 것만 주입
               ▼
┌──────────────────────────────────────┐
│  Layer 2: LLM Context Window         │
│  - System Prompt (게임 마스터 역할)   │
│  - 현재 NPC 페르소나 + 비밀           │
│  - 최근 대화 3~5턴 (sliding window)   │
│  - 관련 단서 요약 (해당 NPC 관련만)   │
│  = 약 2,000~3,000 토큰               │
└──────────────────────────────────────┘
```

핵심은 **LLM에 전체 사건을 넣지 않습니다.** Structured State에서 현재 심문 대상 NPC에 관련된 정보만 추출하여 컨텍스트에 주입합니다.

🧑‍💻 **엔지니어:** 그러면 NPC가 다른 NPC에 대해 질문받을 때는요? 예를 들어 레오나드에게 "클레어가 그날 무슨 옷을 입었나요?"라고 물으면?

🏗️ **아키텍트:** 그 경우 **Cross-NPC Reference Resolver**가 작동합니다.

```python
# pseudo-code: NPC 심문 시 컨텍스트 구성
def build_interrogation_context(case_state, target_npc, question):
    context = {
        "system": GAME_MASTER_PROMPT,
        "npc_persona": case_state.npcs[target_npc].persona,
        "npc_secrets": case_state.npcs[target_npc].secrets,  # NPC가 알고 있는 것만
        "npc_emotion": case_state.npcs[target_npc].current_emotion,
        "recent_dialogue": case_state.dialogue_history[target_npc][-5:],
    }
    
    # 질문에서 다른 NPC/오브젝트 참조 감지
    referenced_entities = extract_entities(question, case_state)
    for entity in referenced_entities:
        # 이 NPC가 해당 엔티티에 대해 "알고 있는 것"만 추가
        context["cross_refs"] = case_state.get_knowledge(target_npc, entity)
    
    return context  # 총 ~2,500 토큰
```

NPC마다 **knowledge graph**가 있어서 "레오나드가 클레어에 대해 아는 것"만 컨텍스트에 들어갑니다. 모르는 것을 물으면 "글쎄요, 잘 모르겠는데요"라고 자연스럽게 응답합니다.

🧑‍💻 **엔지니어:** 대화 기록이 길어지면? 한 NPC에게 20턴 이상 질문하는 유저도 있을 텐데.

🏗️ **아키텍트:** **Sliding Window + Summary** 방식입니다.

- 최근 5턴: 원문 유지
- 6턴 이전: LLM으로 1~2문장 요약 후 `dialogue_summary`로 압축
- 발견된 단서/실언 이벤트: 별도 structured 데이터로 영구 저장

이렇게 하면 20턴이든 50턴이든 컨텍스트는 항상 ~3,000 토큰 이내로 유지됩니다.

---

## Round 2: 핵심 엔진 — SMT 솔버 기반 미스터리 생성

🧑‍💻 **엔지니어:** 리뷰에서 가장 인상적이었던 건 SMT 솔버로 논리적 일관성을 보장한다는 부분입니다. 구체적으로 어떻게 동작하나요? LLM이 미스터리를 생성하면 SMT 솔버가 검증하는 건가요, 아니면 SMT가 먼저 제약을 만들고 LLM이 살을 붙이는 건가요?

🏗️ **아키텍트:** **후자에 가깝습니다.** 우리는 이걸 **Constraint-First Generation**이라고 부릅니다.

```
Step 1: SMT 솔버가 "뼈대" 생성
┌─────────────────────────────────────────────┐
│ 제약 조건 (SAT 문제로 인코딩)                │
│ - 범인은 정확히 1명                          │
│ - 범인은 동기(M), 기회(O), 수단(W)을 모두 가짐│
│ - 비범인 중 최소 2명은 동기를 갖되 기회 없음  │
│ - 단서 D1→범인 제외, D2→범인 제외, D3→범인 확정│
│ - 모든 단서의 조합으로 범인 유일 결정 가능     │
│ - 레드 헤링 최소 2개 (해 결정에 불필요한 단서) │
└─────────────────────────────────────────────┘
        │
        ▼ Z3 SMT 솔버
┌─────────────────────────────────────────────┐
│ 출력: Skeleton (뼈대)                        │
│ - culprit: NPC_3                             │
│ - motives: {NPC_1: greed, NPC_3: revenge,    │
│             NPC_5: jealousy}                 │
│ - opportunity: {NPC_3: "alone_in_kitchen",   │
│                 NPC_1: null, ...}             │
│ - weapon: "poison_from_greenhouse"           │
│ - clues: [D1_alibi_break, D2_witness,        │
│           D3_forensic, RH1_red_herring, ...]  │
│ - solution_path: D1 ∧ D3 → exclude NPC_1,5  │
│                  D2 ∧ D3 → confirm NPC_3     │
└─────────────────────────────────────────────┘
        │
        ▼ LLM (GPT-4 class)
Step 2: LLM이 뼈대에 "살" 붙이기
┌─────────────────────────────────────────────┐
│ - NPC_3 → "빅토리아 블랙우드, 시누이, 45세"  │
│ - revenge → "유언장 변경으로 상속분 축소"     │
│ - poison → "디기탈리스 추출물"               │
│ - D1 → "와인잔 잔여물에서 식물성 독소 검출"  │
│ - NPC 대화 페르소나, 장소 묘사, 감정 맵 등    │
└─────────────────────────────────────────────┘
        │
        ▼ Validator
Step 3: 최종 검증
- LLM 출력이 뼈대 제약을 위반하지 않는지 확인
- 위반 시 해당 부분만 LLM 재생성 (전체 재생성 아님)
```

🧑‍💻 **엔지니어:** Z3를 직접 쓰는 건가요? 프로덕션에서 SMT 솔버의 성능은?

🏗️ **아키텍트:** 네, **Microsoft Z3**를 Python 바인딩(z3-solver)으로 사용합니다.

```python
from z3 import *

def generate_mystery_skeleton(num_suspects=6, num_clues=8, difficulty="hard"):
    s = Solver()
    
    # 변수 정의
    suspects = [Int(f"suspect_{i}") for i in range(num_suspects)]
    is_culprit = [Bool(f"is_culprit_{i}") for i in range(num_suspects)]
    has_motive = [Bool(f"has_motive_{i}") for i in range(num_suspects)]
    has_opportunity = [Bool(f"has_opportunity_{i}") for i in range(num_suspects)]
    has_means = [Bool(f"has_means_{i}") for i in range(num_suspects)]
    
    # 제약 1: 정확히 1명의 범인
    s.add(Sum([If(is_culprit[i], 1, 0) for i in range(num_suspects)]) == 1)
    
    # 제약 2: 범인은 M, O, W 모두 보유
    for i in range(num_suspects):
        s.add(Implies(is_culprit[i], And(has_motive[i], has_opportunity[i], has_means[i])))
    
    # 제약 3: 난이도별 - "어려움"이면 최소 3명이 동기 보유
    if difficulty == "hard":
        s.add(Sum([If(has_motive[i], 1, 0) for i in range(num_suspects)]) >= 3)
    
    # ... 추가 제약 조건
    
    if s.check() == sat:
        model = s.model()
        return extract_skeleton(model)
    else:
        # 제약 완화 후 재시도
        return generate_mystery_skeleton(num_suspects, num_clues - 1, difficulty)
```

성능은 문제없습니다. 용의자 6명, 단서 10개 규모의 SAT 문제는 Z3에서 **10~50ms** 안에 풀립니다. 병목은 LLM 호출(Step 2)이지 SMT가 아닙니다.

🧑‍💻 **엔지니어:** 난이도 조절은 구체적으로 어떻게?

🏗️ **아키텍트:**

| 난이도 | 동기 보유자 | 결정적 단서 수 | 레드 헤링 | 해석 |
|--------|:---------:|:------------:|:--------:|------|
| 쉬움 | 2명 | 1개 | 0개 | 단서 1개로 바로 범인 특정 |
| 보통 | 3명 | 2개 | 2개 | 2개 단서 교차 검증 필요 |
| 어려움 | 4~5명 | 3개+ | 3개+ | 모든 용의자 배제 논리 필요 |
| 악몽 | 전원 | 4개+ | 5개+ | 물리적 증거만으로 판별, 동기는 미끼 |

SMT 제약 조건의 파라미터를 바꾸는 것만으로 난이도가 자연스럽게 조절됩니다.

---

## Round 3: 콘텐츠 파이프라인 — 시나리오 다양성과 스케일링

🧑‍💻 **엔지니어:** 리뷰에서 12건의 사건을 해결했는데 다양성이 유지됐다고 했습니다. LLM 생성의 한계상 10건을 넘기면 패턴이 반복되지 않나요? "부자 저택에서 독살", "부자 저택에서 또 독살"...

🏗️ **아키텍트:** 다양성은 **Template Slot 시스템**으로 보장합니다.

```yaml
# 시나리오 생성 슬롯 (각 슬롯에서 랜덤 조합)
setting_pool:
  - manor_house    # 저택
  - cruise_ship    # 유람선
  - university     # 대학 캠퍼스
  - film_set       # 영화 촬영장
  - ski_resort     # 스키 리조트
  - space_station  # 우주 정거장 (DLC)

crime_type_pool:
  - murder_poison
  - murder_blunt
  - theft_art
  - theft_data
  - disappearance
  - sabotage
  - blackmail

motive_pool:
  - inheritance     # 유산
  - revenge         # 복수
  - cover_up        # 은폐
  - jealousy        # 질투
  - ideological     # 사상
  - debt            # 빚
  - professional    # 직업적 경쟁

relationship_pool:
  - family
  - colleagues
  - old_friends
  - strangers_with_hidden_connection
  - rival_organizations

# 조합 수: 6 × 7 × 7 × 4 = 1,176가지 기본 뼈대
# + NPC 성격 조합, 장소 배치 변형 → 사실상 무한
```

**Step 1 (SMT)**에서 뼈대를 만들 때 이전에 플레이한 조합을 **블랙리스트**로 등록합니다. 같은 세팅 + 같은 범죄 유형이 연속 출현하지 않도록 하죠.

🧑‍💻 **엔지니어:** NPC 성격의 다양성은? 10건 넘으면 "방어적인 남성 용의자"가 반복되지 않나요?

🏗️ **아키텍트:** **Big Five 성격 모델** 기반의 페르소나 생성기를 씁니다.

```yaml
# NPC 페르소나 생성 파라미터
persona_template:
  name: "[LLM 생성]"
  age: "[20-80 랜덤]"
  big_five:
    openness: 0.7        # 0.0~1.0
    conscientiousness: 0.3
    extraversion: 0.8
    agreeableness: 0.2
    neuroticism: 0.6
  speech_style: "formal_sarcastic"  # 말투 풀에서 선택
  secret_type: "affair"  # 비밀 유형
  relationship_to_victim: "business_partner"
  
  # LLM 디렉티브 (시스템 프롬프트에 삽입)
  directive: |
    당신은 {name}입니다. {age}세. 
    말투: 정중하지만 빈정대는 톤.
    비밀: {secret_type}. 이 비밀을 직접적으로 밝히지 않되,
    관련 질문에 동요(neuroticism: 0.6)를 보입니다.
    외향적(0.8)이므로 자발적으로 정보를 많이 제공하지만,
    우호성이 낮아(0.2) 조사관에게 협조적이지 않습니다.
```

Big Five 5차원 × 각 0.0~1.0(0.1 단위) = 100,000가지 조합. 여기에 말투, 비밀 유형, 관계를 곱하면 중복이 체감상 발생하기 어렵습니다.

🧑‍💻 **엔지니어:** DLC 시나리오 팩은 어떤 구조?

🏗️ **아키텍트:** DLC는 **세팅 + 특수 메카닉** 번들입니다.

| DLC 팩 | 세팅 | 특수 메카닉 | 가격 |
|--------|------|-----------|------|
| 기본 (포함) | 저택, 유람선, 대학 | 없음 | $4.99 (기본가) |
| Noir Pack | 1940년대 도시, 재즈바 | 흑백 UI + 하드보일드 톤 | $1.99 |
| Sci-Fi Pack | 우주 정거장, 달 기지 | 감시 카메라 시스템 CCTV 증거 | $1.99 |
| Cozy Mystery | 시골 마을, 제과점 | 요리 미니게임 + 독극물 감별 | $1.99 |
| True Crime | 실제 범죄 유형 기반 | 법의학 도구 확장 | $2.99 |

각 팩은 새로운 `setting_pool` 엔트리 + 전용 `crime_type` + 특수 UI/메카닉 코드를 추가합니다.

---

## Round 4: 안전/윤리 — 콘텐츠 필터링과 법적 리스크

🧑‍💻 **엔지니어:** 자유 텍스트 심문이면 유저가 부적절한 질문을 할 수 있습니다. "이 NPC를 고문하겠다"든지, 아동 관련 시나리오를 요청한다든지. 어떻게 대응하나요?

🏗️ **아키텍트:** **3겹 안전 레이어**를 적용합니다.

```
Layer 1: Input Filter (유저 입력 사전 검사)
├── OpenAI Moderation API 또는 자체 분류기
├── 금지 키워드 + 의미론적 분류
└── 차단 시: "조사관은 그런 방법을 쓰지 않습니다." 인게임 메시지

Layer 2: LLM System Prompt Guard
├── "당신은 미스터리 게임의 NPC입니다. 
│    폭력, 고문, 성적 콘텐츠에 응하지 않습니다.
│    이런 요청에는 캐릭터를 유지하면서 거부합니다."
└── 예: "조사관님, 저는 법적 대리인 없이는 
         더 이상 대화할 수 없습니다."

Layer 3: Output Filter (LLM 출력 사후 검사)
├── 생성된 텍스트의 유해성 점수 체크
└── 점수 초과 시 재생성
```

🧑‍💻 **엔지니어:** 시나리오 자체가 범죄를 다루니까 "살인", "독살" 같은 단어가 당연히 나오잖아요. 오탐(false positive)은?

🏗️ **아키텍트:** **도메인 허용 리스트(allowlist)**로 해결합니다. "살인", "독살", "칼", "혈흔" 등은 미스터리 게임 맥락에서 허용합니다. 필터링 대상은:

- 실제 인물 이름 언급
- 성적 콘텐츠 / 고문 묘사
- 자살/자해 지시
- 실제 범죄 수법의 상세 설명 (how-to)

이 구분은 **맥락 인식 분류기**(fine-tuned BERT)로 처리하며, 미스터리 소설 코퍼스로 학습하여 장르적 맥락을 이해합니다.

🧑‍💻 **엔지니어:** LLM이 실제 유명인을 NPC로 생성하는 경우는?

🏗️ **아키텍트:** NPC 이름 생성 후 **유명인 DB(Wikidata 기반)**와 대조합니다. 유사도 80% 이상이면 이름을 재생성합니다. 비용은 미미하고 (로컬 fuzzy matching) 법적 리스크를 원천 차단합니다.

---

## Round 5: 비용/인프라 — 유저당 비용과 손익분기

🧑‍💻 **엔지니어:** 가장 중요한 질문입니다. LLM 호출이 핵심인데, **유저 1명이 1건의 사건을 해결하는 데 드는 API 비용**은 얼마나 되나요?

🏗️ **아키텍트:** 상세하게 계산해봅시다.

```
사건 1건 처리 비용 추산 (GPT-4o-mini 기준, 2026년 가격)

1. 시나리오 생성 (Step 2: LLM이 뼈대에 살 붙이기)
   - Input: ~1,500 토큰 (뼈대 + 프롬프트)
   - Output: ~3,000 토큰 (6 NPC 프로필 + 장소 묘사 + 단서 묘사)
   - 비용: $0.00015 (input) + $0.0018 (output) ≈ $0.002

2. NPC 심문 (핵심 비용)
   - 평균 심문: 6명 NPC × 5턴/NPC = 30턴
   - 턴당: Input ~2,500 토큰 + Output ~200 토큰
   - 비용: 30 × ($0.00025 + $0.00012) ≈ $0.011

3. 가설 생성/피드백
   - 평균 10회 가설 시도
   - 턴당: Input ~500 토큰 + Output ~100 토큰
   - 비용: 10 × ($0.00005 + $0.00006) ≈ $0.001

4. 해설 생성
   - Input ~2,000 토큰 + Output ~500 토큰
   - 비용: ≈ $0.0005

5. Sliding Window 요약 (6회)
   - 비용: ≈ $0.001

───────────────────────────
총 사건 1건 비용: ~$0.016 (약 ₩23)
───────────────────────────

유저당 월간 비용 추산:
- 캐주얼 유저: 주 2건 × 4주 = 8건 → $0.13/월
- 헤비 유저: 주 5건 × 4주 = 20건 → $0.32/월
- 평균: ~$0.20/월
```

🧑‍💻 **엔지니어:** $4.99 프리미엄 구매에 월 $0.20 서버 비용이면... 25개월 이상 플레이해야 본전인데, DLC 없이는 적자 아닌가요?

🏗️ **아키텍트:** **손익분기 분석:**

```
수익 구조:
- 기본 구매: $4.99 × 0.7 (스토어 수수료 후) = $3.49/유저
- DLC 구매율: 30% (업계 평균)
- DLC 평균 구매: 2팩 × $1.99 × 0.7 = $2.79/유저 (구매자 한정)
- DLC 기여: $2.79 × 0.3 = $0.84/유저 (전체 평균)
- 유저당 총 수입: $3.49 + $0.84 = $4.33

비용 구조 (유저당):
- LLM API: $0.20/월 × 12개월 = $2.40/년 (활성 유저 기준)
- 활성 유지율: 6개월 후 20% (모바일 기준)
- 가중 LLM 비용: $0.20×6 + $0.20×0.2×6 = $1.44/유저/년
- 서버/인프라: ~$0.30/유저/년
- 유저당 총 비용: $1.74/년

───────────────────────────
유저당 1년 이익: $4.33 - $1.74 = $2.59 (마진 약 60%)
손익분기: 출시 첫 달 (구매 시점에 이미 흑자)
───────────────────────────
```

핵심은 GPT-4o-mini급 모델의 비용이 충분히 낮다는 점입니다. 만약 더 저렴한 모델(Gemini Flash 등)이나 **로컬 모델** 옵션을 제공하면 비용은 더 줄어듭니다.

🧑‍💻 **엔지니어:** 로컬 모델 옵션이 현실적인가요?

🏗️ **아키텍트:** PC 버전에서는 **Ollama + Llama 3.2 8B** 기반 로컬 모드를 제공할 수 있습니다.

- 장점: API 비용 제로, 오프라인 플레이 가능
- 단점: NPC 응답 품질 하락 (특히 미묘한 감정 표현), 최소 16GB RAM 필요
- 구현: LLM 호출을 인터페이스로 추상화하여 클라우드/로컬 전환 가능

```python
class LLMProvider(Protocol):
    async def generate(self, prompt: str, max_tokens: int) -> str: ...

class CloudLLM(LLMProvider):       # GPT-4o-mini, Gemini Flash
    ...
class LocalLLM(LLMProvider):       # Ollama + Llama 3.2
    ...
class HybridLLM(LLMProvider):      # 심문은 Cloud, 나머지 Local
    ...
```

**Hybrid 모드**가 가장 현실적입니다. 비용이 많이 드는 NPC 심문만 클라우드, 나머지(가설 피드백, 요약 등)는 로컬로 처리.

---

## Round 6: 기술 스택 — 최종 아키텍처

🧑‍💻 **엔지니어:** 지금까지 논의를 종합하면 어떤 기술 스택이 되나요? 다이어그램으로 보여주세요.

🏗️ **아키텍트:**

```
┌─────────────────────────────────────────────────────────────┐
│                        ClueForge Architecture                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│  │   Client      │    │   Client      │    │   Client      │  │
│  │   (PC/Steam)  │    │   (iOS)       │    │   (Android)   │  │
│  │   Godot 4.x   │    │   Godot 4.x   │    │   Godot 4.x   │  │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘   │
│         │                   │                   │            │
│         └───────────────────┼───────────────────┘            │
│                             │ REST API / WebSocket            │
│                             ▼                                │
│  ┌──────────────────────────────────────────────────────┐    │
│  │                   Backend (Python)                    │    │
│  │                                                       │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │    │
│  │  │  Game Engine │  │ Mystery Gen. │  │  NPC Engine  │ │    │
│  │  │  (FastAPI)   │  │ (Z3 + LLM)   │  │  (LLM Agent) │ │    │
│  │  │             │  │             │  │             │ │    │
│  │  │ - 상태 관리  │  │ - 뼈대 생성  │  │ - 심문 처리  │ │    │
│  │  │ - 세이브/로드│  │ - 검증 루프  │  │ - 감정 추적  │ │    │
│  │  │ - 스코어링  │  │ - 난이도 조절│  │ - 실언 판정  │ │    │
│  │  └─────────────┘  └──────────────┘  └─────────────┘ │    │
│  │                                                       │    │
│  │  ┌─────────────┐  ┌──────────────┐  ┌─────────────┐ │    │
│  │  │Content Filter│  │  State Store │  │  Analytics   │ │    │
│  │  │(Moderation)  │  │ (Redis+SQLite)│  │(PostHog/    │ │    │
│  │  │             │  │             │  │  Mixpanel)   │ │    │
│  │  └─────────────┘  └──────────────┘  └─────────────┘ │    │
│  └──────────────────────────────────────────────────────┘    │
│                             │                                │
│              ┌──────────────┼──────────────┐                 │
│              ▼              ▼              ▼                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  LLM API      │  │  Z3 Solver   │  │  Database     │      │
│  │  (GPT-4o-mini │  │  (Python     │  │  (PostgreSQL  │      │
│  │   / Gemini    │  │   binding)   │  │   + Redis)    │      │
│  │   Flash)      │  │              │  │              │      │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 기술 스택 총괄표

| 레이어 | 기술 | 선택 이유 |
|--------|------|----------|
| **클라이언트** | Godot 4.x (GDScript) | 크로스플랫폼 (PC/iOS/Android), 무료, 텍스트 UI에 적합 |
| **백엔드 API** | Python + FastAPI | Z3/LLM 라이브러리 생태계, 비동기 처리 |
| **미스터리 엔진** | Z3 SMT Solver + LLM | Constraint-First Generation 파이프라인 |
| **NPC 엔진** | LangChain Agent | 체계적 프롬프트 관리, 메모리 추상화 |
| **상태 저장** | Redis (세션) + SQLite (로컬) + PostgreSQL (클라우드) | 세션 성능 + 영구 저장 분리 |
| **LLM 제공자** | GPT-4o-mini (1순위), Gemini 2.0 Flash (2순위), Ollama (로컬) | 비용-품질 밸런스 |
| **콘텐츠 필터** | OpenAI Moderation API + Fine-tuned BERT | 이중 레이어 안전 |
| **분석** | PostHog (오픈소스) | 사건 해결률, NPC 심문 패턴 분석 |
| **배포** | Docker + GCP Cloud Run | 자동 스케일링, 종량제 |
| **CI/CD** | GitHub Actions | 자동화 테스트 + 배포 |

### 런칭 로드맵 (간략)

| Phase | 기간 | 목표 |
|-------|------|------|
| Phase 0 (프로토타입) | 8주 | Z3 + LLM 파이프라인 검증, 터미널 플레이 가능 버전 |
| Phase 1 (Alpha) | 12주 | Godot UI, NPC 심문 5명, 3개 세팅, 증거 보드 |
| Phase 2 (Beta) | 8주 | 6개 세팅, 메타 진행, 밸런싱, 클로즈 베타 테스트 |
| Phase 3 (출시) | 4주 | 스토어 등록, DLC 1팩, 마케팅 |

---

## 핵심 결론

1. **SMT + LLM 하이브리드**는 기술적으로 실현 가능하며, Z3의 성능은 병목이 아님
2. **유저당 LLM 비용 ~$0.016/사건**은 프리미엄 모델($4.99)에서 충분히 수익성 확보 가능
3. **최대 리스크**는 NPC 대화 품질의 장기 다양성 — Big Five 모델 + 콘텐츠 풀 확대로 대응
4. **로컬 모델 하이브리드**는 PC 유저 대상 차별화 및 비용 절감 카드
5. **프로토타입 8주**면 핵심 메카닉 검증 가능 (Z3 + LLM + 터미널 UI)
