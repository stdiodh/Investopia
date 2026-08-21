# 포트폴리오 수정본

면접관이 한 장에서 하나의 주장과 근거를 읽을 수 있도록 정리한 10페이지 포트폴리오입니다.
원본 Figma Make 파일은 수정하지 않았습니다.

- PDF: `../output/pdf/portfolio_visual_revised.pdf`
- Figma 수정본: https://www.figma.com/design/XDYFF0ZT7hoXu2q2DoQ52C

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
```

`qa/capture.mjs`는 각 페이지의 1600×900 크기, 오버플로, 이미지 배율과 인쇄 링크를 확인합니다.
