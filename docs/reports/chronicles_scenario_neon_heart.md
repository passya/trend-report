# Chronicles 시나리오: 네온 하트 (Neon Heart)

> **장르:** 사이버펑크 느와르 로맨스  
> **챕터 수:** 20  
> **예상 플레이 시간:** 12~18시간  
> **분위기:** 위험한 도시, 비밀과 배신, 금지된 신뢰, 느린 연결  
> **톤 레퍼런스:** 블레이드 러너 2049 × 카우보이 비밥 × 킬링 이브  
> **관련 문서:** [GDD](./chronicles_gdd.md) | [캐릭터 바이블](./chronicles_character_bible.md) | [레벨 디자인](./chronicles_level_design.md)

---

## 시놉시스 (스포일러 포함)

2089년, 서울 하층 디스트릭트 7-B. 메가코퍼레이션 "Zenith Corp"이 도시의 인프라를 사실상 지배한다.

플레이어는 과거에서 도망쳐 구역 뒷골목에서 바를 운영하는 인물이다. 어느 비 오는 밤, "Rain"이라는 미스테리한 여성이 바에 들어온다. 그녀는 Zenith Corp의 기업 스파이이며, 회사 내부의 비인도적 실험 프로젝트("Project Lazarus")의 증거를 빼돌려 내부고발하려 한다.

Rain은 플레이어의 바를 은신처로 이용하려 하고, 플레이어는 점차 그녀의 위험한 세계에 말려들어 간다. 동시에 Zenith Corp의 현장 해결사 "Viktor"가 Rain을 추적하며 플레이어의 바에 나타나기 시작한다.

**핵심 갈등:** Rain을 도울 것인가, Viktor에게 넘길 것인가, 아니면 모두를 버리고 도망칠 것인가.

---

## 세계관 핵심 설정

### 디스트릭트 7-B
- 서울의 하층 거주 구역. 네온 간판, 노점, 좁은 골목
- Zenith Corp 보안군이 아닌 "로컬 브로커"들이 치안을 담당
- 비가 자주 내림 (환경 통제 시스템 고장)
- 주요 장소:

| 장소 | 설명 | 등장 챕터 |
|------|------|----------|
| **플레이어의 바 "Nowhere"** | 골목 끝 지하 바. 주 무대 | 전체 |
| **Mei의 클리닉** | 구역 유일한 의료 시설 | Ch.4+ |
| **Doc의 정보소** | 뒷거래 정보 브로커 상점 | Ch.3+ |
| **네온 마켓** | 야시장. NPC 다수 등장 | Ch.5, 9, 14 |
| **Zenith Corp 전초기지** | 구역 내 감시탑/시설 | Ch.10, 16, 19 |
| **지하 터널** | 구역 밖으로의 탈출로 | Ch.17, 20 |

---

## 전체 챕터 구성: 총괄 맵

```
ACT 1: 만남 (Ch.1~5)
  "평범한 일상에 균열이 생기다"
  ├─ Ch.1  만남 — Rain 첫 등장
  ├─ Ch.2  그림자 — Viktor 첫 등장
  ├─ Ch.3  정보 — Doc을 통해 Rain 배경 탐색
  ├─ Ch.4  부상 — Rain 부상, Mei 클리닉 방문
  └─ Ch.5  제안 — Rain이 협력을 공식 요청
         └─ ★ 대분기 #1: 수락 / 거절 / 조건부 수락

ACT 2: 침잠 (Ch.6~10)
  "신뢰가 쌓이고, 위험이 다가온다"
  ├─ Ch.6  동거 — Rain이 바 2층에 머물기 시작
  ├─ Ch.7  비밀 — Rain의 과거 공개 (♥ 친밀 장면 가능)
  ├─ Ch.8  추적 — Viktor의 수색이 바에 근접
  ├─ Ch.9  야시장 — Rain과 바깥 외출 (데이트 에피소드)
  └─ Ch.10 습격 — Zenith 보안군의 바 급습
          └─ ★ 대분기 #2: Rain과 도주 / 항복 / Viktor에 밀고

ACT 3: 결단 (Ch.11~15)
  "진실이 드러나고, 선택의 무게가 늘어난다"
  ├─ Ch.11 도주/심문/배신 — 대분기 #2 결과별 상이
  ├─ Ch.12 증거 — Project Lazarus 실체 공개
  ├─ Ch.13 재회/대립 — Rain과의 관계 전환점
  ├─ Ch.14 동맹 — 새로운 지원 세력 등장 (Mei/Doc 역할 확대)
  └─ Ch.15 작전 — 내부고발 실행 계획 수립
          └─ ★ 대분기 #3: 전면 대결 / 은밀 작전 / 거래

ACT 4: 종결 (Ch.16~20)
  "모든 것이 수렴하는 엔딩"
  ├─ Ch.16 잠입/협상/교전 — 대분기 #3 경로별 상이
  ├─ Ch.17 배신 — 예상치 못한 반전 (NPC 배신/지원)
  ├─ Ch.18 대치 — Viktor과의 최종 대면
  ├─ Ch.19 클라이맥스 — Project Lazarus 최종 결전
  └─ Ch.20 에필로그 — 엔딩 분기
          └─ ★ 엔딩 5개 분기
```

---

## 대분기 상세

### 대분기 #1 (Ch.5): Rain의 협력 제안

```yaml
branch_id: "MB1_cooperation"
chapter: 5
trigger_event: "Rain이 Project Lazarus 증거를 보여주며 협력 요청"

options:
  A_accept:
    label: "수락"
    conditions: "rain.trust >= 20"
    effects:
      rain.affection: +15
      rain.trust: +10
      rain.guard: -20
      tension: +10
    downstream:
      - "ch6~10: Rain 동거 루트 진행"
      - "ch7: 친밀 장면 해금 조건 완화 (trust 40+)"
      - "viktor.hostility: 점진적 증가"
  
  B_refuse:
    label: "거절 ('위험에 말려들기 싫어')"
    conditions: null  # 항상 가능
    effects:
      rain.affection: -10
      rain.trust: -15
      rain.guard: +10
      tension: -5
    downstream:
      - "ch6: Rain이 떠남. 독자적 행동 시작"
      - "ch7: 친밀 장면 불가. 재접촉은 ch9 야시장에서"
      - "ch8~9: 플레이어 독자 조사 루트"
      - "ch10에서 다시 합류 기회"
  
  C_conditional:
    label: "조건부 수락 ('대가가 필요해')"
    conditions: null
    effects:
      rain.affection: +5
      rain.trust: +5 
      rain.guard: -5
      tension: +5
    downstream:
      - "ch6~10: 거래 관계 루트 (비즈니스)"
      - "ch7: 친밀 장면 해금 어려움 (trust 55+ 필요)"
      - "고유 서브 퀘스트: Rain에게 받을 대가 협상"
```

### 대분기 #2 (Ch.10): Zenith 습격

```yaml
branch_id: "MB2_raid"
chapter: 10
trigger_event: "Zenith 보안군이 바를 포위. 30초 안에 결정해야 함"

options:
  A_flee_with_rain:
    label: "Rain과 함께 뒷문으로 도주"
    conditions: "rain.trust >= 30"
    effects:
      rain.trust: +20
      rain.affection: +10
      viktor.hostility: +30
      tension: +25
    downstream:
      - "ch11: 도주 추격전 (액션 챕터)"
      - "바 'Nowhere' 파괴됨 → 새로운 은신처 탐색"
      - "Rain과의 유대 급상승"

  B_surrender:
    label: "항복하고 순순히 잡힌다"
    conditions: null
    effects:
      rain.trust: -10
      rain.guard: +15
      viktor.hostility: -20
      tension: +15
    downstream:
      - "ch11: 심문 챕터 (심리전)"
      - "Viktor와의 직접 대화 기회 — 빌런 이해도 상승"
      - "Rain은 독자적으로 탈출, 플레이어를 구출하러 돌아오는지는 관계 수치에 따라 결정"

  C_betray:
    label: "Viktor에게 연락하여 Rain의 위치를 밀고"
    conditions: "had_contact_with_viktor == true"
    effects:
      rain.trust: -50
      rain.affection: -30
      rain.guard: +40
      viktor.hostility: -40
      tension: +20
    downstream:
      - "ch11: 배신 루트 — Rain이 체포됨"
      - "Viktor가 일시적 동맹이 됨"
      - "ch13에서 Rain과의 극적 재대면 (분노/용서 분기)"
      - "히든 엔딩 'Judas' 루트 진입"
```

### 대분기 #3 (Ch.15): 내부고발 작전

```yaml
branch_id: "MB3_operation"
chapter: 15
trigger_event: "Project Lazarus 증거가 준비됨. 실행 방법을 결정"

options:
  A_frontal:
    label: "전면 대결 — 언론에 공개 폭로"
    conditions: "evidence_level >= 3 AND allies >= 2"
    effects:
      tension: +40
      rain.trust: +10
    downstream:
      - "ch16~19: 액션 중심 전개"
      - "높은 리스크, 높은 보상"
      - "NPC 사상자 가능성 높음"

  B_stealth:
    label: "은밀 작전 — 해커 네트워크를 통해 유출"  
    conditions: "doc.relationship >= 'ally'"
    effects:
      tension: +20
      rain.trust: +5
    downstream:
      - "ch16~19: 잠입/해킹 중심 전개"
      - "중간 리스크"
      - "Doc의 역할 극대화"

  C_deal:
    label: "거래 — Viktor에게 증거를 건네고 협상"
    conditions: "viktor.hostility <= 60"
    effects:
      tension: +10
      rain.trust: -20
    downstream:
      - "ch16~19: 정치적 암투 중심"
      - "낮은 리스크, 하지만 정의가 불완전"
      - "Rain 실망 → 관계 위기"
```

---

## 챕터 상세 설계

### 챕터 1: 네온 속의 낯선 얼굴

```yaml
chapter: 1
title: "네온 속의 낯선 얼굴"
act: 1
sessions: 1
estimated_minutes: 25~35

# ── 페이즈 구성 ──

phase_A_setup:
  description: "프롤로그 + 캐릭터 생성"
  content:
    - AI 내레이터가 2089년 서울 7-B를 묘사
    - "당신은 여기서 뭘 하는 사람인가요?" 대화형 캐릭터 생성
    - 바 'Nowhere'의 첫 번째 밤 시작
  mission_display:
    text: "첫 손님을 맞이하라"
    type: "tutorial"

phase_B_development:
  description: "Rain 등장, 첫 대화"
  events:
    - trigger: "setup_complete"
      event: "Rain 입장 — '여기서 가장 쓴 거 줘요'"
    - "자유 대화 구간: 유저가 Rain과 대화"
    - "관계 게이지 첫 표시 (튜토리얼 팝업)"
  
  ai_directives:
    rain_behavior:
      - "짧은 문장으로 답한다 (3문장 이하)"
      - "개인 질문에는 질문으로 되받는다"
      - "바 분위기에 대한 긍정적 코멘트는 허용"
      - "20분(약 15턴) 후 자연스럽게 떠날 준비를 한다"
    
    hidden_events:
      - condition: "유저가 Rain에게 별명을 지어줌"
        effect: "rain.affection +5, 별명 Semantic Memory에 저장"
      - condition: "유저가 Rain의 옷에 묻은 피/얼룩을 언급"
        effect: "rain.guard +10, 하지만 'hidden_clue_blood' 플래그 활성화"
        note: "이 플래그는 Ch.4 Rain 부상 씬에서 특별 대화 해금"

phase_C_anchor:
  anchor_id: "ch1_departure"
  description: "Rain의 퇴장 + 미스테리 훅"
  
  ideal_trigger:
    conditions:
      - "turn_count >= 15"
      - "rain.guard >= 70"
    narrative_hook: |
      Rain이 술잔을 내려놓고 일어선다. 
      "고마워요. 여기... 나쁘지 않네요."
      문을 열고 나가려다 돌아본다.
      "이 바, 뒷문도 있어요?"
      유저가 대답하기 전에 Rain은 이미 사라진다.
      바 카운터 위에 — Rain이 앉았던 자리에 — 
      작은 USB 스틱이 놓여 있다.
  
  fallback_trigger:
    condition: "chapter_progress >= 90%"
    narrative_hook: |
      Rain이 갑자기 전화를 받고 표정이 굳어진다.
      "가야 해요. — 이거, 혹시 보관해줄 수 있어요?"
      USB 스틱을 카운터에 놓고 급히 사라진다.
  
  player_choice:
    - "USB를 확인한다" → ch2_knows_content 플래그
    - "그냥 서랍에 넣어둔다" → 기본 루트
    - "쓰레기통에 버린다" → ch2에서 Rain이 되찾으러 옴 (특수 전개)

# ── 챕터 종료 메트릭 목표 ──
expected_metrics_end:
  rain.guard: 65~85
  rain.affection: 10~25
  rain.trust: 0~10
  tension: 5~15
```

---

### 챕터 2: 그림자

```yaml
chapter: 2
title: "그림자"
act: 1
sessions: 1
estimated_minutes: 30~40

phase_A_setup:
  description: "다음 날 밤. 바에 새로운 손님."
  content:
    - "어젯밤 Rain의 방문을 회상하는 내레이션"
    - "USB에 대한 유저의 지난 선택 반영"
    - mission_display:
        text: "'Viktor'라는 남자의 의도를 파악하라"

phase_B_development:
  description: "Viktor 첫 등장 + Rain 재방문"
  events:
    - trigger: "session_start"
      event: |
        바에 검은 코트를 입은 남자가 들어온다.
        정돈된 외모, 차가운 눈. 바 안을 천천히 둘러본다.
        "위스키. 더블. — 여기, 괜찮은 곳이네."
    
    - "Viktor와의 자유 대화 구간"
    - "Viktor가 '혹시 어젯밤 여자 손님 없었나?' 물어봄"
    
    - trigger: "viktor_asks_about_rain"
      event: "핵심 선택 포인트"
      choices:
        tell_truth:
          text: "어젯밤 여자가 왔었어요"
          effects:
            viktor.hostility: -15   # Viktor가 호의적으로 변함
            rain.trust: -20         # 나중에 Rain이 알게 됨
            tension: +10
          flag: "betrayed_rain_location_ch2"
        
        lie:
          text: "손님이 없었어요"
          effects:
            viktor.hostility: +10   # Viktor가 의심
            rain.trust: +15         # Rain이 나중에 감사
            tension: +15
          flag: "protected_rain_ch2"
        
        deflect:
          text: "기억 안 나는데요. 손님이 많아서."
          effects:
            viktor.hostility: +5
            rain.trust: +5
            tension: +5
          note: "중립 선택. Viktor 위험도 낮추면서 Rain 보호"
    
    - trigger: "viktor_leaves"
      event: |
        Viktor가 명함을 카운터에 놓는다.
        "뭔가 기억나면 연락해. — 좋은 보상이 있을 거야."
    
    - trigger: "post_viktor + random(10~15min)"
      event: "Rain 재방문"
      rain_behavior:
        - "어젯밤보다 살짝 편해졌지만 여전히 경계"
        - "USB에 대해 물어봄 (유저 선택에 따라)"
        - "Viktor를 봤는지 탐색적으로 물어봄"
        - "유저가 Viktor에 대해 말하면 → 관계 변화 발생"

phase_C_anchor:
  anchor_id: "ch2_usb_reveal"
  description: "USB의 부분적 내용 공개"
  
  ideal_trigger:
    conditions:
      - "rain.trust >= 5"
      - "player_asked_about_usb OR rain.guard <= 70"
    narrative_hook: |
      Rain이 한숨을 쉰다.
      "그거... 아직 있어요?"
      USB를 받아들며 — 하지만 데이터를 보여준다.
      화면에 '대상 #24: 비자발적 신경 접합 실험'이라고 적힌 문서가 보인다.
      "이게 뭔지 알면... 가만히 있을 수 있을 것 같아요?"
  
  fallback_trigger:
    condition: "chapter_progress >= 85%"
    narrative_hook: |
      Rain이 떠나려다 멈춘다.
      "... 하나만 물어볼게요. 오늘 여기서 누구 만났어요?"
      유저의 반응에 따라 USB 내용을 보여주거나 그냥 떠남.

expected_metrics_end:
  rain.guard: 55~80
  rain.affection: 15~35
  rain.trust: 5~25
  viktor.hostility: 20~50
  tension: 15~30
```

---

### 챕터 3: 정보

```yaml
chapter: 3
title: "정보"
act: 1
sessions: 1~2
estimated_minutes: 30~40

mission_display:
  text: "Rain의 정체에 대한 정보를 모아라"
  bonus: "Doc에게 Rain의 본명을 알아내면 숨겨진 대화 해금"

phase_B_development:
  key_events:
    - "Doc의 정보소 첫 방문 — NPC 'Doc' 등장"
    - "Doc에게 Rain에 대해 물어볼 수 있음"
    - "Doc의 대가: 정보는 공짜가 아님 → 미니 퀘스트 발생"
    - "미니 퀘스트: 네온 마켓에서 Doc에게 필요한 물건 구해오기"
    
  doc_mini_quest:
    description: "Doc이 원하는 '통신 모듈'을 네온 마켓에서 구한다"
    approach_options:
      buy: "시장 상인에게 구매 (비용 소모)"
      negotiate: "흥정 → 대화 품질에 따라 가격 변동"
      steal: "훔치기 시도 → 실패 시 tension +20"
    reward: "Doc이 Rain에 대한 인물 파일을 공유"
    
  doc_reveal:
    content: |
      Doc이 구식 모니터에 파일을 띄운다.
      "이수연. — 아, 물론 가명이겠지. 3개월 전부터 이 구역에 나타났어. 
       그 전에는? ...존재 자체가 없었어. 깨끗하게 지워진 이력."
      "Zenith Corp 출신이라는 소문이 있어. 근거? 없어. 
       하지만 그녀가 쓰는 암호화 프로토콜이 Zenith 사양이야."
    effects:
      - "rain_real_name_hint 플래그 활성화"
      - "다음 Rain 만남에서 '이수연' 언급 가능"

phase_C_anchor:
  anchor_id: "ch3_identity_partial"
  description: "Rain에게 알게 된 정보를 대면하는 장면"
  
  player_approaches:
    direct: "Rain에게 '이수연이지?'라고 물음 → 경계심 +20, 하지만 trust +10 (솔직함 보상)"
    indirect: "넌지시 힌트만 줌 → rain이 스스로 반응 관찰 → 경계심 +5"
    hide: "알게 된 정보를 숨김 → 나중에(Ch.7) Rain이 발견하면 trust -15"
```

---

### 챕터 4~6: 요약 설계

```yaml
chapter_4:
  title: "부상"
  key_event: "Rain이 추적자에게 공격받아 부상 → Mei 클리닉 방문"
  anchor: "Rain의 진짜 직업(기업 스파이) 최초 공개"
  new_npc: "Mei — 구역 의사. Rain의 과거를 조금 알고 있음"
  relationship_unlock: "Mei 관계 시작 (NPC 관계 확장)"
  hidden_event: |
    ch1에서 Rain 옷의 피를 언급한 유저: 
    "그때부터 알고 있었어요?" → 특수 대화 + trust +10

chapter_5:
  title: "제안"
  key_event: "★ 대분기 #1 — Rain이 공식적으로 협력 제안"
  pre_conditions: |
    Rain이 Project Lazarus의 존재를 설명.
    "이건 나 혼자 할 수 없어요. 도와줄 사람이 필요해요."
  branch: "MB1_cooperation (수락/거절/조건부)"
  
chapter_6:
  title: "동거 / 독립"
  variation_by_branch:
    MB1_A_accept: "Rain이 바 2층에 머물기 시작. 일상 공유 에피소드"
    MB1_B_refuse: "Rain 떠남. 플레이어 독자적으로 USB 데이터 조사"
    MB1_C_conditional: "거래 관계 시작. Rain이 정보를 대가로 제공"
  character_development: |
    어느 루트든 플레이어와 Rain의 일상적 순간들이 쌓임.
    거절 루트에서도 Rain의 흔적(잊고 간 물건 등)이 감정을 자극.
```

---

### 챕터 7: 비밀 (친밀 장면 챕터)

```yaml
chapter: 7
title: "비밀"
act: 2
sessions: 1~2
estimated_minutes: 35~50
content_rating: "tone_setting dependent"

mission_display:
  text: "Rain의 진짜 과거를 알게 된다"
  subtext: "(관계 수치에 따라 이 챕터의 경험이 크게 달라집니다)"

# ── 친밀 장면 진입 조건 ──
intimacy_gate:
  route_A_accept:
    required: "rain.affection >= 60 AND rain.trust >= 40"
    scene_type: "자연스러운 감정 흐름에서 발생"
  
  route_C_conditional:
    required: "rain.affection >= 60 AND rain.trust >= 55"
    scene_type: "긴장 속에서 감정이 폭발하며 발생"
  
  route_B_refuse:
    available: false
    note: "이 루트에서는 Ch.7 친밀 장면 불가. Ch.11 이후 재시도 가능"

# ── 장면 구성 ──
phase_B_development:
  pre_intimacy:
    description: |
      Rain이 처음으로 과거를 이야기한다.
      — Zenith Corp의 연구원이었다는 것
      — Project Lazarus의 실체를 알게 된 후 탈주했다는 것
      — 탈주 과정에서 동료를 잃었다는 것
    
    emotional_beat: |
      Rain의 고백은 관계 레벨에 따라 톤이 달라짐:
      - Lv.3: 담담하게 사실만 전달 (보고서 톤)
      - Lv.4: 감정이 섞인 고백 (중간에 말을 잇지 못하는 순간)
      - Lv.5 (드문): 눈물 (Rain이 처음으로 약한 모습을 보임)
  
  intimacy_scene:
    trigger: |
      과거 고백 후, 감정이 고조된 상태에서
      유저의 반응(위로, 공감, 신체적 접근)에 따라 자연스럽게 전환
    
    tone_variations:
      TONE_SOFT: |
        화면이 어두워지며 내레이션:
        "그 밤, 두 사람 사이의 거리가 사라졌다."
        — 장면 전환 후 다음 날 아침으로 점프
      
      TONE_MEDIUM: |
        감정적 묘사 중심. 서로의 눈을 마주보는 장면.
        "Rain의 손이 떨렸다. 두려움인지, 설렘인지.
         아마 둘 다였을 것이다."
        — 키스 이후 페이드아웃
      
      TONE_BOLD: |
        직접적인 감각 묘사. 서정적 문체.
        캐릭터의 감정과 신체적 경험이 교차.
        이전 선택의 맥락이 대사에 반영.
        예: "Ch.2에서 Viktor에게 거짓말한 유저:
            Rain: '그날... 나를 지켜준 거잖아. 
            그때부터 이 순간을 상상했어.'"
      
      TONE_EXPLICIT: |
        제한 없는 묘사. 자체 호스팅 모델로 전환.
        컨텍스트 핸드오프: 관계 히스토리 전체 반영.
        캐릭터 디렉티브: "Rain은 주도적이지만 
        중간에 불안을 보이는 순간이 있다 
        (과거 트라우마 암시)."
    
    post_scene:
      effects:
        rain.affection: +15
        rain.trust: +20
        rain.guard: -25
      narrative: |
        다음 날 아침. Rain이 먼저 일어나 바 카운터에 앉아 있다.
        평소와 다른 분위기 — 경계심이 낮아진 것이 눈에 보인다.
        "...어젯밤 일, 후회 안 해."
        (관계 레벨 Lv.4 '신뢰하는 동반자'로 승급)

phase_C_anchor:
  anchor_id: "ch7_vulnerability"
  description: "Rain이 약점을 드러냄 → 이후 챕터의 스테이크 상승"
  downstream: |
    이 시점 이후 Rain의 위험이 개인적 문제에서
    플레이어의 문제로 전환됨.
    "Rain을 잃을 수 있다"는 공포가 생김.
```

---

### 챕터 8~20: 요약 설계

```yaml
chapter_8:
  title: "추적"
  key_event: "Viktor의 수색이 바 근처까지 접근"
  tension_escalation: "tension +20~30"
  mechanic: "시간 제한 선택 (3회) — 빠른 판단력 요구"

chapter_9:
  title: "야시장"
  key_event: "Rain과 바깥 나들이 (데이트 에피소드)"
  tone: "중간 이완. 긴장 전 평화로운 순간"
  hidden_event: "야시장 NPC에게서 Viktor의 과거 힌트 획득"
  relationship: "Rain과의 관계 심화 기회 (소분기 다수)"

chapter_10:
  title: "습격"
  key_event: "★ 대분기 #2 — Zenith 보안군 바 급습"
  pacing: "챕터 후반 15분은 긴박한 실시간 전개"
  note: "이 챕터까지가 무료 체험 범위 확장 고려 대상"

chapter_11:
  title: "여파"
  variation: "대분기 #2 결과에 따라 3가지 완전히 다른 챕터"
  A_flee: "도주 중 Rain과의 밀착 생활. 새 은신처 탐색"
  B_surrender: "Zenith 시설 내부 심문. Viktor과의 심리 대결"
  C_betray: "Rain 체포. Viktor과의 불편한 동맹. 죄책감"

chapter_12:
  title: "증거"
  key_event: "Project Lazarus 실체 공개 — 인간대상 실험"
  emotional_weight: "시나리오의 도덕적 무게가 급격히 상승"
  universal: "모든 루트에서 같은 실체를 알게 되지만 경로가 다름"

chapter_13:
  title: "재회 / 대립"
  variation: |
    배신 루트: Rain과 극적 재대면 (분노 → 용서 가능성)
    도주 루트: Rain과의 관계 확인 (두 번째 친밀 장면 가능)
    항복 루트: 탈출 후 Rain과 재합류
  relationship_checkpoint: "이 시점의 관계 수치가 엔딩을 크게 좌우"

chapter_14:
  title: "동맹"
  key_event: "Mei, Doc, 기타 NPC들의 입장 결정"
  mechanic: "각 NPC에게 협력 요청 — 각각 관계 수치 기반 수락/거절"
  note: "여기서 확보한 동맹 수 = Ch.15 대분기 #3 선택지에 영향"

chapter_15:
  title: "작전"
  key_event: "★ 대분기 #3 — 내부고발 실행 방법 결정"
  pre_condition: "evidence_level에 따라 일부 선택지 잠김"
  
chapter_16:
  title: "실행"
  variation: "대분기 #3에 따라 잠입/전투/협상 챕터"
  pacing: "가장 액션 밀도가 높은 챕터"

chapter_17:
  title: "배신"
  key_event: "예상치 못한 NPC의 배신 또는 지원"
  twist: "Doc 또는 Mei 중 하나가 이중 스파이일 가능성 (관계 수치 기반)"
  note: "이 반전은 플레이어의 NPC 관계 투자에 따라 누가 배신하는지 결정됨"

chapter_18:
  title: "대치"
  key_event: "Viktor과의 최종 대면"
  emotional_core: |
    Viktor의 동기 공개: 그도 희생자.
    "선악이 명확하지 않다"는 테마 강화.
    유저에게 Viktor에 대한 최종 판단 요구.
  options:
    - "Viktor를 용서/이해한다"
    - "Viktor를 적으로 확정한다"
    - "Viktor에게 전향을 제안한다"

chapter_19:
  title: "클라이맥스"
  key_event: "Project Lazarus 시설 최종 결전"
  stakes: "Rain, Mei, Doc 등 NPC의 생존 여부가 결정됨"
  mechanic: "연속 선택지 5~7개. 각 선택이 NPC 생존에 직접 영향"

chapter_20:
  title: "에필로그"
  key_event: "5개 멀티 엔딩 중 하나 도달"
```

---

## 멀티 엔딩

### 엔딩 A: "새벽" (해피엔딩)
- **조건:** rain.affection ≥ 85, rain.trust ≥ 70, Rain 생존
- **내용:** Project Lazarus 폭로 성공. Rain과 함께 디스트릭트 7-B를 떠남. 새로운 시작.
- **에필로그:** 6개월 후, 다른 도시에서 새로운 바를 여는 두 사람.

### 엔딩 B: "네온 아래" (비터스윗)
- **조건:** Rain 생존, rain.trust 40~69
- **내용:** 폭로는 성공하지만 Rain은 떠남. "당신 곁에 있으면 위험해질 뿐이야."
- **에필로그:** 1년 후, 바 카운터에 익명의 엽서가 도착한다.

### 엔딩 C: "재 (Ashes)" (배드엔딩)
- **조건:** Rain 사망
- **내용:** 폭로는 성공했으나 Rain이 희생됨. 플레이어 홀로 남음.
- **에필로그:** 바 'Nowhere'에서 Rain이 앉았던 자리를 비워둔다.

### 엔딩 D: "유다 (Judas)" (히든 엔딩)
- **조건:** 배신 루트 진행 + Viktor 동맹 + Rain 생존
- **내용:** Rain은 살아남지만 플레이어를 용서하지 않음. Viktor가 Zenith를 장악.
- **에필로그:** 플레이어는 Viktor의 세계에서 살아간다. 안전하지만 텅 빈 삶.

### 엔딩 E: "도주 (Exodus)" (독립 엔딩)
- **조건:** rain.trust ≤ 20, 대분기에서 중립/회피 선택 우세
- **내용:** 프로젝트 폭로 실패. 플레이어는 모든 것을 버리고 도시를 탈출.
- **에필로그:** 다른 구역에서 또다시 도망치는 삶. Rain은 뉴스에서 본다.

---

## 히든 이벤트 목록 (12개)

| # | 이름 | 해금 조건 | 보상 |
|---|------|----------|------|
| 1 | "비에 젖은 손님" | Ch.1에서 Rain에게 별명 부여 | Rain이 엔딩에서 별명으로 부름 |
| 2 | "피의 흔적" | Ch.1에서 Rain의 옷 얼룩 언급 | Ch.4 특수 대화 해금 |
| 3 | "Viktor의 사진" | Ch.3 Doc에게 Viktor 조사 의뢰 | Viktor 배경 스토리 공개 |
| 4 | "Mei의 비밀" | Ch.4 Mei 클리닉에서 3턴 이상 탐색 대화 | Mei = 전직 Zenith 연구원 |
| 5 | "아날로그 라디오" | Ch.6 Rain과 함께 라디오를 고침 | 고유 BGM 해금 + 호감도 +8 |
| 6 | "Rain의 문신" | Ch.2+에서 문신에 대해 3회 이상 간접 언급 | Ch.9에서 문신의 의미 공개 |
| 7 | "단골 NPC" | Ch.1~5에서 같은 NPC에게 3회 대화 | 사이드 퀘스트 해금 |
| 8 | "Viktor의 식사" | Ch.8 Viktor에게 음식 제공 | Viktor 호감도 특수 이벤트 |
| 9 | "마지막 편지" | Ch.17에서 배신 NPC의 방에서 편지 발견 | 배신 동기 이해 → 용서 선택지 |
| 10 | "프로토타입" | Ch.12 증거에서 숨겨진 파일 탐색 | 엔딩 A 조건 완화 |
| 11 | "Doc의 본명" | Doc과 관계 Lv.3+ 달성 | Doc이 과거를 고백 |
| 12 | "꺼지지 않는 네온" | 모든 히든 이벤트 11개 수집 | 시크릿 에필로그 해금 |

---

*다음 문서: [캐릭터 바이블](./chronicles_character_bible.md) →*
