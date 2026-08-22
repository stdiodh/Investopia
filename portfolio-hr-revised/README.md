# 최종 제출 포트폴리오

5개 프로젝트의 역할, 구현 내용, 측정 결과, 근거 링크를 9페이지로 정리했습니다.
A&I.com 운영 화면과 측정 기록, 고찌봄 보도·수상 자료, SoloPlay 화면 시안과 테스트 소스를 포함합니다.

- 최종 제출 PDF: `../output/pdf/portfolio_submission_final_v2.pdf`
- 이전 제출 PDF: `../output/pdf/portfolio_submission_final.pdf`
- 이전 제출 Figma 페이지: https://www.figma.com/design/XDYFF0ZT7hoXu2q2DoQ52C?node-id=29-750
- 이전 근거 보강 PDF: `../output/pdf/portfolio_evidence_revised.pdf`
- 이전 근거 보강 Figma 페이지: https://www.figma.com/design/XDYFF0ZT7hoXu2q2DoQ52C?node-id=11-2
- 보존한 기존 PDF: `../output/pdf/portfolio_hr_revised.pdf`
- 보존한 기존 Figma 페이지: https://www.figma.com/design/XDYFF0ZT7hoXu2q2DoQ52C?node-id=6-2

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
`qa/content-audit.mjs`는 9페이지 구성, 중복 수치, 계산식, 프로젝트별 배포 상태, 측정·테스트 원문 링크를 확인합니다.
