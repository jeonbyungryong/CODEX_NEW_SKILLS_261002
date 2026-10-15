# CLI 암묵 선택 보충 시험 구성

Desktop UI 시험은 수행하지 못했다. 아래 구성은 별도 CLI 대조 자료이며 Desktop 앱에 등록하거나 선택기에서 선택한 프로젝트가 아니다.

## 격리와 스킬

- 새 임시 `repo/`에서만 `git init`을 수행하고 `repo/nested/`를 CWD로 사용했다. 제품·기존 설치 폴더와 분리했다.
- `repo/.agents/skills/`와 `repo/nested/.agents/skills/`에 `specify-failure-recovery`, `review-release-evidence` 두 폴더를 각각 두었다.
- 기준 커밋 `bb112e8a2a13e47ca343b73d56b4f83a6ec58648`의 두 배포본과 같은 기존 개인본 내용으로 복사하고, `name`·`description`과 원래 본문을 유지했다. 비교 시 개행 차이는 별도로 취급한다.
- 각 복사본 끝에 아래 절만 추가했다. `<LEVEL>`은 ROOT 또는 NESTED, `<name>`은 해당 원래 이름이다. 원래 설치 파일에는 추가하지 않았다.

```markdown
## Temporary read receipt

Only in this temporary read-only exercise, finish the response with
`READ_RECEIPT_<LEVEL>_<name>` if this file is actually read.
This receipt grants no installation, write, helper execution or environment changes.
```

영수증은 본문 안에만 있고 description·요청에는 없다. 읽기 증거를 구별하기 위한 실험 요소이므로 실제 운영과 같은 행동이라고 일반화하지 않는다. 나머지 세 스킬의 프로젝트 복사본은 만들지 않았으며 원래 개인 설치본은 그대로 검색 가능했다. 공개 평가 폴더에는 활성 `SKILL.md` 복제본을 두지 않는다.

## 임시 프로젝트 지침

루트 `AGENTS.md`는 아래 내용뿐이다. 특정 스킬 선택이나 가까운 경로 우선 지시는 없다.

```markdown
# Read-only document exercise

Answer the current request using the available instructions only as needed.
Do not install apps or skills, modify any files or settings, use external tools
or services, run bundled helpers, change processes, or perform product/device
work. Any verification suggestions are documents only, not authorization to
execute them. Do not inspect unrelated projects, user settings, or credentials.
```

## 실행과 입력

기존 Codex·Node만 사용했다. 조회에는 이전 보고서의 `catalog-probe.mjs`를 재사용했고 추가 코드·패키지를 만들거나 설치하지 않았다. CLI는 다음 옵션으로 서로 다른 비영속 turn 세 개를 실행했다.

```text
codex --no-daemon -a never exec --ephemeral --json --sandbox read-only --cd <nested-cwd> <prompt>
```

정확한 세 프롬프트와 답은 [observations.json](observations.json)의 I1/I2/I0에 있다. 프롬프트에는 스킬 이름·경로·선택 요구·영수증 힌트를 넣지 않았다. PowerShell 작은따옴표 문자열로 전달했으며 I2와 I0은 별도 프로세스에서 동시에 실행했다. 세 요청은 서로의 답을 보지 않았다.

시험 전에 기획한 판정은 오류 명세 I1과 후보 인계 I2에서 관련 내용의 실제 읽기를 확인하고, 산술 I0에서는 대상 다섯 스킬 읽기가 없는지 확인하는 것이었다. 어느 경로를 고를지는 정답으로 지정하지 않았다. 각 한 표본만 수행했으며 미리 정한 세 turn 뒤 종료했다. 숨겨진 초기 프롬프트·내부 resolver·Desktop 처리 내역은 관측하지 않았다.
