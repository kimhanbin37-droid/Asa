#!/usr/bin/env python3
"""실험 Raw data 자동 정리 및 시각화 - GUI 진입점."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from experiment_report.gui import main  # noqa: E402

if __name__ == "__main__":
    main()
