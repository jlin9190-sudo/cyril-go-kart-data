# 佛山P1 2026-10-17 sessions E (15:17) and F (16:04)

Prior A/B/C/D VBO files were not on the box; comparisons to A/B/C/D use published
segment/corner/accel numbers from earlier reports (report_1001 / report_1001b).
Segment gates = same metre marks as analyze.py. Timing line = N22.875316 E113.266340 hdg 206.63.

Caveat: 直7 times vs B are not directly comparable (today's laps are shorter overall
~811-820 m vs B ~834 m). Use whole-lap deltas as ground truth.

## 本仓库里的文件 / Where the files went

- 图：`fig/`（`speed_vs_distance.png`、`line_corners.png`、`segment_delta.png`、`accel_vs_speed.png`）
- 分段表：`sessions/foshan_p1/2026-10-17_15-17/segments.csv`（原 `E_1017_lap_segment_metrics.csv`）、`sessions/foshan_p1/2026-10-17_16-04/segments.csv`（原 `F_1017_lap_segment_metrics.csv`）
- 单圈表：同目录 `laps.csv`，从分段表抽出的每圈一行
- 脚本：`tools/analysis_1017/`（`pipeline.py`、`retime.py`、`analyse2.py`、`final_stats.py`、`figs.py`）。按原样复制，里面的路径仍指向当时的 `/home/box/Downloads/…` 和 `/workspace/report_1017`，没有改到本仓库。
- `res.pkl` / `summ.pkl` 不在上传包里，这里没有放。
