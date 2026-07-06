# 最终报告优化说明

生成时间：2026-07-07

---

## 一、训练曲线修复

### 问题诊断
原始 `scripts/plot_curves.py` 存在以下问题：
1. 直接使用第一个 seed 的 timesteps 作为 `all_ts`，未按 timestep 对齐不同 seed
2. 只按最小长度截断（`min_len`），丢弃了较长 seed 在尾部 timestep 的数据
3. 未处理不同 seed 在不同 timestep 有数据的情况
4. 无 n≥2 闸门保护，单个 seed 也会绘制 std 阴影，产生误导

### 实际数据情况
- DQN aggressive/seed_456：15 个 eval 点，其他 seed 有 14 个
- DQN baseline/seed_42：12 个 eval 点，其他 seed 有 10 个
- DQN balanced/seed_42, seed_123：14 个点，其他 seed 有 10 个
- PPO balanced/seed_42：仅 2 个 eval 点（提前终止于 t=10000）

### 修复方案
新增 `scripts/plot_curves_clean.py`：
1. 使用 pandas 按 timestep 对齐所有 seed（union grid）
2. 缺失值使用 NaN，不补 0
3. mean/std 使用 skipna=True
4. n≥2 闸门：有效 seed 数 < 2 时不绘制 std 阴影
5. 不画单个 seed 的浅色轨迹
6. 仅画 mean line + mean±std shading
7. linewidth=2, alpha=0.15, dpi=300

### 生成的 clean 图
- `figures_clean/training_curves_aggressive_clean.png`
- `figures_clean/training_curves_baseline_clean.png`
- `figures_clean/training_curves_balanced_clean.png`
- `figures_clean/training_curves_comfort_clean.png`
- `figures_clean/training_curves_conservative_clean.png`

### 检查报告
`run_logs/training_curves_clean_check.md` 记录了每个 reward 下各 seed 的 eval 点数、提前终止情况和 n_valid 统计。

---

## 二、新增最终结果对比图

新增 `scripts/plot_final_summary.py`，从 `final_average_ranking.csv` 读取数据生成：

1. **figures_clean/final_avg_success_collision.png**
   - 并列柱状图：各模型的 avg_success_rate 和 avg_collision_rate
   - 清晰显示 PPO aggressive 同时取得最高成功率和最低碰撞率

2. **figures_clean/final_lane_change_collision.png**
   - 双 y 轴图：avg_collision_rate（左轴）+ avg_mean_lc（右轴）
   - 突出 DQN baseline（68.07）和 DQN aggressive（66.59）的异常高变道次数

---

## 三、正文图表精选

最终正文保留 7 张图（从原来的 6 张 old 图扩展并精选）：

| 编号 | 文件 | 说明 |
|------|------|------|
| 图1 | figures_clean/training_curves_aggressive_clean.png | aggressive 训练曲线 |
| 图2 | figures_clean/training_curves_baseline_clean.png | baseline 训练曲线 |
| 图3 | figures/seed_variance_aggressive.png | Seed 方差箱线图 |
| 图4 | figures/reward_components_ppo.png | PPO 奖励分量 |
| 图5 | figures/reward_components_dqn.png | DQN 奖励分量 |
| 图6 | figures_clean/final_avg_success_collision.png | 成功率与碰撞率对比 |
| 图7 | figures_clean/final_lane_change_collision.png | 变道次数与碰撞率对比 |

**不再作为正文重点展示的图**：
- `training_curves_balanced.png` → 替换为 clean 版，保留在 figures_clean/ 供参考
- comfort、conservative 的训练曲线 → 保留在 figures_clean/
- balanced、comfort、conservative 的 seed 方差图 → 保留在 figures/

---

## 四、Word 表格修复

| 表号 | 修复内容 |
|------|---------|
| 表1 | 真实 Word 表格（Table Grid 样式），3列，表头加粗蓝底，五号字 |
| 表2 | 真实 Word 表格，7列，表头加粗蓝底，五号字，`allow_break_across_pages=False` |
| 表3 | 真实 Word 表格，8列，表头加粗蓝底，7.5pt 字，`allow_break_across_pages=False` |

所有表格：
- 无 Markdown 符号残留
- 无制表符伪表格
- 表头蓝色底纹 (#D9E2F3) + 加粗
- 表格居中
- 禁止跨页断行

---

## 五、图题修复

- 统一格式：`图N 描述`，宋体五号（9pt），居中，位于图片下方
- 每张图仅一条图题，无重复
- 图片宽度统一 14 cm

---

## 六、Markdown 残留清理

- Word 中：0 个 `####`、`**` 残留
- Markdown 中：`####` 已替换为 `###`（标准 Heading 3 语法）

---

## 七、语言表达优化

| 原文 | 修改后 |
|------|--------|
| "德国于 2017 年通过了全球首部自动驾驶伦理准则" | "部分国家已开始推进自动驾驶伦理和安全监管规则建设" |
| "真实部署通常要求 99.9999% 以上" | "真实道路部署对安全性的要求远高于仿真实验中的成功率水平" |
| 列举 Waymo/Tesla/百度/Mobileye 具体方案 | "北美企业...中国企业...欧洲企业" 宏观描述 |
| "ISO 34502" | "自动驾驶测试场景相关标准" |
| "5x10^{-4}" | "5×10^{-4}" |
| 新增训练曲线说明 | "按照 timestep 对各 seed 的评估结果进行重新对齐" |

---

## 八、Word 格式设置

| 项目 | 设置 |
|------|------|
| 纸张 | A4 (21.0 × 29.7 cm) |
| 页边距 | 上 2.54 cm，下 2.54 cm，左 2.8 cm，右 2.8 cm |
| 中文正文 | 宋体 |
| 英文/数字 | Times New Roman |
| 正文 | 小四（12pt），1.5 倍行距，首行缩进 2 字符 |
| 题目 | 黑体，三号（16pt），加粗，居中 |
| Heading 1 | 黑体，小三（15pt），加粗 |
| Heading 2 | 黑体，小四（12pt），加粗 |
| Heading 3 | 黑体，小四（12pt），加粗 |
| 页码 | 页脚居中 |
| 目录 | 未插入自动目录，但 Heading 1/2/3 样式已正确设置 |

---

## 九、完整性确认

- [x] 未重新训练模型
- [x] 未重新评估 OOD
- [x] 未修改实验数据
- [x] 未删除 logs、figures、run_logs
- [x] 所有结论来自 `final_average_ranking.csv` 等现有数据
- [x] 课程名称《模式识别与机器学习》
- [x] 报告中突出复杂工程问题求解能力
- [x] OccupancyGrid + MlpPolicy，不涉及 CNN 图像训练
- [x] Word 中已清理 Markdown 残留
- [x] Word 中使用真实表格（非制表符伪表格）
- [x] 已添加页码
- [x] 已使用真正的 Heading 1/2/3 样式
- [x] 图片居中，图题统一

---

## 十、仍需人工检查项

1. **字体渲染**：在 WPS 中确认中文宋体、英文 Times New Roman
2. **表格跨页**：确认表2和表3完整显示（已设 `allow_break_across_pages=False`）
3. **目录生成**：在 WPS 中"引用 → 目录"一键生成
4. **页码**：确认正文第1页起始页码
5. **图题与图片同页**：确认 7 张图片与图题均在同一页
6. **公式编号**：如需可在 WPS 中手动添加

---

## 十一、输出文件清单

| 文件 | 路径 | 说明 |
|------|------|------|
| 最终 Word | `final_submit/基于DQN与PPO的高速公路自主变道决策研究_最终提交版.docx` | 正式提交版 |
| 最终 Markdown | `docs/final_report_final.md` | 与 Word 一致 |
| Clean 训练曲线脚本 | `scripts/plot_curves_clean.py` | 新脚本 |
| 总结图脚本 | `scripts/plot_final_summary.py` | 新脚本 |
| Word 生成脚本 | `scripts/generate_final_report.py` | 最终版生成脚本 |
| Clean 图表目录 | `figures_clean/` | 7 张新图 |
| 曲线检查报告 | `run_logs/training_curves_clean_check.md` | 数据对齐详情 |
| Word 检查报告 | `run_logs/final_docx_review_before_fix.md` | 修复前检查 |
| 本优化说明 | `run_logs/final_report_optimization_notes.md` | 本文档 |
