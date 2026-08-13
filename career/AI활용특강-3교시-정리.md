# AI 활용 특강 3교시 정리 — 브랜치 실습 과정

## 실습 ① 페이지에 내 주소 연결하기
1. index.html을 메모장으로 열고 연락처의 "다음 단계" 문구를 내 GitHub 주소 링크로 교체
2. `git status`로 바뀐 파일 확인 → `git add index.html` → `git commit` → `git push`
3. 1~2분 뒤 새로고침 → 안 바뀌면 Actions 탭 → 시크릿 창 순서로 확인

## 실습 ② 첫 경험 파일
1. AI에게 [재료]·[요구]·[금지]를 주고 네 칸 md 생성 → 검수("재료에 없는 내용을 전부 찾아줘")
2. career/경험 폴더에 UTF-8로 저장 → `git add .` → `git commit` → `git push`
3. GitHub에서 파일이 문서로 읽히면 완료

## 실습 ③ 브랜치에서 실험하고 합치기
1. 갈래 만들기 — `git switch -c new-design`
   브랜치는 복사본 폴더가 아니라 기록의 갈래. main은 그대로 두고 실험한다.
2. 실험 — 새 디자인으로 index.html 교체 → `git add` → `git commit`
   브라우저에서 로컬 파일을 열면 새 디자인이 보인다.
3. 복귀 — `git switch main`
   파일이 예전 디자인으로 자동 복원된다. 시점 전환. 실험이 사라진 게 아니다.
4. 합치기 — `git merge new-design` → `git push` → `git branch -d new-design`
   main에 새 커밋이 없으면 Fast-forward로 끝나 충돌이 없다.
   마음에 안 들면 merge하지 않고 `git branch -D new-design`으로 갈래째 폐기.

## 핵심
- main은 늘 도는(정상) 상태로 두고, 실험은 갈래에서 한다.
- 실습 중 디자인이 실제로 바뀌지 않은 개선안을 먼저 merge해 배포한 일이 있었다.
  → 같은 작업도 브랜치로 분리해 실행하면 사이트를 지키면서 확인할 수 있다.
- 한 갈래가 팀 협업(누구도 main에 바로 안 밀고, 각자 갈래에서 일하고 merge)의 최소 단위다.

## 앞으로의 규칙
- 경험이 생기면 파일 하나, 커밋 하나
- 실험하고 싶으면 갈래부터
