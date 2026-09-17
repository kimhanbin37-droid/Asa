"""커맨드라인 진입점.

사용 예:
    python main.py --config config.yaml
    python main.py --raw data/raw.xlsx --reference REF --samples A-01,A-02 --output output/report.xlsx
"""
from __future__ import annotations

import argparse
import os
import sys

import yaml

from .pipeline import RunConfig, run


def _load_yaml_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_run_config(args: argparse.Namespace) -> RunConfig:
    file_cfg: dict = {}
    if args.config:
        file_cfg = _load_yaml_config(args.config)

    raw_data_path = args.raw or file_cfg.get("raw_data_path")
    reference = args.reference or file_cfg.get("reference")
    samples_arg = args.samples
    samples = (
        [s.strip() for s in samples_arg.split(",") if s.strip()]
        if samples_arg
        else file_cfg.get("samples", [])
    )
    output_path = args.output or file_cfg.get("output_path", "output/report.xlsx")
    sheet_name = args.sheet if args.sheet is not None else file_cfg.get("sheet_name", 0)
    column_map = file_cfg.get("column_map")

    if not raw_data_path:
        raise SystemExit("raw data 경로가 필요합니다 (--raw 또는 config의 raw_data_path).")
    if not reference:
        raise SystemExit("기준 샘플명이 필요합니다 (--reference 또는 config의 reference).")
    if not samples:
        raise SystemExit("비교할 샘플명이 필요합니다 (--samples 또는 config의 samples).")

    return RunConfig(
        raw_data_path=raw_data_path,
        reference=reference,
        samples=samples,
        output_path=output_path,
        sheet_name=sheet_name,
        column_map=column_map,
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="실험 Raw data 자동 정리 및 시각화")
    parser.add_argument("--config", help="설정 yaml 파일 경로")
    parser.add_argument("--raw", help="raw data 엑셀 파일 경로")
    parser.add_argument("--sheet", help="raw data 시트명/인덱스 (기본: 0)")
    parser.add_argument("--reference", help="기준 샘플명")
    parser.add_argument("--samples", help="비교할 샘플명 (쉼표로 구분, 기준 샘플은 자동 포함)")
    parser.add_argument("--output", help="출력 엑셀 파일 경로")
    args = parser.parse_args(argv)

    run_config = build_run_config(args)
    os.makedirs(os.path.dirname(run_config.output_path) or ".", exist_ok=True)
    summary = run(run_config)
    print(f"완료: {run_config.output_path}")
    print(f"  기준 샘플: {summary.reference}")
    print(f"  비교 샘플: {', '.join(summary.compare_samples)}")
    print(f"  정리 항목: {', '.join(summary.item_labels)}")


if __name__ == "__main__":
    main(sys.argv[1:])
