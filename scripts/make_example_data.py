#!/usr/bin/env python3
"""예시 raw data 엑셀 파일 생성 (data/raw_data_example.xlsx)."""
import sys
from pathlib import Path

import pandas as pd

ROWS = [
    # 샘플명, TSC(%), RTVM(cP), Mn, Mw, PDI  -- 샘플당 2회 반복 측정
    ("REF", 45.2, 1200, 12000, 24000, 2.00),
    ("REF", 45.4, 1180, 11900, 23800, 2.00),
    ("A-01", 46.1, 1350, 13500, 28000, 2.07),
    ("A-01", 45.9, 1320, 13400, 27600, 2.06),
    ("A-02", 44.5, 1050, 11200, 21800, 1.95),
    ("A-02", 44.7, 1080, 11300, 22000, 1.95),
    ("A-03", 45.0, 1210, 12100, 24300, 2.01),
    ("A-03", 45.1, 1230, 12200, 24500, 2.01),
]

COLUMNS = ["샘플명", "TSC(%)", "RTVM(cP)", "Mn", "Mw", "PDI"]


def main() -> None:
    out_path = Path(__file__).parent.parent / "data" / "raw_data_example.xlsx"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(ROWS, columns=COLUMNS)
    df.to_excel(out_path, index=False, sheet_name="Raw")
    print(f"생성됨: {out_path}")


if __name__ == "__main__":
    sys.exit(main())
