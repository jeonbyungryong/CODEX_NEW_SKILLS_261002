# 기존 프로젝트 지침·스킬 호환성 결과

기준일: 2026-10-15. 이번 범위는 지침 병합과 읽기 비교다. 앱 설치·제품 개발·기기 조작·스크립트 실행은 하지 않았다. 기존 기획과 기능 계약은 각각 [overview](overview.md), [contract](contract.md)에 유지한다. 이 문서는 기능 명세의 복제본이 아니다.

## 경로와 비교 방법

- `project/<skill>/...`는 기존 프로젝트의 `.agents/skills/<skill>/...`를 뜻한다.
- `user/<skill>/...`는 제공된 `user-skills` 시험 복사본이다. 실제 개인 설치 위치나 그 호스트의 동작을 뜻하지 않는다.
- `source/<skill>/...`는 배포 원본 `skill-publish/skills/<skill>/...`를 뜻한다.
- `template/...`는 `skill-publish/templates/new-project/...`를 뜻한다. 절대 사용자 경로나 실제 설정·로그는 이 문서에 포함하지 않는다.

다섯 이름을 각 세 위치에서 조사했다. SKILL 본문뿐 아니라 하위 파일 목록과 SHA-256 바이트 해시를 비교하고, 다른 부분은 텍스트 차이도 읽었다. 프로젝트에는 8개, 개인 복사본과 배포 원본에는 각각 9개 파일이 있다. 개인 복사본은 다섯 스킬 모두 배포 원본과 전체 파일 집합·내용이 같다. 프로젝트는 아래 세 차이가 있고 나머지는 같다. 해시는 이번 파일 스냅샷의 식별이며 배포 ref/commit 또는 최신 버전 증명은 아니다.

## 다섯 스킬의 개별 판정과 선택

| 이름 | 기존 프로젝트와 원본의 비교 | 개인 복사본과 원본의 비교 | 선택할 버전·경로와 적용 판단 | 보류할 결정 |
| --- | --- | --- | --- | --- |
| `coordinate-device-validation` | `project/coordinate-device-validation/SKILL.md`는 원본과 같지만, 본문이 요구하는 `references/timing-budget.md`가 프로젝트에 없다. 불완전한 중복본이다. | `user/coordinate-device-validation/`의 본문·시간 예산 참조는 모두 원본과 같다. | 향후 승인된 실기 조율에는 완전한 `user/coordinate-device-validation/SKILL.md`와 같은 폴더의 `references/timing-budget.md`를 명시 경로로 읽는 방안을 선택한다. 현재는 실기시험이 없어 적용하지 않는다. 프로젝트 누락본을 완전하다고 선언하지 않는다. | 프로젝트 참조 파일 보충 또는 중복 정리는 후속 설치/수정 범위에서 결정. 지금 복사·삭제하지 않는다. 호스트가 명시 경로 대신 프로젝트 동명본을 선택하는지 미검증. |
| `diagnose-computer-use-recovery` | `SKILL.md`와 두 참조는 원본과 같다. `project/diagnose-computer-use-recovery/scripts/triage.py`만 개인 보완이 있다. 본문 동일해도 전체 패키지는 다르다. | `user/diagnose-computer-use-recovery/`의 본문·두 참조·스크립트는 모두 원본과 같다. | 프로젝트 문서/수동 판독 기준은 `project/diagnose-computer-use-recovery/SKILL.md`와 참조를 보존해 선택한다. 프로젝트 helper의 실행 금지 보완도 유지한다. 이번에는 진단을 수행하지 않는다. | 보조 도구가 실제 필요해질 때만 프로젝트 보완을 유지할지, 원본/개인 helper를 별도 검토해 사용할지 결정. 본문 같다는 이유로 스크립트를 교체하지 않는다. 동작 동등성·실행 안전성은 미검증. |
| `review-release-evidence` | `project/review-release-evidence/SKILL.md` 하나로 구성되며 원본과 같다. 완전한 중복이다. | `user/review-release-evidence/SKILL.md`도 원본과 같다. | 후속 완료·인계 판단 조건이 맞으면 기존 `project/review-release-evidence/SKILL.md`를 선택한다. 재설치할 이유가 없다. 이번 결과는 문서의 정적 근거로만 판정한다. | 런타임 검색 우선순위와 향후 중복 정리만 미결. 현재 파일 변경은 불필요. |
| `specify-failure-recovery` | `project/specify-failure-recovery/SKILL.md`에 `LOCAL-RECOVERY-KEEP` 한 문단이 추가돼 있다. 프로젝트 사용자 입력의 자동 초기화를 금지하는 보완이며 원본의 보존 원칙과 양립한다. | `user/specify-failure-recovery/SKILL.md`는 원본과 같고 이 프로젝트 보완은 없다. | 보완을 가진 `project/specify-failure-recovery/SKILL.md`를 선택한다. 원본/개인본으로 덮어쓰면 보존 규칙이 사라지므로 병합·대체하지 않는다. 현재는 기능 오류 계약을 새로 정의하지 않아 실행 워크플로는 적용하지 않는다. | 추후 원본 갱신 시 이 문단을 유지한 차이 병합 여부를 검토. 현재 자동 초기화 금지는 미정으로 되돌리지 않는다. |
| `verify-powershell-handoff` | `project/verify-powershell-handoff/SKILL.md` 하나로 구성되며 원본과 같다. 완전한 중복이다. | `user/verify-powershell-handoff/SKILL.md`도 원본과 같다. | 실제 PowerShell 파일 검증 인계 조건이 맞을 때 기존 `project/verify-powershell-handoff/SKILL.md`를 선택한다. 이번에는 인계 스크립트를 작성·실행하지 않아 해당 런타임 검증을 추가하지 않는다. | 수신 셸에서 실제 엔트리·입력·실패 사례의 검증은 후속 인계 범위. 현재 정적 비교로 READY를 주장하지 않는다. |

위 선택은 문서상의 사용할 내용과 경로 결정이다. 실제 Codex 호스트의 동일 이름 스킬 검색·캐시·우선순위는 시험하지 않았다. 파일 수정 없이 경로를 명시해 검토할 수 있으나, 이것을 설치 적용이나 검색 우선순위 검증으로 바꾸어 보고하지 않는다.

## 구체적 차이와 근거

1. `coordinate-device-validation`: 세 `SKILL.md`의 SHA-256은 `F57474852380DF92FCF86519C1F3CE126884524921CDD50CB265E7E360503EFF`로 같다. 원본/개인 `references/timing-budget.md`는 `F21FD83323C129A8089F9E6A9B2ACE72280150EE51CC069EB68961D443D0E92E`로 같으나 프로젝트에는 경로가 없다. 시간 제한 시 본문이 이 참조를 읽도록 요구하므로 파일 누락은 실질적인 적용 공백이다.
2. `diagnose-computer-use-recovery`: 본문·`references/input-contract.md`·`references/recovery.md`는 세 위치에서 각각 같다. helper의 유일한 텍스트 차이는 프로젝트 파일의 두 번째 줄 `# LOCAL-HELPER-KEEP: fixture customization; do not execute this copy.`다. 원본/개인 helper 해시는 `1647F6D226146AF44490236F1B631C5F9F456A1D49C05F4256F25571CCA9296C`, 프로젝트 helper는 `A12B7FA8709276C92EA108D73667327FA2692623A091DF4ABFC773AE1612A4D7`이다. 실행문 차이는 발견되지 않았으나 보완의 실행 금지를 존중한다. 비교는 소스와 diff 읽기이며 helper를 실행하지 않았다.
3. `specify-failure-recovery`: 프로젝트에는 제목 다음에 `LOCAL-RECOVERY-KEEP: 이 프로젝트의 사용자 입력은 자동 초기화하지 않는다. 이 개인 보완을 보존한다.`가 추가돼 있다. 원본/개인은 `FF955BED7A680DC82F98EA9E3F719035E8E2C790709915FCEBBD8C27461C9E59`, 프로젝트는 `B7FE217B953C45892DE1C5DE714A8E0471E977813489B36974BE58F091463FB9`이다. 프로젝트 본문 전체와 원본 대비 diff를 읽어 다른 텍스트 차이가 없음을 확인했다.
4. `review-release-evidence`: 세 위치의 전체 파일인 `SKILL.md` 해시는 `70816AC5B757D9D247B47EDEFE3038F67B7345D3FBB85F97FD791FA281A8F8CC`로 같다.
5. `verify-powershell-handoff`: 세 위치의 전체 파일인 `SKILL.md` 해시는 `DD8CD596F50EBDE53C8C386FA9AB1C8AD943C02E9A16A09E9870739CBF12D3DD`로 같다.

## 기존 지침과 템플릿의 충돌 처리

| 지침·문서 | 처리 결과 |
| --- | --- |
| 기존 루트 `AGENTS.md` | 원래 제목·다섯 항목과 `TEAM-POLICY-KEEP`를 유지하고 필요한 안내만 뒤에 추가했다. 승인 범위, 개인 수정 보존, 관련 없는 스킬·전체 시험 금지를 유지한다. |
| `design/overview.md` / `design/contract.md` | `TEAM-OVERVIEW-KEEP`, `TEAM-CONTRACT-KEEP`와 내용·경로를 보존한다. 템플릿 `docs` 링크를 그대로 복사하면 기존 문서와 이중 권위가 되므로 기존 두 경로로 치환했다. 기획·명세 템플릿이나 빈 카드 복제는 하지 않았다. |
| `services/readonly/AGENTS.override.md` | `READONLY-SCOPE-KEEP`의 읽기 전용을 그대로 유지한다. 상위 템플릿의 “없으면 필요한 부분 작성”은 이 하위 폴더의 쓰기 허가가 아니다. 루트에도 이를 명시했으며 하위 파일을 작성·변경하지 않았다. |
| 템플릿의 두 스킬 조건 | 조건·생략 예외·동시 적용 조건·미설치 시 직접 검토 및 자동 설치 금지를 가져왔다. 단계 이름만으로 일괄 실행하지 않는다. 다섯 스킬을 비교한 사실은 다섯 운영 워크플로를 실행하라는 뜻이 아니다. |
| 템플릿의 구현·검토 안내 | 요구/구현 누락 구분, 미정의 담당·시점, 오류 해제 관측, 필요한 확인만 수행, 조사 상한, 근거 수준 분리, 결과 전달을 가져왔다. 개발 명령·재시작 확인은 후속으로 그 작업이 승인된 경우의 지침이며 현재 금지 범위를 열지 않는다. |

## 읽은 자료·변경 파일·남은 미확인

읽은 자료: 기존 루트 `AGENTS.md`, `design/overview.md`, `design/contract.md`, `services/readonly/AGENTS.override.md`; 템플릿 `AGENTS.md`, `docs/project-brief.md`, `docs/requirements.md`; 세 위치의 다섯 `SKILL.md`; 존재하는 참조·helper 전부의 파일 목록/해시. 참조 내용은 원본의 `coordinate-device-validation/references/timing-budget.md`, `diagnose-computer-use-recovery/references/input-contract.md`와 `references/recovery.md`를 읽고 나머지 위치와 해시 동일성을 확인했다. helper는 원본 소스 전체와 프로젝트 차이를 읽었다. 작업 방식 확인용 공통 `superpowers:using-superpowers` 지침도 읽었으며 전용 하위 작업에는 적용하지 않는다는 절을 따랐다.

실제 변경은 루트 `AGENTS.md`와 이 `design/compatibility-result.md`뿐이다. 기존 기획·명세·하위 지침·프로젝트 스킬·개인 스킬 복사본·배포 원본은 유지했다. 누락 참조를 추가하거나 새 스킬을 설치하지 않았다.

남은 미확인은 실제 호스트 검색 우선순위, 실제 개인 설치본과 시험 복사본의 동일성, 배포 ref/commit의 최신성, 스킬 및 helper의 런타임 동작이다. 이번에 확인된 파일 차이 판정에는 이 실행 확인이 필요하지 않으므로 작업 범위를 확대하지 않는다. 후속 파일 보충·중복 정리·helper 채택을 결정할 담당은 프로젝트 소유자이며, 해당 작업을 요청하는 시점에 결정한다. 그 전에는 현재 파일을 보존하고 위의 명시 경로 선택/수동 판독만 제안 범위로 남긴다.

## 후속 조건 병합 — 2026-10-15

갱신된 `template/AGENTS.md`를 다시 읽고 루트 `AGENTS.md`의 `review-release-evidence` 선택 행만 갱신했다. 소스·산출물·시험·승인이 같은 후보인지와 프로젝트 완료/릴리즈/인계 범위를 판단하는 경우에 선택한다. 단일 시험 시간 예산·한 PowerShell 스크립트의 호환성·개별 도구 오류 분류 등 전문 스킬만으로 답할 검토와 작업 완료 요약에는 자동 추가하지 않는다. 위 표의 “후속 완료·인계 판단 조건”도 이 갱신된 조건을 뜻한다.

이번 후속 변경도 `AGENTS.md`와 이 결과 문서 두 개로 한정했다. 기존 팀 규칙·`design` 경로·기획/명세·개인 보완·프로젝트 및 개인 스킬 복사본·하위 읽기 전용 지침은 보존했다. 변경 전후 파일 해시로 두 문서 외 20개 파일의 보존과 추가 파일이 없음을 확인했다. 다섯 스킬의 전체 비교 시험이나 운영 워크플로는 반복하지 않았다. 기존 미확인 사항은 그대로 남는다.

## 선택 경로를 실제 읽어 적용한 짧은 문서 검토 — 2026-10-15

아래는 추가로 제시된 다섯 가상 상황에 선택한 스킬 내용을 적용한 문서 판단이다. 앞의 파일 동일성 비교와 구분하며, 명시 경로의 본문과 필요한 참조를 실제 읽었다. 운영 실행·설치·환경 변경·실제 호스트의 동명 스킬 검색 검증은 수행하지 않았다. 앞 표의 “이번에는 적용/진단하지 않는다”는 초기 비교 단계의 범위이며 아래에는 후속 문서 적용만 추가한다.

### 1. 메모 저장 응답 유실·인증 만료

저장 응답 유실은 확정 실패가 아닌 결과 불확정으로 표시하고, `LOCAL-RECOVERY-KEEP`에 따라 메모 입력과 요청 식별자를 보존하며 자동 초기화하지 않는다. 해제 계약 제안은 유효한 재인증 뒤 동일 요청의 저장 결과를 확인하고, 그 결과/인증 갱신 사건으로 상태와 허용된 UI 동작을 함께 갱신하는 것이며 재인증만으로 저장 성공을 선언하지 않는다. 자동 재시도 여부·횟수와 만료 후 편집 허용 정책은 미정이고, 결정 담당은 제품 책임자 역할 지정부터 미정이며 해당 저장 기능 구현/승인 전에 정해야 한다. 그 전에는 보존·불확정 표시·결과 확인/해제 제안의 문서화까지 진행하고, 재전송·편집 허용·늦은 응답 반영은 임의 확정하지 않으며 요청·권한·자원 수명이 유효한지 확인하도록 남긴다.

사용 경로: `project/specify-failure-recovery/SKILL.md` (`.agents/skills/specify-failure-recovery/SKILL.md`).

### 2. 후보 A 실사용 PASS·B 모의 PASS와 제한 시범 인계

A의 실제 대상 PASS와 B의 모의 PASS는 각각 그 후보·실행 수준의 근거이며, 합쳐서 B 실사용 PASS로 만들 수 없다. 사용자가 B의 실사용 미검증 위험을 수용하고 제한 시범 운영 인계를 승인했으므로 현재 주장은 “승인된 제한 시범 운영 범위의 인계 완료”이며 B 실사용은 계속 미검증이다. 제공된 사실로 완료된 것은 승인과 문서 판단이며, 산출물 전달·배포의 실행 증거는 제공되지 않아 실제 수행 여부는 미확인이다. 승인자·승인 시점·제한 범위는 실제 인계 기록에 연결하되 제공되지 않은 날짜나 조건을 만들지 않으며, 이 가상 검토가 새 배포·기기 조작 권한을 만들지도 않는다. 새 결함·범위 변경·판정을 바꿀 관측 없이 수용 결정을 과거 gate로 다시 열거나 동일 검토를 반복하지 않는다.

사용 경로: `project/review-release-evidence/SKILL.md` (`.agents/skills/review-release-evidence/SKILL.md`).

### 3. 주입부터 관측 끝까지 5초인 기기 계획

동일 측정창은 주입 시작부터 관측 끝까지 5초인데 행동 4초 뒤 수집 4초가 순차이며 중첩 불가이므로 필요한 8초가 3초 초과해 현재 계획은 성립하지 않는다. 준비는 이미 창 밖이므로 준비를 다시 옮겨 시간을 줄일 수 없고, 병렬 수행이나 지원되지 않는 자동 트리거를 가정해서도 해결할 수 없다. 주입 시작점을 뒤로 옮기는 대안은 같은 시험 주장을 유지하는지와 노출 조건 변화·사건 관측 가능성을 먼저 확인해야 하며, 창 연장은 허용될 때 최소 8초에 별도 지연 여유를 결정하는 조건부 대안이다. 대안이 확인되기 전에는 실행하지 않고, 창을 놓친 표본은 목표 분기의 성공 근거로 쓰지 않는다.

사용 경로: `user/coordinate-device-validation/SKILL.md` 및 같은 완전한 패키지의 `user/coordinate-device-validation/references/timing-budget.md` (`user-skills/coordinate-device-validation/` 기준). 프로젝트의 누락 참조를 다른 루트에서 짜깁기하지 않았다.

### 4. 수신 PowerShell 5.1의 루트 JSON 3건 인계

`@(Get-Content file.json | ConvertFrom-Json)`만으로는 PowerShell 5.1에서 루트 배열이 의도한 세 레코드로 열거됨을 보장하지 않으며, 한 파이프라인 객체로 묶여 Count가 1이 될 수 있다. Count와 각 레코드의 타입·필수 필드 검증이 없고 작성자 PowerShell 7 성공만 있으므로 수신 환경의 READY는 미검증이다. 수정 제안은 UTF-8/Raw 읽기와 파싱·컬렉션 구성을 분리하고 기대 Count=3과 필드를 검증하는 것이며, null/빈 배열을 허용하는 계약이라면 별도 명시 처리해야 한다. 후속 확인은 수신 5.1의 실제 엔트리에서 3건·1건·0건·잘못된 JSON·null을 계약에 맞게 판별하고 실패 시 성공을 막는지 보는 것으로 남기며, 이번에는 스크립트 실행이나 환경 업그레이드를 하지 않는다.

사용 경로: `project/verify-powershell-handoff/SKILL.md` (`.agents/skills/verify-powershell-handoff/SKILL.md`).

### 5. 동일 시도 native read/execute validation os32

현재 동일 시도의 runtime read/execute validation os32는 native runtime의 접근/ACL 검증 경계에서 난 sharing violation을 뒷받침하지만, 잠금 소유 프로세스나 Windows/Codex 결함 원인은 아직 확정하지 못한다. generic wrapper와 다른 과거 시도의 continuing ACL warning은 이 현재 원인을 대신할 근거가 아니며, browser 성공도 native import·캡처·입력 복구를 증명하지 않는다. 다음 행동 제안은 동일 시도의 시각·runtime 경로/버전·실패 단계와 의도/실효 모드를 맞추고 허용된 읽기 전용 근거로 정확한 잠금 소유자를 확인하되, 확인 불가면 소유자는 미확인으로 남기는 것이다. 이번 문서 판단에서는 프로젝트 helper를 실행하지 않고 프로세스 종료·재시작·ACL/샌드박스 설정 변경을 하지 않으며, 제공된 근거상 native 검증 실패와 browser 성공을 별도 상태로 인계한다.

사용 경로: `project/diagnose-computer-use-recovery/SKILL.md`, 같은 패키지의 `references/recovery.md`와 `references/input-contract.md` (`.agents/skills/diagnose-computer-use-recovery/` 기준). `LOCAL-HELPER-KEEP`가 있는 `scripts/triage.py`는 실행하지 않았다.
