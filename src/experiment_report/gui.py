"""간단한 Tkinter GUI.

엑셀 파일을 고르고, 자동으로 감지된 샘플명 중에서 기준 샘플/비교 샘플을
선택한 뒤 버튼 한 번으로 보고서를 생성한다.
"""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from .data_loader import load_raw_data
from .pipeline import RunConfig, run


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("실험 Raw Data 자동 정리 및 시각화")
        self.geometry("520x520")
        self.raw_path: str | None = None
        self.samples: list[str] = []
        self._build_widgets()

    def _build_widgets(self) -> None:
        pad = {"padx": 10, "pady": 6}

        frame_file = ttk.LabelFrame(self, text="1. Raw data 엑셀 선택")
        frame_file.pack(fill="x", **pad)
        self.file_label = ttk.Label(frame_file, text="(선택된 파일 없음)", foreground="#555")
        self.file_label.pack(side="left", padx=8, pady=8)
        ttk.Button(frame_file, text="파일 선택...", command=self._choose_file).pack(
            side="right", padx=8, pady=8
        )

        frame_ref = ttk.LabelFrame(self, text="2. 기준(Reference) 샘플")
        frame_ref.pack(fill="x", **pad)
        self.ref_combo = ttk.Combobox(frame_ref, state="readonly", values=[])
        self.ref_combo.pack(fill="x", padx=8, pady=8)

        frame_cmp = ttk.LabelFrame(self, text="3. 비교할 샘플 (여러 개 선택 가능)")
        frame_cmp.pack(fill="both", expand=True, **pad)
        self.cmp_list = tk.Listbox(frame_cmp, selectmode="extended", exportselection=False)
        self.cmp_list.pack(fill="both", expand=True, padx=8, pady=8)

        frame_out = ttk.LabelFrame(self, text="4. 결과 저장 위치")
        frame_out.pack(fill="x", **pad)
        self.output_var = tk.StringVar(value=os.path.join("output", "report.xlsx"))
        ttk.Entry(frame_out, textvariable=self.output_var).pack(
            side="left", fill="x", expand=True, padx=8, pady=8
        )
        ttk.Button(frame_out, text="변경...", command=self._choose_output).pack(
            side="right", padx=8, pady=8
        )

        ttk.Button(self, text="보고서 생성", command=self._generate).pack(pady=14)
        self.status = ttk.Label(self, text="", foreground="#0a6")
        self.status.pack()

    def _choose_file(self) -> None:
        path = filedialog.askopenfilename(
            title="Raw data 엑셀 파일 선택",
            filetypes=[("Excel files", "*.xlsx *.xls")],
        )
        if not path:
            return
        try:
            result = load_raw_data(path)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("파일을 읽을 수 없습니다", str(exc))
            return

        self.raw_path = path
        self.file_label.config(text=os.path.basename(path))
        samples = list(result.averaged.index)
        self.ref_combo.config(values=samples)
        if samples:
            self.ref_combo.current(0)
        self.cmp_list.delete(0, tk.END)
        for s in samples:
            self.cmp_list.insert(tk.END, s)

    def _choose_output(self) -> None:
        path = filedialog.asksaveasfilename(
            title="결과 저장 위치",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
        )
        if path:
            self.output_var.set(path)

    def _generate(self) -> None:
        if not self.raw_path:
            messagebox.showwarning("확인 필요", "먼저 raw data 엑셀 파일을 선택해 주세요.")
            return
        reference = self.ref_combo.get()
        if not reference:
            messagebox.showwarning("확인 필요", "기준 샘플을 선택해 주세요.")
            return
        selected = [self.cmp_list.get(i) for i in self.cmp_list.curselection()]
        if not selected:
            messagebox.showwarning("확인 필요", "비교할 샘플을 하나 이상 선택해 주세요.")
            return

        output_path = self.output_var.get().strip() or os.path.join("output", "report.xlsx")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)

        config = RunConfig(
            raw_data_path=self.raw_path,
            reference=reference,
            samples=selected,
            output_path=output_path,
        )
        try:
            run(config)
        except Exception as exc:  # noqa: BLE001
            messagebox.showerror("보고서 생성 실패", str(exc))
            return

        self.status.config(text=f"완료: {output_path}")
        messagebox.showinfo("완료", f"보고서가 생성되었습니다:\n{output_path}")


def main() -> None:
    App().mainloop()


if __name__ == "__main__":
    main()
