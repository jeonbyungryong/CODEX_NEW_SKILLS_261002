# 다른 PC에서 DWG를 편집 가능한 3D 모델로 변환

2026-10-31. `image-to-cad`와 `solidworks-dwg-to-native`를 사용자 스킬로 등록했다.
두 스킬은 일괄 설치 목록에 포함된다. 기존 upstream `cad` 패키지·라이선스·해시는
그대로 유지하므로 upstream 갱신이 네이티브 모델링 절차를 덮어쓰지 않는다.

## 설치할 때 복사할 요청문

```text
https://github.com/jeonbyungryong/CODEX_NEW_SKILLS_261002 의 최신 상태와
AGENTS.md, docs/native-cad-setup.md를 확인해줘.
현재 CODEX_HOME, 기존 스킬/플러그인과 같은 이름의 사용자 수정본을 확인한 뒤
image-to-cad와 solidworks-dwg-to-native를 함께 설치해줘.
STEP 검사도 필요하므로 cad가 없으면 함께 설치해줘.
검증한 커밋과 설치한 파일을 확인하고 기존 사용자 수정본은 보존해줘.
이 PC의 SolidWorks, AutoCAD 또는 ODA, Python/uv와 API 접근 상태를 확인하고
스킬 파일 설치와 실제 CAD 실행 가능 여부를 분리해 알려줘.
프로그램 추가 설치나 라이선스 변경이 필요하면 해당 사항을 먼저 설명해줘.
```

전체 모음은 [27개 설치 안내](bulk-install.md)를 따른다. 선택 설치 시에도 저장소
검증과 목적지 중복 검사를 먼저 하고, 설치 가능한 missing 항목만 공식
`skill-installer` helper에 전달한다. 검증한 커밋을 `--ref`에 지정한다:

```text
python <skill-installer>/scripts/install-skill-from-github.py --repo jeonbyungryong/CODEX_NEW_SKILLS_261002 --ref <검증한-커밋> --path skills/image-to-cad skills/solidworks-dwg-to-native
```

이미 같은 이름이 있으면서 내용이 다르면 자동 덮어쓰지 않는다. 파일별 차이와
백업을 준비한 뒤 승인된 범위만 갱신한다. 이 저장소의 CAD 스킬은 upstream 원본이므로,
기존 PC의 `cad`에 별도로 추가한 사용자 지침이 있으면 설치 충돌로 보고 보존한다.
두 전용 스킬을 명시 호출하면 upstream cad 본문 수정 없이 네이티브 경로를 사용할 수 있다.

## 실제 도면을 변환할 때 복사할 요청문

```text
$image-to-cad와 $solidworks-dwg-to-native를 사용해 첨부 DWG를
수정 가능한 SolidWorks SLDPRT로 만들어줘.
스케치는 원점 (0,0,0)을 기준으로 적절한 치수·기하 관계로 완전 구속하고,
돌출·컷·구멍 가공 마법사·필렛·구배를 형상에 맞게 사용해줘.
도면의 명시 치수, 실제 벡터, 추정 깊이와 불명확한 주기를 구분해줘.
주요 치수를 실제 변경·재생성·복원하고 최종 파일을 저장 후 다시 열어 검증해줘.
원본은 보존하고 SLDPRT, 필요하면 STEP, 수정 방법과 검증 결과를 제공해줘.
```

## 필요한 실행 환경과 한계

| 항목 | 필요성 |
|---|---|
| Windows + 사용 가능한 SolidWorks | 네이티브 SLDPRT 모델링·API/화면 조작. 라이선스와 템플릿 별도 |
| ODA File Converter 또는 DXF 내보내기가 가능한 CAD | DWG 벡터 추출. ODA가 있으면 AutoCAD는 필수가 아님 |
| Python 3.12+ / uv | 이미지·도면 복원 helper. 실행 시 선언된 의존성을 격리 환경에 준비 |
| cad/cadgen | 선택적 STEP 독립 검사와 미리보기 |

스킬 복사만으로 설계 프로그램, 계정, MCP 또는 라이선스가 생기지 않는다.
실행 파일·COM·템플릿 위치는 해당 PC에서 찾는다. 안내의 API 관측은 SolidWorks
2022 SP5에서 확인한 것으로, 다른 버전/다른 설계 프로그램에서는 기능과 결과를
별도로 검증해야 한다. 다른 CAD를 요구하면 그 프로그램의 네이티브 피처로 같은
구속·편집·저장 검증 기준을 적용하되, SolidWorks 전용 API를 그대로 사용하지 않는다.

검증 순서는 **합성 DXF 복원 → 해당 PC의 작은 네이티브 부품 편집·재열기 → 실제 도면**이다.
구체적인 확인 절차는 [환경 참조](../skills/solidworks-dwg-to-native/references/environment-setup.md)에 있다.
스킬은 다음 turn/새 대화의 목록에서 확인한다. GitHub 업데이트가 기존 PC에 자동으로
설치되지는 않으며, 검토된 버전으로 각 PC에서 갱신한다.

## 근거와 배포 범위

직전 실제 DWG 변환에서 네이티브 스케치 16개 완전 정의, 8개 변수의 개별/동시 변경과
복원·재열기를 검증했다. 이 경험을 참조 지침으로 정리했다. 특정 도면의 치수, 구배,
R5 보류 결정은 다음 도면의 기본값으로 사용하지 않는다.

이 패키지는 생산용 복원 helper와 합성 검증만 배포한다. 개인 도면, 사용자별 절대경로,
출처/재배포 범위가 확인되지 않은 이미지 fixture와 그 전용 회귀시험은 포함하지 않았다.
원래 로컬 파일은 그대로 보존한다. 따라서 합성 검증 통과를 모든 래스터/PDF 도면의
정확도 또는 다른 PC의 SolidWorks 실측 성공으로 확대하지 않는다.

공개 저장소 연동은 리뷰 브랜치/PR로 제공한다. main 병합은 명시 승인 후 수행하며,
병합 전에는 PR의 검증된 커밋을 설치 대상으로 지정할 수 있다.

### 이번 패키지 검증

- 설치 목록과 YAML: 27개 고유 스킬 확인.
- 패키지/설치 회귀 19개 및 기존 컴퓨터 사용 복구 회귀 18개 통과.
- 빈 임시 폴더에 27개 전체 지원 파일 설치와 두 번째 실행의 동일 패키지 건너뛰기 확인.
- 별도 의존성 환경에서 합성 DXF의 원호 보존, 80 × 240 mm 외곽 및 면적 확인.
- mm/inch/m 도면의 허용오차 환산, 원본 단위·CIRCLE·ARC·bulge 보존 및 0.1 mm 간극이 0.05 mm 기준에서 닫히지 않음 확인.
- upstream `cad`와 `third_party` 원본·해시는 변경하지 않음.

위 결과는 현재 Windows PC의 패키지·복원 시험이다. 다른 물리 PC의 SolidWorks
실행/라이선스/API는 미검증이며, 설치 후 해당 PC에서 위의 네이티브 부품 시험을 수행한다.
