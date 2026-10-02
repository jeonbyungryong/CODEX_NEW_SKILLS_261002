# 두 Skill 설치 후 검증

2026-10-02 KST · v0.2 후속 기록. 단일 Windows PC의 설치와 제한된 적용 확인이며, 장치 수락시험이나 일반적인 효율 향상의 인증이 아니다.

## 결론

사용자 승인으로 `coordinate-device-validation`과 `verify-powershell-handoff`를 설치했다. 설치 파일 일치, 명시 경로를 통한 지침 적용, 두 PowerShell 엔진의 실제 파일 검사와 후속 사용 가능 목록 등록을 확인했다. 적절한 자동 선택·장기 효과·Computer Use 복구는 미검증이다. Skill 본문은 수정하지 않았다.

## 확인된 사실

| 항목 | 관측 결과 | 판정 범위 |
| --- | --- | --- |
| 설치 출처 | [고정 커밋 82f8550](https://github.com/jeonbyungryong/CODEX_NEW_SKILLS_261002/tree/82f8550851e8bd4cfdc8355e80bfeda1fe42670a)의 두 Skill 경로 | 해당 버전만 확인 |
| 설치 방법 | bundled `skill-installer`의 `install-skill-from-github.py`, 고정 ref·download 방식, exit 0 | 공식 helper 실행 성공 |
| 기존본 보호 | 같은 이름 폴더 0개, 덮어쓰기 없음. 기존 개인 Skill 지침 11개·루트 디렉터리 12개 보존 확인 | 기존 supporting 파일 전체의 재귀 감사는 아님 |
| 파일 일치 | 원격 Git blob·검토한 로컬본·최종 설치본의 3개 파일 일치 | 아래 SHA256으로 버전 식별 |
| metadata | 이름·설명·delimiter·코드 펜스 등의 단순 검사 통과 | 공식 YAML 검증기 PASS는 아님 |
| 명시 경로 적용 | GPT-6.1 Sol / High, 새 문맥 2개에서 설치 지침 읽기와 적용 확인 | Skill당 1개 사례, 자동 선택 검증은 아님 |
| 목록 등록 | 후속 사용자 turn의 제공된 사용 가능 Skill 목록에 두 이름 확인 | 등록 사실만 확인, 올바른 자동 선택은 미검증 |

설치 중 제품·태블릿·브라우저 권한·네트워크 설정을 변경하지 않았다. 두 대상이 없었으므로 대체할 기존본과 별도 백업 대상도 없었다. 다른 PC의 설치 성공을 보장하지 않는다.

### 설치된 파일 SHA256

저장소 상대 경로 기준이다. hash는 본문 버전을 확인하기 위한 값이지 지침 효과의 증거가 아니다.

| 파일 | SHA256 |
| --- | --- |
| `skills/coordinate-device-validation/SKILL.md` | `7AD1A4033351DEEAD4EB9D88AA83EBCA82A3646047E18916624AC10A0F91173B` |
| `skills/coordinate-device-validation/references/timing-budget.md` | `829FD3ACF773A3A93F162D28AF56FD14346C418928C43CB9CE5A0FDAD59CD8F2` |
| `skills/verify-powershell-handoff/SKILL.md` | `4619EEDF5AA58DF0F80BAA234B650660F076EEC52C9AAA2A6B1E235177A12B93` |

## 적용 확인과 비평

두 사례의 판정 기준을 실행 전에 고정했다. 진행자가 완전한 응답과 실제 도구 입력을 대조했으며 별도 채점자나 새로운 A/B 비교는 아니다. 아래 숫자는 합성 입력의 조건으로, 제품 요구사항이나 보편적인 시간 기준이 아니다.

장치 사례는 계획 검토만 수행했다. 표시 readiness timeout이 목표였으며, 24초 창과 순차 2+7+12=21초를 계산했다. 잔여 3초를 승인된 오차 예산으로 간주하지 않았다. 실제 동기화·단계 관측·timeout 분기가 불명인 상태를 조건부로 유지했다. 오류 코드만으로 잘못된 미디어와 timeout을 구분해 PASS를 내리지 않았다. 실제 장치 조작·주입·전원 리셋은 수행하지 않았다.

PowerShell 사례는 실제 설치 manifest의 정확히 3개 레코드와 검증식의 정적 검토였다. 허용 경로·중복·필드·hash 검사와 마지막 성공 출력 조건을 확인했지만, 자식 프로세스에 변수를 전달하는 호출 방식이 없으므로 전체 실행을 인증하지 않았다. 일반적인 모든 JSON schema의 검사로 확대하지 않았다. 진행자는 이후 각 자식의 `-Command` 안에 manifest 경로를 명시하고 인수 배열과 즉시 exit code 수집으로 아래 실행을 확인했다.

PowerShell 검토 응답은 장치 조율 지침과 시간 참조까지 추가로 읽었다. 불필요한 읽기 부담 가능성을 단일 관측으로 남긴다. 범위 밖 조작은 없었지만 모든 Skill 상호작용이 안전하거나 효율적이라는 증거도 아니다.

## 실제 읽기 전용 실행

정상 manifest는 설치된 3개 파일의 실제 bytes를 hash로 검사했다. 고의 오류 사례는 manifest의 SHA256 하나를 틀리게 만든 입력이다. 설치 파일 자체는 변경하지 않았다.

| 엔진 | 정상 manifest | 고의 잘못된 SHA256 |
| --- | --- | --- |
| Windows PowerShell 5.1.26100.9444 | 3개 파일 확인, exit 0 | `Installed file hash mismatch`, exit 1 |
| PowerShell 7.6.5 | 3개 파일 확인, exit 0 | `Installed file hash mismatch`, exit 1 |

총 4개 자식 실행이다. 오류 입력의 exit 1은 기대한 차단 성공이며 설치 실패가 아니다. 이전 [엔진별 17개 기초 시험](powershell-handoff.md)과 합산하지 않는다. 이번 검사는 native helper의 인수 경계·Unicode stress·전체 운영 인계의 재검증이 아니다.

보조 metadata 검사 명령의 pipeline 문법 오류는 파서로 재현한 뒤 배열 부분식으로 감싸 재검사했다. 설치된 지침 결함으로 분류하지 않았다. 실행 trace 추출도 실제 `custom_tool_call`·`task_complete` 기록 구조로 정정했다. 최초 추출 누락을 도구 호출 0회로 보고하지 않는다.

## 미검증과 다음 사용

- PyYAML 부재로 이번 공식 `quick_validate.py`는 NOT_RUN이다. 단순 metadata 검사로 대체 인증하지 않으며 의존성을 추가 설치하지 않았다.
- 적절한 자동 선택·비선택, 다중 Skill 상호작용 전체, 장기 세션·컨텍스트 압축 이후 행동은 미검증이다.
- 실제 장치 수락·브라우저 복구·모든 운영 인계·다른 PC의 설치 호환성은 미검증이다.
- 사용자 시간·비용·토큰 절감은 측정하지 않았다. 기존 [A/B 평가](validation.md)와 이번 설치 확인은 서로 다른 시험이다.

관련 업무에서만 `$coordinate-device-validation` 또는 `$verify-powershell-handoff`를 명시해 사용할 수 있다. 일반 Git 게시나 문장 수정에 억지로 적용하지 않는다. 새로운 실무 관측에서 유용성과 추가 읽기 비용을 확인하며, 새 업무 없이 같은 smoke를 자동 반복하지 않는다. 이번 확인 모델은 GPT-6.1 Sol / High였고 모델 override는 없었다.

## 근거와 공개 범위

근거는 로컬 설치 receipt, 사전 smoke 기준, 응답·실제 도구 입력 기록, 엔진별 runtime 검사 결과와 후속 turn의 제공 목록이다. 개인 PC 절대 경로·실행 식별자·도구 전체 목록은 공개하지 않았다. 원본은 로컬에 보존하며 이 문서는 비식별 요약이다. 따라서 외부 독자가 원본 실행 trace를 독립 재현·감사할 수 있는 완전한 증거 패키지는 아니다.

지침 파일의 고정 버전은 위 커밋과 SHA256으로 확인할 수 있다. 기존 공개 [검증 자료](../evals/README.md)와 [PowerShell 자료](../evals/powershell-handoff/README.md)는 각각의 이전 시험 근거이며 이번 실행 로그를 대신하지 않는다.
