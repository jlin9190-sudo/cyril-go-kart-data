# 佛山P1国际赛车场 / Foshan P1

- 赛道 id：`foshan_p1`。中文名：佛山P1国际赛车场。
- 车手：Cyril33。
- 数据来源：RaceBobo，站点 [carrot.racebobo.cn](https://carrot.racebobo.cn)。原始文件是 VBO，读法见 [docs/vbo_format.md](../../docs/vbo_format.md)。
- 车辆：租赁卡丁。不同场次的车况会变，不要把两场当成同一台车来比绝对圈速。
- 地图：`map_aerial.jpg` 是航拍；`map_corners.jpg` 是带 T1–T17 的官方示意图。弯号以示意图为准。

## 官方走向 / Official flow

按 `map_corners.jpg`（维修区画在图的上方）：

主直道在图上方。浅色条是维修区，右端 **Pit In** 驶入，左端 **Pit Out** 驶出，在 T1 之前汇入。主直道末端是 **T1 左发卡**，接着 T2、T3、T4、T5、T6、T7，到图左下的 T8，沿底部经过 T9，进入中部的 T10、T11、T12，再到底部的 T13、T14，沿右侧上行 T15、T16，由 **T17** 接回主直道。

示意图主直道上有一条绿色短线，还没有和 GPS 计时线对过，不要把它当成已经测过的计时线坐标。

On the schematic the lap is: main straight → T1 left hairpin → T2 through T16 → T17 back onto the main straight. Pit in is at the right end of that straight; pit out is at the left end and rejoins before T1.

## 弯号 / Corner numbers

官方弯号是 **T1–T17**。之后的分析都用这套名字。

2026-10-17 里的内部 T1–T8 是按 GPS 轨迹切出来的粗分区（8 个弯加 7 段直道），不是示意图上的弯号。两套编号不要混用，也不要把旧的米标套到同名的官方弯上。旧分区留在 `track.json` 的 `legacy_internal_corners_t1_t8`，只作历史记录。每个官方弯的 GPS 门以后再标。

计时线和扇区估计仍用原来的 GPS 工作值。扇区是估计，场地没有公布坐标。

Official labels are T1–T17. The earlier T1–T8 set was a coarser GPS partition and is superseded. Timing line and sector estimates are unchanged. Per-corner GPS gates are not set yet.
