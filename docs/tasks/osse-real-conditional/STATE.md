# 真实观测的条件性A/B分析

- 状态：完成。
- 结果：默认local中心两站仅B相容；25主情景SPO为A/B/both/neither=3/7/1/14，CGO=7/7/2/9；不跨情景稳健。
- 配置：事先确定SPO all_x1.25、CGO all_x1.5；直接复用冻结selection宽度，未重新校准或缩放真实值。
- 输出：experiments/KIE_sites/results/osse_real_conditional下REPORT.md、results.json、scenarios.csv、conditional_real_ab.png/pdf/svg；脚本analysis/osse_real_conditional.py。
- 命令：PYTHONPATH=/tmp/osse-scienceplots OPENBLAS_NUM_THREADS=1 python3 experiments/KIE_sites/analysis/osse_real_conditional.py。无随机数。
- 验证：输入SHA256、已通过配置、冻结与确认一致、56行输出、独立分类检查、真实数组未修改均通过；UTF-8无BOM及文档链接通过，PNG已检查。
- 限制：部分真实扣源D幅度低于OSSE固定锚点；迁移后的区间覆盖率未经验证。中心假设与误差改善均非本站已实现事实；未重新校准，不声称真实选择B。
- 下一步：独立约束辅助中心和误差，检查校准信号幅度的适用性。

## 版本记录

- 已准备v0.1结果检查点及VERSION.md、MANIFEST.json；提交仅限本轮结果及必要依赖，无远程推送。
- 本轮检查结果输入哈希与56行数据一致；不重跑科学计算。
