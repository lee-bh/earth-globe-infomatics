# earth-globe-infomatics

## 세계 최저임금 지구본

나라별 법정 최저임금을 월 환산 미국 달러로 바꿔 3D 지구본 위에 색으로 표시합니다.

- **드래그**로 지구본 회전, **스크롤/핀치**로 확대·축소 (키보드: 방향키, `+`/`-`)
- 나라에 마우스를 올리면 툴팁, 누르면 현지 통화 금액·월 환산 금액·적용 환율·한국 대비 비율을 보여 줍니다
- 오른쪽 순위표에서 검색·지역 필터, 항목을 누르면 지구본이 그 나라로 돌아갑니다
- 범례 구간에 마우스를 올리면 그 구간의 나라만 강조됩니다
- 라이트/다크 모드 지원

### 실행

`index.html`을 브라우저로 바로 열면 됩니다(웹 서버 필요 없음). 글꼴만 Google Fonts에서 받아 오고, 없으면 시스템 글꼴을 씁니다.

### 파일 구성

| 경로 | 내용 |
|---|---|
| `index.html` | 지구본 페이지 (D3 정사영 투영 + Canvas 렌더링) |
| `data/minimum-wage.csv` | **원본 데이터.** 나라별 법정 금액, 통화, 단위(시/일/주/월), 월 환산 계수, 시행 시점, 환율, 출처, 비고 |
| `data/minimum-wage.js` | CSV에서 생성한 페이지용 데이터 (직접 수정하지 말 것) |
| `data/world-50m.js` | Natural Earth 1:50m 국경 (world-atlas@2.0.2) |
| `vendor/` | d3@7.9.0, topojson-client@3.1.0 |
| `scripts/build_data.py` | CSV → `data/minimum-wage.js` 생성 |
| `scripts/build_standalone.py` | 데이터를 모두 넣은 단일 HTML 파일 생성 |

데이터를 고친 뒤에는 다음을 실행하세요.

```sh
python3 scripts/build_data.py
```

### 계산 방법

```
월 환산(현지 통화) = 법정 금액 × 월 환산 계수
월 환산(USD)       = 월 환산(현지 통화) ÷ 환율(1달러당 현지 통화)
```

- 시급: 주 40시간 × 52주 ÷ 12 ≈ 173.33시간 (한국 209시간, 호주 38시간 기준 164.67시간, 파나마 48시간 기준 208시간)
- 일급: 월 26일 (멕시코 30.4일)
- 유럽연합 국가는 Eurostat의 월 환산 유로 금액(연 14회 지급 국가는 12개월로 환산된 값)을 그대로 씁니다
- 환율은 2026년 10월 초 기준(ECB 기준환율, Fed H.10 등)이며 일부 통화는 근사치입니다
- 세전 명목 금액이며 구매력(PPP)은 반영하지 않았습니다

### 데이터에 대한 주의

- 기준 시점: 2026년 10월에 확인 가능한 최신 법정 최저임금 (나라마다 시행일이 다르며 CSV `effective` 열에 기록)
- 지역별로 다른 나라는 수도 또는 최고 등급 지역 기준(중국 상하이, 인도네시아 자카르타, 베트남 1지역, 태국 방콕, 필리핀 NCR), 일본은 전국 가중평균, 미국·캐나다는 연방 기준입니다
- `source`가 `공개 보도 종합(원문 미확인)`인 행은 공식 고시를 직접 확인하지 못한 값입니다. 정책 자료로 쓰려면 각국 노동부 고시와 대조하세요
- 법정 최저임금이 없는 나라(북유럽, 스위스, 이탈리아, 오스트리아, 싱가포르, 걸프 국가 일부 등)는 빗금으로 표시합니다

### 주요 출처

- [Eurostat – Minimum wage statistics](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Minimum_wage_statistics)
- [Trading Economics – Minimum wages by country](https://tradingeconomics.com/country-list/minimum-wages)
- [IndexBox – Europe minimum wage July 2026](https://www.indexbox.io/blog/minimum-wage-in-europe-july-2026-rankings-and-inflation-impact/)
- [Rivermate – Minimum wage Latin America 2026](https://rivermate.com/blog/minimum-wage-latin-america-2026)
- [Africa HR – Minimum wage across Africa](https://africa-hr.com/blog/minimum-wage-across-africa/)
- [ECB euro reference rates](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html), [Federal Reserve H.10](https://www.federalreserve.gov/releases/h10/current/)
- 지도: [Natural Earth](https://www.naturalearthdata.com/) via [world-atlas](https://github.com/topojson/world-atlas)
