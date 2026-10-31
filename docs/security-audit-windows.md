# Windows Security Audit 보고서 CLI

Windows 10/11에서 기본 Windows PowerShell 5.1과 Node 22 이상을 사용한다.
Linux·WSL·유료 API·별도 모델 계정 없이 기존 두 명령을 그대로 실행할 수 있다.

```powershell
node "$env:USERPROFILE/.codex/skills/security-audit/validate-findings.cjs" ./findings.json
node "$env:USERPROFILE/.codex/skills/security-audit/validate-coverage-ledger.cjs" ./coverage-ledger.json
```

정상 문서에는 `PASS`와 종료 코드 0, 잘못된 문서에는 설명과 종료 코드 1을 반환한다.
한글·공백이 포함된 로컬 경로를 지원한다. 파일은 로컬 일반 파일이어야 한다.
UNC·네트워크 드라이브·장치·대체 데이터 스트림·reparse point/링크는 거부한다.
보고서가 OneDrive 등 reparse point 아래 있으면 일반 로컬 작업 폴더로 복사해 검증한다.

Windows에서 POSIX 전용 open flags를 생략하는 대신 Win32 handle 기반 입력 경로를 추가했다.
부모 디렉터리와 입력 파일을 쓰기·삭제 공유 없이 고정하고, reparse point 자체를 열어
파일 종류·속성·크기를 검사한다. 5 MiB 제한, 엄격한 UTF-8, JSON 깊이·개수·스키마·의미
검사와 오류 메시지 정리는 유지한다. PowerShell 자식 프로세스에는 4초 제한을 둔다.
입력 경로나 JSON을 명령 문자열에 삽입하지 않으며 실행 정책·계정·방화벽 설정도 변경하지 않는다.
Win32 API 근거와 구현 범위는 [패치 안내](../patches/security-audit/README.md)에 연결했다.

원본 커밋·MIT 라이선스는 그대로 추적한다. 변경한 검증기/시험 4개와 추가한 Windows
reader 2개는 `patches/security-audit/`에 별도 보관하며 `bundle.json`과 lock이 원본 해시,
패치 해시 및 적용 파일을 구분한다. 수정 대상 upstream 파일이 달라지면 updater는
자동 덮어쓰기 전에 중단한다. 이 모음의 일괄 설치는 Windows 패치까지 포함한다.

이 변경은 보고서·coverage 검증 CLI를 Windows에서 사용할 수 있도록 한다.
감사 대상 코드를 실행하는 빌드·퍼징·브라우저 시험의 OS 격리를 제공하는 변경은 아니다.
그 실행에는 원본 스킬의 네트워크 차단·읽기 전용 대상·환경·자원 제한 요구가 그대로 적용된다.
소스 검토, finding/coverage 작성·검증, 검증된 내용을 이용한 보고서 작성은 Windows에서 수행한다.
