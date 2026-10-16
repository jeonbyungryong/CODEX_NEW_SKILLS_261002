# 원본 업데이트 추적과 반영

## 자동화 범위

[GitHub Actions](../.github/workflows/skill-bundle.yml)는 매시간 17분(UTC, 한국시간도 분은 17분)에 확인한다. `workflow_dispatch`는 Actions의 **Run workflow**로 즉시 검사 요청을 할 수 있고, 인증된 외부 연동용 `repository_dispatch`의 `upstream_skill_update`도 지원한다.

이 구성은 **실시간 푸시 수신을 보장하는 미러가 아니다.** 원본 3개 저장소의 웹훅/Actions를 수정할 권한은 없으며, 사용자 저장소만으로 그 저장소의 모든 push 이벤트를 자동 구독할 수 없다. 외부 dispatch를 실제 연결하려면 별도 신뢰된 연동이 필요하다. GitHub 일정은 지연·누락될 수 있고 공개 저장소는 60일 비활동 시 일정이 비활성화될 수 있다. [GitHub 공식 일정·dispatch 설명](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule)

## 가져오는 버전

- text-to-cad: 원본이 권장하는 배포용 `latest` 브랜치. 개발 main의 미출시 변경을 바로 섞지 않는다.
- ponytail: 원본 `main`의 승인된 6개 스킬 패키지.
- REA: 원본 `main`의 사용자용 스킬 1개. npm 최신 릴리즈와 동일 버전이라는 보장은 없다.

브랜치는 검사 시 정확한 40자리 커밋으로 해석한다. 파일별 Git blob identity와 SHA-256, 원본 경로, 저작권·라이선스 해시를 [upstream-lock.json](../third_party/upstream-lock.json)에 기록한다. 안정 브랜치를 그대로 추적하므로 기능이 언제나 유용하거나 호환된다고 자동 판정하지 않는다.

## 검증 후 리뷰 경로

1. `python -B scripts/skill_bundle.py sync`가 변경된 커밋을 감지한다. 같으면 파일을 쓰지 않고 종료한다.
2. 선택된 스킬의 폴더 전체와 필요한 추가 출처를 가져온다. 원본 코드를 실행하거나 pip/npm 설치를 하지 않는다.
3. 임시 후보의 목록·이름·참조·해시를 검증한 뒤 갱신한다. 기존 vendored 파일에 로컬 편집이 있거나 라이선스가 바뀌면 중단한다. 삭제된/이름이 바뀐 스킬도 사람 검토가 필요하다.
4. 패키지 검사·복사/충돌 시험·기존 회귀시험을 통과하면 `automation/upstream-skills` 브랜치에 push한다. force-push하지 않으며 main과 충돌하면 중단한다.
5. 허용된 경우 같은 브랜치의 PR을 생성/갱신한다. **자동 병합은 하지 않는다.** 검토자가 지시문·스크립트·외부 통신·런타임 호환성까지 확인하고 병합한다. main에서 설치하는 다른 PC는 그 이후 새 버전을 받는다.

2026-10-16 확인 시 이 저장소는 Actions 실행이 켜져 있고 기본 workflow 권한은 read이며 Actions의 PR 생성/승인 옵션은 꺼져 있었다. 이를 임의 변경하지 않는다. 이 경우 검증된 브랜치와 Actions summary의 비교 링크는 제공하지만 PR 생성은 경고로 남을 수 있다. 저장소 소유자가 허용하려면 **Settings → Actions → General → Allow GitHub Actions to create and approve pull requests**를 별도로 검토한다. [공식 설정 설명](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository#preventing-github-actions-from-creating-or-approving-pull-requests)

스킬 추가/제거·이름 변경은 자동으로 24개 목록을 확대하지 않는다. `bundle.json`과 문서·검사를 함께 승인 변경한다. 새 원본 스킬은 lock의 `unselected_skills`에 드러나므로 조용히 사라진 것으로 처리하지 않는다.

## 이미 설치된 PC는 별도

GitHub 갱신은 각 PC의 설치본·설정·캐시·MCP를 변경하지 않는다. 새 버전 설치는 별도 요청으로 현재 내용과 차이를 확인한다. 변경된 동명 패키지는 기본 설치기가 덮어쓰지 않는다. 기존본 백업·원복 방법과 해당 PC의 스킬/런타임 버전을 검토한 뒤 갱신한다. 자동 설치·자동 자체 수정·원격 PC 접근 기능은 없다.

구조·해시 검증은 지시문의 안전성이나 실제 CAD/REA 성능을 증명하지 않는다. 원본의 사용자용 스킬 전체를 보존하되 실행 권한은 현재 사용자 요청에서 별도로 판단한다.
