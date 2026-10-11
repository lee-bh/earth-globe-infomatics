# earth-globe-infomatics

## 세계 지표 지구본

세계 각국의 지표를 3D 지구본 위에 색으로 칠해 비교하는 페이지입니다.

- **왼쪽 · 지표 목록**: 지표를 고르면 지구본 색, 범례, 순위표가 그 지표로 바뀝니다. 아래에 지표 설명·계산 방법·출처가 나옵니다.
- **가운데 · 지구본**: 드래그로 회전, 스크롤/핀치로 확대(키보드: 방향키, `+`/`-`). 마우스를 올리면 툴팁, 누르면 오른쪽에 상세가 열립니다. 범례 구간에 마우스를 올리면 그 구간만 강조됩니다.
- **오른쪽 · 세부 데이터**: 선택한 나라의 값·순위·한국 대비 비교·세부 항목, 시계열이 있는 지표는 추이 그래프(한국과 비교), 같은 나라의 다른 지표 값, 그리고 검색·지역 필터가 되는 순위표.
- 주소 끝에 `#minimum-wage`, `#life-expectancy`, `#gdp-per-capita`, `#fertility`, `#population`, `#population-density`, `#unemployment`, `#co2-per-capita`를 붙이면 해당 지표로 바로 열립니다.
- 라이트/다크 모드, 휴대폰 화면 지원.

### 들어 있는 지표

| 지표 | 기준 | 범위 | 출처 |
|---|---|---|---|
| 최저임금 (월, 미국 달러) | 2026년 10월 | 101개국 + 법정 최저임금 없는 15개국 | Eurostat, Trading Economics 등 (아래 참고) |
| 기대수명 (출생 시, 남녀 전체·남·여, 1950–2023 추이) | 2023년 추정치 | 236개 국가·지역 | [UN World Population Prospects 2024](https://population.un.org/wpp/) |
| 1인당 GDP (미국 달러 명목, 2000–2023 추이) | 2023년 (없으면 2019년 이후 최근 값) | 209개 국가·지역 | [World Bank](https://data.worldbank.org/indicator/NY.GDP.MKTP.CD) GDP ÷ 인구 |
| 합계출산율 (1950–2023 추이) | 2023년 추정치 | 236개 국가·지역 | [UN World Population Prospects 2024](https://population.un.org/wpp/) |
| 인구 (남·여, 2050·2100년 전망, 1950–2026 추이) | 2026년 (중위 추계) | 236개 국가·지역 | [UN World Population Prospects 2024](https://population.un.org/wpp/) |
| 인구밀도 (km²당 명) | 2026년 | 215개 국가·지역 | UN 인구 ÷ [World Bank 육지 면적](https://data.worldbank.org/indicator/AG.LND.TOTL.K2) |
| 실업률 (남·여, 1991–2025 추이) | 2025년 (ILO 모형 추정) | 186개 국가·지역 | [World Bank / ILO](https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS) |
| 1인당 CO2 배출량 (소비 기준 값, 1950–2024 추이) | 2024년 | 213개 국가·지역 | [Global Carbon Budget 2025](https://globalcarbonbudgetdata.org/) via [Our World in Data](https://github.com/owid/co2-data) |

### 실행

`index.html`을 브라우저로 바로 열면 됩니다(웹 서버 필요 없음). 글꼴만 Google Fonts에서 받아 오고, 없으면 시스템 글꼴을 씁니다.

### 파일 구성

| 경로 | 내용 |
|---|---|
| `index.html` | 페이지 (D3 정사영 투영 + Canvas 지구본) |
| `data/countries.csv` | 나라 목록: UN M49 코드, ISO3, 한국어·영어 이름, 지역 |
| `data/minimum-wage.csv` | 최저임금 원본: 법정 금액, 통화, 단위, 월 환산 계수, 시행 시점, 환율, 출처, 비고 |
| `data/life-expectancy.csv` | 기대수명 원본: 최신 연도 남녀 전체·남·여 |
| `data/life-expectancy-series.csv` | 기대수명 연도별 추이 (1950–2023) |
| `data/gdp-per-capita.csv` | 1인당 GDP 원본: 연도, GDP(달러), 인구, 1인당 GDP |
| `data/gdp-per-capita-series.csv` | 1인당 GDP 연도별 추이 (2000–2023, 빈칸 = 자료 없음) |
| `data/fertility.csv`, `data/fertility-series.csv` | 합계출산율 최신값과 연도별 추이 (1950–2023) |
| `data/population.csv`, `data/population-series.csv` | 인구 기준연도 값(남·여, 2050·2100년 전망)과 연도별 추이 (1950–2026) |
| `data/population-density.csv` | 인구밀도 원본: 인구, 육지 면적(km²), 면적 기준 연도, 밀도 |
| `data/unemployment.csv`, `data/unemployment-series.csv` | 실업률 최신값(전체·남·여)과 연도별 추이 (1991–2025) |
| `data/co2-per-capita.csv`, `data/co2-per-capita-series.csv` | 1인당 CO2 최신값, 총배출량, 소비 기준 1인당 값과 연도별 추이 (1950–2024) |
| `data/countries.js`, `data/indicators/*.js` | CSV에서 생성한 페이지용 데이터 (직접 수정하지 말 것) |
| `data/world-50m.js`, `data/world-110m.js` | Natural Earth 국경 (world-atlas@2.0.2). 지구본은 멈춰 있을 때 1:50m, 움직이는 동안 1:110m을 그림 |
| `vendor/` | d3@7.9.0, topojson-client@3.1.0 |
| `scripts/import_sources.py` | UN WPP 2024, 세계은행 GDP·인구·육지 면적·실업률, Our World in Data CO2, i18n-iso-countries에서 `countries.csv`와 모든 지표 CSV(최저임금 제외)를 다시 만듦 (사용법은 파일 머리말) |
| `scripts/build_data.py` | CSV → `data/*.js` 생성 |
| `scripts/build_standalone.py` | 모든 데이터를 넣은 단일 HTML 파일 생성 |

CSV를 고친 뒤에는 다음을 실행하세요.

```sh
python3 scripts/build_data.py
```

나라 이름과 지역은 `data/countries.csv` 한 곳에서만 가져옵니다(`minimum-wage.csv`의 이름·지역 열은 읽기 편하라고 남겨 둔 것입니다). 나라 키는 UN M49 숫자 코드로, 지도 파일의 국가 id와 같습니다. 코소보는 지도 파일에 id가 없어 이름으로 연결하고 UN 코드 412를 씁니다.

### 지표 추가하기

1. `data/`에 원본 CSV를 넣습니다 (나라 키는 `countries.csv`의 `id`).
2. `scripts/build_data.py`에 `build_<지표>()` 함수를 추가해 `push_indicator({...})`를 호출합니다. 넣을 항목:
   - `id`, `order`, `group`, `name`, `longName`, `summary`, `asOf`, `unitLabel`
   - 표시 형식: `prefix`, `suffix`, `bigUnit`, `decimals`
   - 색 구간: `thresholds`(5개 경계값 → 6구간), `binLabels`, `legendTitle`
   - 한국 비교 방식: `compare`(`"ratio"` 비율 / `"diff"` 차이), 값이 없는 나라 표시용 `noneLabel`
   - 선택: `barScale: "log"`(값 차이가 큰 지표의 막대), `rankLabel`(순위표 제목 옆 설명), `seriesLabel`(추이 그래프 제목), `format: "count"`(사람 수를 "5,156만 명"처럼 표시), `diffSuffix`(한국과의 차이 단위, 예: `"%p"`)
   - `method`(문단 목록), `sources`(`{name, url}` 목록)
   - `rows`: 나라 키별 `{status: "value" | "none", value, tip, details: [[이름, 값], ...], note, series: {start, values}}`
3. `index.html`의 지표 `<script>` 목록에 `data/indicators/<id>.js`를 추가합니다.

페이지는 지표 목록, 범례, 순위, 상세 카드, 추이 그래프를 이 설명만 보고 그립니다.

### 계산 방법

**최저임금**: `월 환산(USD) = 법정 금액 × 월 환산 계수 ÷ 환율(1달러당 현지 통화)`
- 시급은 주 40시간 × 52주 ÷ 12 ≈ 173.33시간 (한국 209시간, 호주 주 38시간, 파나마 주 48시간), 일급은 월 26일(멕시코 30.4일)
- 유럽연합 국가는 Eurostat의 월 환산 유로 금액을 그대로 사용
- 지역별로 다른 나라는 수도 또는 최고 등급 지역 기준, 일본은 전국 가중평균, 미국·캐나다는 연방 기준
- 환율은 2026년 10월 초 기준(일부 통화는 근사치), 세전 명목 금액(구매력 미반영)
- `source`가 `공개 보도 종합(원문 미확인)`인 행은 공식 고시를 직접 확인하지 못한 값

**1인당 GDP**: 세계은행 GDP(현재 미국 달러) ÷ 같은 해 세계은행 인구로, 세계은행의 NY.GDP.PCAP.CD와 같은 계산입니다. 2023년 값이 없으면 2019년 이후 가장 최근 값을 쓰고 연도를 표시합니다. 그보다 오래된 값만 있는 나라와 세계은행 비회원(대만, 북한 등)은 자료 없음입니다. 명목 금액이라 구매력은 반영하지 않았습니다.

**합계출산율**: UN WPP 2024의 2023년 추정치입니다. 인구 대체 수준(2.1명)이 범례 구간 경계이며, 상세 카드에 대체 수준과의 차이와 역대 최고치를 보여 줍니다.

**인구**: UN WPP 2024 값입니다. 2023년까지는 추정치, 그 뒤(2026년 기준값 포함)는 중위 추계입니다. 상세 카드에 2050·2100년 중위 추계와 증감률을 함께 보여 줍니다.

**인구밀도**: 인구 지표와 같은 UN 2026년 인구를 세계은행 육지 면적(내수면 제외, 최신 연도)으로 나눴습니다. 세계은행에 면적이 없는 곳(대만 등)은 자료 없음입니다. 나라 전체 평균이라 사막·산지가 넓은 나라는 체감 밀도보다 낮게 나옵니다.

**실업률**: 국제노동기구(ILO)가 나라별 조사 방식을 같은 기준으로 맞춘 모형 추정치(세계은행 SL.UEM.TOTL.ZS)입니다. 각국 공식 실업률과 다를 수 있고, 비공식 부문이 큰 나라는 낮게 나오는 경향이 있습니다. 한국과의 차이는 %p로 표시합니다.

**1인당 CO2 배출량**: Global Carbon Budget 2025의 화석연료·시멘트 CO2(생산 기준)를 인구로 나눈 Our World in Data 값입니다. 토지 이용 변화와 다른 온실가스는 빠져 있고, 국제 항공·해운 연료는 어느 나라에도 들어가지 않습니다. 상세 카드에 무역을 반영한 소비 기준 값과 1990년 대비 변화를 함께 보여 줍니다.

**기대수명**: UN WPP 2024 추정치를 그대로 사용합니다. 그해의 연령별 사망률이 평생 유지된다고 가정한 값이라, 전쟁·감염병이 있던 해에는 크게 떨어질 수 있습니다. 모나코·산마리노 같은 작은 국가와 해외 영토도 UN 집계에 포함되어 순위에 들어갑니다.

### 주요 출처

- [UN World Population Prospects 2024](https://population.un.org/wpp/) via [PPgp/wpp2024](https://github.com/PPgp/wpp2024)
- [Global Carbon Budget 2025](https://globalcarbonbudgetdata.org/) via [owid/co2-data](https://github.com/owid/co2-data)
- [World Bank Unemployment (modeled ILO estimate)](https://data.worldbank.org/indicator/SL.UEM.TOTL.ZS), [Land area](https://data.worldbank.org/indicator/AG.LND.TOTL.K2) via [datasets/world-development-indicators](https://github.com/datasets/world-development-indicators)
- [World Bank GDP (current US$)](https://data.worldbank.org/indicator/NY.GDP.MKTP.CD), [Population](https://data.worldbank.org/indicator/SP.POP.TOTL) via [datasets/gdp](https://github.com/datasets/gdp), [datasets/population](https://github.com/datasets/population)
- [Eurostat – Minimum wage statistics](https://ec.europa.eu/eurostat/statistics-explained/index.php?title=Minimum_wage_statistics)
- [Trading Economics – Minimum wages by country](https://tradingeconomics.com/country-list/minimum-wages)
- [IndexBox – Europe minimum wage July 2026](https://www.indexbox.io/blog/minimum-wage-in-europe-july-2026-rankings-and-inflation-impact/)
- [Rivermate – Minimum wage Latin America 2026](https://rivermate.com/blog/minimum-wage-latin-america-2026)
- [Africa HR – Minimum wage across Africa](https://africa-hr.com/blog/minimum-wage-across-africa/)
- [ECB euro reference rates](https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html), [Federal Reserve H.10](https://www.federalreserve.gov/releases/h10/current/)
- 나라 이름: [i18n-iso-countries](https://github.com/michaelwittig/node-i18n-iso-countries) (일부 표기 수정)
- 지도: [Natural Earth](https://www.naturalearthdata.com/) via [world-atlas](https://github.com/topojson/world-atlas)
