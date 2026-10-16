# CODEX New Skills

실제 EQ215 태블릿·DWG→PDF 프로젝트에서 반복된 기획, 검수, 문제해결, 기기시험과 Windows 자동화의 판단 방법을 정리한 개인 Codex Skill 저장소입니다. 기존 지침과 비교해 필요성을 검토하며, 제품 성공과 Skill의 추가 효과를 별도로 평가합니다.

## 현재 상태 — 2026-10-16

**기존 Skill 3개를 유지하고, 명세·회고용 참고 Skill 2개를 추가해 총 5개를 제공합니다.** 새 두 스킬의 [초기 기획부터 개발 검토까지 단계별 사용법과 복사할 요청 예시](docs/planning-review-skills.md)를 먼저 읽으세요. 모든 접속 장애 해결이나 전체 환경 검증이 완료됐다는 뜻은 아닙니다.

새 프로젝트에는 [AGENTS.md와 초기 기획·명세 템플릿](templates/README.md)을 적용할 수 있습니다. 오류·복구 계약이나 후보별 완료 판단이 필요한 요청에서만 두 스킬을 선택하도록 구성했습니다.

현재 PC의 Desktop을 직접 확인하려면 [수동 검증 절차·복사용 요청문](docs/desktop-manual-skill-check.md)과 [빈 결과 기록 양식](templates/desktop-skill-check-results.md)을 사용하세요. 새 임시 프로젝트만 준비하고 선택기 시험과 암묵 선택을 새 대화로 분리합니다. 이 안내의 게시가 Desktop 시험 통과를 뜻하지는 않습니다.

- 2026-10-16 암묵 선택 전용 후속: 새 대화 생성 요청을 별도로 검토했지만 준비한 nested 폴더와 일치하는 등록 프로젝트가 없고, 생성 도구에는 그 기존 절대경로를 직접 지정하는 인자가 없었습니다. 실제 시험 대화 CWD를 확인하지 못해 **I1·I2·I0는 미실행·미검증**으로 남겼습니다. 선택기 시험과는 다른 사전 조건입니다. [전용 새 대화 검토·재개 조건](evals/desktop-identity-tool-boundary-20261016/README.md#6-후속-전용-도구의-새-대화에서-암묵-선택만-가능한가)에 구분해 기록했으며 기존 설치본·설정은 바꾸지 않았습니다.

- 2026-10-16 앱 정체·도구 경계 후속: 패키지·실행 경로·제품 메타데이터로 **OpenAI.Codex 패키지와 ChatGPT 표시명의 공존**을 확인했습니다. 전용 프로젝트 목록 조회는 성공했지만 선택기·칩·암묵 선택 시험 기능은 제공되지 않아 Desktop 항목은 미검증입니다. 창 제목만으로 앱을 구분하지 않으며, UI 자동화 제한은 우회하지 않습니다. [읽기 전용 근거·전용 도구 검토·보존 범위](evals/desktop-identity-tool-boundary-20261016/README.md)를 기록했습니다.

- 2026-10-15 Desktop 후속: 직접 관측 도구 초기화 실패로 Desktop 선택기·암묵 선택은 **미검증**입니다. 임시 프로젝트의 CLI 자연어 요청 두 건은 해당 스킬을 읽었고 산술 음성 대조에는 대상 파일 읽기 이벤트가 없었습니다. 이를 Desktop 통과나 제품 간 동등성으로 합치지 않습니다. [실제 관측·CLI 비교·종료 한계](evals/desktop-skill-boundary-20261015/README.md)를 기록했으며 기존 설치본·템플릿은 변경하지 않았습니다.

- 2026-10-15 실제 Codex 확인: 설치된 CLI의 검색에는 다섯 동명 스킬의 개인·루트·하위본이 함께 나타났습니다. 이번 하위 CWD 명시 호출은 하위본을 읽었고, 개인본 경로 지정 대조는 개인본을 읽었습니다. 목록의 첫 항목을 보장된 선택 우선순위로 해석하지 않습니다. [실측·재현 자료·Desktop UI 등 미검증 범위](evals/codex-skill-discovery-20261015/README.md)를 기록했습니다. 기존 패키지·설정 11개 파일은 해시가 같습니다.

- 2026-10-15 후속: 다섯 스킬 모두 미설치 모의 환경과 기존 지침·동명 패키지에서 문서 적용을 시험했습니다. 전문 단일 검토에 릴리즈 검토를 공통 추가한 과잉 선택을 발견해 템플릿의 조건 한 행을 좁혔습니다. 독립 재시험에서 전문 스킬만 선택하고, 후보별 인계 검토에서는 필요한 스킬을 유지했습니다. [시험·정정·한계](evals/skill-compatibility-20261015/README.md)를 공개합니다. 실제 설치본·다섯 스킬 본문은 변경하지 않았습니다.

- 2026-10-15 초기: 두 서브에이전트가 단순 계산기와 복구 메모 서비스에 템플릿을 적용했습니다. 초기 작성과 후속 요청 네 단계의 선택·문서 결과가 사전 기준과 일치했습니다. [적용 예시와 한계](evals/template-application-20261015/README.md)를 게시했으며, 그 표본에서는 관측된 결함이 없어 본문을 유지했습니다. 위 후속 시험은 다른 조건에서 발견한 보완입니다.

- 2026-10-14 추가: `specify-failure-recovery`, `review-release-evidence`. 본문 형식·독립 적용·현재 PC 설치본 일치를 확인했습니다. [게시 범위와 검증 한계](docs/planning-review-validation-20261014.md)를 함께 기록합니다. 성능 향상이나 시간 절감을 입증한 판정은 아닙니다.

아래는 기존 세 스킬에 대한 2026-10-08 검증·범위 기록입니다.

- 최신 공식 형식 검사: Skill 3개 **LIMITED_PASS**. 결함 표본 3개와 정상 대조 1개도 예상대로 판정했습니다.
- 같은 합성 과제의 기준선/기존 체크리스트: 둘 다 **PARTIAL**. 구체적인 원복 절차 누락을 전체 PASS로 바꾸지 않았습니다.
- 구조적 원복 항목 초안: 별도 답변 1건에 요구 문안이 포함됐지만 효과·반복성·전이·채택은 미검증입니다. 초안은 로컬에 보관하며 새 Skill로 배포하지 않습니다.
- Edge 이번 비교는 사용자 지정으로 **범위 제외**입니다. 신규 브라우저·로컬 접속 Skill과 native 격리·에뮬레이터 적용은 **보류**합니다.
- 이번 추가 검증·문서 게시에서 완료된 태블릿 프로젝트와 실제 태블릿을 조작하지 않았습니다. 기존 Skill 본문·공개 체크리스트·설치 상태도 변경하지 않았습니다.

기존 세 스킬의 최신 근거는 [10/8 추가 검증 보고](docs/additional-validation-20261008.md)입니다. 초기 PyYAML 누락에 따른 BLOCKED와 이전 PARTIAL은 당시 기록으로 보존하며, 후속 결과를 소급 적용하지 않습니다.

## 제공하는 Skill 5개

| Skill | 용도 | 현재 채택·검증 경계 |
| --- | --- | --- |
| [specify-failure-recovery](skills/specify-failure-recovery/SKILL.md) | 초기 명세와 개발 검토에서 오류 발생·보존·복구·해제와 미정 정책을 연결 | 재사용 참고. 단순 오류에는 필요한 항목만 적용하며 제품 수정·실행을 승인하지 않음 |
| [review-release-evidence](skills/review-release-evidence/SKILL.md) | 후보별 원본·시험·수용 제한을 대조하고 우선순위와 검토 종료 판단 | 재사용 참고. 회고 완료와 제품 수정·재배포를 구분하며 효과·타PC 실사용은 미검증 |
| [coordinate-device-validation](skills/coordinate-device-validation/SKILL.md) | 사용자와 agent의 실기시험 준비·행동·관측·복귀를 조율하고 시간 예산을 검토 | 조건부 유지. 실제 기기 수락·인증·전원 조작을 대신하지 않음 |
| [verify-powershell-handoff](skills/verify-powershell-handoff/SKILL.md) | 대상 PowerShell의 JSON 배열·인수·인코딩·실패 처리와 인계 증거 검토 | 제한적 채택 유지. 브라우저 복구·Git 게시·제품 수용 판정을 대신하지 않음 |
| [diagnose-computer-use-recovery](skills/diagnose-computer-use-recovery/SKILL.md) | Windows native setup·파일 충돌·캡처 실패를 분류하고 승인된 복구/원복을 검토 | 실험적 참고·진단 후보 유지. 영구 복구·타PC 효과·브라우저 전체 복구는 미검증 |

이 저장소는 **지침 파일 모음**입니다. 브라우저 연결·포트·권한을 자동으로 고치는 프로그램이나 장치 제어 도구가 아닙니다. 기존 제품 전용 release-gate를 복제하거나 전역 교체하지 않습니다.

## 검증 결과와 해석

| 대상 | 확인된 범위 | 입증하지 않은 것 |
| --- | --- | --- |
| 공식 형식 검사 | 승인된 검증 폴더의 PyYAML을 검사 프로세스에서 사용. 기존 검사기와 세 스냅샷으로 형식 수락·결함 거부 확인 | 의미적 유효성 전체, 실제 행동·자동 선택·제품 수용 |
| PowerShell 인계 | 과거 동일 입력 비교, 5.1·7 기초 실행 및 의도적 실패 처리 기록 | 모든 운영 인계·시간/토큰 절감 |
| DWG 적용 | 해당 PC의 승인된 개발·검증·인계 종료 기록과 Skill 명시 로딩·실행 근거 | 다음 AutoCAD·타PC 수용, 제품 PASS만으로 Skill 효과 입증 |
| Chrome | 과거 작은 합성 파일 전송과 공개 HTTPS 읽기·클릭·새로고침 후 대상 재식별의 제한 관측 | 원래 로컬 포트·권한 장애 해결, 연결 단절 복구·장기 신뢰도 |
| 판단 비교 | 같은 합성 입력 1+1 답변 및 독립 정적 리뷰에서 둘 다 PARTIAL | 통제된 인과 A/B, 체크리스트의 효과 또는 무효 입증 |
| native 진단 후보 | 과거 오류 재현·진단 도구 회귀 기록 | 영구 복구, 타PC 일반화, 신규 Skill의 추가 효과 |

공식 형식 통과, 문안 검토, 실제 실행, 제품 수용, Skill 효과는 서로 다른 판정입니다. 주변 지침·표본 수·환경이 제한된 관측을 일반적인 성공률이나 모델 우열로 확대하지 않습니다. 자세한 조건·횟수·한계는 아래 보고서에서 확인하세요.

## 보류·미검증과 재개 조건

현재 축소 범위의 필수 추가 개발·시험은 없습니다. 다음 항목은 완료를 위해 PASS로 바꾸지 않고 보류·미검증으로 남깁니다.

- 원래 saved permission·로컬 포트 장애 복구와 실제 서비스 이전/원복.
- AppContainer/WFP·에뮬레이터의 실제 격리. 증거 export나 fake 단위시험은 격리 PASS가 아닙니다.
- Edge 이번 비교, 장기 신뢰도, 반복 안정성, 신규 Skill의 인과 효과·시간/토큰 절감.
- 형식 검사 설치 시 발생한 임시 흔적의 전체 정리와 전체 PC 무변화 감사.

기존 지침을 적용해도 실제 업무에서 같은 판단 누락이 반복되고, 더 작은 지침 보완이 불충분할 때만 신규 후보를 재검토합니다. 구체적 목표·승인 범위·복구/종료 조건·독립 표본과 동일 조건 비교를 먼저 마련합니다. 이미 성공한 시험을 새 목표 없이 반복하거나 별도 승인 없이 Edge·제품·기기를 재조작하지 않습니다.

[로컬 접속 체크리스트](docs/local-access-checklist.md)는 사람이 명시적으로 읽는 참고 문서이며 설치형 Skill이나 권한 부여 수단이 아닙니다. 정상적인 승인된 서비스 이전과 명시적 도구 거부의 우회를 구분합니다.

## 설치·사용

먼저 [사용 안내](docs/usage.md)를 읽고 지침 파일을 명시적으로 지정해 시험하세요. 전역 설치는 명시적인 요청과 결과 확인을 거칩니다. 이번 두 스킬은 요청자의 기존 개인 설치본이 있어 중복 설치 없이 게시 파일과 일치를 확인했습니다. 다른 사용자의 PC에는 자동 설치되지 않습니다.

기획·명세·개발 검토에는 다음 요청으로 두 스킬만 설치할 수 있습니다. [단계별 안내](docs/planning-review-skills.md)에는 프로젝트 전용 설치와 여섯 단계 요청 예시도 있습니다.

```text
$skill-installer를 사용해 https://github.com/jeonbyungryong/CODEX_NEW_SKILLS_261002 의
skills/specify-failure-recovery 와 skills/review-release-evidence 를 설치해줘.
같은 이름·같은 내용이면 건너뛰고, 내용이 다르면 기존 수정본을 보존하며 차이를 알려줘.
설치 파일과 사용 가능 목록을 확인해줘.
```

```text
https://github.com/jeonbyungryong/CODEX_NEW_SKILLS_261002 의
skills/coordinate-device-validation 을 검토한 뒤 설치해줘.
같은 이름의 기존 Skill이 있으면 덮어쓰지 말고 차이를 먼저 알려줘.
```

PowerShell 인계에는 `skills/verify-powershell-handoff`, Windows native 진단에는 `skills/diagnose-computer-use-recovery`를 지정할 수 있습니다. 저장소를 열거나 다운로드한 것만으로 설치가 완료되지는 않습니다. 필요한 스킬만 선택하세요.

사용 시 목표·승인 범위·현재 상태·실행 환경·복귀 조건과 증거를 제공합니다. 설치되어 사용 가능한 환경에서는 `$coordinate-device-validation` 또는 `$verify-powershell-handoff` 등을 요청에 명시할 수 있습니다. 사용자 실물 관측, 도구 로그, 권고와 실제 완료를 구분하세요.

## 문서 안내

| 문서 | 내용 |
| --- | --- |
| [Desktop 수동 확인 안내](docs/desktop-manual-skill-check.md) | 기존 설치본을 보존하는 임시 준비, 선택기·암묵 요청문, 증거 수준과 중단 기준 |
| [Desktop 결과 기록 양식](templates/desktop-skill-check-results.md) | 미실행 빈 양식. 선택기·칩·본문/경로·CLI 비교·보존·공개 정보 점검 |
| [Desktop 관측 한계·CLI 암묵 선택 — 10/15](evals/desktop-skill-boundary-20261015/README.md) | UI 초기화 실패, 두 양성·산술 음성의 실제 읽기, CLI와 Desktop을 합칠 수 없는 한계 |
| [실제 Codex 동명 검색·선택 — 10/15](evals/codex-skill-discovery-20261015/README.md) | CLI의 세 CWD 검색, 이름별 실제 읽기와 개인본 경로 대조, 보존·전송/UI 한계 |
| [다섯 스킬 호환성 시험 — 10/15](evals/skill-compatibility-20261015/README.md) | 미설치·기존 지침·동명 패키지, 보존 해시, 과잉 선택 보완과 독립 재시험 |
| [프로젝트 템플릿 적용 시험 — 10/15](evals/template-application-20261015/README.md) | 두 프로젝트·네 단계의 스킬 선택 보고, 실제 기획·명세·인계 예시와 확인 범위 |
| [새 프로젝트 템플릿](templates/README.md) | 프로젝트용 AGENTS.md, 초기 기획·명세, 조건별 스킬 선택과 복사 요청 |
| [기획·명세·개발 검토 단계별 사용법](docs/planning-review-skills.md) | 두 스킬의 역할, 여섯 단계 복사 요청, 다른 PC·프로젝트 설치와 중복 방지 |
| [두 스킬 게시 검증 — 10/14](docs/planning-review-validation-20261014.md) | 저장소 업로드 원칙·기존 세 스킬과의 비교·본문 식별·독립 적용 한계 |
| [기존 세 스킬 추가 검증 — 10/8](docs/additional-validation-20261008.md) | 공식 형식 후속 통과, 1+1 PARTIAL, 구조적 초안·독립 리뷰 한계 |
| [초기 최종 정리·범위 종료](docs/final-summary-20261008.md) | 초기 checkpoint와 후속 결과 안내, Edge 제외·재개 조건 |
| [축소 검증 마감 기록](docs/validation-closeout-20261008.md) | 범위 조정, 초기 형식 BLOCKED·native 격리 보류 |
| [설계·채택 기준](docs/design.md) | 후보 분석, 기존 기능 중복 제거와 비평 |
| [초기 검증 결과](docs/validation.md) | 기준선·같은 입력 비교·추가 사례의 조건과 한계 |
| [설치·사용 안내](docs/usage.md) | 명시 파일 적용과 설치 요청 |
| [설치 후 검증](docs/installation-verification.md) | 단일 PC 설치·등록·적용 근거와 미검증 범위 |
| [PowerShell 비교 검증](docs/powershell-handoff.md) | 비교 응답과 대상 엔진의 기초 실행 시험 |
| [Computer Use 평가](docs/computer-use-assessment.md) | 브라우저·권한·표시·전송·실행 계층의 기록과 생성 보류 판단 |
| [DWG 적용 점검](docs/dwg-application-review-20261007.md) | 실제 로딩·실행 근거와 제품/Skill 효과 구분 |
| [native 진단 후보 기록](docs/computer-use-recovery-20261007.md) | 오류 재현·회귀 시험·복구 미검증·타PC 인계 |
| [사람용 로컬 접속 체크리스트](docs/local-access-checklist.md) | 오류 계층·정상 포트 이전·반복 종료·독립 업무 구분 |

날짜별 상세 보고서와 실패 표본은 역사 근거로 보존합니다. README는 최신 상태의 요약이며, 과거 보고서의 개별 PASS·PARTIAL·BLOCKED를 변경하지 않습니다.

## 자료·보존·안전

- `skills/`: 지침과 필요한 참조. `docs/`: 설계·사용·검증·한계. `evals/`: 가상 사례와 비교 응답이며 실제 장치 로그가 아닙니다.
- 과거 상태는 Git 이력과 기존 작업 브랜치로 보존합니다. 강제 push·기존 자료 일괄 삭제는 하지 않습니다.
- 원시 trace·스크린샷·인증정보·서명 키·APK·회사 내부 원본·장치 식별정보·검증용 설치 패키지는 공개 자료에 넣지 않습니다.
- 프로젝트 승인 기준과 도구의 현재 제한이 우선입니다. Skill은 권한을 부여하거나 인증·정책을 우회하지 않습니다.
- 시간 부족·미실시를 PASS로 바꾸지 않습니다. 복구 성공과 원인 규명도 구분합니다.
- 별도 라이선스는 아직 지정하지 않았습니다. 공개 저장소라는 이유만으로 특정 오픈소스 라이선스 적용을 가정하지 마세요.
