"""raw data 로딩 -> 정리/비교 -> 엑셀 보고서 생성까지의 전체 파이프라인."""
from __future__ import annotations

from dataclasses import dataclass

from .data_loader import LoadResult, load_raw_data
from .excel_report import write_report
from .summarizer import SummaryResult, build_summary


@dataclass
class RunConfig:
    raw_data_path: str
    reference: str
    samples: list[str]
    output_path: str = "output/report.xlsx"
    sheet_name: str | int = 0
    column_map: dict[str, str] | None = None


def load(config: RunConfig) -> LoadResult:
    return load_raw_data(config.raw_data_path, sheet_name=config.sheet_name, column_map=config.column_map)


def summarize(load_result: LoadResult, config: RunConfig) -> SummaryResult:
    return build_summary(load_result, reference=config.reference, samples=config.samples)


def run(config: RunConfig) -> SummaryResult:
    """전체 파이프라인을 실행하고 엑셀 보고서를 저장한다."""
    load_result = load(config)
    summary = summarize(load_result, config)
    write_report(summary, config.output_path)
    return summary
