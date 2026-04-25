# ARC 调研笔记：官方方法脉络、Program Synthesis + RL 路线、以及可继续深挖的文献方向

## 0. 这份文档怎么用

这份文档尽量少写“泛泛总结”，而是按**官方资料 + 近两年论文**来整理信息，目标是让后续调研可以直接顺着文献继续推进。

本文重点回答三件事：

1. ARC 官方在 2025 年前后认可和强调的有效方法路线是什么。
2. 如果项目想做 `program synthesis + RL`，现有文献里有哪些最接近的技术路径。
3. 除了 ARC 本身，还有哪些“任务不同但技术结构相似”的工作值得借鉴，尤其是 reward、action、model 的设计。

本文选文标准：

- 优先官方资料、期刊/会议论文、arXiv 原文。
- 优先 2024-2025 的新工作。
- 只有在官方材料里直接点名、或与 `program synthesis + RL + verifiable reward` 高度相关时，才放入更早的代表性工作。

另外，考虑到你后面要做项目设计，本文额外记录一项信息：**每篇文章公开披露的模型规模与训练规模**。这里的“训练规模”优先记录参数量、backbone、训练 token 数、训练样本量、steps；若论文或官方页面没有明确写，我会直接标注“未披露”。

---

## 1. 官方资料到底在强调什么

### 1.1 ARC 官方 Guide 给出的主线

ARC Prize 官方 Guide（2025）明确把当前主流方法整理成几个方向，包括 **program synthesis**、**deep learning-guided program synthesis**、**test-time training / active inference**、以及多系统融合。[ARC Prize Guide (2025)](https://arcprize.org/guide)

从项目角度，Guide 里最重要的信号不是“哪一篇论文最好”，而是官方已经把问题结构讲清楚了：

- ARC 不是普通视觉分类，而是**从少量示例中归纳规则**。
- 纯 brute-force program search 有上限。
- 单纯 end-to-end deep learning 也不够。
- 更被看好的方向是**结构化程序搜索 + 学习型引导**。

这对你们的项目非常关键，因为它直接说明：如果要做 `program synthesis + RL`，并不是偏题，而是顺着官方最认可的路线在往前走。

### 1.2 两份“2025 官方 technical report”需要区分

ARC 这里容易混淆，因为和 2025 赛季直接相关的官方技术文档其实有两份：

- [ARC-AGI-2: A New Challenge for Frontier AI Reasoning Systems (2025)](https://arcprize.org/blog/arc-agi-2-technical-report)
  更偏 `benchmark / dataset design`。
- [ARC Prize 2025: Technical Report (2026)](https://arxiv.org/abs/2601.10904)
  发布于 `2026-01-19`，但总结的是 `2025` 赛季，因此标题里是 `2025`。这份更偏 `比赛结果 / 方法趋势 / 官方总结`。

如果你们报告里要写“ARC 2025 tech report”，更准确的写法通常应当是第二篇；如果要写 ARC-AGI-2 的 benchmark 设计，则是第一篇。

### 1.3 2025 官方 ARC-AGI-2 report 的关键含义

2025 年 ARC-AGI-2 官方技术报告 [ARC-AGI-2: A New Challenge for Frontier AI Reasoning Systems (2025)](https://arcprize.org/blog/arc-agi-2-technical-report) 重点不是“列所有求解算法”，而是说明新 benchmark 为什么更难。

报告里对方法设计最有用的几点是：

- ARC-AGI-2 刻意降低了 naive brute-force search 的有效性。
- 任务更强调 symbolic interpretation、composition、context-sensitive rule application。
- 官方评测设计更强调**泛化真实性**，而不是只在公开题上刷分。

这意味着：

- 只靠搜索预算堆出来的方法，在 ARC-AGI-2 上更危险。
- 如果做程序搜索，必须更重视**搜索引导**和**解的泛化判断**。
- 如果做 RL，reward 不能只奖励“过当前示例”，而要尽量逼近“学到了可泛化规则”。

### 1.4 ARC Prize 2025 Technical Report 的关键含义

[ARC Prize 2025: Technical Report (2026)](https://arxiv.org/abs/2601.10904) 是你这次特别指出来的那份文献，这篇对当前调研其实非常重要，因为它已经明确总结了 2025 赛季的技术趋势。

这篇报告里最值得你们项目直接吸收的几点是：

- 2025 年的主旋律是 `refinement loop`。
- 官方把 refinement loop 定义为：针对单个 task，在反馈信号指导下，反复把当前程序或模型版本改得更好。
- 它列出的典型 refinement loop 包括：
  - test-time training 中对权重的 refinement
  - zero-pretraining deep learning
  - evolutionary program synthesis
  - verifier-guided chain-of-thought optimization
- 报告特别点名了两类在 2025 年最重要的进展：
  - `Evolutionary Program Synthesis`
  - `Zero-Pretraining Deep Learning Methods`

从你们项目角度，这篇报告最大的价值是：它把 `program synthesis + feedback-driven iterative improvement` 提升成了官方认可的年度方法主题，而不是某篇孤立论文的局部技巧。

报告里还给出了几个非常具体、值得写进综述的数据点：[ARC Prize 2025: Technical Report (2026)](https://arxiv.org/abs/2601.10904)

- ARC Prize 2025 Kaggle 比赛共有 `1,455` 支队伍、`15,154` 次提交。
- ARC-AGI-2 private set 的最高分达到 `24.03%`。
- 报告明确写到：2025 年顶级方案继续推进了 `test-time training` 和 `ensemble techniques`。
- 论文奖第一名是 `Tiny Recursive Model (TRM)`，官方特别强调它只有 `7M parameters`，但仍然能取得 competitive ARC performance。
- 论文奖第二名是 `SOAR`，核心就是 `self-improving evolutionary program synthesis framework`，并且会把自己的搜索轨迹再拿来微调 LLM。

这篇报告对你们项目最直接的启示是：

1. 如果做 ARC，不应该只盯着“单次生成一个答案”，而应重视 `per-task iterative refinement`。
2. refinement 不一定发生在 token 上，也可以发生在 `program space`、`weight space`、`search trace space`。
3. reward / feedback 的作用，在官方最新总结里已经不是辅助项，而是整个方法闭环的核心。

### 1.5 2024 ARC Prize Technical Report 是方法综述的最好入口

真正系统总结方法谱系的，是 [ARC Prize 2024: Technical Report (2024)](https://arxiv.org/abs/2412.04604)。这份报告可以当作 ARC 方法调研的主索引。

它最值得注意的不是单个分数，而是它把高分方法归纳成了几条清晰路线：

- 经典离散程序搜索
- 神经引导的程序归纳
- 直接 transduction / grid prediction
- test-time adaptation
- 多求解器融合

如果只读一份官方材料来理解“现在公认有效的方法是什么”，这份报告最值得优先读。

---

## 2. ARC 相关文献：按文章逐篇整理

这一节不做太多二次发挥，而是把每篇文章的技术路线拆开看。建议后续调研时也沿着同样的维度记笔记：

- 任务设定是什么
- 解空间是什么
- 训练阶段做了什么
- 推理阶段做了什么
- reward / feedback 来自哪里
- 它和你们要做的 `program synthesis + RL` 有多接近

### 2.1 [Combining Induction and Transduction for Abstract Reasoning (2024)](https://arxiv.org/abs/2411.02272)

这篇文章的重要性很高，因为它不是只押注一种 ARC 解法，而是明确论证了：**program induction 和 direct transduction 的优势任务分布不同，组合后更强**。

技术路线可以概括为：

- `induction branch`：通过程序归纳/搜索去找能解释示例对的规则。
- `transduction branch`：直接从示例映射到输出 grid。
- `combination`：把两条路线的结果做系统性融合，而不是二选一。

模型/训练规模：

- 论文摘要页没有直接写参数量。
- 公开二手总结普遍将这篇工作的两个分支都描述为共享 `Llama 3.1 8B Instruct` 级别的架构，并在约 `400k` 个 synthetic ARC-style problems 上训练；如果后面要在报告里写得很死，建议回原文 PDF 或作者代码仓库再核一遍这一项。[公开总结 1](https://chatpaper.com/paper/112488) [公开总结 2](https://paperswithcode.com/paper/combining-induction-and-transduction-for)

这篇文章对你们最重要的启发有三点：

1. ARC 不是“统一用一种 solver 就够了”的任务。
2. program synthesis 这条线并没有过时，反而是混合系统里的重要组成部分。
3. 如果你们后面做 RL，不一定非要让 RL 直接输出最终 grid，也可以让它只优化某一条 program-synthesis 分支。

你后续读这篇文章时，建议重点看：

- 它怎么定义 induction / transduction 的分工。
- 它们的融合是在 score 层、候选层还是结构层做的。
- 它用什么标准判断哪个分支更可信。

### 2.2 [The Surprising Effectiveness of Test-Time Training for Abstract Reasoning (2024)](https://arxiv.org/abs/2411.07279)

这篇文章说明：**每个 task 上做 test-time adaptation** 在 ARC 里非常有效。

技术路线：

- 不把问题显式表示成程序搜索。
- 而是在测试时，利用当前 task 的 train pairs 对模型做临时适应。
- 适应后直接输出 test grid。

模型/训练规模：

- 论文摘要明确写到最好结果使用的是 `8B-parameter language model`。[论文页](https://huggingface.co/papers/2411.07279)
- 官方 ARC Prize 2024 进展博客也重复提到它是在 `8B` 模型上取得 `53%` public validation accuracy。[ARC Prize 进展总结 (2024)](https://arcprize.org/blog/2024-progress-arc-agi-pub)
- 摘要页没有直接给出完整训练 token 数；但从方法描述看，训练重点在 `initial finetuning + test-time LoRA adaptation + per-instance training`，所以它的“规模”更体现在 test-time 更新量，而不是单次超大 backbone。

这篇文章和你们的项目表面上不一样，因为它不是 program synthesis；但它很值得读，因为它把一个重要事实讲清楚了：

- ARC 的关键并不只是“模型多大”，而是**模型能否针对当前 task 快速适应**。

对你们项目的价值在于：

- 即使主线做 program synthesis，后面也可以借鉴它的思路做 per-task policy adaptation。
- 如果 RL policy 是代码模型，完全可以考虑让它在每个 task 上做短期更新，再生成候选程序。

后续阅读时建议重点看：

- 它的 adaptation 单位是参数、prefix 还是 latent state。
- 它使用了哪些 augmentation。
- 它是怎样避免只记住示例而不泛化的。

### 2.3 [Product of Experts with LLMs: Boosting Performance on ARC Is a Matter of Perspective (2024)](https://huggingface.co/papers/2411.17830)

这篇工作对应的是 ARC Prize 体系里一个很有代表性的趋势：**不是让单个模型“一把梭”，而是让不同 representation / prompting perspective 的 solver 协同工作**。

技术路线：

- 使用多个不同“视角”的 LLM 解题器。
- 每个视角给出候选解或打分。
- 通过 product-of-experts 方式融合。

模型/训练规模：

- 这条路线后续正式发表为 ICML 2025 论文 [Product of Experts with LLMs: Boosting Performance on ARC Is a Matter of Perspective (2025)](https://proceedings.mlr.press/v267/franzen25a.html)。
- 作者公开的 ARC 模型卡显示，主力公开模型是 `Mistral-NeMo-Minitron-8B-Base` 微调版，即 `8B` 参数；同时也发布了 `Llama-3.2-3B` 版本，说明这条路线并不完全依赖超大模型。[8B 模型卡](https://huggingface.co/da-fr/Mistral-NeMo-Minitron-8B-ARChitects-ReArc1200-bnb-4bit) [3B 模型卡](https://huggingface.co/da-fr/Llama-3.2-3B-ARChitects-ReArc-bnb-4bit)
- 公开模型卡还提到只用 `ReArc` 数据做 finetuning；最佳结果包含 test-time retraining。

这类方法和 program synthesis + RL 的关系在于：

- 你们的 RL policy 后面很可能也不会只生成 1 个候选程序。
- 真正有用的系统形态通常是“多候选 + verifier + reranking / fusion”。

这篇文章不直接解决 RL，但很适合用来思考：

- 候选程序是单样本生成，还是多视角生成。
- 最终系统是否需要单独的 selector / reranker。

### 2.4 [Searching Latent Program Spaces (2024)](https://arxiv.org/abs/2411.08706)

这篇文章很值得单独关注，因为它在 ARC 上尝试绕开“显式程序空间太难搜”的问题，转而在**latent program space** 中做搜索。

技术路线：

- 不直接在手工 DSL 或原始代码 token 空间搜索。
- 先学一个潜在程序表示。
- 再在这个更连续、更可搜索的空间中寻找候选解。

模型/训练规模：

- ARC-AGI 主实验使用的是 `178M-parameter LPN`，latent dimension 为 `256`。[原文 HTML](https://arxiv.org/html/2411.08706)
- 论文明确写到：训练 `100k steps`、`batch size 256`，总计约 `51M` I/O pairs；ARC-AGI 配置对应 encoder 8 层、decoder 6 层、总参数量 `178M`。[架构与超参数](https://arxiv.org/html/2411.08706)
- 这一点很值得注意，因为它说明 ARC 上并不是只有 `8B/70B` 量级的方法才有研究价值，小得多的结构化模型也能做出可比性很强的实验。

它的重要性在于：

- 它直接对应你们关心的 `action` 问题。
- 如果 token-level action 太稀疏、DSL-level action 太刚性，那么 latent action / latent program 可能是第三条路。

这篇工作对后续调研最有价值的问题是：

- latent space 是怎么训练出来的。
- 搜索仍然如何和 verifier 交互。
- latent program 最后如何解码回显式可执行程序。

### 2.5 [Towards Efficient Neurally-Guided Program Induction for ARC-AGI (2024)](https://arxiv.org/abs/2411.17708)

这篇文章几乎是你们项目最直接的近邻之一，因为它把重点放在**neural guidance 如何帮助 program induction**。

技术路线：

- 保留程序归纳的整体框架。
- 用神经模型提供搜索引导，而不是完全依赖暴力枚举。
- 目标是提升搜索效率与候选质量。

模型/训练规模：

- 当前公开可直接访问的摘要/索引页面没有明确写出统一参数规模。[JST 索引页](https://jglobal.jst.go.jp/public/202402203282119371)
- 作者公开代码仓库 [GridCoder2024](https://github.com/SimonOuellette35/GridCoder2024) 表明这是一个自定义程序归纳系统，而不是简单调用现成 8B/70B LLM 的黑箱方案；如果后面要把这篇当强 baseline，建议进一步读仓库里的 `model/LVM.py` 和 Kaggle 模型卡来补参数规模。
- 这篇论文目前更适合在报告中写成“**方法结构与搜索引导机制非常相关，但公开页面对参数规模披露不完整**”。

和你们项目的关系非常直接：

- 它回答的是“怎么让程序搜索更聪明”。
- 你们若加入 RL，回答的是“怎么让模型在执行反馈下越来越会搜索”。

可以把这篇工作看成你们项目的强 baseline 类型。你们后续调研时，建议重点提取：

- 它引导的对象是什么：primitive、branch、partial program 还是 full program。
- 它的监督来自离线数据、搜索 trace 还是执行反馈。
- 它是否已经隐含用了类似 reward shaping 的机制。

### 2.6 [ARCLE: The Abstraction and Reasoning Corpus Learning Environment for Reinforcement Learning (2025)](https://proceedings.mlr.press/v274/lee25a.html)

ARCLE 很重要，因为它不是“又一个 ARC solver”，而是直接把 ARC 变成了一个 RL environment。

技术路线：

- 将 ARC 任务包装成 agent-environment 交互形式。
- action 对应对 grid 的操作或环境中的解题动作。
- 可以直接测试 RL 算法在 ARC 上的可行性。

模型/训练规模：

- ARCLE 的重点是 `environment`，不是固定某个 backbone，所以没有单一“模型大小”。
- 这类工作更应该记录的是 `state/action/reward` 定义和 baseline RL 算法，而不是参数量本身。

它和 program synthesis 路线不同，但非常适合帮你们理解：

- ARC 上 RL 为什么难。
- 如果不用程序表示而直接在环境动作空间中学，会遇到什么困难。

这篇文章的价值不在于它就是最强 solver，而在于它能回答你们一个非常现实的问题：

- 如果 reward、action、state 定义得不好，ARC 上 RL 可能会卡在哪一步。

建议重点看：

- 它的 action space 多大。
- reward 是 exact 还是 shaped。
- 基线算法在环境中为什么效果有限。

---

## 3. 从 ARC 文献里已经能看出的技术分歧

读完上面几篇后，ARC 方法的分歧基本集中在三个维度：

### 3.1 解空间选哪里

- `显式 DSL / 显式程序`
  代表：经典 program induction、neurally-guided induction。
- `直接 grid output`
  代表：transduction、test-time training。
- `latent program`
  代表：Searching Latent Program Spaces。
- `多系统候选融合`
  代表：PoE / mixture / hybrid systems。

这会直接影响 reward 能不能定义得干净、action 能不能压缩、以及模型是否容易训练。

### 3.2 test-time 预算花在哪里

- 花在程序搜索上。
- 花在模型适应上。
- 花在候选修复上。
- 花在系统融合和 reranking 上。

很多 ARC 论文表面看都在“解题”，但其实预算花费位置完全不同，这也是比较它们时最需要记录的点。

### 3.3 泛化是怎么被约束的

- 有的靠显式程序结构来保证泛化。
- 有的靠 augmentation consistency。
- 有的靠 test-time adaptation。
- 有的靠多个 solver 的 agreement。

这对你们后续做 reward 很关键，因为 reward 不应只围绕“过 train pairs”，还要想办法逼近“泛化可信度”。

---

## 4. 不同 task 上的相似项目：这些更接近你们要做的技术路线

下面这些工作不一定做 ARC，但它们和你们的目标非常相似，因为它们都在解决同一类问题：

- 输出是程序/推理轨迹/形式化证明，而不是简单分类。
- reward 可以通过执行器、单元测试、定理检查器或环境验证器自动得到。
- 核心挑战也是 reward 稀疏、action 长程、credit assignment 困难。

### 4.1 [RLEF: Grounding Code LLMs in Execution Feedback with Reinforcement Learning (2025)](https://proceedings.mlr.press/v267/gehring25a.html)

这是最值得你们细读的非 ARC 论文之一。

技术路线：

- 任务是代码生成。
- 模型生成代码后执行。
- 把 execution feedback 变成 RL 信号。
- 训练目标不是单次静态生成，而是让模型在执行反馈下学会更好的代码行为。

模型/训练规模：

- 论文摘要明确写到同时在 `8B` 和 `70B` 两个规模上验证了方法。[RLEF 论文页](https://proceedings.mlr.press/v267/gehring25a.html)
- 这对你们很有参考价值，因为它说明 execution-feedback RL 并不是只在单一小模型上“玩具式有效”，而是在中等和较大规模上都能工作。

这和你们项目的相似度非常高，因为 ARC program synthesis 本质上也是：

- 生成程序；
- 运行程序；
- 根据执行结果得到 reward；
- 再更新策略。

你们后续读这篇时，建议重点摘录：

- execution feedback 被离散成了哪些类型。
- reward 是二值、分层还是多轮累积。
- 模型是否学习 repair，而不只是 initial generation。

### 4.2 [StepCoder: Improving Code Generation with Reinforcement Learning from Compiler Feedback (2024)](https://aclanthology.org/2024.acl-long.251/)

StepCoder 和你们项目的关联点在于：它不是只看最终对错，而是利用了**更细粒度的编译/执行反馈**。

技术路线：

- 代码生成不是一次性完成，而是分步优化。
- 使用 compiler feedback 来给更中间层的信号。
- 借助 curriculum 或 staged optimization，降低长程序训练难度。

模型/训练规模：

- StepCoder 在 APPS+ 主实验里采用 `DeepSeek-Coder-Instruct-6.7B` 作为 backbone，并与 PPO、PPOCoder、RLTF 在同一 `6.7B` backbone 上公平比较。[论文 PDF](https://aclanthology.org/2024.acl-long.251.pdf)
- 论文还同时列了多个 baseline 的参数规模：`StarCoder 15.5B`、`CodeLlama-Instruct 13B`、`WizardCoder-Python 13B`、`DeepSeek-Coder-Base 6.7B`。[同上](https://aclanthology.org/2024.acl-long.251.pdf)
- 这说明它的方法增益不只是“换了个更大模型”，而是确实来自 compiler-feedback RL 设计。

这对 ARC 很有借鉴意义，因为 ARC 也可以做类似的分层反馈：

- 语法是否合法
- 是否能运行
- 是否通过部分 pair
- 是否接近目标 grid

你们做 reward 设计时，这篇文章是很好的参考模板。

### 4.3 [B-Coder: Value-Based Deep Reinforcement Learning for Program Synthesis (2024)](https://openreview.net/forum?id=0_cQmB4QYo)

B-Coder 的价值在于，它直接把 program synthesis 看成一个 RL 问题，并探索了**value-based** 路线。

技术路线：

- 状态表示部分程序构造过程。
- 动作对应程序扩展。
- 用 value-based RL 估计哪些 partial program 更有前景。

模型/训练规模：

- 当前公开可直接访问的摘要页面没有明确给出统一 backbone 的参数量。[ICLR 摘要页](https://proceedings.iclr.cc/paper_files/paper/2024/hash/7e9c2053258b1bdd32ff2654802cd594-Abstract-Conference.html)
- 论文强调的是 `value-based RL + pretrained LM initialization`，但对“到底是几 B / 几百 M 参数”的披露，在摘要层面并不充分。
- 因此，如果你们后续把它放进严格对比表，建议单列为“**参数规模待从原文 PDF 或代码仓库补充**”。

虽然任务和 ARC 不完全相同，但它对你们特别有用，因为它正好对应你们最关心的 `action` 设计：

- action 到底是 token、AST node、DSL primitive，还是编辑操作。

如果你们之后考虑“是不是不该直接在 full-program token 上做 RL”，这篇可以作为很好的参照。

### 4.4 [CodeRL: Mastering Code Generation through Pretrained Models and Deep Reinforcement Learning (2022)](https://openreview.net/forum?id=WaGvb7OzySA)

虽然 CodeRL 较早，但它仍然是 `code generation + RL + unit-test feedback` 这条线的代表性起点。

技术路线：

- 先有 pretrained code model。
- 用单元测试反馈作为强化学习信号。
- 借助 critic / reward estimator 提升训练稳定性。

模型/训练规模：

- CodeRL 对应的主 actor backbone 是 `CodeT5-large / CodeT5-large-ntp-py`，规模是 `770M` 参数。[CodeT5-large 模型卡](https://huggingface.co/Salesforce/codet5-large/blob/main/README.md) [CodeT5-large-ntp-py 模型卡](https://huggingface.co/Salesforce/codet5-large-ntp-py)
- 这篇文章很有参考价值的一点是：它证明了 verifier-based RL 在不到 1B 的代码模型上就已经可以成立。

这篇文章对 ARC 项目仍有参考价值，因为 ARC 的 verifier 在某种意义上比单元测试更理想：

- 自动化；
- 无需人工偏好；
- 反馈确定性高。

因此它更像一个“早期模板”：告诉你 verifier-based RL 在程序任务上是可以成立的。

### 4.5 [DeepSeekMath: Pushing the Limits of Mathematical Reasoning in Open Language Models (2024)](https://arxiv.org/abs/2402.03300)

这篇工作的重要性在于，它系统推广了 **GRPO（Group Relative Policy Optimization）** 在可验证推理任务上的使用。

技术路线：

- 同一道题采样多条答案。
- 用可验证 reward 评分。
- 做组内相对比较，而不是只依赖单样本绝对回报。

模型/训练规模：

- 论文核心 base / instruct / RL 模型都是 `7B`：`DeepSeekMath-Base 7B`、`DeepSeekMath-Instruct 7B`、`DeepSeekMath-RL 7B`。[DeepSeekMath 原文 HTML](https://arxiv.org/html/2402.03300)
- Base 模型从 `DeepSeek-Coder-Base-v1.5 7B` 初始化，并继续训练 `500B tokens`。[同上](https://arxiv.org/html/2402.03300)
- 论文还报告了一个 `1.3B` 数学继续预训练实验，用来分析数据配比和语料构造的作用。[同上](https://arxiv.org/html/2402.03300)
- 如果你们后面要做 GRPO，这篇论文在“模型并不极端大，但靠高质量训练与 grouped RL 依然显著提升”这一点上很有借鉴意义。

对你们项目特别关键的一点是：

- ARC program synthesis 也天然适合“每个 task 采样一组候选程序，再按 verifier 打分”。

如果你们说的 `GPRO` 实际上指的是 `GRPO`，那这篇是必须读的。建议重点看：

- 组内 advantage 怎么算。
- reward 的尺度是否需要特别校准。
- 多样本采样对训练稳定性的影响。

### 4.6 [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning (2025)](https://arxiv.org/abs/2501.12948)

DeepSeek-R1 不直接做程序合成，但它在“**纯 RL + verifiable reward 能否催生更强推理行为**”这个问题上很有代表性。

对你们项目的意义主要有两点：

- 它说明，如果 verifier 足够可靠，RL 不一定只是微调末梢，而可能显著改变策略行为。
- 它也说明，组内比较、长链 reasoning、以及多样本采样是可行的。

不过 ARC 和数学推理仍有差别：

- 数学题往往答案短。
- ARC program synthesis 输出更长、更结构化，执行失败点也更多。

所以这篇更像“训练框架借鉴”，而不是任务机制借鉴。

模型/训练规模：

- 官方仓库明确写到 `DeepSeek-R1` 与 `DeepSeek-R1-Zero` 都是 `671B total parameters / 37B activated parameters` 的 MoE 模型。[DeepSeek-R1 官方仓库](https://github.com/deepseek-ai/DeepSeek-R1)
- 同时公开了 distilled dense models：`1.5B`、`7B`、`8B`、`14B`、`32B`、`70B`。[同上](https://github.com/deepseek-ai/DeepSeek-R1)
- 因此它对你们的主要借鉴不是“照着训练一个 671B”，而是理解其 `grouped verifiable-reward optimization` 如何迁移到小得多的 program-synthesis policy 上。

### 4.7 [Reasoning Gym: Reasoning Environments for Reinforcement Learning with Verifiable Rewards (2025)](https://arxiv.org/abs/2505.24760)

这篇工作/项目最值得借鉴的是 infrastructure 思路：

- 怎么把 reasoning task 包装成可重复训练的 RLVR 环境。
- 怎么稳定组织 rollout、verification、scoring 和 grouped updates。

对你们的实际价值非常高，因为如果后面真的要做实验，难点常常不是“公式”，而是：

- environment 怎么批量跑；
- verifier 怎么统一接口；
- reward 怎么缓存；
- sampling / grouping / logging 怎么组织。

如果要做项目落地，这篇和它对应代码库值得优先看。

模型/训练规模：

- 这是一个 `environment / dataset framework`，不是单一模型论文，因此没有固定参数量。[Reasoning Gym 仓库](https://github.com/open-thought/reasoning-gym)
- 更应该记录的是它支持什么训练框架、任务数目、是否支持动态生成样本和 verifier 接口。

### 4.8 [AlphaProof (2025)](https://www.nature.com/articles/s41586-025-09002-4)

AlphaProof 做的是形式化数学证明，不是 ARC，但技术结构和你们的目标非常接近：

- 输出是长结构解。
- 正确性由 proof checker 自动验证。
- 搜索与学习都很关键。

它能提供的借鉴主要是：

- 在极其稀疏的成功信号下，如何组织搜索与训练。
- 为什么 verifier 很强时，系统设计会从“学一个打分模型”转向“尽量利用环境验证器本身”。

模型/训练规模：

- 公开页面强调的是 formal proof pipeline 与成绩，**没有完整披露可复现实验级别的参数规模**。[Nature 页面](https://www.nature.com/articles/s41586-025-09002-4)
- 在报告里更适合把它当作“验证器极强的长程结构输出任务”参照，而不是参数量可直接横向比较的对象。

### 4.9 [AlphaEvolve (2025)](https://deepmind.google/discover/blog/alphaevolve-a-coding-agent-for-scientific-and-algorithmic-discovery/)

AlphaEvolve 不是 RL 论文，但它对你们也有价值，因为它展示了另一种“程序空间 + 自动评测器”的路线：

- 生成程序候选；
- 用 evaluator 跑性能；
- 根据结果继续搜索和改写。

它更偏 evolutionary / iterative search，但和 ARC 的 program synthesis 很像：

- 都不是一次性预测。
- 都依赖外部可执行验证器。
- 都需要从大量候选里挑更好者。

如果你们后续发现在线 RL 太难，AlphaEvolve 这类思路也可以作为“搜索式 baseline”参考。

模型/训练规模：

- 官方博客公开的是系统路线，不是论文级的完整训练配方，因此没有明确参数量。[AlphaEvolve 官方博客](https://deepmind.google/discover/blog/alphaevolve-a-coding-agent-for-scientific-and-algorithmic-discovery/)
- 它更适合借鉴 candidate generation + evaluator + iterative search 这套系统结构。

---

## 5. 专门围绕 reward / action / model 做一次文献整理

这一节不讲抽象“应该怎么做”，而是把现有文献在这三件事上的不同处理方式列清楚。

### 5.1 Reward：文献里已经出现的几种做法

| reward 类型 | 代表文献 | 具体形式 | 对 ARC program synthesis 的意义 |
| --- | --- | --- | --- |
| 最终通过/失败 | [CodeRL](https://openreview.net/forum?id=WaGvb7OzySA), [DeepSeekMath](https://arxiv.org/abs/2402.03300) | unit test pass、答案对错 | 最干净，但对 ARC 太稀疏 |
| 编译/执行分层反馈 | [StepCoder](https://aclanthology.org/2024.acl-long.251/), [RLEF](https://proceedings.mlr.press/v267/gehring25a.html) | parse error、compile error、runtime error、partial correctness | 很适合 ARC，能从“程序能否运行”开始塑形 |
| 部分正确性 | [RLEF](https://proceedings.mlr.press/v267/gehring25a.html), [Reasoning Gym](https://arxiv.org/abs/2505.24760) | 部分测试点、过程反馈、可验证子目标 | ARC 可对应为 pair-level pass、cell accuracy |
| 组内相对奖励 | [DeepSeekMath](https://arxiv.org/abs/2402.03300), [DeepSeek-R1](https://arxiv.org/abs/2501.12948) | 同题多样本、按组归一化比较 | 非常适合 ARC 上每题多候选程序采样 |
| 环境式 sparse reward | [ARCLE](https://proceedings.mlr.press/v274/lee25a.html), [AlphaProof](https://www.nature.com/articles/s41586-025-09002-4) | 成功才给强奖励 | 说明纯 sparse reward 往往需要更强搜索/分层动作 |

从这些工作里，可以明确提炼出一个结论：

- 如果你们在 ARC 上做 RL，**不要只试 exact-match binary reward**。
- 更值得优先做的是 verifier-based layered reward。

一个更贴合 ARC 的 reward 结构，文献上可以对应成下面这种组合：

1. `syntax / parse validity`
2. `runtime success`
3. `train pair pass count`
4. `cell-level correctness`
5. `augmentation consistency`
6. `program length / runtime penalty`

其中前四项在代码 RL 文献里已经有明显先例；第五项是 ARC 文献特别值得补上的部分，因为 ARC 的核心问题一直是“怎么区分真的学到规则，还是只拟合了示例”。

### 5.2 Action：不同论文在“动作空间”上的选择

| action 形式 | 代表文献 | 优点 | 风险 |
| --- | --- | --- | --- |
| token-level generation | [CodeRL](https://openreview.net/forum?id=WaGvb7OzySA), [RLEF](https://proceedings.mlr.press/v267/gehring25a.html) | 最容易复用现有 LLM 框架 | 序列长，非法程序多，credit 差 |
| step-wise / staged code generation | [StepCoder](https://aclanthology.org/2024.acl-long.251/) | 更容易利用中间反馈 | 需要人为划分阶段 |
| partial program expansion | [B-Coder](https://openreview.net/forum?id=0_cQmB4QYo), [Towards Efficient Neurally-Guided Program Induction for ARC-AGI](https://arxiv.org/abs/2411.17708) | 更接近 program synthesis 本质 | 状态设计更复杂 |
| latent action / latent program search | [Searching Latent Program Spaces](https://arxiv.org/abs/2411.08706) | 可能兼顾灵活性与可搜索性 | 可解释性和执行映射更难 |
| environment manipulation | [ARCLE](https://proceedings.mlr.press/v274/lee25a.html) | 环境定义直接 | 未必真正学到规则程序 |

这张表对你们的直接启发是：

- 如果项目目标明确是 `program synthesis + RL`，最值得优先尝试的不是 grid-editing action，而是**partial program / edit-based / staged generation**。
- 这类 action 更容易接 execution feedback，也更容易做 reward shaping。

### 5.3 Model：policy 放在哪一层最合理

| model 角色 | 代表文献 | 说明 |
| --- | --- | --- |
| code LLM as generator | [CodeRL](https://openreview.net/forum?id=WaGvb7OzySA), [RLEF](https://proceedings.mlr.press/v267/gehring25a.html) | 最直接，容易开始 |
| neural guide for symbolic search | [Towards Efficient Neurally-Guided Program Induction for ARC-AGI](https://arxiv.org/abs/2411.17708) | 不完全代替搜索，而是给搜索提速 |
| task-adaptive predictor | [The Surprising Effectiveness of Test-Time Training for Abstract Reasoning](https://arxiv.org/abs/2411.07279) | 重点不在程序，而在 per-task 适应 |
| grouped RL policy | [DeepSeekMath](https://arxiv.org/abs/2402.03300), [DeepSeek-R1](https://arxiv.org/abs/2501.12948) | 适合 verifiable reward、多候选采样 |
| solver ensemble / selector | [Combining Induction and Transduction for Abstract Reasoning](https://arxiv.org/abs/2411.02272), [Product of Experts with LLMs](https://huggingface.co/papers/2411.17830) | 最终系统往往不是单一 policy |

从这几类工作看，比较现实的系统结构通常不是“一个模型直接 end-to-end 搞定”，而是：

- generator / proposer
- verifier
- reranker / selector
- optional repair policy

如果你们后面真的实现，最容易做成项目成果的也往往是这个形态。

### 5.4 这些文献的模型规模与训练规模汇总

为了后面做项目设计，这里把上面分散的信息压成一个对比表。表里只记录**公开可验证**的信息；没公开的地方我明确标成“未披露”。

| 文献 | 模型规模 | 训练规模 / 备注 | 对项目的直接意义 |
| --- | --- | --- | --- |
| [Combining Induction and Transduction for Abstract Reasoning (2024)](https://arxiv.org/abs/2411.02272) | 公开摘要页未直写；公开总结通常记为 `8B` 级共享架构 | 公开总结常提到约 `400k` synthetic ARC-style tasks；正式数字建议回原文核对 | 说明 induction 与 transduction 可以共享中等规模 backbone 并形成互补 |
| [The Surprising Effectiveness of Test-Time Training for Abstract Reasoning (2024)](https://arxiv.org/abs/2411.07279) | `8B` LM | test-time LoRA / per-instance training 是重点，非单纯更大 backbone | 说明 ARC 上 per-task adaptation 在 8B 规模就很强 |
| [Product of Experts with LLMs (2025)](https://proceedings.mlr.press/v267/franzen25a.html) | 最佳公开模型 `8B`；另有 `3B` 版本 | 仅用 `ReArc` finetuning，并结合 test-time retraining | 说明 ARC 高分方法不一定依赖超大模型 |
| [Searching Latent Program Spaces (2024)](https://arxiv.org/abs/2411.08706) | `178M` | `100k steps`、`batch 256`、约 `51M` I/O pairs | 说明结构化小模型也能在 ARC 上形成有价值路线 |
| [Towards Efficient Neurally-Guided Program Induction for ARC-AGI (2024)](https://arxiv.org/abs/2411.17708) | 未披露 | 公开代码表明是自定义程序归纳系统 | 可作为 program-induction baseline，但参数规模需补查 |
| [ARCLE (2025)](https://proceedings.mlr.press/v274/lee25a.html) | 无固定模型 | 重点是环境，不是 backbone | 用来设计 state/action/reward，不是比参数量 |
| [RLEF (2025)](https://proceedings.mlr.press/v267/gehring25a.html) | `8B` 和 `70B` | 多步执行反馈 RL | 最像你们“程序生成 + 执行反馈 + RL”的非 ARC 参照 |
| [StepCoder (2024)](https://aclanthology.org/2024.acl-long.251/) | 主 backbone `6.7B` | 与 PPO / PPOCoder / RLTF 用同一 `6.7B` backbone 比较 | 非常适合参考 reward shaping 与 staged action |
| [B-Coder (2024)](https://openreview.net/forum?id=0_cQmB4QYo) | 未披露 | 强调 value-based RL + pretrained LM init | 适合借鉴 value-based search，不适合直接拿参数量比较 |
| [CodeRL (2022)](https://openreview.net/forum?id=WaGvb7OzySA) | `770M` | actor 基于 `CodeT5-large` | 说明 verifier-based RL 在 <1B 代码模型上就能成立 |
| [DeepSeekMath (2024)](https://arxiv.org/abs/2402.03300) | 核心模型 `7B`；另有 `1.3B` 分析实验 | Base 继续预训练 `500B tokens` | 是 GRPO 路线最关键的直接参照 |
| [DeepSeek-R1 (2025)](https://arxiv.org/abs/2501.12948) | `671B total / 37B activated`; distill 为 `1.5B` 到 `70B` | 多阶段 RL + distillation | 借鉴训练框架，不必照搬其超大规模 |
| [Reasoning Gym (2025)](https://arxiv.org/abs/2505.24760) | 无固定模型 | 重点是 environment / verifier framework | 对你们搭实验基础设施最有用 |
| [AlphaProof (2025)](https://www.nature.com/articles/s41586-025-09002-4) | 未披露 | 验证器极强、结构输出长 | 借鉴“稀疏成功信号下如何组织系统” |
| [AlphaEvolve (2025)](https://deepmind.google/discover/blog/alphaevolve-a-coding-agent-for-scientific-and-algorithmic-discovery/) | 未披露 | evaluator-guided iterative search | 可作为非 RL 搜索式 baseline 灵感 |

---

## 6. 哪些文章最像你们要做的项目

如果只从“和 `ARC + program synthesis + RL` 最相近”这个角度挑文章，建议优先级如下。

### 第一优先级：必须细读

1. [Towards Efficient Neurally-Guided Program Induction for ARC-AGI (2024)](https://arxiv.org/abs/2411.17708)
   因为它最接近“ARC 上如何做 smarter program search”。

2. [RLEF (2025)](https://proceedings.mlr.press/v267/gehring25a.html)
   因为它最接近“程序生成 + 执行反馈 + RL”。

3. [StepCoder (2024)](https://aclanthology.org/2024.acl-long.251/)
   因为它最接近“如何把极稀疏 reward 拆成更可学的反馈”。

4. [DeepSeekMath (2024)](https://arxiv.org/abs/2402.03300)
   因为它最接近“如果要用 GRPO，该怎么组织多候选和组内奖励”。

### 第二优先级：和 ARC 任务结构关系很强

5. [Combining Induction and Transduction for Abstract Reasoning (2024)](https://arxiv.org/abs/2411.02272)
6. [The Surprising Effectiveness of Test-Time Training for Abstract Reasoning (2024)](https://arxiv.org/abs/2411.07279)
7. [Searching Latent Program Spaces (2024)](https://arxiv.org/abs/2411.08706)
8. [ARCLE (2025)](https://proceedings.mlr.press/v274/lee25a.html)

### 第三优先级：做系统设计和 baseline 时有帮助

9. [Reasoning Gym (2025)](https://arxiv.org/abs/2505.24760)
10. [CodeRL (2022)](https://openreview.net/forum?id=WaGvb7OzySA)
11. [B-Coder (2024)](https://openreview.net/forum?id=0_cQmB4QYo)
12. [AlphaProof (2025)](https://www.nature.com/articles/s41586-025-09002-4)

---

## 7. 你接下来可以怎么继续调研：给出具体问题，不只是方向名

这一节是给你继续查资料时用的。每一项我都尽量写成“该查什么、为什么查、查完能回答什么问题”。

### 7.1 继续查 reward：重点查“部分正确性怎么定义”

需要继续查的问题：

- 代码 RL 里，`partial correctness` 最常见的定义有哪些？
- 是按 test case 数量算，还是按 execution trace 的中间状态算？
- ARC 上是否已经有人把 `cell-level accuracy` 和 `program-level correctness` 结合起来？

建议继续搜的关键词：

- `ARC cell-level reward program synthesis`
- `execution feedback partial correctness reinforcement learning code generation`
- `verifiable rewards partial credit program synthesis`

你希望最后拿到的不是“reward 很重要”这种话，而是一个表：

| 论文 | 最终 reward | 中间 reward | 是否有稳定性约束 | 是否惩罚长度/耗时 |
| --- | --- | --- | --- | --- |

### 7.2 继续查 action：重点查“编辑式动作是否优于从零生成”

需要继续查的问题：

- 有哪些程序生成论文不是从零写完整程序，而是做 patch / edit / repair？
- 哪些工作把 action 定义为 AST 扩展、DSL primitive 选择、或 partial program completion？
- 这些 action 是否更适合 RL 的 credit assignment？

建议继续搜的关键词：

- `program repair reinforcement learning code generation`
- `AST action reinforcement learning program synthesis`
- `edit-based policy code generation reinforcement learning`

你查完后，应该能明确比较三种 action：

1. token-level
2. partial-program-level
3. edit-level

### 7.3 继续查 model：重点查“policy 是单模型还是双阶段系统”

需要继续查的问题：

- 现有成功工作里，policy 是否单独承担生成和修复两种角色？
- 有没有“generator + verifier + selector + repairer”这种多模块系统的成熟模式？
- 在 verifiable reward 场景下，critic 是否真的必要？

建议继续搜的关键词：

- `generator verifier selector program synthesis reinforcement learning`
- `critic-free reinforcement learning verifiable rewards code generation`
- `GRPO code generation execution feedback`

你最终应该能得到一个系统结构对比：

| 系统结构 | 代表工作 | 优势 | 对 ARC 的适配性 |
| --- | --- | --- | --- |

### 7.4 继续查 ARC 专用数据和训练 curriculum

需要继续查的问题：

- ARC program-synthesis 路线是否系统依赖 RE-ARC / BARC 等 synthetic data？
- curriculum 是按 task 难度、program depth 还是 object complexity 来组织？
- 如果做 RL，是否应该先在 synthetic ARC-like tasks 上训练，再迁移到真实 ARC？

建议继续搜的关键词：

- `RE-ARC curriculum ARC program synthesis`
- `BARC synthetic data ARC reasoning`
- `curriculum learning ARC program induction`

这部分会直接影响你们项目是否能训练起来，因为 ARC 原始训练集本身太小。

### 7.5 继续查“如何判断程序真的泛化”

这是 ARC 上经常被忽略但实际非常关键的一点。

需要继续查的问题：

- 高分 ARC 系统如何区分“过了示例”和“真的学到规则”？
- 是否使用了 augmentation stability、candidate agreement、program simplicity 之类的泛化 proxy？
- 有没有工作专门比较“最短程序”“最稳定程序”“得分最高程序”之间的差异？

建议继续搜的关键词：

- `ARC augmentation stability candidate selection`
- `program simplicity generalization ARC`
- `solver agreement ARC benchmark`

如果你们后面做 RL，这部分很可能直接变成 reward 的一部分。

---

## 8. 如果现在就要把项目范围收窄，我建议优先收缩到这三个问题

基于上面的文献脉络，当前最值得收缩成项目问题的，不是“做一个很大的 ARC 系统”，而是下面三个更聚焦的问题。

### 8.1 问题一：ARC 上怎样设计 layered verifier reward

这是最重要的问题，因为它决定 RL 能不能真正学起来。

一个较可靠的最小研究问题可以写成：

> 在 ARC 的 program synthesis 设定下，binary exact-match reward、pair-level reward、cell-level reward、以及 augmentation-stability reward，哪种组合最能提升候选程序质量？

这个问题的好处是：

- 和你们当前担心的 reward 稀疏直接对应。
- 能很明确地设计对照实验。
- 不需要一开始就做超大系统。

### 8.2 问题二：从零生成 vs 编辑式修复，哪个更适合 ARC RL

可以把问题写成：

> 在 ARC program synthesis 中，RL policy 直接生成完整程序，是否不如“先生成初稿，再基于 execution feedback 做 edit-based repair”？

这个问题的重要性在于：

- 它直接对应 action 设计。
- 也能借鉴 RLEF / StepCoder 的思路。

### 8.3 问题三：GRPO 是否适合 ARC 的 verifier-based program search

可以把问题写成：

> 若每个 ARC task 采样多条候选程序，基于 verifier 的 grouped relative optimization 是否比单样本 policy-gradient 更稳定？

这个问题的重要性在于：

- 它直接对应你提到的 `GPRO/GRPO`。
- 也是目前最接近“大模型可验证推理 RL”主线的话题。

---

## 9. 一份更实用的阅读顺序

如果你希望最短时间内把这块文献读出结构，我建议按下面顺序读。

### 第一步：先建立 ARC 方法地图

1. [ARC Prize Guide (2025)](https://arcprize.org/guide)
2. [ARC Prize 2025: Technical Report (2026)](https://arxiv.org/abs/2601.10904)
3. [ARC Prize 2024: Technical Report (2024)](https://arxiv.org/abs/2412.04604)
4. [ARC-AGI-2 官方技术报告 (2025)](https://arcprize.org/blog/arc-agi-2-technical-report)

目标：

- 搞清 ARC 官方认可的主线。
- 明确 ARC-AGI-2 为什么会让 brute-force 更难。

### 第二步：再看 ARC 内部最相关的技术路线

5. [Combining Induction and Transduction for Abstract Reasoning (2024)](https://arxiv.org/abs/2411.02272)
6. [The Surprising Effectiveness of Test-Time Training for Abstract Reasoning (2024)](https://arxiv.org/abs/2411.07279)
7. [Towards Efficient Neurally-Guided Program Induction for ARC-AGI (2024)](https://arxiv.org/abs/2411.17708)
8. [Searching Latent Program Spaces (2024)](https://arxiv.org/abs/2411.08706)
9. [ARCLE (2025)](https://proceedings.mlr.press/v274/lee25a.html)

目标：

- 搞清 ARC 上不同 solver 的“状态空间和解空间差异”。

### 第三步：最后补 program synthesis + RL 的方法论

10. [RLEF (2025)](https://proceedings.mlr.press/v267/gehring25a.html)
11. [StepCoder (2024)](https://aclanthology.org/2024.acl-long.251/)
12. [DeepSeekMath (2024)](https://arxiv.org/abs/2402.03300)
13. [Reasoning Gym (2025)](https://arxiv.org/abs/2505.24760)
14. [CodeRL (2022)](https://openreview.net/forum?id=WaGvb7OzySA)

目标：

- 把 ARC 项目真正落到 reward / action / model 设计上。

---

## 10. 现阶段可以直接写进报告的结论

基于 2024-2026 年公开的 ARC 官方报告与相关论文，当前 ARC 的有效解法并未收敛到单一范式，而是形成了几条并行主线：程序归纳、直接 transduction、test-time adaptation，以及围绕反馈信号展开的 refinement loop。官方材料尤其强调，ARC-AGI-2 已经显著降低了 naive brute-force search 的有效性，因此单纯依赖大搜索预算的程序搜索路线将更难持续扩展；而在 `ARC Prize 2025: Technical Report` 中，官方进一步把 `refinement loop` 视为 2025 年最核心的方法主题。与之相对，结合神经模型的 program induction、task-specific adaptation，以及多 solver 融合，被视为更有前景的方向。[ARC Prize Guide (2025)](https://arcprize.org/guide)、[ARC Prize 2025: Technical Report (2026)](https://arxiv.org/abs/2601.10904)、[ARC Prize 2024: Technical Report (2024)](https://arxiv.org/abs/2412.04604)、[ARC-AGI-2 官方技术报告 (2025)](https://arcprize.org/blog/arc-agi-2-technical-report)

对于本项目拟采用的 `program synthesis + RL` 路线，最直接相关的文献并不是单纯的 ARC solver，而是“程序生成 + 可执行验证 + 强化学习”这一类工作。例如 [RLEF (2025)](https://proceedings.mlr.press/v267/gehring25a.html)、[StepCoder (2024)](https://aclanthology.org/2024.acl-long.251/)、[CodeRL (2022)](https://openreview.net/forum?id=WaGvb7OzySA) 提供了 execution-feedback RL 的成熟范式；[DeepSeekMath (2024)](https://arxiv.org/abs/2402.03300) 与 [DeepSeek-R1 (2025)](https://arxiv.org/abs/2501.12948) 则说明 grouped verifiable-reward optimization 在推理任务中已经具备可行性。综合这些工作，当前最值得优先解决的不是“换更大的模型”，而是：如何为 ARC 设计 layered verifier reward、如何把 action 从纯 token 生成改造成更适合 credit assignment 的程序编辑/分阶段生成，以及是否采用 GRPO 这类更适合 task-wise 多候选比较的优化框架。
