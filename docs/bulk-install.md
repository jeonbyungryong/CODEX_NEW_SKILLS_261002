# 27개 스킬 일괄 설치와 전체 기능 준비

2026-10-31. 이 문서는 설치 요청과 검증 범위를 구분한다. [기계 판독 목록](../bundle.json)이 설치 대상의 기준이다. 과거 `evals/`의 모의 스킬은 설치하지 않는다.

## 다른 PC에서 복사할 요청문

```text
https://github.com/jeonbyungryong/CODEX_NEW_SKILLS_261002 를 확인하고
루트 AGENTS.md와 docs/bulk-install.md에 따라 bundle.json의 27개 스킬을 일괄 설치해줘.
원본 커밋·라이선스·파일 해시와 지원 파일을 먼저 검증해줘.
현재 사용 중인 개인/프로젝트 스킬과 플러그인에 동명 항목이 있는지도 확인해줘.
같은 이름·같은 전체 내용은 건너뛰고, 다른 내용이나 중복 등록은 덮어쓰지 말고 차이를 보고해줘.
실제 CODEX_HOME과 설치 대상을 확인한 뒤 미설치 항목만 설치하고 결과를 알려줘.
스킬 파일 설치와 CAD/REA 실행 도구·MCP·계정 준비 상태를 별도로 보고해줘.
이 요청만으로 런타임 설치, MCP 설정 변경, 외부 주문이나 과금을 실행하지 마.
```

스킬은 설치 후 다음 turn/새 대화의 실제 사용 가능 목록에서 확인한다. 파일이 있다는 사실만으로 Desktop 선택기·암묵 선택이나 도구 연결을 통과했다고 보고하지 않는다.

## 설치 목록 — 27개

| 그룹 | 이름 | 수 |
| --- | --- | ---: |
| 기존 사용자 | `coordinate-device-validation`, `diagnose-computer-use-recovery`, `review-release-evidence`, `specify-failure-recovery`, `verify-powershell-handoff` | 5 |
| DWG 네이티브 변환 | `image-to-cad`, `solidworks-dwg-to-native` | 2 |
| text-to-cad | `bambu-labs`, `cad`, `dfam-check`, `dfm`, `dxf`, `engineering-drawing`, `gcode`, `sdf`, `sendcutsend`, `srdf`, `step-parts`, `urdf` | 12 |
| ponytail | `ponytail`, `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`, `ponytail-review` | 6 |
| REA | `reverse-engineer-anything` | 1 |
| Anatomy | `anatomy` — 전체 kit·scripts·references·8개 예제 | 1 |

설치 가능하다는 뜻이지 모든 작업에 27개를 호출하라는 뜻이 아니다. 일반 소스 검토에는 REA를 생략하고, CAD 모델 생성과 기존 도면 윤곽 복원(`image-to-cad`)도 구분한다. 다른 프로젝트의 기존 AGENTS.md를 이 저장소의 지침으로 덮어쓰지 않는다.

DWG에서 수정 가능한 SolidWorks 모델을 만드는 전용 설치·준비 절차는 [다른 PC CAD 안내](native-cad-setup.md)를 따른다. 원본 upstream `cad`와 사용자 확장을 별도로 유지하여 업데이트 시 확장이 덮어써지지 않게 한다.

## 설치·중복 처리의 실제 동작

Python 3.10 이상이 이미 있는 환경에서 clone한 저장소 루트에서 실행할 수 있다. Python 자체를 이 스크립트가 설치하지 않는다.

```text
python -B scripts/skill_bundle.py validate
python -B scripts/skill_bundle.py install --dest <확인한-CODEX_HOME의-skills-절대경로>
```

두 번째 명령은 계획만 출력하고 폴더를 만들지 않는다. `skill-installer`가 있으면 계획의 `missing` 목록만 그 공식 설치 helper에 `--repo jeonbyungryong/CODEX_NEW_SKILLS_261002 --ref <검증한-저장소-커밋> --path skills/<이름> ...`로 전달한다. helper가 없는 환경의 파일 복사 대안은 아래와 같다.

```text
python -B scripts/skill_bundle.py install --dest <확인한-설치-절대경로> --apply
```

- `identical`: 전체 상대경로·파일 내용이 같아 건너뛴다. 본문이 같아도 필요한 참조·라이선스가 다르면 같다고 숨기지 않는다.
- `conflict`: 동명 다른 내용/다른 폴더의 같은 frontmatter 이름. 종료 코드 2이며 **어느 패키지도 쓰지 않는다**. 기존 항목을 보존하고 별도로 갱신 승인을 받는다.
- `missing`: 승인된 apply에서만 전체 폴더를 복사한다. 기존 폴더는 빈 폴더여도 덮어쓰지 않는다.
- 설치 경로의 symlink/junction과 원본 저장소와 겹치는 경로는 거부한다. 실제 디스크 쓰기 오류는 이미 복사한 신규 폴더를 남길 수 있으므로 결과를 확인하고 임의 덮어쓰기 재시도를 하지 않는다.

이 도구가 검사하는 중복 범위는 **명시한 목적지의 직접 하위 스킬 폴더**다. 모든 플러그인 캐시·다른 프로젝트·원격 host의 등록 상태까지 자동 조사하지 않는다. 따라서 요청문에서 현재 에이전트의 목록도 대조하도록 했다. 동명 스킬 선택 우선순위는 보장하지 않는다.

## 왜 세 저장소 전체가 아니라 스킬 패키지를 포함하는가

이것은 스킬 본문만 잘라내거나 일부 기능을 재작성하는 배포가 아니다.

- **CAD:** 안정 배포 `latest` 브랜치가 제공하는 12개 스킬 모두와 각 폴더의 참조·스크립트·요구사항·UI metadata·라이선스를 포함한다. 이 브랜치는 원본도 권장하는 배포용 구성이다. 개발용 웹사이트·예제 모델·서버 개발 소스까지 복사하는 것과 실제 CAD 엔진 설치는 다른 일이다.
- **ponytail:** 일반 사용자용 6개를 모두 포함한다. 별도 에이전트용 중복 포맷과 저장소 개발 도구는 설치하지 않는다. `ponytail-gain`의 수치 출처인 원본 README·벤치마크 문서도 함께 보존한다. 이 배포는 플러그인 hooks나 세션 시작 시 자동 활성화 설정을 설치하지 않으며, 원본 문서의 플러그인 전용 표기/설정이 skills-only 모드에 자동 적용되지는 않는다.
- **REA:** 사용자용 `reverse-engineer-anything`과 모든 참조를 포함한다. 제외한 3개(`rea-changelog-update`, `rea-ci-tests-audit`, `rea-tool-design`)는 REA 자체의 릴리즈·CI·도구 개발용이며 역공학 엔진이 아니다.

**사용자 우려대로, 스킬 파일만 설치하면 CAD·REA 전체 기능이 바로 준비되는 것은 아니다.** 런타임·엔진·MCP가 빠진 상태에서 모델 생성이나 바이너리 분석이 된다고 약속하지 않는다. 반대로 전체 Git 저장소를 다운로드하는 것만으로도 런타임 설치·빌드·MCP 등록이 완료되지는 않는다.

## 전체 기능이 필요할 때의 별도 준비 경로

다른 PC에서 기능까지 필요하면 다음 요청을 별도로 사용한다.

```text
설치된 CAD/REA 스킬을 실제 도구와 연결해 사용할 수 있도록 공식 전체 설치 경로를 검토해줘.
현재 OS·런타임·기존 플러그인·MCP·공급 엔진과 스킬/패키지 버전을 대조해줘.
다운로드 용량, 변경할 설정·백업·원복, telemetry와 외부 연결을 먼저 설명해줘.
승인 후 필요한 구성만 설치하고, 중복 스킬 등록을 피한 뒤 실제 도구 목록과 작은 결과물로 검증해줘.
이미 있는 스킬을 setup이 교체하려 하면 차이를 먼저 보여줘.
```

| 대상 | 실제 기능을 위한 추가 구성·원본 안내 |
| --- | --- |
| CAD | [공식 전체 설치](https://github.com/earthtojake/text-to-cad#-install). 현재 동봉 스킬은 `cadgen==0.7.21`, uv 관리 Python 3.13을 지시한다. 첫 사용에 다운로드가 있고 snapshot은 브라우저 구성도 받을 수 있다. `dfam-check`의 requirements도 포함했지만 설치하지 않았다. 원본은 기본 사용 통계·오류 보고를 안내하므로 선택을 확인한다. |
| REA | [공식 설치·설정](https://github.com/morluto/rea#quick-start). 지원 Node/npm, REA 런타임/MCP 및 대상에 필요한 JADX/JDK 또는 분석 엔진을 별도로 준비한다. npm 버전과 동봉 스킬 커밋이 일치한다고 가정하지 않는다. `npx`의 doctor/dry-run도 패키지·캐시 다운로드가 생길 수 있다. |
| ponytail | 스킬 모드는 외부 분석 엔진이 필요 없다. 원본의 플러그인/hook 방식이 필요하면 [공식 설치 안내](https://github.com/DietrichGebert/ponytail)를 따르고 기존 6개와 이중 등록하지 않는다. |

공식 플러그인 전체 설치와 이 저장소의 skills-only 설치를 같은 앱에 겹치게 적용하지 않는다. 설치·MCP 등록·실제 도구 호출·결과물 검증은 별개 단계다. 프린터, 제조업체 계정, 주문·결제 권한은 이 배포가 만들지 않는다.

## 검증과 남는 한계

패키지 검사는 27개 목록·고유 이름·참조 존재·원본 해시와 라이선스를 확인한다. 임시 목적지에서 지원 파일 포함 복사, 재실행 skip, 동명 충돌 시 무변경을 시험한다. CAD 모델 생성, 제조 검사 정확도, REA 엔진 실행, 플러그인 hook 동작, 타PC 선택기·암묵 선택의 일반 성능은 이 패키지 검사로 입증하지 않는다. [검증 기록](../evals/bundle/README.md)과 [업데이트 정책](upstream-updates.md)을 확인한다.

## Anatomy 추가 — 2026-10-29

[Anatomy 설치·검증](anatomy-20261029.md)을 참고하세요. 원본 저장소 자체가 하나의 스킬인 구성도 업데이트 검사에 포함합니다. Node.js 20.10+와 Chrome/Chromium이 필요하며 Windows에서도 지원합니다. 별도 API 키는 필요하지 않지만 Codex 사용량은 발생합니다. 전체 패키지를 포함했으며 커뮤니티 게시·추가 과금은 별도 요청 없이 실행하지 않습니다.
