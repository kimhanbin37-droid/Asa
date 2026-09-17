"""샘플별 평균 데이터를 기준 샘플과 비교 샘플 표로 정리."""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from .data_loader import ITEM_DEFS, LoadResult


@dataclass
class SummaryResult:
    reference: str
    compare_samples: list[str]
    item_labels: list[str]
    organized: pd.DataFrame  # index=항목 라벨, columns=[기준, 비교샘플...]
    counts: pd.DataFrame  # index=항목 라벨, columns=[기준, 비교샘플...] (반복측정 n)
    comparison: dict[str, pd.DataFrame] = field(default_factory=dict)  # 샘플별 값/차이/차이(%)


def build_summary(load_result: LoadResult, reference: str, samples: list[str]) -> SummaryResult:
    """기준 샘플 + 비교 샘플들에 대한 정리표/비교표를 생성한다."""
    compare_samples = [s for s in samples if s != reference]
    all_samples = [reference, *compare_samples]

    known = set(load_result.averaged.index)
    missing = [s for s in all_samples if s not in known]
    if missing:
        raise ValueError(
            f"raw data에서 다음 샘플명을 찾을 수 없습니다: {missing}. "
            f"raw data에 있는 샘플명: {list(known)}"
        )

    item_codes = load_result.item_codes
    item_labels = [ITEM_DEFS[c]["label"] for c in item_codes]

    organized = load_result.averaged.loc[all_samples, item_codes].T
    organized.index = item_labels
    organized.columns = all_samples

    counts = load_result.counts.loc[all_samples, item_codes].T
    counts.index = item_labels
    counts.columns = all_samples

    comparison: dict[str, pd.DataFrame] = {}
    ref_vals = organized[reference]
    for sample in compare_samples:
        vals = organized[sample]
        diff = vals - ref_vals
        pct = (diff / ref_vals.replace(0, pd.NA)) * 100
        pct = pct.replace([float("inf"), float("-inf")], pd.NA)
        comparison[sample] = pd.DataFrame(
            {"값": vals, "기준 대비 차이": diff, "기준 대비 차이(%)": pct},
            index=item_labels,
        )

    return SummaryResult(
        reference=reference,
        compare_samples=compare_samples,
        item_labels=item_labels,
        organized=organized,
        counts=counts,
        comparison=comparison,
    )
