# Layer 1 — Architectural Specification / アーキテクチャ仕様

> **License: CC0 1.0 Universal (Public Domain)**
> This is the commons. Read it, redistribute it, build on it, teach it, criticize it, refine it. No permission needed.
>
> **ライセンス：CC0 1.0 Universal（パブリックドメイン）**
> これは共有財産である。読み、再配布し、その上に構築し、教え、批評し、洗練してよい。許可は不要。

---

## What is in this layer / この層の内容

The Architectural Specification layer contains the **mathematics, constraints, and structural decisions** that define the FPGA Spectrum Engine. It is written for a competent engineer to read directly. In combination with current language model capabilities, it is sufficient input for that engineer to regenerate a working implementation.

アーキテクチャ仕様層には、FPGA Spectrum Engine を定義する**数学、制約、構造的決定**が含まれる。有能なエンジニアが直接読めるように書かれている。現代の言語モデル能力との組み合わせにより、そのエンジニアが動作する実装を再生成するに十分な入力である。

---

## Documents / 文書

*Documents in this layer are accumulated over time. The list below reflects the current state and will grow.*
*この層の文書は時間とともに蓄積される。以下のリストは現状を反映しており、拡張されていく。*

### Planned / 予定

- `overview.md` — High-level architectural overview / 高レベルアーキテクチャ概要
- `core_mathematics.md` — Maclaurin truncation, error bounds, polynomial evaluation / マクローリン打ち切り、誤差上界、多項式評価
- `system_architecture.md` — 3-layer hardware (PC / ARM HPS / FPGA) / 3層ハードウェア
- `bin_direct_addressing.md` — The bin-addressing principle vs voice allocation / ビンアドレス原理対ボイス割当
- `synthesis_paradigm_unification.md` — FM, additive, fractal, polygonal as bin patterns / FM、加算、フラクタル、ポリゴナルがビンパターンとして
- `idft_sdft_duality.md` — Duality with sliding DFT, robotics applications / スライディング DFT との双対性、ロボティクス応用
- `design_constraints.md` — Cyclone V resources, throughput targets, error budget / Cyclone V リソース、スループット目標、誤差予算
- `implementation_arena.md` — Open dimensions for implementer choice / 実装者選択のための開かれた次元

### Currently available / 現在利用可能

The Hackaday.io Build Logs serve as the initial Layer 1 documentation while these formal documents are being prepared:

これらの正式文書が準備される間、Hackaday.io の Build Log が初期の第1層文書として機能する：

- Build Log #1: Why 11th-order Maclaurin / なぜ11次マクローリンか
- Build Log #2: 2020 prototype and the wrong turn / 2020年プロトタイプと誤った方向
- Build Log #3: Synthesis paradigm lineage *(forthcoming)* / 合成パラダイムの系譜（準備中）
- Build Log #4: Open Prompt declaration / オープンプロンプト宣言

---

## How to read this layer / この層の読み方

For a high-level entry: start with `overview.md` (when available) or with Build Log #2 on Hackaday.io.

高レベルからの入り口：`overview.md`（利用可能になり次第）または Hackaday.io の Build Log #2 から始める。

For deep technical understanding: follow the cross-references between documents. Mathematical claims will reference their derivations; structural decisions will reference their constraints.

深い技術的理解のため：文書間の相互参照に従う。数学的主張は導出を参照し、構造的決定は制約を参照する。

For regenerating your own implementation: Layer 1 alone is not optimal. Pair it with Layer 2 (Reasoning Traces) so you can resume the design dialogue with your own LLM collaborator from where the original author left off.

自身の実装を再生成するため：第1層単独では最適ではない。第2層（推論軌跡）と組み合わせ、オリジナル著者が中断した地点から自身の LLM 協働者と設計対話を再開できるようにする。

---

## How to contribute / 貢献の方法

See the root-level `CONTRIBUTING.md`. Layer 1 contributions are released into the public domain (CC0) by the act of submission.

ルートの `CONTRIBUTING.md` を参照。第1層への貢献は、提出行為によりパブリックドメイン (CC0) で公開される。
