# Layer 3 — Sample Implementations / サンプル実装

> **License: MIT (default; see per-artifact specifications)**
> These are reference points, not blueprints. One possible implementation, not the implementation.
>
> **ライセンス：MIT（デフォルト；アーティファクトごとの指定を参照）**
> これらはリファレンスポイントであり、設計図ではない。一つの可能な実装であり、唯一の実装ではない。

---

## What is in this layer / この層の内容

This layer contains the **concrete artifacts** produced by the original author in the course of building the FPGA Spectrum Engine: Verilog skeletons, MAX patches, scripts, and similar. These are *illustrative, not normative*.

この層には、FPGA Spectrum Engine 構築の過程でオリジナル著者が生成した**具体的成果物**が含まれる：Verilog スケルトン、MAX パッチ、スクリプトなど。これらは*例示的であり規範的ではない*。

---

## A critical distinction / 重要な区別

A regenerated implementation produced by another engineer from Layer 1 (Architecture) and Layer 2 (Reasoning Traces) is **NOT a derivative work** of these samples. The regenerator owns their implementation outright.

第1層（アーキテクチャ）と第2層（推論軌跡）から他のエンジニアが再生成した実装は、これらのサンプルの**派生物ではない**。再生成者はその実装を完全に所有する。

| Source path / 出発点 | Result / 結果 |
|---|---|
| Forking a Layer 3 sample → modify → redistribute / 第3層サンプルをフォーク→改変→再配布 | Derivative work, MIT license obligations apply / 派生著作物、MIT ライセンス義務が適用 |
| Reading Layers 1 & 2 → regenerate from architecture → produce new implementation / 第1層・第2層を読む→アーキテクチャから再生成→新しい実装を生成 | Independent work, regenerator's own license / 独立著作物、再生成者自身のライセンス |

This distinction is the structural innovation of Open Prompt. Forking the sample is permitted (under MIT). Regenerating from the architecture is *also* permitted, and the resulting work has no license inheritance from the sample.

この区別がオープンプロンプトの構造的革新である。サンプルのフォークは許可される（MIT のもと）。アーキテクチャからの再生成も許可される——そして結果として得られる著作物にはサンプルからのライセンス継承がない。

---

## Inventory / 一覧

*Sample implementations are accumulated over time as the project progresses. The list below reflects the current state.*
*サンプル実装はプロジェクトの進展とともに蓄積される。以下は現状を反映する。*

### Planned / 予定

- `horner_pipeline_verilog/` — Reference Verilog skeleton for the Horner-method polynomial sine pipeline / Horner 法多項式正弦パイプラインのリファレンス Verilog スケルトン
- `bin_pattern_generators/` — Python scripts generating bin assignment patterns for FM, additive, fractal, and other paradigms / FM、加算、フラクタル他のパラダイムのためのビン割当パターンを生成する Python スクリプト
- `max_patches/` — MAX/MSP patches for control of the engine via MIDI and OSC / MIDI と OSC によるエンジン制御のための MAX/MSP パッチ
- `arm_hps_scene_expander/` — ARM HPS-side software for expanding abstract scene descriptions into bin assignments / 抽象シーン記述をビン割当に展開する ARM HPS 側ソフトウェア

### Currently available / 現在利用可能

*To be added as the project progresses.*
*プロジェクト進展に応じて追加。*

---

## Per-artifact licenses / アーティファクトごとのライセンス

Unless specified otherwise within a subdirectory, all sample implementations are released under the **MIT License**. Subdirectories with different licenses will contain their own `LICENSE` file.

サブディレクトリ内で別途指定がない限り、すべてのサンプル実装は **MIT ライセンス**で公開される。異なるライセンスを持つサブディレクトリは独自の `LICENSE` ファイルを含む。

Standard MIT terms: copyright notice and license text must be included in substantial portions of redistributions; provided "as is" without warranty.

標準的な MIT 条項：再配布のかなりの部分には著作権表示とライセンス文を含めなければならない；保証なしで「現状のまま」提供される。

---

## How to use this layer responsibly / この層を責任を持って利用する方法

### If you want to fork and modify / フォークして改変したい場合

Standard open-source practice. Follow MIT terms. Your fork is a derivative work.

標準的なオープンソース実践。MIT 条項に従う。あなたのフォークは派生著作物である。

### If you want to learn from this and build your own / これから学んで自身のものを構築したい場合

Read the samples for understanding, but **do not begin by copying them**. Instead, read Layers 1 and 2, then implement from scratch (with or without LLM assistance). Use the samples only for comparison after your own implementation exists.

理解のためにサンプルを読むが、**コピーから始めない**こと。代わりに第1層と第2層を読み、ゼロから実装する（LLM 補助の有無を問わず）。自身の実装が存在した後の比較のみのために、サンプルを使う。

This is the recommended path because it preserves the Open Prompt structure: your implementation is genuinely yours, not a fork of someone else's code.

この経路を推奨する理由はオープンプロンプト構造を保持するからである：あなたの実装は本当にあなた自身のものであり、他人のコードのフォークではない。

### If you want to contribute / 貢献したい場合

See the root-level `CONTRIBUTING.md`. Direct contributions to the original author's samples require prior discussion. The recommended alternative is to publish your own Open Prompt repository and link to it.

ルートの `CONTRIBUTING.md` を参照。オリジナル著者のサンプルへの直接貢献は事前議論を必要とする。推奨される代替案は、自身のオープンプロンプトリポジトリを公開してリンクすることである。

---

## Why "samples," not "the implementation" / なぜ「実装」ではなく「サンプル」か

Calling these "the implementation" would imply that they are the canonical answer. They are not. They are **one possible answer**, made by one engineer (the original author), under one set of constraints (the original author's hardware, time, error budget, and aesthetic preferences), at one moment in time.

これらを「実装」と呼ぶことは、それらが正典的な答えであることを含意する。そうではない。それらは**一つの可能な答え**であり、一人のエンジニア（オリジナル著者）が、一組の制約（オリジナル著者のハードウェア、時間、誤差予算、美的選好）のもとで、一時点で作成したものである。

Other engineers — under different constraints, with different aesthetic preferences, on different hardware, at different moments in time — will produce different implementations from the same Layer 1 and Layer 2 inputs. Those implementations are equally legitimate. **The mathematics is the commons. The implementations are the contributions.**

他のエンジニアは——異なる制約のもとで、異なる美的選好を持ち、異なるハードウェア上で、異なる時点で——同じ第1層と第2層の入力から異なる実装を生み出す。それらの実装は等しく正当である。**数学は共有財産である。実装は貢献である。**
