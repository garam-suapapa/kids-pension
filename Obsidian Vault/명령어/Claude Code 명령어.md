# Claude Code 명령어 정리

## 슬래시 명령어

| 명령어               | 설명                  |
| ----------------- | ------------------- |
| `/help`           | 도움말                 |
| `/clear`          | 대화 초기화              |
| `/compact`        | 대화 압축 (컨텍스트 절약)     |
| `/config`         | 설정 (테마, 모델 등)       |
| `/cost`           | 현재 세션 토큰 비용 확인      |
| `/doctor`         | Claude Code 상태 진단   |
| `/fast`           | 빠른 모드 토글 (Opus 4.6) |
| `/init`           | CLAUDE.md 초기화       |
| `/login`          | Anthropic 로그인       |
| `/logout`         | 로그아웃                |
| `/mcp`            | MCP 서버 관리           |
| `/memory`         | 메모리 관리              |
| `/model`          | 모델 변경               |
| `/permissions`    | 권한 관리               |
| `/review`         | PR 코드 리뷰            |
| `/status`         | 현재 상태 확인            |
| `/terminal-setup` | 터미널 설정              |
| `/vim`            | Vim 모드 토글           |
| `/bug`            | 버그 리포트              |

## 키보드 단축키

| 단축키 | 설명 |
|--------|------|
| `Enter` | 메시지 전송 |
| `Shift+Enter` | 줄바꿈 (전송 안 함) |
| `Ctrl+C` | 작업 취소 |
| `Ctrl+D` | 종료 |
| `↑ / ↓` | 이전/다음 명령어 기록 |
| `Alt+T` | 확장 사고(Extended Thinking) 토글 |
| `Ctrl+O` | 사고 과정 출력 토글 |

## 특수 입력

| 입력 | 설명 |
|------|------|
| `!명령어` | 쉘 명령어 직접 실행 (예: `!git status`) |
| `/skill명` | 스킬 실행 |

## 주요 스킬 (슬래시로 실행)

| 스킬 | 설명 |
|------|------|
| `/plan` | 구현 계획 수립 |
| `/review` | 코드 리뷰 |
| `/tdd` | 테스트 주도 개발 워크플로우 |
| `/security-review` | 보안 검토 |
| `/docs` | 라이브러리 문서 조회 |
| `/update-codemaps` | 코드맵 업데이트 |
| `/init` | CLAUDE.md 초기화 |
| `/verify` | 빌드/린트/테스트 검증 |
| `/save-session` | 현재 세션 저장 |
| `/schedule` | 예약 에이전트 생성 |

## 설정 파일 위치

| 파일 | 용도 |
|------|------|
| `~/.claude/settings.json` | 글로벌 설정 (MCP, 모델 등) |
| `.claude/settings.local.json` | 프로젝트별 권한 설정 |
| `CLAUDE.md` | 프로젝트 지시사항 |
| `~/.claude/projects/*/memory/` | 프로젝트 메모리 |

## MCP 서버 설정 예시

```json
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer YOUR_TOKEN\"}"
      }
    }
  }
}
```
