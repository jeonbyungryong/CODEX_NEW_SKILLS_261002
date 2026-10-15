# 임시 검색 시험 자료와 요청

아래는 이번 합성 자료의 재구성 명세다. 배포 스킬을 설치·교체하는 스크립트가 아니다. 기존 사용자 스킬은 보존하고 이미 사용 가능한 Codex·Node만 사용했다.

## 폴더와 탐침

서로 다른 새 임시 폴더 `empty/`, `repo/`에서 각각 `git init`으로 검색 경계만 만들었다. 제품 파일이나 커밋은 만들지 않았다. `repo/nested/`를 하위 CWD로 사용했다. `empty/`에는 프로젝트 스킬이 없다.

`repo/.agents/skills/<name>/SKILL.md`와 `repo/nested/.agents/skills/<name>/SKILL.md`에 아래 텍스트를 각각 작성했다. `<name>`은 저장소의 다섯 스킬 이름, `<SCOPE>`는 `ROOT` 또는 `NESTED`다. 파일명·frontmatter name은 각각 동일하게 맞췄다. 별도 alias 이름, openai.yaml, helper, 참조는 추가하지 않았다. 마커를 제외한 합성 본문은 같다. 개인본의 description·본문은 바꾸지 않았다.

```markdown
---
name: <name>
description: Use only for a read-only SKILL_DISCOVERY_20261015 catalog and selection probe; not for product work.
---

# Temporary collision probe

Marker: <SCOPE>_<name>

For the read-only SKILL_DISCOVERY_20261015 task only, report this marker
and the path of this loaded file. Do not install, write, execute helpers,
change settings, or perform any product or device work.
```

`repo/AGENTS.md`에는 다음 읽기 전용 범위만 넣었다. 가까운 본을 고르라거나 특정 표식을 답하라는 기대 정답은 주지 않았다.

```markdown
# Temporary skill discovery probe

This is a read-only skill discovery experiment, not a product project.
Do not install anything, change user/global settings, run bundled helpers,
write files, or perform product/device work. Read only the selected skill file
if needed and report its exact source and probe marker. Do not manually compare
all skill copies or infer a priority rule from this instruction.
```

## 검색 호출

`catalog-probe.mjs`의 인수는 **현재 설치된 Codex 실행 파일 경로**와 조회할 CWD 한 개 이상이다. 추가 패키지·로그인 변경·설치 작업을 하지 않는다. Node와 Codex가 없으면 이번 확인 범위 밖으로 남기며 새로 설치하지 않는다.

```text
node catalog-probe.mjs <existing-codex-binary> <empty-cwd>
node catalog-probe.mjs <existing-codex-binary> <repo-cwd> <nested-cwd>
```

새 stdio 프로세스에 `initialize` → `initialized` → `skills/list`를 보냈다. `skills/list` 요청은 `cwds`와 `forceReload: true`뿐이며 extra user root·영구 설정 쓰기·thread/turn 생성은 이 조회 스크립트에 없다. 첫 호출 후 root/nested 탐침을 만들고 두 번째 호출을 했다. 이는 새 프로세스 간 관측이며 동일 프로세스의 hot reload 검증은 아니다. 도구 결과는 개인 경로를 별칭으로 바꾼 뒤 게시했다.

## 선택 호출

세 번 모두 다음 옵션을 사용했다. 모델은 따로 지정하지 않았다. `$name`을 셸이 변수로 확장하지 않도록 실제 호출에서는 프롬프트를 PowerShell 작은따옴표 문자열로 전달했다.

```text
codex --no-daemon -a never exec --ephemeral --json --sandbox read-only --cd <nested-cwd> <prompt>
```

### S1 — 단일 이름

```text
SKILL_DISCOVERY_20261015 read-only selection probe. Use $review-release-evidence.
Do not install anything, write files, change settings, use the network,
run helpers, or do any product work. Do not compare all duplicate copies.
Report the marker and source of the skill that Codex selected or injected
for this request. If there is no marker, report that and the source you
actually read. Keep the answer under 100 words.
```

### S2 — 나머지 네 이름, 한 요청

```text
SKILL_DISCOVERY_20261015 read-only selection probe.
Use $specify-failure-recovery, $coordinate-device-validation,
$verify-powershell-handoff and $diagnose-computer-use-recovery.
Do not install anything, write files, change settings, use external services
or the network, run helpers, or do product work. For each of these four skill
names, report the marker and the source actually selected or read for this
request. Do not compare all duplicate copies. If a selected skill has no
marker, report that and its actual source. This is solely a catalog probe,
not an error-recovery or device-operation request.
Keep the final answer under 200 words.
```

### S3 — 개인본 경로 지정 대조

아래 `USER_SKILLS` 별칭은 실제 호출에서 기존 개인 설치본의 절대 경로로 바꿨다. `$review-release-evidence`를 함께 넣지 않았다.

```text
SKILL_DISCOVERY_20261015 read-only explicit-path control. For this request
use exactly the skill file USER_SKILLS/review-release-evidence/SKILL.md
rather than resolving a skill by name. Read only this chosen skill file.
Report the source actually read, its first Markdown heading, and its probe
marker if one exists. Do not compare other copies. Do not install, write files,
change settings, use external services or the network, run helpers, or perform
product work. Keep the final answer under 100 words.
```

선택 요청 자체는 정상적인 Codex 서비스 추론을 사용한다. 프롬프트의 네트워크 제한은 모델의 외부 도구 작업을 금지하는 것이며 Codex 서비스를 오프라인으로 실행했다는 뜻이 아니다. `--json` 파일 읽기 이벤트와 최종 답을 함께 확인했다. 임시 프로젝트·게시 clone은 결과 보존과 원격 일치 확인 뒤 정리하며 기존 설치 폴더는 정리 대상이 아니다.
