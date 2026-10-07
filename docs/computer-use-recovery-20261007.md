# Windows Computer Use 진단·복구 Skill — 2026-10-07

## 목적과 채택 범위

사용자의 명시 요청으로 `diagnose-computer-use-recovery`를 추가했습니다. 반복되는 Windows native Computer Use 오류를 현재 시도의 증거로 분류하고, 승인된 복구와 원복을 다른 PC에서도 이어갈 수 있게 하는 **실험적 진단 지침과 로컬 분류 도구**입니다. Codex 실행 파일을 수정하거나 자동으로 복구하는 프로그램은 아닙니다.

기존 브라우저 시험에 관한 [생성 보류 평가](computer-use-assessment.md)와 [DWG 적용 점검](dwg-application-review-20261007.md)은 당시의 결론으로 유지합니다. 이번 추가는 native 런타임의 새 재현 증거와 사용자의 제작 요청에 따른 것입니다. 기존 지침 대비 생산성 향상이나 모든 PC에서의 복구 효과가 입증됐다는 뜻은 아닙니다.

## 원인 분석과 실제 관측

2026-10-07 08:25:56 UTC native Node 도구에서 sky import를 시도했지만 커널이 시작 단계에서 종료됐습니다. 같은 시도의 08:25:59 UTC setup 로그에서 다음 경계가 확인됐습니다.

```text
runtime read/execute validation failed
node_repl.exe: open ACL target for root-only update
os error 32 — sharing violation
setup refresh had errors
```

이는 런타임 파일의 권한 갱신에 필요한 접근이 파일 사용 충돌로 실패했다는 증거입니다. 잠금 보유 프로세스의 정확한 핸들, Codex 내부 결함과 발생 조건은 확인되지 않았습니다. 같은 문구가 나타나는 다른 PC의 원인도 별도로 조사해야 합니다. 전체 로그·사용자 경로·설정·업무 도면 정보는 게시하지 않습니다.

| 실제 시험 | 확인된 결과 | 제한 |
|---|---|---|
| elevated native 재연결 | 커널 FAIL, import 이후 NOT_RUN | BLOCKED |
| 이전 승인된 cold restart | CLI sandbox probe PASS, 이후 native 오류 재발 | 지속 복구 실패; 반복 재시작 중단 |
| 이전 승인된 unelevated 임시 시험 | 창/접근성/키보드 PASS, capture FAIL, geometry 사용 불가 | PARTIAL 임시 우회 |
| 이전 원복 검증 | elevated 설정과 재실행 확인 | 이번 native 재현은 계속 실패 |
| 다른 PC | 새 증거 미수집 | 복구 효과 미검증 |

[OpenAI 공식 Windows sandbox 안내](https://learn.chatgpt.com/docs/windows/windows-sandbox)를 2026-10-07 확인했습니다. elevated/unelevated, setup·접근·로그온 정책의 경계를 구분합니다. 임시 unelevated 전환은 계정·네트워크 격리가 약해지므로 해당 범위의 승인이 필요합니다. 이전 PC의 승인이 다른 PC로 자동 확장되지는 않습니다.

## 구현과 해결 경로

- [SKILL.md](../skills/diagnose-computer-use-recovery/SKILL.md): native/브라우저 계층 구분, 현재 증거, 복구·원복·종료 기준.
- [복구 참조](../skills/diagnose-computer-use-recovery/references/recovery.md): 파일 충돌/권한/로그온/캡처/geometry/helper 분기와 cross-PC 인계.
- [입력 계약](../skills/diagnose-computer-use-recovery/references/input-contract.md): 같은 시도의 로컬 JSON, 요청 기능과 설정 복귀 상태.
- [triage.py](../skills/diagnose-computer-use-recovery/scripts/triage.py): Python 3.9+ 표준 라이브러리만 사용. 입력을 분류해 새 JSON을 만들며 UI·프로세스·설정·네트워크를 조작하지 않음.

파일 충돌은 정확한 잠금 소유자 확인과 지원되는 setup/update 경로로 조사합니다. 이미 수행한 1회 재시작 뒤 재발하면 같은 재시작을 반복하지 않습니다. 임시 설정은 대상 키/존재 여부만 원복하고 동시 변경된 모델 등 다른 설정은 보존합니다. 캡처 실패는 커널 설정 실패와 분리하여 설치된 공식 Computer Use 지침 안에서 제한적으로 조사합니다.

## 검증과 한계

[회귀 검증](../evals/computer-use-recovery/test_triage.py)은 18개 통과했습니다. 실제 Windows의 제공된 Python에서 Unicode·공백 경로, UTF-8 BOM 입력, 기존 출력 덮어쓰기 차단도 실행했습니다. 공식 skill-creator의 quick_validate 결과는 `Skill is valid!`입니다. 검증 의존성은 저장소 밖의 격리된 작성용 폴더에만 설치했습니다.

분류 도구를 작성하기 전 도구 부재 실패를 관측했고, 독립 검토의 오류를 새 테스트로 재현한 뒤 수정했습니다. 현재 setup wrapper만으로 원인을 단정하지 않으며, 이전 로그/비치명적인 profile 경고를 원인으로 취급하지 않습니다. 요청 기능만의 실패·부분 성공과 진단용 다른 기능의 성공을 구분하고, 사용한 재시작을 다시 권하는 모순을 제거했습니다.

스킬 미사용 기준선 agent도 핵심 안전 판단을 올바르게 수행했습니다. 적용 agent는 같은 합성 시나리오와 이전 로그/캡처 단독 실패를 검토하고 도구 결함을 발견했습니다. **행동 비교의 실패 기준선이나 추가 효과는 입증되지 않았습니다.** 5회 이상 반복한 효율/자동 선택 연구, 다른 PC의 실복구, 영구적인 플랫폼 수리는 미검증입니다. 사용자의 제작 요청에 따라 참고·진단용 실험 후보로 게시합니다.

## 다른 PC에서 사용·수정·회귀

1. 별도 작업 폴더에서 이 저장소를 clone하고 현재 `git rev-parse HEAD`를 기록합니다.
2. 전체 Skill 폴더를 유지한 채 SKILL.md의 실제 경로를 Codex에 전달합니다. 전역 설치는 별도로 요청합니다.
3. 해당 PC의 앱/Windows/runtime 버전, native 도구, 현재 sandbox 모드, 동일 시도 로그와 기능별 결과를 로컬에 기록합니다. raw 자료는 Git에 넣지 않습니다.
4. 먼저 읽기 전용 분류를 실행하고, 필요한 복구에 이미 유효한 승인이 있는지 확인합니다. 미승인 보안 변경·타 앱 종료·무한 재시작을 하지 않습니다.
5. 수정 시 `codex/<작업명>` 브랜치를 만들고 18개 회귀 검증과 실제 해당 PC 기능 검증을 수행합니다. 원인 미상/NOT_RUN도 그대로 기록합니다.
6. 검증 결과를 개인정보 제거 후 문서에 반영합니다. 설치본 업데이트 전 원본을 보존하고 차이를 검토합니다.
7. 문제가 생기면 기록한 이전 커밋을 별도 폴더/분리된 worktree에서 확인하거나 이후 커밋을 revert합니다. 원격 main을 강제로 되돌리지 않습니다.

이번 추가 전 기준 커밋은 `c1b7b5c`입니다. 이전 두 Skill과 평가 자료를 보존합니다. Skill 버전 회귀는 Windows sandbox 설정 원복과 별개입니다.
