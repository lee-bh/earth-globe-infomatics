"""Import third-party source data into the repo's CSV files.

Run this only when refreshing the sources; the page is built from the CSVs it
writes (see build_data.py), so day-to-day edits happen in data/*.csv.

Usage:
    pip install rdata pandas
    git clone --depth 1 https://github.com/PPgp/wpp2024      # UN World Population Prospects 2024
    npm pack i18n-iso-countries@7.14.0 && tar xzf i18n-iso-countries-7.14.0.tgz
    git clone --depth 1 https://github.com/datasets/gdp          # World Bank GDP (current US$), refreshed monthly
    git clone --depth 1 https://github.com/datasets/population   # World Bank population, refreshed monthly
    git clone --depth 1 https://github.com/datasets/world-development-indicators   # World Bank WDI mirror (land area)
    python3 scripts/import_sources.py --wpp path/to/wpp2024 --i18n path/to/package \
        --gdp path/to/gdp --population path/to/population --wdi path/to/world-development-indicators

Writes:
    data/countries.csv               id, iso3, name_ko, name_en, region
    data/life-expectancy.csv         latest-year life expectancy at birth (total / male / female)
    data/life-expectancy-series.csv  total life expectancy for every year since 1950
    data/fertility.csv               latest-year total fertility rate
    data/fertility-series.csv        total fertility rate for every year since 1950
    data/gdp-per-capita.csv          latest available GDP, population and GDP per capita (2019 or later)
    data/gdp-per-capita-series.csv   GDP per capita for every year since 2000 (blank when missing)
    data/population.csv              UN population for the reference year (total / male / female) and 2050 / 2100 projections
    data/population-series.csv       UN population for every year 1950 to the reference year
    data/population-density.csv      reference-year UN population ÷ World Bank land area (km²)
"""
import argparse
import csv
import json
from pathlib import Path

import rdata

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

# Korean names that differ from i18n-iso-countries' wording (current official or common usage).
KO_OVERRIDES = {
    "643": "러시아", "158": "대만", "203": "체코", "807": "북마케도니아", "792": "튀르키예",
    "180": "콩고민주공화국", "178": "콩고공화국", "748": "에스와티니", "132": "카보베르데",
    "410": "대한민국", "408": "북한", "840": "미국", "826": "영국", "344": "홍콩", "446": "마카오",
    "583": "미크로네시아", "275": "팔레스타인", "626": "동티모르", "862": "베네수엘라",
    "068": "볼리비아", "364": "이란", "760": "시리아", "834": "탄자니아", "418": "라오스",
    "016": "아메리칸사모아", "028": "앤티가 바부다", "090": "솔로몬 제도", "136": "케이맨 제도",
    "140": "중앙아프리카공화국", "196": "키프로스", "214": "도미니카공화국", "231": "에티오피아",
    "234": "페로 제도", "238": "포클랜드 제도", "268": "조지아", "292": "지브롤터", "296": "키리바시",
    "304": "그린란드", "412": "코소보", "417": "키르기스스탄", "531": "퀴라소",
    "535": "보네르·신트외스타티위스·사바", "580": "북마리아나 제도", "584": "마셜 제도",
    "598": "파푸아뉴기니", "616": "폴란드", "620": "포르투갈", "624": "기니비사우", "638": "레위니옹",
    "652": "생바르텔레미", "654": "세인트헬레나", "659": "세인트키츠 네비스", "662": "세인트루시아",
    "663": "생마르탱", "666": "생피에르 미클롱", "670": "세인트빈센트 그레나딘", "674": "산마리노",
    "694": "시에라리온", "710": "남아프리카공화국", "716": "짐바브웨", "772": "토켈라우",
    "784": "아랍에미리트", "788": "튀니지", "795": "투르크메니스탄", "796": "터크스 케이커스 제도",
    "798": "투발루", "876": "왈리스 푸투나", "212": "도미니카 연방",
}
EN_OVERRIDES = {"412": "Kosovo"}
AREA_KO = {
    "Africa": "아프리카", "Asia": "아시아", "Europe": "유럽",
    "Latin America and the Caribbean": "중남미", "Northern America": "북미", "Oceania": "오세아니아",
}
# Western Asia reads as the Middle East, except the Caucasus (Asia) and Cyprus (Europe); Iran joins it.
MIDDLE_EAST_EXCEPT = {"051": "아시아", "031": "아시아", "268": "아시아", "196": "유럽"}


def code3(n):
    return str(int(n)).zfill(3)


def region_for(loc):
    cid = code3(loc["country_code"])
    if cid in MIDDLE_EAST_EXCEPT:
        return MIDDLE_EAST_EXCEPT[cid]
    if loc["reg_name"] == "Western Asia" or cid == "364":
        return "중동"
    return AREA_KO.get(loc["area_name"], "")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wpp", required=True, type=Path)
    ap.add_argument("--i18n", required=True, type=Path)
    ap.add_argument("--gdp", required=True, type=Path)
    ap.add_argument("--population", required=True, type=Path)
    ap.add_argument("--wdi", required=True, type=Path)
    a = ap.parse_args()

    with (a.wpp / "data" / "UNlocations.txt").open(encoding="utf-8") as f:
        locs = [r for r in csv.DictReader(f, delimiter="\t") if r["location_type"] == "4"]

    ko = json.loads((a.i18n / "langs" / "ko.json").read_text(encoding="utf-8"))["countries"]
    en = json.loads((a.i18n / "langs" / "en.json").read_text(encoding="utf-8"))["countries"]
    codes = json.loads((a.i18n / "codes.json").read_text(encoding="utf-8"))
    by_num = {c[2]: (c[0], c[1]) for c in codes}

    def pick(names, a2):
        v = names.get(a2)
        return v[0] if isinstance(v, list) else v

    countries = []
    for loc in locs:
        cid = code3(loc["country_code"])
        a2, a3 = by_num.get(cid, ("", ""))
        name_ko = KO_OVERRIDES.get(cid) or (pick(ko, a2) if a2 else None) or loc["name"]
        name_en = EN_OVERRIDES.get(cid) or (pick(en, a2) if a2 else None) or loc["name"]
        if cid == "412":  # Kosovo: UN code 412, ISO user-assigned XKX
            a3 = "XKX"
        countries.append({"id": cid, "iso3": a3, "name_ko": name_ko, "name_en": name_en, "region": region_for(loc)})
    countries.sort(key=lambda c: c["id"])
    with (DATA / "countries.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "iso3", "name_ko", "name_en", "region"])
        w.writeheader()
        w.writerows(countries)

    e0 = rdata.read_rda(str(a.wpp / "data" / "e01dt.rda"))["e01dt"]
    country_ids = {int(l["country_code"]) for l in locs}
    e0 = e0[e0["country_code"].astype(int).isin(country_ids)]
    latest = int(e0["year"].max())
    years = sorted(int(y) for y in e0["year"].unique())

    with (DATA / "life-expectancy.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "year", "life_expectancy", "male", "female"])
        for _, r in e0[e0["year"] == latest].sort_values("country_code").iterrows():
            w.writerow([code3(r["country_code"]), latest, f"{r['e0B']:.2f}", f"{r['e0M']:.2f}", f"{r['e0F']:.2f}"])

    with (DATA / "life-expectancy-series.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id"] + years)
        for cc, g in e0.sort_values(["country_code", "year"]).groupby("country_code"):
            w.writerow([code3(cc)] + [f"{v:.1f}" for v in g["e0B"]])

    print(f"countries: {len(countries)}, life expectancy year: {latest}, series {years[0]}-{years[-1]}")

    import_fertility(a.wpp, country_ids)
    import_gdp_per_capita(a.gdp, a.population, countries)
    import_population(a.wpp, country_ids, countries, a.wdi)


def write_series(path, series, years, fmt):
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id"] + years)
        for cid in sorted(series):
            w.writerow([cid] + [fmt(series[cid][y]) if y in series[cid] else "" for y in years])


def import_fertility(wpp, country_ids):
    tfr = rdata.read_rda(str(wpp / "data" / "tfr1dt.rda"))["tfr1dt"]
    tfr = tfr[tfr["country_code"].astype(int).isin(country_ids)]
    latest = int(tfr["year"].max())
    years = sorted(int(y) for y in tfr["year"].unique())
    series = {}
    for _, r in tfr.iterrows():
        series.setdefault(code3(r["country_code"]), {})[int(r["year"])] = float(r["tfr"])
    with (DATA / "fertility.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "year", "tfr"])
        for cid in sorted(series):
            w.writerow([cid, latest, f"{series[cid][latest]:.3f}"])
    write_series(DATA / "fertility-series.csv", series, years, lambda v: f"{v:.2f}")
    print(f"fertility: {len(series)} countries, {years[0]}-{latest}")


MIN_GDP_YEAR = 2019  # older figures are left out rather than shown beside 2023 values


def import_gdp_per_capita(gdp_repo, pop_repo, countries):
    by_iso = {c["iso3"]: c["id"] for c in countries if c["iso3"]}

    def load(path):
        out = {}
        with path.open(encoding="utf-8") as f:
            for r in csv.DictReader(f):
                cid = by_iso.get(r["Country Code"])
                if cid and r["Value"]:
                    out.setdefault(cid, {})[int(r["Year"])] = float(r["Value"])
        return out

    gdp = load(gdp_repo / "data" / "gdp.csv")
    pop = load(pop_repo / "data" / "population.csv")
    pc = {cid: {y: v / pop[cid][y] for y, v in ys.items() if pop.get(cid, {}).get(y)} for cid, ys in gdp.items()}
    pc = {cid: ys for cid, ys in pc.items() if ys}

    rows = []
    for cid, ys in sorted(pc.items()):
        y = max(ys)
        if y < MIN_GDP_YEAR:
            continue
        rows.append([cid, y, f"{gdp[cid][y]:.0f}", f"{pop[cid][y]:.0f}", f"{ys[y]:.1f}"])
    with (DATA / "gdp-per-capita.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "year", "gdp_usd", "population", "gdp_per_capita_usd"])
        w.writerows(rows)

    kept = {r[0] for r in rows}
    years = list(range(2000, max(r[1] for r in rows) + 1))
    write_series(DATA / "gdp-per-capita-series.csv", {c: pc[c] for c in kept}, years, lambda v: f"{v:.0f}")
    print(f"gdp per capita: {len(rows)} countries (latest year >= {MIN_GDP_YEAR})")



POP_YEAR = 2026  # UN WPP 2024 estimates run to 2023; later years are its medium-variant projection


def import_population(wpp, country_ids, countries, wdi):
    est = rdata.read_rda(str(wpp / "data" / "popAge1dt.rda"))["popAge1dt"]
    est = est[est["country_code"].astype(int).isin(country_ids) & (est["year"] >= 1950)]
    est = est.groupby(["country_code", "year"])[["popM", "popF", "pop"]].sum().reset_index()
    proj = rdata.read_rda(str(wpp / "data" / "popproj1dt.rda"))["popproj1dt"]
    proj = proj[proj["country_code"].astype(int).isin(country_ids)].copy()
    proj["pop"] = proj["popM"] + proj["popF"]

    # values are in thousands
    total, male, female = {}, {}, {}
    for frame in (est, proj):
        for _, r in frame.iterrows():
            key = (code3(r["country_code"]), int(r["year"]))
            total[key], male[key], female[key] = r["pop"] * 1000, r["popM"] * 1000, r["popF"] * 1000

    ids = sorted({cid for cid, _ in total})
    with (DATA / "population.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "year", "population", "male", "female", "population_2050", "population_2100"])
        for cid in ids:
            w.writerow([cid, POP_YEAR] + [f"{v:.0f}" for v in (
                total[cid, POP_YEAR], male[cid, POP_YEAR], female[cid, POP_YEAR], total[cid, 2050], total[cid, 2100])])

    years = list(range(1950, POP_YEAR + 1))
    series = {cid: {y: total[cid, y] for y in years if (cid, y) in total} for cid in ids}
    write_series(DATA / "population-series.csv", series, years, lambda v: f"{v:.0f}")

    # World Bank land area: latest non-empty year per economy
    by_iso = {c["iso3"]: c["id"] for c in countries if c["iso3"]}
    land = {}
    with (wdi / "indicators" / "ag.lnd.totl.k2" / "data.csv").open(encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cid = by_iso.get(r["Country Code"])
            if cid and r["Value"] and (cid not in land or int(r["Year"]) > land[cid][0]):
                land[cid] = (int(r["Year"]), float(r["Value"]))
    with (DATA / "population-density.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "year", "population", "land_area_km2", "land_area_year", "density_per_km2"])
        for cid in ids:
            if cid in land and land[cid][1] > 0:
                pop = total[cid, POP_YEAR]
                w.writerow([cid, POP_YEAR, f"{pop:.0f}", f"{land[cid][1]:.2f}".rstrip("0").rstrip("."), land[cid][0], f"{pop / land[cid][1]:.2f}"])
    print(f"population: {len(ids)} countries ({POP_YEAR}); density: {sum(1 for c in ids if c in land)} with land area")


if __name__ == "__main__":
    main()
