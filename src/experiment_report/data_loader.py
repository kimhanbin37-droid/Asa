"""실험 Raw data(엑셀) 로딩 및 정규화.

입력 엑셀은 한 시트에 시료(샘플)별로 여러 행(반복 측정)이 있는 형태를 기본으로 가정한다.

    | 샘플명 | TSC(%) | RTVM(cP) | Mn    | Mw    | PDI  |
    |--------|--------|----------|-------|-------|------|
    | REF    | 45.2   | 1200     | 12000 | 24000 | 2.00 |
    | REF    | 45.4   | 1180     | 11900 | 23800 | 2.00 |
    | A-01   | 46.1   | 1350     | 13500 | 28000 | 2.07 |
    ...

같은 샘플명이 여러 행에 걸쳐 있으면(반복 측정) 자동으로 평균을 낸다.
컬럼명이 다르면 config의 column_map 으로 매핑을 지정할 수 있다.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

import pandas as pd

# 항목 코드 -> (표시용 라벨, 기본 별칭 목록)
ITEM_DEFS: dict[str, dict] = {
    "TSC": {"label": "TSC (%)", "aliases": ["tsc"]},
    "RTVM": {"label": "RTVM (cP)", "aliases": ["rtvm"]},
    "Mn": {"label": "Mn", "aliases": ["mn"]},
    "Mw": {"label": "Mw", "aliases": ["mw"]},
    "PDI": {"label": "PDI (Mw/Mn)", "aliases": ["pdi"]},
}

SAMPLE_ALIASES = ["sample", "샘플", "샘플명", "시료", "시료명"]


def _normalize(text: str) -> str:
    """비교를 위해 영숫자만 남기고 소문자로 변환."""
    return re.sub(r"[^0-9a-zA-Z가-힣]", "", str(text)).lower()


@dataclass
class LoadResult:
    raw: pd.DataFrame  # 원본에서 읽은 그대로 (정규화된 컬럼명 포함)
    averaged: pd.DataFrame  # 샘플별 평균 (index=샘플명, columns=item code)
    counts: pd.DataFrame  # 샘플별 반복측정 횟수 (item code 별)
    item_codes: list[str] = field(default_factory=list)


def _guess_column_map(columns: list[str]) -> dict[str, str]:
    """헤더 문자열을 보고 샘플/항목 컬럼을 자동으로 추정한다."""
    mapping: dict[str, str] = {}
    normalized = {col: _normalize(col) for col in columns}

    for col, norm in normalized.items():
        if any(norm.startswith(_normalize(a)) for a in SAMPLE_ALIASES):
            mapping.setdefault("sample", col)
            break

    for code, info in ITEM_DEFS.items():
        for col, norm in normalized.items():
            if col in mapping.values():
                continue
            if any(norm.startswith(_normalize(a)) for a in info["aliases"]):
                mapping[code] = col
                break
    return mapping


def load_raw_data(
    path: str,
    sheet_name: str | int = 0,
    column_map: dict[str, str] | None = None,
) -> LoadResult:
    """엑셀 raw data를 읽어 샘플별 평균 데이터로 정리한다.

    Args:
        path: 엑셀 파일 경로.
        sheet_name: 시트명 또는 인덱스 (기본: 첫 번째 시트).
        column_map: {"sample": "샘플명", "TSC": "TSC(%)", ...} 형태로
            컬럼명을 직접 지정하고 싶을 때 사용. 지정하지 않은 항목은
            헤더 이름으로 자동 추정한다.
    """
    df = pd.read_excel(path, sheet_name=sheet_name)
    df.columns = [str(c).strip() for c in df.columns]

    guessed = _guess_column_map(list(df.columns))
    if column_map:
        guessed.update({k: v for k, v in column_map.items() if v})

    if "sample" not in guessed:
        raise ValueError(
            "샘플명 컬럼을 찾을 수 없습니다. config의 column_map에 "
            "{'sample': '실제 컬럼명'} 형태로 지정해 주세요. "
            f"현재 컬럼: {list(df.columns)}"
        )

    item_codes = [code for code in ITEM_DEFS if code in guessed]
    if not item_codes:
        raise ValueError(
            "TSC / RTVM / Mn / Mw / PDI 중 어떤 항목 컬럼도 찾지 못했습니다. "
            f"현재 컬럼: {list(df.columns)}"
        )

    rename = {guessed["sample"]: "sample"}
    rename.update({guessed[code]: code for code in item_codes})
    tidy = df[[guessed["sample"], *[guessed[c] for c in item_codes]]].rename(columns=rename)

    tidy["sample"] = tidy["sample"].astype(str).str.strip()
    tidy = tidy[tidy["sample"] != ""]
    for code in item_codes:
        tidy[code] = pd.to_numeric(tidy[code], errors="coerce")

    averaged = tidy.groupby("sample", sort=False)[item_codes].mean()
    counts = tidy.groupby("sample", sort=False)[item_codes].count()

    return LoadResult(raw=tidy, averaged=averaged, counts=counts, item_codes=item_codes)
