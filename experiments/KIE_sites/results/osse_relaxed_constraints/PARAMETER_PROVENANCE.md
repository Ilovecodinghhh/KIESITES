# OSSE 参数与误差来源审计

审计日期：2026-10-26。范围：ABSOLUTE_ERRORS.md 的全部20项辅助参数、SPO/CGO月度观测残差、正反演固定常数及缩放/抽样假设。不是整个仓库所有历史实验的文献审计。

**结论：当前输入不是“全部由文献支持的站点参数及1σ误差”。部分中心值有直接依据，部分由数据拟合得到；多项宽度是实验设定，且Douglas源δD存在95%置信区间被当作1σ使用的口径不一致。现有通过结果只能保留为当前假设下的条件性辨别能力。** 本次不改科学参数、不重跑OSSE、不以补上相关引用代替验证。

## 判定原则

- 直接支持：原文数值、单位、统计定义及使用条件相符。
- 数据派生：可以从有来源的数据计算，但不是论文直接给出的参数。
- 部分支持：数量级或中心值有依据，统计定义、区域适用性或具体选择未获支持。
- 情景设定/未核实：在本次查阅材料中未找到该精确值及其1σ解释的直接依据。不是断言全世界不存在相关文献。
- 文献中的全球平均、生态系统端点或实验室296 K结果，不自动成为SPO/CGO背景筛选空气的有效参数。

## 全部辅助参数逐项审计

| 参数 | 当前参考值；代码宽度 | 中心值依据 | 宽度与适用性判定 |
|---|---|---|---|
| d13_source | −62‰；5‰ | Riddell-Young 2025 主文Table 1微生物源−62.0±1.3‰；SI Table S4湿地−62.1±0.7‰，均标1σ [R1] | −62是近似参考；**5‰不是该表给出的1σ**。统一用于三源区属简化；未核实精确5‰依据。 |
| q_annual | 580；50 Tg/年 | Saunois 2025 给出2010–2019全球自上而下575 [553–586] Tg/年 [R2] | 支持量级，不直接支持580±50的1σ。范围是模型集合最小/最大，不是高斯σ。与2005–2010站点时段也不完全一致。 |
| B_SH | 0.0044；0.00088 Tg/月 | Li本地NetCDF的2005–2010月气候态谐波重算 [R3] | 中心可复现；20%×绝对系数未由集合传播验证。 |
| C_SH | 0.0776；0.01552 Tg/月 | 同上 | 同上。 |
| B_T | 0.2729；0.05458 Tg/月 | 同上 | 同上。 |
| C_T | −0.5848；0.11696 Tg/月 | 同上 | 同上。 |
| B_NH | −0.1985；0.03970 Tg/月 | 同上，实际选60–90°N的NH_high | 同上；不是整个北半球源的观测约束。 |
| C_NH | −1.2436；0.24872 Tg/月 | 同上 | 同上。 |
| dD_SH | −301‰；15‰ | Douglas Table 1的<30°N湿地类别 [R4] | **15‰被定义为均值95%CI的不确定性，不是明示1σ**；映射到SH_extra是模型选择。 |
| dD_T | −301‰；15‰ | Douglas Table 1，同上 | 同样存在95%CI→代码1σ口径问题。 |
| dD_NH | −374‰；10‰ | Douglas Table 1 >60°N湿地 [R4] | 中心与NH_high匹配；10‰的95%CI不能直接标成文献1σ。 |
| f_oh | 0.84；0.04 | Riddell-Young SI S3为0.835 [R1] | 0.84是调整后的闭合分配；0.04未找到精确1σ依据，且全球汇份额并非站点有效份额。 |
| f_cl | 0.035；0.01 | Riddell-Young SI S3有0.035 [R1] | 中心有表格依据；0.01未找到精确1σ依据。 |
| f_soil | 0.06；0.02 | Riddell-Young SI S3为0.07 [R1] | 当前0.06为选择值而非逐字沿用；0.02未找到精确1σ依据。 |
| alpha_d_oh | 1.294；0.01 | Saueressig 2001：1.294±0.018，2σ，296 K [R5] | 对应实验1σ=0.009；代码0.01可视作近似，但并非原文精确σ。站点有效温度与代表性未验证。 |
| alpha_c_cl | 1.066；0.005 | Saueressig 1995：297 K为1.066±0.002 [R6] | 中心直接支持；代码0.005的精确1σ依据未核实，不能直接冒充实验误差。 |
| alpha_d_cl | 1.508；0.05 | Saueressig 1996 Table B：296 K为1.508±0.041，2σ [R7] | 实验1σ=0.0205；代码0.05是更宽设定，非原文1σ。 |
| w_nh | 默认0；0.02 | 实际被28格情景覆盖：主格0或0.04/0.06/0.08/0.10 | **情景参数**；默认0不代表各格真实权重都为0；0.02无站点实测σ支持。 |
| w_trop | 默认0；0.10 | 主格0/0.1/0.2/0.3/0.4/0.5 | **情景参数**；0.10无站点实测σ支持。 |
| lag_months | 2.8月；0.5月 | 旧phase6注释用简化交换响应估算约2.8月 | **近似/情景设定**；不是站点输送诊断，0.5月未找到观测σ依据。仅作用于NH响应。 |

代码证据：[core参数和widths](../../analysis/osse_manuscript_core.py)、[原phase6常数](../../analysis/phase6_phasor.py)、[实际抽样与缩放](../../analysis/osse_manuscript_validation.py)。phase6中“Li2026 ensemble spread”的注释不足以证明各B/C独立20%标准差。

## 统计口径问题的影响

Douglas正文§2.4明确将同位素源签名不确定性定义为源类别均值的95%置信区间；Table 1列出15、15、10‰。当前代码把相同数值作为辅助估计误差高斯σ，同时作为隐藏真值提议分布的尺度。不能只改表头宣称已对齐文献。

若仅按正态近似把95%CI半宽除以1.96，三项参考σ约为7.65、7.65、5.10‰，而非15、15、10‰；但该转换仍不证明类别均值不确定性可以代表站点源条件分布。此前图中的绝对σ是代码实际值，算术没有错；它们缺少同等意义的文献认证。任何改动都需形成新版本并重新校准/验证，不能沿用旧通过率。

## 两站观测数据和O组

- δ13C原始事件文件头直接给出 Michel et al. 2023、版本2023-09-21、DOI 10.15138/9p89-1x02 [R8]。
- δD来自本地Riddell-Young数据包的cgo/spo原始文件，论文数据声明对应NOAA 10.15138/setb-jy31 [R9]。本次验证本地处理链，未完成远端发布文件的校验和同一性核对。
- 实际重跑既有读取和月配对函数（不写原结果）：SPO 33个月、CGO 29个月；年月完全相同；δ13C/δD月均最大差≤0.0000501‰，与CSV四位小数舍入一致。
- 重算月残差σ：SPO为0.0724138723/2.92551372‰；CGO为0.0957617888/2.50770074‰（碳/氘）。这是数据派生值，非文献仪器精度。
- 乘O=0.05后：SPO为0.00362069361/0.146275686‰；CGO为0.00478808944/0.125385037‰。**5%及上述目标精度没有被文献证明可达。**
- 当前phase1按月配对，不能据此宣称逐瓶严格同时配对。δ13C仅检查拒绝标志第一位；MBL站点标记不等于逐事件气象背景筛选已经完成。两站δD选择INSTAAR原始序列，读取函数未施加显式跨实验室偏移；README关于全体均已统一到MPI尺度的文字不能替代处理链证据。是否上游已校正还需核对原发布包。
- OSSE各月噪声独立、两同位素保留残差协方差，不含独立建模的漂移或时间相关误差。这些是模拟假设，非该数据来源自动支持的性质。

## 表外固定值与遗漏的不确定性

| 值 | 核查结果 |
|---|---|
| A=1.0039、B=1.0054 | 有实验依据 [R5,R10]，但原测量有误差：A±0.0004、B±0.0009（2σ，见R5比较）。当前仅测试固定点假设，不是对两篇文献完整概率分布的辨别。 |
| 大气δ13C=−47.3‰ | Riddell-Young主文Table 1出现该全球值 [R1]；固定映射到两站不同年代仍属近似。 |
| 大气δD=−86‰ | 当前代码有值；本次未核实精确来源及其站点/时段适用性。Riddell-Young表中为−78.4‰，不能直接引用其表支持−86。 |
| 土壤碳KIE=1.022 | 在相关土壤研究范围内，但本次未从对应原始研究核实“固定全球值1.022”的直接支持；Snover 2000报告的两个生态系统碳值为1.0173与1.0181 [R11]。 |
| 土壤氘KIE=1.066 | Snover 2000森林土壤端点有直接依据（±0.007），非全球统一无误差值 [R11]。当前固定会遗漏生态系统差异。 |
| 平流层碳/氘KIE=1.013/1.16 | 手稿称有效近似，但未找到两者作为当前站点整体平流层汇参数的直接推导。1.013也是R5中O(1D)单反应碳KIE，不能以此证明整体平流层等效值。Riddell-Young SI值为1.003/1.179 [R1]。 |
| 平流层份额0.065 | 1−OH−Cl−soil的闭合余项，非独立测量；随其余三项联动。 |
| 站点D汇振幅 | 从真实月序列与名义源修正推导后固定；属于数据驱动锚点，不是独立真值验证。 |

## 所有缩放值与试验规则

SPO S/L/T/O=.05/.125/.075/.05，CGO=.075/.16/.075/.05：全部为OSSE候选配置中经当前模拟验证的条件性目标，**不是文献报告的现状σ，也不是已证明能实现的观测方案**。绝对数值仍由原宽度相乘所得。

隐藏真值±2参考宽度截断高斯、辅助误差高斯且投影前各参数独立、物理单纯形投影、输送网格和压力格，以及80%正确率/5%误判/95%覆盖/±0.00015偏差门槛，均为本研究试验设计选择。单纯形是物理可行性处理，不等于这些参数的联合概率分布经过文献验证。

## 已执行验证与证据边界

1. 本地Li NetCDF独立重做2005–2010三源区谐波：所有均值和B/C与JSON差<5.01e-5 Tg/月。文件单位kg CH4 month-1，时间注释支持Jan2000=1；文件只有均值场，未提供本轮可传播的集合维。
2. 从本地原始事件重新生成两站月均：上述舍入精度内一致，并重算残差。
3. 输入与计算代码SHA-256见[input_checks.json](../../../../docs/tasks/osse-parameter-provenance/input_checks.json)。验证脚本[verify_inputs.py](../../../../docs/tasks/osse-parameter-provenance/verify_inputs.py)。运行命令：PASS: three source bands and two site monthly series reproduced within rounding; input hashes recorded.。h5py仅安装于临时目录，未改项目依赖。
4. 读取ImportantReferences中的原文Markdown，核对在线原始论文摘要/正文或机构存档。Li Zenodo以及NOAA DOI落地页本轮web工具无法打开，故不声称已验证远端文件身份或Li最终出版状态。
5. 未改科学代码、未覆盖原始数据/模拟NPZ/图像；未重新认证任何配置。当前图与通过率须与本审计一起阅读。

## 引用及定位

- [R1] Riddell-Young et al. (2025), Microbial driver of 2006–2023 CH4 growth indicated by trends in atmospheric δD-CH4 and δ13C-CH4. [论文DOI](https://doi.org/10.1073/pnas.2516543122)。本次证据为[本地主文Table 1](../../../../ImportantReferences/Riddell-Young2025PNAS/Riddell-Young2025PNAS.md)和[SI Tables S3/S4](../../../../ImportantReferences/Riddell-Young2025PNAS_SI/Riddell-Young2025PNAS_SI.md)，SI Markdown行70–76。
- [R2] Saunois et al. (2025), Global Methane Budget 2000–2020, ESSD 17, 1873–1958. [正文](https://essd.copernicus.org/articles/17/1873/2025/)，摘要及Table 3；575 [553–586]为2010–2019自上而下估计。
- [R3] Li et al. (2026), Global natural wetland methane emissions (2000–2025). [本地手稿](../../../../ImportantReferences/Li2026ESSD/Li2026ESSD.md)，§2与数据声明行225；[声明的数据DOI](https://doi.org/10.5281/zenodo.18870108)。本次复算[本地数据文件](../../../../ImportantReferences/Li2026ESSD_DS.nc)，未将文件名ESSD当作最终发表证明。
- [R4] Douglas et al. (2021), Geographic variability in freshwater methane hydrogen isotope ratios and its implications for global isotopic source signatures. Biogeosciences 18, 3505–3527. [论文](https://bg.copernicus.org/articles/18/3505/2021/)；[本地原文](../../../../ImportantReferences/Douglas2021EGU/Douglas2021EGU.md)行111–114，§2.4及Table 1。文件夹EGU不代表本文只是会议摘要。
- [R5] Saueressig et al. (2001), Carbon 13 and D kinetic isotope effects in the reactions of CH4 with O(1D) and OH. JGR 106, 23127–23138. [原始论文](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/2000JD000120)，摘要明确296 K和2σ。
- [R6] Saueressig et al. (1995), Carbon kinetic isotope effect of the reaction of CH4 with Cl atoms. [作者机构存档](https://yorkspace.library.yorku.ca/items/90c65b83-ce9c-48ea-b22a-b789ba331c06)，297 K摘要结果。未用二手OCR中的指数符号代替原始实验数值。
- [R7] Saueressig et al. (1996), D/H kinetic isotope effect in the reaction CH4 + Cl, GRL 23, 3619–3622, DOI 10.1029/96GL03292. [机构存档原始PDF](https://yorkspace.library.yorku.ca/server/api/core/bitstreams/482350d3-1fa2-4b7e-b20d-4e9496d6f0b8/content)，Table B（印刷页3621）明确2σ。
- [R8] Michel et al. (2023), INSTAAR/NOAA atmospheric methane 13C data, version2023-09-21. [DOI](https://doi.org/10.15138/9p89-1x02)。依据为两站事件文件CITATION头，非本轮远端下载。
- [R9] Riddell-Young et al. (2025), site-level δD and global isotope data. [数据DOI](https://doi.org/10.15138/setb-jy31)。依据为论文Data, Materials, and Software Availability及本地原始包；远端一致性未核实。
- [R10] Cantrell et al. (1990), Carbon kinetic isotope effect in the oxidation of methane by the hydroxyl radical, JGR 95, 22455–22462. [原始论文](https://agupubs.onlinelibrary.wiley.com/doi/10.1029/JD095iD13p22455)。
- [R11] Snover and Quay (2000), Hydrogen and carbon kinetic isotope effects during soil uptake of atmospheric methane, GBC 14, 25–39. [原始论文](https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/1999GB900089)，摘要区分草地/森林的现场测量与扩散修正后的氧化KIE。

## 下一步的最小修订顺序

先统一95%CI、1σ、2σ及温度/区域口径；将无法溯源的宽度明确留作情景假设，或从原集合/数据推导。随后单独修订参数版本并重跑相同工作流，报告结果是否改变。不要为了“都有引用”任意更换中心值，也不要把目前已通过配置直接称为文献约束下的稳健结论。
