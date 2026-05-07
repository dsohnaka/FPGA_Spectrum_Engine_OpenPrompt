# WPMS Synthesizer Layer 1 Drafting — Chapters 1 and 2
# WPMS シンセサイザー第1層仕様起草 — 第1章および第2章

## Trace Metadata / 軌跡メタデータ

| Field | Value |
|---|---|
| **Date / 日付** | 2026-05-02 |
| **Participants / 参加者** | Tsuneo Ohnaka (FPGA Architect, 40+ years); Claude (Anthropic, Claude Opus 4.7) |
| **Topic / トピック** | Drafting dialogue for Chapter 1 (Scope and Boundary Conditions) and Chapter 2 (Maclaurin Pipeline Specification) of the WPMS Synthesizer Layer 1 specification |
| **Status / 状態** | Layer 2 trace — single-AI multi-stage drafting dialogue / 第2層軌跡 — 単一AI複数段階起草対話 |
| **Original language / 原言語** | Japanese (with English technical terminology) / 日本語（英語技術用語を交える） |
| **License / ライセンス** | CC0 1.0 Universal (Public Domain) |
| **Direct outputs** | `WPMS_Layer1_Chapter1_Scope_and_Boundary_Conditions.md`, `WPMS_Layer1_Chapter2_Maclaurin_Pipeline.md` |

---

## Reading Notes / 読解上の注

This trace records the dialogue that produced the first two chapters of the WPMS Synthesizer Layer 1 specification. The dialogue is the application of Open Prompt methodology to itself: the synthesizer's specification is being drafted through reasoning that will be archived as Layer 2, so that future engineers regenerating or extending the synthesizer can replay the design judgments that went into each decision.

本軌跡は WPMS シンセサイザー第 1 層仕様の最初の 2 章を生み出した対話を記録する。対話自体が Open Prompt 方法論の自己適用である：シンセサイザーの仕様は第 2 層としてアーカイブされる推論を通して起草されており、将来のエンジニアが本シンセサイザーを再生成または拡張する際に、各決定に至った設計判断を再生できる。

**Notable conceptual progressions across the dialogue:**

**対話を通じた特筆すべき概念的進展：**

1. **From "synthesizer architecture" to "regeneration target"** — the dialogue constructs Chapters 1 and 2 not just as a description of what to build, but as an artifact that another engineer plus an LLM should be able to use to rebuild the synthesizer independently. This shaped the level of detail at every step: enough to constrain implementation, sparse enough to leave Implementation Arena variants open. / 「シンセサイザーアーキテクチャ」から「再生成ターゲット」へ——対話は第 1 章と第 2 章を、何を構築するかの記述としてだけでなく、別のエンジニアと LLM がシンセサイザーを独立に再構築するために使えるアーティファクトとして構築した。これは各ステップでの詳細レベルを形成した：実装を制約するに十分、Implementation Arena 変種を開いたままにするに疎ら。

2. **The discovery that C5G's 24-bit phase resolution was a memory-format artifact** — when the phase accumulator bit-width came up, the architect recalled that C5G used 24 bits because of M10K block constraints (16+8 BRAM construction). With WPMS's difference-engine architecture eliminating per-bin parameter memory, that constraint vanished. The dialogue then chose 32 bits, and recognized that the choice produces ~89× finer frequency resolution than originally targeted, while consuming half the M10K blocks for any future memory-resident variant. This is a worked example of how reasoning-trace continuity reveals optimization opportunities that source code alone cannot. / **C5G の 24 ビット位相分解能はメモリフォーマット由来の人為だった、という発見**——位相累算器ビット幅が議題になったとき、アーキテクトは C5G が M10K ブロック制約（16+8 BRAM 構成）のため 24 ビットを用いたことを思い出した。WPMS の差分エンジンアーキテクチャがビン別パラメータメモリを排除したことで、その制約は消滅した。対話は 32 ビットを選び、選択が当初目標より約 89 倍細かい周波数分解能を生む一方、将来のメモリ常駐変種について M10K ブロック消費を半減することを認識した。これは推論軌跡の連続性が、ソースコード単独では捉えられない最適化機会を明らかにする実例である。

3. **The articulation of "spend richly outside the core" as an explicit principle** — what began as a question about bit widths progressively crystallized into a design principle: where DSP block cost is discrete (1 block or 0 blocks, not fractional), and where the cost does not increase with precision, claim the maximum precision. This principle was named, codified in Chapter 2 § 2.4.3, and added to the chapter's epigraph. / 「コア外では贅沢に」を明示原則として定式化——ビット幅についての問いとして始まったものが、漸進的に設計原則へと結晶化した：DSP ブロックコストが離散的（1 ブロックか 0 ブロック、小数値ではない）で、精度を上げてもコストが増加しないところでは、最大精度を主張せよ。この原則は命名され、第 2 章 § 2.4.3 で成文化され、章のエピグラフに加えられた。

4. **The Tie Decision Pattern, applied at two scales** — the dialogue applied the pattern at two different scales in the same drafting session. At the **architecture scale**, the bin-count question (Compact vs Standard vs Extended modules) was declared a tie at the Implementation Arena level, with Compact selected as the *first reference implementation* without committing the architecture. At the **micro-decision scale**, the Approach A vs Approach B Horner choice (recorded as a tie in the 2026-04-29 trace) was *partially resolved*: Approach B is selected for WPMS specifically, while preserving the tie for future variants. This dual-scale application demonstrated that the pattern is not just a way to defer; it is a way to record context-dependent specialization without erasing prior generality. / **2 つのスケールに適用された引き分け判断パターン**——対話は同じ起草セッションで 2 つの異なるスケールでパターンを適用した。**アーキテクチャスケール**では、ビン数の問い（Compact 対 Standard 対 Extended モジュール）が Implementation Arena レベルで引き分け宣言され、Compact がアーキテクチャをコミットせず*最初のリファレンス実装*として選定された。**マイクロ決定スケール**では、Approach A 対 B の Horner 選択（2026-04-29 軌跡で引き分けとして記録）が*部分的に解決*された：Approach B は WPMS について特定的に選定される一方、引き分けは将来の変種について保持される。この双スケール適用は、パターンが単に決定を先送りする方法ではなく、先行する一般性を消去せずに文脈依存特殊化を記録する方法であることを実証した。

---

## Notable Decision Points / 重要な決定ポイント

### 1. WPMS as the first deliverable / 最初の成果物としての WPMS

| Field | Value |
|---|---|
| **Point** | What should the first deliverable of the FPGA Spectrum Engine project be? |
| **Alternative A** | Full Spectrum Engine (10,240-bin fractal-capable, with HPS and PC integration) — the original architectural target |
| **Alternative B** | WPMS Synthesizer (physical-layer-only, no HPS, no PC) — a strict subset focused on getting sound out |
| **Chosen** | **B (WPMS Synthesizer)** |
| **Rationale** | Three independent reasons converge on the same choice: (1) Earliest path from "repository contents" to "sound coming out of speaker" — minimizes the time during which Hackaday.io readers cannot validate the project. (2) Components built for WPMS (Maclaurin pipeline, sequence-modulation processor, HDMI audio path, AXI input switch) are also components of the eventual full Engine — nothing built here is throwaway. (3) WPMS is structurally simple enough to serve as the first real test of the Open Prompt regeneration loop. The simpler the deliverable, the more confidently we can claim "Layer 1 + Layer 2 + LLM regenerates Layer 3." |

### 2. Bin count and module configuration / ビン数とモジュール構成

| Field | Value |
|---|---|
| **Point** | How many bins should the WPMS Synthesizer support, and across how many parallel modules? |
| **Alternatives** | Compact (2 modules × 2,048 = 4,096 bins); Standard (5 modules × 2,048 = 10,240 bins, C5G-equivalent); Extended (10 modules × 2,048 = 20,480 bins, DE25-nano target) |
| **Chosen** | **Tie at the Implementation Arena level. Compact selected as first reference implementation, by convention not by commitment.** |
| **Rationale** | Logically, the three configurations differ only in a single `generate` parameter at compile time. The Maclaurin pipeline, sequence-modulation processor, summation tree, and bin allocation are all parameterized. **However, implementation reality is not the same as logical equivalence.** Increasing module count brings non-linear pressures: routing congestion, clock-tree skew, BRAM port contention, DSP placement constraints, Fmax erosion. Each module-count threshold is a real engineering frontier; crossing it typically requires implementation-level work (retiming, replication, manual placement, occasionally architectural refinement that raises Fmax — which can in turn unlock the next tier, creating a recursive expansion path). **This is one of the strongest reasons for the existence of Open Prompt as a methodology**: the reasoning behind a specific Fmax breakthrough does not survive in source code alone. By keeping all three configurations in the Arena and starting with Compact, we preserve maximum DSP headroom for the first reference implementation while inviting future Layer 2 traces to record each module-count breakthrough as it happens. |

### 3. Horner variant selection (partial tie resolution) / Horner 変種選定（部分的引き分け解決）

| Field | Value |
|---|---|
| **Point** | Which Horner variant should the Maclaurin pipeline use? |
| **Alternative A** | Textbook Horner: 1 clock per stage, 28-bit fractional precision in 36-bit datapath. Lower precision, lower latency. |
| **Alternative B** | Refactored Horner with constant absorption (Gemini-recommended): 2 clocks per stage (~80 ns overhead), +4 bits fractional via 13× dynamic range compression. Higher precision, higher latency. |
| **Chosen** | **B for WPMS reference implementation; tie preserved at methodology level for future variants.** |
| **Rationale** | The 4,096-bin Compact configuration leaves ample latency headroom (35-clock budget per bin vs. ~17 clocks consumed by 11-stage Approach B at 2 clk/stage). Audio-rate synthesis values precision over latency — 80 ns is inaudible; +4 bits is musically relevant. Future engineers regenerating the synthesizer for latency-critical applications (real-time control loops, active acoustic sensing) may legitimately select Approach A. The methodology rule applied here: **a partial tie resolution does not erase the tie at the methodology level.** The 2026-04-29 reasoning trace's tie remains valid; this dialogue records that "WPMS chose B" without claiming "B is universally correct." |

### 4. Phase accumulator bit width / 位相累算器ビット幅

| Field | Value |
|---|---|
| **Point** | What bit width should the phase accumulator use? |
| **Alternatives** | A: 24 bits (Q0.24, C5G-compatible, ~2.86 mHz resolution, M10K 16+8 construction); B: 26 bits (~0.72 mHz, M10K 18+8); C: 27 bits (~0.36 mHz, M10K 18+9); D: 32 bits (~11.2 µHz, M10K 32-bit single block) |
| **Chosen** | **D (32 bits, Q0.32)** |
| **Rationale** | The C5G 24-bit choice was driven by M10K block constraints when parameters were stored in BRAM (16+8 = 24 bits across two M10K configurations). WPMS uses difference-engine register storage instead of per-bin BRAM, so that constraint does not apply. Once analyzed, 32 bits emerged as the optimal choice across all dimensions: (a) M10K 1-block configuration if BRAM is later added (half the C5G M10K consumption); (b) frequency resolution ~89× finer than the 0.001 Hz original target; (c) integer alignment with float32 OSC messages (forward-compatible with the intermediate-layer phase); (d) DSP 27×27 mode compatibility — when phase increment is a multiplier input, it can be truncated to 27 bits with negligible audible cost. **The architect's reflection on this point became one of the most consequential moments of the dialogue**: "今回のあなたとの協議で明らかになったのは C5G 版は、使用リソースに対する性能の最適化が詰められていなかったということです。" — the 5-year-old C5G choice was correct under its constraints; reopening the design space with current AI collaboration revealed an optimization the original development missed. |

### 5. Internal precision policy: "spend richly outside the core" / 内部精度方針：「コア外では贅沢に」

| Field | Value |
|---|---|
| **Point** | Should the entire WPMS pipeline be constrained to 27-bit operands (DSP-mode efficient), or should the constraint apply only to the Maclaurin core internal multiplies? |
| **Alternative A** | Whole-pipeline 27-bit ceiling: simplest DSP accounting, smallest resource use, but reduces sin(x) output precision and summation-tree precision. |
| **Alternative B** | Constraint applies only to Maclaurin core internal; outside the core, precision is preserved at maximum (Q0.40 sin output, 64–108-bit summation accumulators). |
| **Chosen** | **B** |
| **Rationale** | The architect articulated the underlying principle: **"if DSP cost is the same whether 64-bit or 108-bit, take 108-bit."** Cyclone V's chained-DSP adders implement wide accumulators within a single DSP block; widening from 64 bits to 108 bits costs zero additional DSP. The amplitude multiplier (sin × A_k) instantiates only twice per module (once per output channel), unlike the per-Horner-stage multipliers; doubling its DSP cost is amortized across 2,048 bin computations between instances. This principle, named **Free Precision Floor**, was added to Chapter 2 § 2.4.3 and codified as the chapter's closing epigraph: *"Spend the precision you have for free; constrain only what costs you."* This is a candidate Open Prompt design pattern for the CONTRIBUTING.md pattern catalog. |

### 6. Argument range reduction (four-quadrant) / 引数範囲縮小（4 象限）

| Field | Value |
|---|---|
| **Point** | What input range should the Maclaurin polynomial be evaluated over? |
| **Alternative A** | Full range x ∈ [0, 2π) — C5G's choice. Simple, but Maclaurin truncation error at x = 2π is (2π)¹³/13! ≈ 4 × 10⁻³ — relatively large. |
| **Alternative B** | Range-reduced x' ∈ [0, π/2) using sin's symmetries. Truncation error at x' = π/2 is (π/2)¹³/13! ≈ 4 × 10⁻⁸ — five orders of magnitude smaller. |
| **Chosen** | **B (four-quadrant decomposition)** |
| **Rationale** | The five-orders-of-magnitude error reduction matches the 24-bit DAC quantum (≈ 1.2 × 10⁻⁷), placing the Maclaurin truncation precisely at the audible-precision floor. **Without range reduction, the Maclaurin truncation would dominate the error budget; with range reduction, it ceases to be the dominant source.** This redirects the precision budget toward fixed-point format choices (which are the next dominant source). The implementation cost is two pre-pipeline bits of state (`reflect`, `result_sign`) propagated alongside the data, derivable from the top 2 bits of the phase accumulator. The 2π scaling is absorbed into the formatting of x' (no constant-multiplier DSP block required) — a "free" optimization in the same family as the Free Precision Floor principle. |

### 7. sin(x) output bit width / sin(x) 出力ビット幅

| Field | Value |
|---|---|
| **Point** | At what precision should the Maclaurin core deliver sin(x) to the downstream amplitude multiplier? |
| **Alternative A** | Q0.27 — fits in a single 27×27 DSP block at the amplitude multiplication stage. Compact resource use, but loses precision below 2⁻²⁶. |
| **Alternative B** | Q0.40 — full Maclaurin core internal precision. Amplitude multiplier becomes Q0.40 × Q10.14 = Q10.54, requiring multiple DSP blocks per multiply (but only once per module per output channel). |
| **Chosen** | **B (Q0.40 signed, 41 bits)** |
| **Rationale** | This is the canonical application of the Free Precision Floor principle. The 13 bits of additional precision (Q0.40 vs Q0.27) directly map to better SNR in the final summed output. With 4,096 bins summed, low-order bits matter for the total's precision floor. The 24-bit DAC at the HDMI output ultimately discards bits below 2⁻²³, but **internal precision must exceed DAC precision to avoid quantization noise floor lift**. The amplitude multiplier's increased DSP cost is amortized across 2,048 bin computations between instances, so the cost increase per second is negligible. |

### 8. Camera-block role and architectural treatment / カメラブロックの役割とアーキテクチャ的扱い

| Field | Value |
|---|---|
| **Point** | How should the OV7670 camera input be integrated into the WPMS Synthesizer? |
| **Alternatives** | Direct mapping (camera output → parameter inputs hardcoded); abstracted (camera output → AXI-stream behind input switch, source-selectable at runtime); fully external (camera handled by HPS, only AXI traffic enters FPGA fabric — but HPS is out of scope per Chapter 1) |
| **Chosen** | **AXI-Stream-style input switch behind which the camera is one source among several. Camera block treated as a "Spin-Off-Ready Subsystem."** |
| **Rationale** | The architect identified that camera-driven modulation is genuinely interesting in its own right and could become a separate Open Prompt project ("real-time video processing on FPGA"). The AXI input switch is the structural commitment that allows this: the switch's other inputs (ISSP, future HPS, future external) can take over without the camera block's removal damaging the synthesizer. **This is a new Open Prompt design pattern**, candidate name: *Spin-Off-Ready Subsystem Pattern*. Chapter 1 § 1.9 records both the immediate role (stimulus source for parameter modulation in the WPMS phase) and the spin-off pathway (the same block can fork into an independent project). |

### 9. Required vs Optional input interface partition / 必須対オプション入力インターフェース分割

| Field | Value |
|---|---|
| **Point** | Should the camera input be a required part of the Layer 1 specification, or optional? |
| **Alternative A** | Required: every reference implementation must support OV7670. |
| **Alternative B** | Required-subset (DIP+buttons, ISSP, ISMCE) plus optional extension (camera). |
| **Chosen** | **B** |
| **Rationale** | A reader should be able to write the `.rbf` to a DE10-nano and hear sound *without buying or wiring an OV7670*. Making camera required would gate the entire deliverable on additional hardware acquisition. Making it optional preserves the path-to-sound minimality (Chapter 1 Intention 1) while inviting the camera experiment for engaged readers. The optional partition also crisply separates the synthesizer's testing burden: the required interfaces must work correctly to declare the implementation valid; the camera extension is best-effort. |

### 10. Pipeline depth budget margin / パイプライン深度予算余裕

| Field | Value |
|---|---|
| **Point** | The Approach B Maclaurin pipeline uses 16 clocks of latency. How much should be reserved? |
| **Alternative A** | Tight budget: ~17 clocks reserved (just enough for Standard configuration's expected retiming requirements). |
| **Alternative B** | Generous budget: 30-clock total budget, 14 clocks reserved beyond the 16-clock implementation. |
| **Chosen** | **B (30-clock budget, 14-clock reserve)** |
| **Rationale** | The 35-clock-per-bin budget at 100 MHz × 20.833 µs / 2,048 bins is generous; reserving margin proportionally is cheap. The reserved margin absorbs (a) unforeseen retiming requirements during synthesis, (b) Standard-configuration timing pressure when 5 modules contend for routing resources, (c) Extended-configuration stretch cases. **Pipeline depth is "engineering insurance"** — once exhausted, recovering it requires architectural change. Generous reserve at Layer 1 specification time costs nothing at compile time and protects against unbounded future cost. |

---

## Major Themes / 主要テーマ

### Theme 1 — Self-application of Open Prompt methodology / Open Prompt 方法論の自己適用

This drafting dialogue exemplifies what Open Prompt looks like in active practice. The synthesizer's specification is being constructed through dialogue that will itself become Layer 2 of the synthesizer's repository. Future engineers regenerating the WPMS Synthesizer will:

本起草対話は、活動的な実践における Open Prompt がどのようなものかを例示する。シンセサイザーの仕様は、それ自体がシンセサイザーのリポジトリの第 2 層となる対話を通して構築されている。WPMS シンセサイザーを再生成する将来のエンジニアは：

1. Read Chapters 1 and 2 to understand *what* to build / 第 1 章と第 2 章を読んで*何を*構築するかを理解する
2. Read this trace to understand *why* each decision was made / 本軌跡を読んで*なぜ*各決定がなされたかを理解する
3. If their constraints differ (different FPGA, different latency requirements, different DSP budget), they can revisit specific decisions and re-derive a variant that fits / 制約が異なる場合（異なる FPGA、異なるレイテンシ要件、異なる DSP 予算）、特定の決定を再訪し、自身の状況に適合する変種を再導出できる
4. Their re-derivation, if recorded, becomes a sibling Layer 2 trace, with the original choices preserved as Implementation Arena variants / 彼らの再導出は、記録されれば兄弟第 2 層軌跡となり、元の選択は Implementation Arena 変種として保持される

The recursive structure of Open Prompt repositories — "the dialogue that produced Open Prompt becomes Open Prompt's first Layer 2 example" — extends here: "the dialogue that drafted the synthesizer becomes the synthesizer's regeneration manual."

Open Prompt リポジトリの再帰構造——「Open Prompt を生み出した対話が Open Prompt の最初の第 2 層の例となる」——はここで拡張される：「シンセサイザーを起草した対話がシンセサイザーの再生成マニュアルとなる」。

### Theme 2 — The C5G optimization gap / C5G 最適化ギャップ

A recurring observation through the dialogue: the C5G prototype, while a successful proof-of-existence, was not optimized to its constraints. Three concrete optimizations emerged in this drafting session that were not present in the C5G implementation:

対話を通じた繰り返し観察：C5G プロトタイプは、存在証明としては成功した一方、その制約に最適化されていなかった。本起草セッションで、C5G 実装には存在しなかった 3 つの具体的最適化が生まれた：

1. **Argument range reduction (four-quadrant)** — C5G evaluated Maclaurin over the full [0, 2π) range, accepting a (2π)¹³/13! ≈ 4 × 10⁻³ truncation error. WPMS evaluates over [0, π/2), reducing the truncation error to ≈ 4 × 10⁻⁸ — five orders of magnitude. / **引数範囲縮小（4 象限）**——C5G は完全な [0, 2π) 範囲でマクローリンを評価し、(2π)¹³/13! ≈ 4 × 10⁻³ の打ち切り誤差を受容していた。WPMS は [0, π/2) で評価し、打ち切り誤差を ≈ 4 × 10⁻⁸ に削減——5 桁の改善。
2. **32-bit phase accumulator** — C5G used 24 bits because of M10K BRAM construction (16+8). WPMS uses register-resident phase, freeing the choice; 32 bits gives ~89× finer resolution while consuming half the M10K blocks if BRAM-resident variants are added later. / **32 ビット位相累算器**——C5G は M10K BRAM 構成（16+8）のため 24 ビットを用いた。WPMS はレジスタ常駐位相を用い、選択を解放する；32 ビットは将来 BRAM 常駐変種が追加される場合、M10K ブロック消費を半減する一方、約 89 倍細かい分解能を与える。
3. **Free Precision Floor for Q0.40 sin output** — C5G truncated sin(x) earlier to fit a tighter DSP budget across 5 modules. WPMS, with 2 modules, has DSP headroom to preserve full Q0.40 precision into the amplitude multiplier. / **Q0.40 sin 出力の無料精度床**——C5G は 5 モジュールにわたるよりタイトな DSP 予算に収めるため、より早く sin(x) を切り詰めていた。WPMS は 2 モジュールで、振幅乗算器に完全な Q0.40 精度を保持する DSP 余裕を持つ。

**The architect's response to this** — "今回のあなたとの協議で明らかになったのは C5G 版は、使用リソースに対する性能の最適化が詰められていなかったということです" — is an exemplary statement of how Open Prompt enables design re-examination. The C5G choices were not wrong under their constraints (limited time, exploratory phase, no AI collaborator); they were locally optimal. Re-opening the design space with current methodology revealed global optima that had been masked by the original constraint set.

**この点に対するアーキテクトの応答**——「今回のあなたとの協議で明らかになったのは C5G 版は、使用リソースに対する性能の最適化が詰められていなかったということです」——は、Open Prompt がいかに設計再検討を可能にするかの模範的言明である。C5G の選択は当時の制約（限られた時間、探索段階、AI 協働者なし）の下で誤りではなかった。それは局所最適であった。現代の方法論で設計空間を再開放することで、元の制約セットによりマスクされていた大域最適が明らかになった。

### Theme 3 — Two new candidate Open Prompt design patterns / 2 つの新しい Open Prompt 設計パターン候補

The drafting dialogue produced two candidate design patterns that should be considered for inclusion in CONTRIBUTING.md alongside the existing Tie Decision Pattern and Polynomial Bin-Sequence Pattern:

起草対話は、既存の引き分け判断パターンと多項式ビン系列パターンと並んで、CONTRIBUTING.md への含有を検討すべき 2 つの設計パターン候補を生み出した：

**Pattern A — Free Precision Floor:**

**パターン A — 無料精度床：**

Where a hardware resource cost is discrete (1 unit or 0 units, not fractional), and where the cost does not increase with internal precision (e.g., a wider accumulator inside a single DSP block), claim the maximum precision. The opposite — accepting reduced precision because "we don't need that much" — leaves precision on the table that was free to claim. The pattern instructs: **before deciding what precision is needed, check whether higher precision is free; if so, take it.**

ハードウェアリソースコストが離散的で（1 単位か 0 単位か、小数値ではない）、コストが内部精度とともに増加しない場合（単一 DSP ブロック内のより広い累算器など）、最大精度を主張せよ。その反対——「そんなに必要ない」と精度削減を受容すること——は、無料で主張できた精度をテーブルに残す。パターンは指示する：**何の精度が必要かを決定する前に、より高い精度が無料かどうかを確認せよ；そうであれば、それを取れ。**

**Pattern B — Spin-Off-Ready Subsystem:**

**パターン B — 暖簾分け準備済みサブシステム：**

When a subsystem could plausibly be developed as an independent project — has its own internal logic, its own audience, its own evolution trajectory — but is being integrated into a larger project for now, structure the integration so that the subsystem can be forked out later without damage. The pattern manifests in: (a) a clear interface boundary (in WPMS's case, the AXI input switch); (b) explicit acknowledgment in the documentation that this subsystem is fork-friendly; (c) avoidance of dependencies that would require the larger project's continuation for the subsystem to make sense.

サブシステムが独立プロジェクトとして発展し得る場合——独自の内部ロジック、独自の聴衆、独自の発展軌跡を持つ——しかし当面より大きなプロジェクトに統合される場合、サブシステムが後に損傷なくフォーク可能であるよう統合を構造化せよ。パターンは以下に現れる：(a) 明確なインターフェース境界（WPMS の場合、AXI 入力スイッチ）、(b) 文書におけるこのサブシステムがフォークに優しいという明示的承認、(c) サブシステムが意味をなすためにより大きなプロジェクトの継続を要求するであろう依存関係の回避。

### Theme 4 — Deferred decisions as a discipline / 規律としての先送り決定

Both Chapter 1 and Chapter 2 contain explicit "Open Questions Carried Forward" tables. This is a discipline, not laziness:

第 1 章と第 2 章の両方が明示的な「持ち越される未解決問題」表を含む。これは規律であり、怠惰ではない：

- **Empirical questions** (e.g., audible bias from truncation policy) require measurement, not deduction. They cannot be resolved at specification time without manufacturing pseudo-precision. / **経験的問題**（切り詰め方針からの可聴バイアスなど）は推論ではなく測定を要求する。仕様時に擬似精度を製造することなく解決できない。
- **Downstream-context questions** (e.g., whether folded "X = (2π·ξ)²" is feasible) require Chapter 4's structure to be settled first. Premature decisions would over-constrain the downstream chapters. / **下流コンテキスト問題**（畳み込み「X = (2π·ξ)²」が実現可能かなど）は、第 4 章の構造がまず確定することを要求する。早すぎる決定は下流章を過剰制約する。
- **Variant-implementation questions** (e.g., 9th-order microcontroller-class variant) belong to alternate paths, not the main path. Recording them as Open Questions invites future implementers to take them up without expecting them as part of the reference implementation. / **変種実装問題**（9 次マイクロコントローラ級変種など）は、主経路ではなく代替経路に属する。それらを未解決問題として記録することは、将来の実装者にリファレンス実装の一部として期待することなく取り上げるよう招待する。

**The discipline is to record what is not decided, with as much clarity as what is decided.** A Layer 1 specification that quietly omits open questions misleads future implementers; one that lists them honestly invites collaborative completion.

**規律は、決定されたものと同じくらい明確に、決定されていないものを記録することである。** 未解決問題を静かに省略する第 1 層仕様は将来の実装者を誤導する；それらを誠実に列挙するものは協働的完成を招待する。

### Theme 5 — Hackaday.io engagement signal / Hackaday.io エンゲージメントシグナル

After Chapters 1 and 2 were posted to Hackaday.io as Build Logs, page views rose from ~30/day to 80–90/day, and follower count doubled (2 → 4). This is a noteworthy data point in the methodology's evaluation: **technical density did not deter readers; it attracted them.** The Hackaday.io audience self-selects for engineers who want depth; reducing depth to broaden appeal would be misaligned with this audience.

第 1 章と第 2 章が Build Log として Hackaday.io に投稿された後、ページビューは約 30/日から 80〜90/日に上昇し、フォロワー数は倍増した（2 → 4）。これは方法論の評価における注目すべきデータポイントである：**技術的密度は読者を遠ざけず、引き付けた。** Hackaday.io の聴衆は深さを求めるエンジニアに自己選択している；魅力を広げるために深さを削減することは、この聴衆と整合しない。

This signal supports a hypothesis worth recording: **Open Prompt's value proposition (deep specifications + reasoning traces, not just artifacts) is well-matched to the Hackaday-class engineering audience.** The methodology's primary distribution channel and its structural form may be co-evolved.

このシグナルは記録に値する仮説を支持する：**Open Prompt の価値提案（単なるアーティファクトではなく、深い仕様＋推論軌跡）は、Hackaday クラスのエンジニア聴衆と良くマッチする。** 方法論の主要な配布チャネルとその構造的形式は共進化し得る。

---

## Resumption Hooks / 再開フック

### Hook A — Chapter 3 (Sequence-Modulation Pipeline Processor) / 第 3 章（数列変調パイプラインプロセッサ）

The next chapter must specify the difference-engine processor that produces the Q0.32 phase accumulator value (Chapter 2's input contract) for each bin every clock. Five sub-questions are anticipated:

次章は、各ビンについて毎クロック Q0.32 位相累算器値（第 2 章の入力契約）を生成する差分エンジンプロセッサを仕様化しなければならない。5 つのサブ問題が予期される：

1. Bit widths for the nine scalar parameters (α, β, γ, δφ, ψ, f₀, A₀, φ₀) and the count parameter N / 9 個のスカラーパラメータ（α, β, γ, δφ, ψ, f₀, A₀, φ₀）と数量パラメータ N のビット幅
2. Internal accumulator bit widths for the difference recurrences (likely wider than 32 bits to preserve α·k² accumulation precision over N bins) / 差分漸化式のための内部累算器ビット幅（N ビンにわたる α·k² 累積精度を保つため、おそらく 32 ビットより広い）
3. Amplitude A_k computation: linear-domain DSP multiply per bin vs. log-domain accumulation / 振幅 A_k 計算：ビンごとの線形領域 DSP 乗算 対 対数領域累算
4. Instruction set / register architecture for the general-purpose pipeline processor — designed for forward compatibility with fractal synthesis and SDFT modes / 汎用パイプラインプロセッサの命令セット／レジスタアーキテクチャ——フラクタル合成および SDFT モードとの前方互換性のために設計
5. Parameter ingestion from the AXI input switch (protocol details, write atomicity, parameter validation) / AXI 入力スイッチからのパラメータ取り込み（プロトコル詳細、書き込みアトミック性、パラメータ検証）

**Starting question**: What bit width should α use, given that α·k² accumulates over k = 0...N−1 (with N up to 2,048), and that the result must remain bounded within the Q0.32 phase accumulator range without losing precision in the small-α regime?

### Hook B — Empirical validation against the 2020 Dirichlet recording / 2020 年 Dirichlet 録音に対する経験的検証

Chapter 2 § 2.8.3 designates the 2020 Dirichlet kernel waveform as the verification anchor. To make this operational, a measurement protocol is needed: how is "RMS difference of output PCM against reference recording" computed? What threshold qualifies as "passing"? How is the 2020 recording itself archived?

第 2 章 § 2.8.3 は 2020 年 Dirichlet カーネル波形を検証アンカーに指定する。これを動作可能にするため、測定プロトコルが必要である：「参照録音に対する出力 PCM の RMS 差」はどう計算されるか？ 何の閾値が「合格」を構成するか？ 2020 年録音自体はどうアーカイブされるか？

**Starting question**: What level of waveform difference (RMS dB, or peak deviation) constitutes a passing match between a regenerated WPMS Synthesizer's KEY[1] output and the 2020 reference, given that the regeneration may use different precision choices, different DSP placement, or different synthesis tools?

### Hook C — Free Precision Floor pattern formalization / 無料精度床パターンの形式化

The pattern was named in this dialogue and codified in Chapter 2 § 2.4.3. Adding it to CONTRIBUTING.md alongside Tie Decision Pattern and Polynomial Bin-Sequence Pattern requires a worked example template. The dialogue contains the WPMS-specific instances; formalizing requires extracting the abstract structure.

パターンは本対話で命名され第 2 章 § 2.4.3 で成文化された。引き分け判断パターンと多項式ビン系列パターンと並んで CONTRIBUTING.md に追加するには、具体例テンプレートが要求される。対話は WPMS 特定のインスタンスを含む；形式化には抽象構造の抽出が要求される。

**Starting question**: Articulate the Free Precision Floor pattern abstractly: when does it apply, when does it not, and what are its failure modes (e.g., taking maximum precision when it requires asymmetric resource costs that compound elsewhere)?

### Hook D — Spin-Off-Ready Subsystem pattern formalization / 暖簾分け準備済みサブシステムパターンの形式化

Same as Hook C but for the camera block pattern. The pattern encompasses (a) interface boundary discipline, (b) documentation discipline, (c) dependency discipline. Formalizing it in CONTRIBUTING.md will let future Open Prompt projects identify their own spin-off candidates early.

Hook C と同じだがカメラブロックパターンについて。パターンは (a) インターフェース境界規律、(b) 文書化規律、(c) 依存関係規律を包含する。CONTRIBUTING.md でこれを形式化することで、将来の Open Prompt プロジェクトが自身の暖簾分け候補を早期に識別できるようになる。

**Starting question**: What is the difference between a Spin-Off-Ready Subsystem and a "modular component"? The latter is mainstream software-engineering practice; what makes the former specifically Open Prompt?

### Hook E — Module-count breakthrough Layer 2 traces / モジュール数突破第 2 層軌跡

Chapter 1 § 1.5 anticipates that each module-count tier (Compact → Standard → Extended) will require its own Layer 2 trace recording the Fmax-threshold breakthrough. These traces do not yet exist; they will emerge as implementation progresses.

第 1 章 § 1.5 は、各モジュール数階層（Compact → Standard → Extended）が独自の Fmax 閾値突破を記録する第 2 層軌跡を要求することを予期する。これらの軌跡はまだ存在しない；実装が進むにつれて現れる。

**Starting question**: When the first Compact-to-Standard scaling attempt happens, what specific timing-closure failures or routing-congestion symptoms should be looked for as the "tell" that an Fmax threshold has been hit? What is the recommended diagnostic flow?

---

## End of Trace / 軌跡の末尾

> *Code is ephemeral; the knowledge architecture is the commons.*
> *コードは一時的なものであり、知識アーキテクチャこそが共有財産である。*

> *Spec is what; trace is why; together they regenerate.*
> *仕様は何を、軌跡はなぜを、そして合わさって再生成する。*

This trace is released into the public domain under CC0 1.0 Universal. Replay it. Resume it. Surpass it.

本軌跡は CC0 1.0 Universal のもとパブリックドメインに公開される。再生せよ。再開せよ。超えてゆけ。
