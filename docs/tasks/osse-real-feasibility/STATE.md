# OSSE现实资料可达性核查

- 状态：完成当前资料与已通过条件的对照；尚未证明现实可达性。
- 结论：SPO/CGO当前月残差σ分别为目标16/13.33倍；S/L引用宽度比目标更宽，部分源汇和全部T误差仍无匹配站点约束。不能由条件OSSE推断真实观测支持A/B。
- 使用karpathy-guidelines；没有改变科学模型、筛选规则或重新运行OSSE。CodeGraph因node不可用，直接核查现有代码/结果。
- 输出：experiments/KIE_sites/results/osse_real_feasibility/REPORT.md、evidence.json；复算脚本docs/tasks/osse-real-feasibility/check.py。
- 执行：OPENBLAS_NUM_THREADS=1 python3 docs/tasks/osse-real-feasibility/check.py。联合趋势/谐波、协方差n−4；无随机数；记录输入SHA256。初次脚本误用pandas row.T为字段，已改为row['T']后成功。
- 检查：复算残差与ABSOLUTE_ERRORS一致；验证选定配置passes及有限集合最大通过O。文档/脚本/JSON UTF-8无BOM与相对文件链接检查通过。
- 下一步：保持工作流，核实原始同位素配对、QC/背景筛选和衔接，复算O；寻找独立站点S/L/T辅助约束。未找到证据的误差继续明确为情景假设。
- 未验证：新观测接入、穷尽全球最新技术、完整原始背景筛选及同烧瓶审计、时间相关和模型结构误差、A/B自身实验室误差传播。

## 本轮可视化

- 新增plot.py，读取evidence.json并校验3个输入SHA256及残差倍率；使用SciencePlots，英文标注。
- 命令：PYTHONPATH=/tmp/osse-scienceplots OPENBLAS_NUM_THREADS=1 python3 docs/tasks/osse-real-feasibility/plot.py。成功生成feasibility_gap.png/pdf/svg。
- 已查看PNG并修正对数轴标签重叠与页脚间距。未重跑OSSE或修改数据。
