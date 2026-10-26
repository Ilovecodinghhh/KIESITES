# Literature-normalized parameter version

本版本沿用手稿月趋势/年谐波、源复向量扣除、振幅比及多汇反演；不新增模型项。所有概率宽度按1σ明确记录。

| 参数 | 修正前 | 修正后 | 证据与限制 |
|---|---|---|---|
| 湿地源δ13C均值/σ | −62 / 5‰ | −62.1 / 0.7‰ | Riddell-Young 2025 SI Table S4湿地均值与1σ；统一应用三源区仍是情景映射，不代表局地源实测。 |
| SH/T源δD σ | 15‰ | 15/1.96=7.653061‰ | Douglas 2021 §2.4、Table 1：均值95%CI；用正态近似转换，非作者直接给出的标准差。 |
| NH源δD σ | 10‰ | 10/1.96=5.102041‰ | 同上。源均值−301/−301/−374‰保持。 |
| OH氘KIE σ | 0.01 | 0.009 | Saueressig 2001：1.294±0.018，2σ，296 K。 |
| Cl碳KIE σ | 0.005 | 0.001 | Crowley et al. 1999摘要明确1.066±0.002（2σ），298 K，独立确认Saueressig 1995；σ=.002/2。 |
| Cl氘KIE σ | 0.05 | 0.0205 | Saueressig 1996 Table B：1.508±0.041，2σ，296 K。 |

不能把不同来源的区域均值置信度、实验室测量误差直接解释为已验证的站点自然变异。这里将文献归一化后的宽度用于同一OSSE结构，仍是条件性假设。

## 明确保留的情景假设

- 年源强归一化580±50 Tg/年，三区域B/C宽度各为绝对系数20%；不伪称精确文献1σ。B/C中心由Li本地NetCDF派生，前轮已复算。
- 汇比例OH=.84、Cl=.035、soil=.06、strat=.065；σ=.04/.01/.02，平流层为余项。部分中心值有文献数量级支持，站点有效性与精确σ未认证。
- 输送默认权重零，实际由既有28格指定；σ_NH=.02、σ_T=.1、延迟2.8月且σ=.5月。均为情景设置。
- 固定土壤KIE1.022/1.066、平流层KIE1.013/1.16及大气δ13C/δD=−47.3/−86‰保持原计算值，作为原模型固定假设；缺失的不确定性不宣称为零。
- A/B仍为1.0039/1.0054两个固定点假设，未传播实验室假设自身的误差。
- O基准来自各站月残差协方差，不是仪器精度；月份独立噪声假设保持，未新增漂移模型。
- 2%、5%及此前放宽配置是OSSE条件目标，没有新增可达性证据。

## 比较设计

每站两参数版本×四配置。基准四组倍率均1；全部2%；全部5%；放宽配置SPO=.05/.125/.075/.05、CGO=.075/.16/.075/.05（S/L/T/O）。不搜索新配置。

seed=2026102602；phase0为校准、phase1为独立验证；每格/每真值4000次校准、10000次验证。每版每配置均覆盖相同28格、A/B两方向。版本间使用相同标准化随机数，但均值与参考宽度修正会同时改变隐藏真值分布和辅助估计误差；因此不是只替换反演器的试验。同一参数版本内隐藏真值分布不随信息缩放改变。源极端格保持±2个本版本参考宽度，汇极端格不变。

校准、选择区间算法与80%正确率/5%误判率/95%覆盖率/±0.00015原始均值偏差判据不变；保留原每站64设计比较预算（本轮每站8版本-配置组合），避免小批次放松置信界。新校准全部冻结后才验证；无失败重试、无中心平移。偏差区间仍为t近似。上轮通过不保证本轮新样本一定通过。

## 引用

- Riddell-Young et al. (2025), [论文](https://doi.org/10.1073/pnas.2516543122)，[本地SI Table S4](../../../../ImportantReferences/Riddell-Young2025PNAS_SI/Riddell-Young2025PNAS_SI.md)。
- Douglas et al. (2021), [§2.4/Table 1](https://bg.copernicus.org/articles/18/3505/2021/)，[本地原文](../../../../ImportantReferences/Douglas2021EGU/Douglas2021EGU.md)。
- Saueressig et al. (2001), [原论文](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2000JD000120)。
- Crowley et al. (1999), Carbon kinetic isotope effect in the reaction CH4+Cl: a relative rate study using FTIR spectroscopy, Chemical Physics Letters 303, 268–274, [DOI 10.1016/S0009-2614(99)00243-2](https://doi.org/10.1016/S0009-2614(99)00243-2)。检索摘要明确2σ，出版商全文本轮403；不声称检查全文。
- Saueressig et al. (1996), [原PDF Table B](https://yorkspace.library.yorku.ca/server/api/core/bitstreams/482350d3-1fa2-4b7e-b20d-4e9496d6f0b8/content)。
- 其余项目的来源缺口见[上一轮逐项审计](../osse_relaxed_constraints/PARAMETER_PROVENANCE.md)。
