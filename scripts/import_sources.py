"""Import third-party source data into the repo's CSV files.

Run this only when refreshing the sources; the page is built from the CSVs it
writes (see build_data.py), so day-to-day edits happen in data/*.csv.

Usage:
    pip install rdata pandas
    git clone --depth 1 https://github.com/PPgp/wpp2024      # UN World Population Prospects 2024
    npm pack i18n-iso-countries@7.14.0 && tar xzf i18n-iso-countries-7.14.0.tgz
    python3 scripts/import_sources.py --wpp path/to/wpp2024 --i18n path/to/package

Writes:
    data/countries.csv               id, iso3, name_ko, name_en, region
    data/life-expectancy.csv         latest-year life expectancy at birth (total / male / female)
    data/life-expectancy-series.csv  total life expectancy for every year since 1950
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


if __name__ == "__main__":
    main()
