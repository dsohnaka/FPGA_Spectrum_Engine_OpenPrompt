# FPGA Spectrum Engine — Open Prompt Repository

> **A real-time iDFT engine on FPGA — 10,240 independent oscillators, 1-sample latency, 0.001 Hz resolution.**
> Released as the first reference implementation of **Open Prompt**, a knowledge-sharing paradigm for the LLM era.
>
> **FPGA上のリアルタイムiDFTエンジン — 10,240本の独立オシレータ、1サンプル遅延、0.001Hz分解能。**
> **オープンプロンプト**——LLM時代のための知識共有パラダイム——の最初のリファレンス実装として公開。

---

## What this repository is / このリポジトリは何か

This is not a conventional open-source repository. It is structured as an **Open Prompt** distribution — a three-layer scheme that places architectural knowledge and reasoning traces in the public commons, while sample implementations are released as illustrative reference points.

これは従来のオープンソースリポジトリではない。**オープンプロンプト**配布として構造化されている——アーキテクチャ知識と推論軌跡を共有財産に置き、サンプル実装は例示的なリファレンスポイントとして公開する3層構造。

For the full Open Prompt declaration, see [Build Log #4 on Hackaday.io](https://hackaday.io/) *(URL to be added upon publication)*.

完全なオープンプロンプト宣言については、[Hackaday.io の Build Log #4](https://hackaday.io/) を参照してください *(公開時にURL追加予定)*。

---

## Three-layer structure / 3層構造

```
FPGA_Spectrum_Engine_OpenPrompt/
│
├── 01_Architecture/                 ← Layer 1: Specification (commons)
│                                       第1層: 仕様（共有財産）
│
├── 02_Reasoning_Traces/             ← Layer 2: Design dialogues (commons)
│                                       第2層: 設計対話（共有財産）
│
├── 03_Sample_Implementations/       ← Layer 3: Reference code (author-licensed)
│                                       第3層: リファレンス実装（著者ライセンス）
│
├── LICENSE_OpenPrompt.md            ← License declarations for all three layers
├── CONTRIBUTING.md                  ← How others can contribute
└── README.md                        ← This file
```

### Layer 1 — Architectural Specification / アーキテクチャ仕様

The mathematics, constraints, and structural decisions. **Public domain (CC0).** Read it, redistribute it, build on it, teach it.

数学、制約、構造的決定。**パブリックドメイン (CC0)。** 読み、再配布し、その上に構築し、教えてよい。

### Layer 2 — Reasoning Trace / 推論軌跡

The actual design dialogues that led from constraints to implementation. **Public domain (CC0).** Available in human-readable Markdown and LLM-ingestible JSON. A reader who replays these dialogues with their own language model collaborator can resume the reasoning, not just read it.

制約から実装へと至った実際の設計対話。**パブリックドメイン (CC0)。** 人間可読の Markdown と LLM 取り込み可能な JSON で提供。これらの対話を自身の言語モデル協働者と再生する読者は、推論を*読む*だけでなく*再開*できる。

### Layer 3 — Sample Implementations / サンプル実装

The Verilog skeletons, MAX patches, and other concrete artifacts produced by the original author. **Released under permissive open-source licenses** (see `03_Sample_Implementations/README.md` for specifics). These are illustrative, not normative — one possible implementation, not the implementation.

オリジナル著者が生成する Verilog スケルトン、MAX パッチ、その他の具体的成果物。**寛容なオープンソースライセンスで公開**（詳細は `03_Sample_Implementations/README.md` を参照）。これらは例示的であり規範的ではない——一つの可能な実装であり、唯一の実装ではない。

---

## How to use this repository / このリポジトリの使い方

### As a reader / 読者として

Start with `01_Architecture/overview.md` for the high-level picture. Follow the cross-references into the deeper specifications. When you want to understand *why* a particular decision was made, dive into `02_Reasoning_Traces/`. When you want to see *how* it was actually built, explore `03_Sample_Implementations/`.

`01_Architecture/overview.md` から始めて全体像を掴み、相互参照に従ってより深い仕様へ。**なぜ**特定の決定がなされたかを理解したくなったら `02_Reasoning_Traces/` に飛び込む。実際に**どう**作られたかを見たくなったら `03_Sample_Implementations/` を探索する。

### As an engineer regenerating your own implementation / 自身の実装を再生成するエンジニアとして

You are encouraged to:
1. Read Layer 1 (Architecture) directly
2. Replay Layer 2 (Reasoning Traces) with your own LLM collaborator to resume the design dialogue from where the original author left off
3. Use Layer 3 (Sample Implementations) only as a reference point for comparison, not as a starting point to fork

Your regenerated implementation is **your own**, not a derivative work of the sample. You may license it however you choose. Publishing is encouraged but not required.

以下を推奨します：
1. 第1層（アーキテクチャ）を直接読む
2. 第2層（推論軌跡）を自身の LLM 協働者と再生し、オリジナル著者が中断した地点から設計対話を再開する
3. 第3層（サンプル実装）は比較のためのリファレンスポイントとしてのみ用い、フォークの起点としては用いない

あなたが再生成した実装は**あなた自身のもの**であり、サンプルの派生物ではない。任意のライセンスを選択できる。公開は推奨されるが必須ではない。

### As a contributor / 貢献者として

Contributions to Layer 1 and Layer 2 are welcome — clarifications, additional reasoning traces, translations, alternative explanations. See `CONTRIBUTING.md`.

第1層と第2層への貢献を歓迎します——明確化、追加の推論軌跡、翻訳、代替説明。`CONTRIBUTING.md` を参照。

---

## Status / 現状

This repository is **the inaugural Open Prompt repository**, established April 2026 as the reference distribution structure for the paradigm.

このリポジトリは **Open Prompt の最初のリポジトリ**であり、本パラダイムのリファレンス配布構造として 2026 年 4 月に確立されました。

**Current contents / 現在の内容：**
- ✅ Repository structure established / リポジトリ構造の確立
- ✅ Layer 2 inaugural reasoning trace (this dialogue) / 第2層の最初の推論軌跡（本対話）
- 🔄 Layer 1 architectural documents / 第1層アーキテクチャ文書 (in progress)
- 🔄 Layer 3 sample implementations / 第3層サンプル実装 (in progress)

This is a living repository. Layers 1, 2, and 3 will accumulate over time as the FPGA Spectrum Engine project progresses.

これは生きたリポジトリである。FPGA Spectrum Engine プロジェクトが進展するにつれ、第1層、第2層、第3層は時間とともに蓄積されていく。

---

## Author / 著者

**Tsuneo Ohnaka** — Senior FPGA Architect with 40+ years of experience.

- Hackaday.io: [Tsuneo.Ohnaka](https://hackaday.io/Tsuneo.Ohnaka)
- Project page: [https://dsohnaka.github.io/FPGA_Spectrum_Engine/](https://dsohnaka.github.io/FPGA_Spectrum_Engine/)

---

## Adopting Open Prompt for your own project / あなた自身のプロジェクトでオープンプロンプトを採用する

If you wish to release your own engineering project under Open Prompt, you are welcome to use the structure of this repository as a template. The adoption procedure is described in [Build Log #4](https://hackaday.io/) *(URL to be added)* and summarized in `LICENSE_OpenPrompt.md`.

ご自身の工学プロジェクトをオープンプロンプトとして公開したい場合、このリポジトリの構造をテンプレートとして利用できます。採用手順は [Build Log #4](https://hackaday.io/) *(URL追加予定)* で説明され、`LICENSE_OpenPrompt.md` で要約されています。

---

> *Code is ephemeral; the knowledge architecture is the commons.*
> *コードは一時的なものであり、知識アーキテクチャこそが共有財産である。*
