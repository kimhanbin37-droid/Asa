# 실험 Raw Data 자동 정리 및 시각화 프로그램

실험 Raw data(TSC, RTVM, GPC[Mn, Mw, PDI])를 엑셀로 입력받아,
지정한 **기준 샘플**과 **비교 샘플**을 자동으로 정리하고 표/차트가 포함된
엑셀 보고서를 생성하는 프로그램입니다.

## 주요 기능

- 엑셀 raw data에서 샘플별 반복 측정값을 자동으로 평균 처리
- 기준 샘플 대비 각 비교 샘플의 값/차이/차이(%) 자동 계산
- 정리표, 기준대비 비교표, 항목별 비교 막대차트가 담긴 엑셀 보고서 자동 생성
- CLI(설정 파일) 방식과 GUI(마우스 클릭) 방식 모두 지원

## 설치

```bash
pip install -r requirements.txt
```

## 입력 데이터 형식 (Raw Data)

엑셀 파일의 한 시트에 **샘플명 컬럼 + 측정 항목 컬럼**들이 있는 형태입니다.
같은 샘플명이 여러 행에 걸쳐 있으면 반복 측정으로 간주하여 자동 평균됩니다.

| 샘플명 | TSC(%) | RTVM(cP) | Mn    | Mw    | PDI  |
|--------|--------|----------|-------|-------|------|
| REF    | 45.2   | 1200     | 12000 | 24000 | 2.00 |
| REF    | 45.4   | 1180     | 11900 | 23800 | 2.00 |
| A-01   | 46.1   | 1350     | 13500 | 28000 | 2.07 |
| A-01   | 45.9   | 1320     | 13400 | 27600 | 2.06 |

- 예시 파일: `data/raw_data_example.xlsx` (`python scripts/make_example_data.py` 로 재생성 가능)
- 필요한 항목(TSC / RTVM / Mn / Mw / PDI)만 있으면 되고, 없는 항목은 자동으로 제외됩니다.
- 컬럼명은 "TSC", "RTVM", "Mn", "Mw", "PDI", "샘플/Sample" 로 시작하는 이름을 자동 인식합니다.
  회사/장비마다 헤더가 다르면 `config.yaml`의 `column_map`으로 직접 매핑할 수 있습니다.

## 사용법 1: CLI (설정 파일 방식, 반복 작업에 추천)

1. `config.example.yaml`을 `config.yaml`로 복사 후 값을 수정합니다.

   ```yaml
   raw_data_path: data/raw_data_example.xlsx
   reference: REF
   samples:
     - A-01
     - A-02
     - A-03
   output_path: output/report.xlsx
   ```

2. 실행합니다.

   ```bash
   python main.py --config config.yaml
   ```

CLI 인자만으로 바로 실행할 수도 있습니다.

```bash
python main.py --raw data/raw_data_example.xlsx \
  --reference REF --samples A-01,A-02,A-03 \
  --output output/report.xlsx
```

## 사용법 2: GUI (마우스로 파일/샘플 선택)

```bash
python gui_main.py
```

1. Raw data 엑셀 파일을 선택하면 샘플명이 자동으로 추출되어 목록에 표시됩니다.
2. 기준 샘플과 비교할 샘플(들)을 선택합니다.
3. 저장 위치를 지정하고 "보고서 생성" 버튼을 누르면 완료됩니다.

> GUI는 Python 표준 라이브러리 Tkinter를 사용합니다. Windows/Mac 공식 Python
> 설치본에는 기본 포함되어 있습니다. Linux에서 `tkinter`가 없다면
> `sudo apt install python3-tk` 등으로 설치해 주세요.

## 결과 보고서 구성

생성되는 엑셀 파일(`output/report.xlsx`)은 3개 시트로 구성됩니다.

1. **정리표** — 기준 샘플(강조 표시) + 비교 샘플들의 항목별 평균값과 반복 측정 횟수(n)
2. **기준대비 비교** — 비교 샘플별 값 / 기준 대비 차이 / 기준 대비 차이(%) (조건부 서식으로 색상 표시)
3. **차트** — 항목(TSC, RTVM, Mn, Mw, PDI)별 샘플 비교 막대차트 (엑셀 네이티브 차트로, 엑셀에서 직접 수정 가능)

## 프로젝트 구조

```
main.py                 CLI 진입점
gui_main.py             GUI 진입점
config.example.yaml     설정 파일 예시
data/                   예시 raw data
scripts/                예시 데이터 생성 스크립트
src/experiment_report/
  data_loader.py         raw data 엑셀 로딩 및 정규화
  summarizer.py          기준/비교 샘플 정리·비교표 계산
  excel_report.py        엑셀 보고서(표+차트) 생성
  pipeline.py            전체 파이프라인 연결
  cli.py                 CLI 인자/설정 처리
  gui.py                 Tkinter GUI
tests/                  자동화 테스트 (pytest)
```

## 테스트

```bash
pip install pytest
pytest tests/ -v
```
