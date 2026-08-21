# HR 검토용 포트폴리오 수정본

이력서와 겹치는 설명을 줄이고, 면접관이 한 장에서 문제·판단·결과·근거를 읽을 수 있도록 정리한 9페이지 포트폴리오입니다.
수치는 전후 결과와 짧은 측정 조건만 표기하며 계산식은 넣지 않았습니다. 원본 소스·PDF·Figma 파일은 수정하지 않았습니다.

- PDF: `../output/pdf/portfolio_hr_revised.pdf`
- Figma 수정본: https://www.figma.com/design/XDYFF0ZT7hoXu2q2DoQ52C?node-id=6-2

## 실행

```bash
npm ci
npm run dev
```

## 검증

```bash
npm run typecheck
npm run lint
npm run build
npm run qa
```

`qa/capture.mjs`는 각 페이지의 1600×900 크기, 오버플로, 이미지 배율과 인쇄 링크를 확인합니다.
`qa/content-audit.mjs`는 9페이지 구성, 중복 수치, 계산식, 프로젝트별 배포 상태를 확인합니다.
