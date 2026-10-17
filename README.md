# cyril-go-kart-data

Cyril 的卡丁车 GPS / 圈速数据。原始记录来自 RaceBobo（[carrot.racebobo.cn](https://carrot.racebobo.cn)），按赛道与场次分开存放。

Karting GPS and lap data for driver Cyril33. Raw logs come from RaceBobo. Tracks, sessions, and analysis live in separate trees.

VBO 字段说明见 [docs/vbo_format.md](docs/vbo_format.md)。

## 目录 / Layout

```
tracks/<track_id>/          赛道定义：计时线、弯道米标、备注
raw/<track_id>/<date>/      原始 RaceBobo VBO（文件名用开始时刻）
sessions/<track_id>/<id>/   一场的 meta.json、laps.csv、segments.csv
analysis/<date>_<topic>/    对比说明与图
tools/                      分析脚本（可后补）
docs/vbo_format.md          VBO 读法
```

当前内容：

- 赛道 `tracks/foshan_p1/`（佛山P1国际赛车场）
- 2026-10-17 两场：`15:17:37`（E）与 `16:04:10`（F）
- 对比：`analysis/2026-10-17_e_vs_f/`
- 当天脚本原样放在 `tools/analysis_1017/`（路径仍是当时的绝对路径，没有改成仓库内路径）

## 增加一条赛道 / Add a track

1. 新建 `tracks/<track_id>/`。
2. 写 `track.json`：名称、计时线经纬度与过线航向、弯道「距计时线米数」区间。官方没有公布的扇区线标成 estimate，不要填未核对过的坐标。
3. 写 `notes.md`（场地、车辆、数据来源）。有赛道图再放 `map.png`；没有就先不放文件。

## 增加一场 / Add a session

1. 把 VBO 放到 `raw/<track_id>/<YYYY-MM-DD>/<HH_MM_SS>.vbo`。用北京时间的开始时刻命名，不要保留中文原名。
2. 新建 `sessions/<track_id>/<YYYY-MM-DD_HH-MM>/`。
3. 写 `meta.json`：`track`、开始时间、`timezone`（`Asia/Shanghai`）、`source`、场地公布最快圈、租赁车说明。
4. 有单圈表就放 `laps.csv`。没有就不要造表，在 `meta.json` 里写明省略原因。
5. 有分段表就放 `segments.csv`。
