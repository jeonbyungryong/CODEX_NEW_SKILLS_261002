# 다섯 저장소 전체 설치 — 2026-10-31

사용자가 다섯 저장소의 모든 사용자용 스킬을 개인 Codex 공용 경로에 설치하고 이 모음에 연동하도록 요청했다. 유료 API와 추가 결제는 허용하지 않았다.

## 승인한 패키지

| 원본 | 포함 패키지 | 라이선스 |
| --- | --- | --- |
| Leonxlnx/taste-skill | `design-taste-frontend` | MIT |
| hugohe3/ppt-master | `ppt-master` | MIT |
| heygen-com/hyperframes | `hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`, `figma`, `slideshow`, `remotion-to-hyperframes`, `reverse-any-video` | Apache-2.0 |
| pbakaus/impeccable | `impeccable` — 24개 명령을 포함한 단일 패키지 | Apache-2.0 |
| cloudflare/security-audit-skill | `security-audit` | MIT |

12개 신규 패키지를 기존 27개에 추가해 총 39개다. HyperFrames 저장소 자체 개발용 `.agents/` 스킬은 사용자 배포 목록에 넣지 않는다. HyperFrames의 `figma`는 영상 연동용 지침이며 Figma 플러그인을 대체하거나 중복 설치하지 않는다.

모든 선택 디렉터리의 지원 파일을 포함한다. Taste는 원본 폴더 `skills/taste-skill`과 frontmatter 이름 `design-taste-frontend`가 달라 명시적 경로 매핑을 사용한다. 원본 Git blob SHA-1을 확인하고 배포 파일 SHA-256, 커밋, 경로와 라이선스 해시를 lock에 기록했다. Windows checkout 줄바꿈 변환도 원본 blob과 대조한다. 패키지에 없는 루트 LICENSE/NOTICE는 원본 그대로 보충한다. 기존 27개 패키지는 변경하지 않는다.

## 현재 PC의 무료 실행 준비

- Taste: 기존 Node 24와 Chrome/Edge를 사용할 수 있다. API 키를 등록하지 않았다.
- PPT Master: 전용 `~/.codex/tools/ppt-master/.venv`에 전체 requirements를 설치했다. 이 환경의 Python으로 스크립트를 실행한다. 원본 attribution·sponsor·license와 실행 guard를 유지한다. 유료 이미지 생성·모델 호출은 실행하지 않는다.
- HyperFrames: 사용자 범위 CLI `0.8.223`, FFmpeg `9.0.2`와 기존 Chrome을 사용한다. telemetry를 끈다. `render`는 로컬 실행이며 `cloud render`, HeyGen 생성·로그인·요금제·모델 API는 사용하지 않는다. whisper/Kokoro/MusicGen 등의 대형 선택 모델은 자동 설치하지 않는다.
- Impeccable: 공식 Windows x64 engine `0.1.18`을 패키지의 checksum과 대조해 개인 cache에 설치했다. telemetry를 끈다. 에이전트 hooks는 별도 신뢰 승인 없이 활성화하지 않는다.
- Security Audit: 전체 지침·스키마·검증 도구를 포함한다. 소스 검토에 사용할 수 있다. 대상 코드 실행은 네트워크 차단, 환경 allowlist, 읽기 전용 대상과 scratch, 자원·시간 제한을 모두 갖춘 OS sandbox가 필요하다. 이번 설치가 해당 격리를 준비하거나 모든 프로젝트의 보안 검사를 수행했다는 뜻은 아니다.

Security Audit 원본 Node 검증기 시험은 이 Windows에서 65개 중 46개 통과, 7개 실패, 12개 skip이었다. 실패한 7개는 findings CLI가 `OS no-follow and nonblocking input protection is unavailable`로 입력을 거부하는 플랫폼 제한이다. 보호 장치를 제거하거나 원본을 수정하지 않았다. 순수 데이터 검증·소스 검토와 파일을 여는 보고서 CLI의 준비 상태를 구분한다. 보고서 CLI 전체 사용에는 호환되는 Linux 환경에서의 별도 검증이 필요하다.

개인 공용 설치는 해당 Windows 사용자로 실행하는 Codex의 모든 프로젝트에서 사용할 수 있는 범위다. 다른 사용자 계정·다른 PC·WSL 내부는 자동 설치하지 않는다. 새 대화 또는 앱 재시작 후 사용 가능 스킬 목록을 확인한다. 파일·실행 도구 검증만으로 자동 선택 성능이나 모든 선택 기능의 준비를 주장하지 않는다.

## GitHub 업데이트

로컬 연기 시험에서 PPT Master는 SVG 품질 gate를 거쳐 수정 가능한 1장 PPTX를 생성했다. gate와 postflight는 통과했으며 샘플 스타일·언어 선언 관련 경고 5개가 남았다. HyperFrames는 단일 worker로 320×180, 10fps, 0.5초 MP4(5프레임)를 4.7초에 로컬 렌더했다. Impeccable의 공식 engine은 임시 HTML을 검사해 JSON 결과를 반환했다. 이 시험은 프레젠테이션/영상 전체 품질이나 프로젝트 보안 판정이 아니다. 유료 모델·클라우드 렌더·로그인·결제 호출은 하지 않았다.

기존 업데이트 방식에 다섯 source를 추가한다. 새 upstream 패키지는 자동 승인하지 않고 기존 선택 목록만 추적한다. Apache-2.0은 명시 승인한 두 source에서만 허용하며 라이선스 내용이 바뀌면 쓰기 전에 중단한다. 자동 갱신은 검증된 리뷰 브랜치/PR을 만들며 main과 개인 PC 설치본을 자동 변경하지 않는다.

이 문서는 이 PC의 설치 기록이다. 다른 PC에서 일괄 설치하는 기본 명령은 스킬 파일만 설치하며 런타임·모델·계정·hooks는 별도다. 기존 프로젝트나 전역 Python 패키지를 변경하는 설치 안내로 해석하지 않는다.
