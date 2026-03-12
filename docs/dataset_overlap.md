# ARC-AGI vs ARC-AGI-2 数据集重叠分析

## 数据集规模

| 数据集 | Training | Evaluation | 总计 |
|--------|----------|------------|------|
| ARC-AGI | 400 | 400 | 800 |
| ARC-AGI-2 | 1,000 | 120 | 1,120 |

## 重叠统计

| 类别 | 数量 |
|------|------|
| 两个数据集都有的 task | 773 (96.6% of ARC-AGI) |
| 仅在 ARC-AGI | 27 |
| 仅在 ARC-AGI-2（新增） | 347 |
| 两个数据集合计去重 | 1,147 |

**结论：ARC-AGI-2 基本是 ARC-AGI 的超集**，仅移除了 27 个旧 task，新增了 347 个 task。

## 跨 Split 迁移详情

ARC-AGI 的 task 在 ARC-AGI-2 中的去向：

| ARC-AGI Split | -> ARC2 Training | -> ARC2 Evaluation | -> 被移除 |
|---------------|------------------|--------------------|----------|
| Training (400) | 391 | 0 | 9 |
| Evaluation (400) | 376 | 6 | 18 |

ARC-AGI-2 新增 task 来源：

| ARC-AGI-2 Split | 新增数量 |
|------------------|----------|
| Training | 233 |
| Evaluation | 114 |

**注意**：ARC-AGI evaluation 中有 376 个 task 被移入了 ARC-AGI-2 的 training split，说明 ARC-AGI-2 将大量原本用于评估的 task 降级为训练数据。ARC-AGI-2 的 evaluation set 几乎全是新 task（114/120）。

## 仅存在于 ARC-AGI 的 27 个 Task ID

Training split (9):
`0dfd9992`, `29ec7d0e`, `3631a71a`, `40853293`, `73251a56`, `9ecd008a`, `a3df8b1e`, `c3f564a4`, `dc0a314f`

Evaluation split (18):
`08573cc6`, `1e97544e`, `3ed85e70`, `477d2879`, `47996f11`, `4aab4007`, `55783887`, `604001fa`, `67b4a34d`, `79fb03f4`, `903d1b4a`, `929ab4e9`, `af22c60d`, `c663677b`, `ca8f78db`, `e66aafb8`, `e95e3d8e`, `f4081712`
