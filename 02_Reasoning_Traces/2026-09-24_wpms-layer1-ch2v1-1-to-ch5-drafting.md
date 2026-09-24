# WPMS Layer 1 Drafting — Chapter 2 v1.1 through Chapter 5
# and the Customer–Profile Boundary with PTSG-WPMS-Formation
# WPMS 第1層起草 — 第2章 v1.1 〜 第5章、および PTSG-WPMS-Formation との顧客–プロファイル境界

## Trace Metadata / 軌跡メタデータ

| Field | Value |
|---|---|
| **Dates / 日付** | 2026-09-04 → 2026-09-24 (prelude: 2026-05, summarized) |
| **Participants / 参加者** | **Tsuneo Ohnaka (大中庸生)** — FPGA architect, 40+ years; orchestrator and ruling authority. **Claude (Anthropic)** — WPMS amanuensis, customer side. **PTSG-WPMS-Formation amanuensis** — a separate Claude session owning the L2 profile; its messages were relayed by the architect. |
| **Model record / モデル記録** | Turns of 2026-09-23 and 2026-09-24 (Ch.2 v1.1 – Ch.5, this trace, the oracle): **Claude Opus 5.5**. Earlier turns of the same thread (2026-05, 2026-09-04) may have run on other Claude models; the thread does not record which. The model of the profile session is not recorded here. |
| **Topic / トピック** | Drafting of WPMS Layer 1 Chapter 2 v1.1 (errata), Chapter 3 (L1 difference engine and L2 binding), Chapter 4 (output path), Chapter 5 (boundary, input switch, address map); customer requirements to PTSG-WPMS-Formation |
| **Status / 状態** | Layer 2 trace — single-AI drafting with relayed inter-session correspondence |
| **Direct outputs / 直接成果物** | `WPMS_Layer1_Chapter2_Maclaurin_Pipeline_v1_1.md`, `WPMS_Layer1_Chapter3_L1_Engine_and_L2_Binding.md`, `WPMS_Layer1_Chapter4_Output_Path.md`, `WPMS_Layer1_Chapter5_Boundary_and_Address_Map.md`, `wpms_layer1_oracle.py` (proposed path `04_Verification/oracle/`) |
| **Related repositories** | FPGA_Spectrum_Engine_OpenPrompt (this); PTSG-WPMS-Formation (L2 profile: register map v0.2, Decision Register W v0.5) |
| **License / ライセンス** | CC0 1.0 Universal (Public Domain) |

---

## Reading Notes / 読解上の注

**Who this trace is for.** Two readers in particular: (1) the **PTSG-WPMS-Formation amanuensis**, about to read Layer 1 Chapters 1–5 in full and rule on the customer requirements; (2) **Claude Code** or any context-isolated agent that opens this repository to generate HDL, testbenches or tools. Both will meet documents that appear to contradict each other. They do not; they record different moments and different owners. This trace is the map.

**本軌跡の読み手。** (1) 第 1 層第 1〜5 章を通読し顧客要求を裁定する PTSG-WPMS-Formation 祐筆殿、(2) HDL・テストベンチ・ツールを生成するためにリポジトリを開く Claude Code などコンテキスト非共有のエージェント。両者は互いに矛盾して見える文書に出会うが、それは異なる時点と異なる所有者を記録しているためで、本軌跡がその地図になる。

**Read in this order.** § Precedence → § Ruling State → § Supersession History → § Naming Map → the decision points you need → § Evidence (run the oracle).

**この順に読む。** 優先順位 → 裁定状態 → 置き換え履歴 → 名称対応 → 必要な決定点 → 根拠（オラクルを実行）。

---

## Precedence (proposed) / 優先順位（提案）

1. **Layer 1 chapters state the customer's requirements; the L2 register map states what the profile currently implements.** Neither silently overrides the other. Where they differ, the difference is a pending ruling, listed in § Ruling State. / 第 1 層の章は顧客の要求を、L2 レジスタマップはプロファイルの現状を述べる。どちらも他方を黙って上書きしない。
2. **Within Layer 1, the later version supersedes the earlier** (Ch.2 v1.1 > v1.0). Chapter 5 Appendix 5.A is the consolidated state as of 2026-09-24. / 第 1 層内では新版が旧版に優先。付録 5.A が 09-24 時点の集約。
3. **The architect's rulings resolve differences.** Until ruled, an agent generating code should implement the Layer 1 requirement *and* flag the difference, never pick one side silently. / 裁定が差異を解決する。裁定前は、第 1 層の要求を実装しつつ差異を明示し、黙って一方を選ばない。

---

## Prelude — 2026-05 (summarized; not previously archived here) / 前史

The Chapter 3 dialogue of May 2026 opened when the architect presented the **PTSG** specification (four opcodes; Stay separating time from state; shadow execution during Stay; 16 timing signals; a one-bit external Condition). Claude recognized it as a general-purpose control architecture, a third path between HDL FSMs and soft CPUs, and unusually easy for an LLM to program. The architect chose **Approach 1** (fixed pipeline, Stay-counted) for WPMS and kept Approach 2 (per-element routing) as a trailer of what PTSG makes possible.

The architect then introduced the **period layers** — L1 bin (100 MHz), **L2 packet (new)**, L3 sample (48 kHz), L4 control (≈ 1 kHz) — and the question that governs Chapter 3: *at which layer should each coefficient be computed?* He placed the Gaussian's exp() initial values (A₀, M₀, C) at L4 and the recurrences A_{k+1} = A_k·M_k, M_{k+1} = M_k·C at L1. Claude proposed Upper/Lower PTSG instances; the architect agreed (same IP, two instances, differences absorbed by parameters), decided to **spin PTSG off** as its own Open Prompt repository and Hackaday.io project, and separated sessions: this session became a **PTSG user**. Customer requirements R1–R7 and W1–W2 were written; a spin-off Build Log announced the decision.

On 2026-05-06 Hackaday.com featured the project ("Taking Polyphony To A New Level", Jenny List: *an SDR for the world of acoustics*). On 2026-05-30 the architect's Build Log "The Despair of a 300-Meter-Long Hammond Organ" presented the four-layer architecture publicly.

2026 年 5 月の第 3 章対話は、設計者による PTSG 仕様の提示で始まった。設計者は周期レイヤー（L2 パケットは新概念）と「各係数をどのレイヤで求めるべきか」という問いを導入し、PTSG を暖簾分けし、本セッションを PTSG の利用者とした。5 月 6 日に Hackaday.com 本誌掲載。

---

## Timeline / 時系列

| Date | Event |
|---|---|
| 09-04 | Architect returns: PTSG-Core in on-board debug; path Core → CPU-Formation → **PTSG-WPMS-Formation = the L2 Formation**. The profile amanuensis sends three points: (1) a unified correction of Ch.2 § 2.5's clock-budget wording; (2) *the f → φ mapping belongs to no one*; (3) it will supply the ISA-visible register map, leaving Q and wiring to Ch.3. Claude accepts (1), lists owners A/B/C for (2). The profile adds: 1/48000 is a constant, so the mapping is one MAC by a reciprocal anywhere — **the deciding factor is who knows Fs and at which period f changes.** The architect rules **L4 outside WPMS**, first realized as a verification tool (a new Open Prompt Layer 4). Deliverable 1 (register map v0.1) arrives; Claude answers as customer (Q column, RT.OUT numbering, slot set complete, Mode T supported, Ch.2 errata; recorded by the profile as the "09-07 answers"). |
| 09-23 | Repository PTSG-WPMS-Formation published (register map v0.2, Decision Register W v0.5, oracle CLEAN). Architect ratifies the Q proposals (**W-R10**) and asks for Ch.2 v1.1 first; Deliverables 2–3 not yet issued. Claude issues **Ch.2 v1.1**. Architect asks for the **full Chapter 3**, with undecided points stated top-down as customer requirements. Claude drafts Ch.3 and, in doing so, **retracts its own ratified amplitude proposal** (§ DP-3). |
| 09-24 | Architect rules **C3-D1 Fixed**; defers amplitude and the relay of requirements until Ch.4 is seen; the profile will read Layer 1 in full after Ch.5. Claude drafts **Ch.4**: the log-domain amplitude meets no obstacle on the way out and helps (master gain = one adder). Architect approves the **MiSTer boundary** (regenerate, do not copy) and the **latency disclosure**. Claude drafts **Ch.5** with Appendix 5.A for the full review, then this trace and the consolidated oracle. |

---

## Ruling State as of 2026-09-24 / 2026-09-24 時点の裁定状態

| Item | State |
|---|---|
| L4 outside WPMS; realized first as a verification tool (Open Prompt Layer 4) | **Ruled** 09-04 |
| W-R10 phase part: PH\*/OM\* Q0.32 modular; RT.OUT bit 0 = L, bit 1 = R | **Ruled** 09-23, stands |
| W-R10 amplitude part: A0 Q1.31; AR1/AR2/E0 Q4.28; SHV = 28 | Ruled 09-23; **superseded by the Ch.3 proposal; re-ruling pending** |
| Ch.2 v1.1 first (W-R11) | **Ruled** 09-23; issued |
| C3-D1: only phase- and log-domain integers cross the WPMS boundary | **Ruled Fixed** 09-24 |
| C3-D4 / CR3-A1: amplitude in the log₂ domain | **Pending** — full review |
| Relay of CR3-xx and CR5-xx to the profile | **Pending** — full review (Appendix 5.A) |
| C4-D11: MiSTer framework is prior art; the four HDMI-side blocks are regenerated | **Ruled** 09-24 |
| C4-D10: latency stated as compute 1 period / 1.031 periods to the wire / sink separately | **Ruled** 09-24 (to be used in publication) |
| CR5-L1: level glide, LPT at +0x9 | **Pending** — profile feasibility (clamp, N_min) |
| All other C3-D\*, C4-D\*, C5-D\* | Drafted within the chapters' own scope; subject to the full review |

---

## Supersession History / 置き換え履歴

| Was | Became | Where | Why |
|---|---|---|---|
| Amplitude linear: A0 Q1.31, AR1/AR2/E0 Q4.28 (customer proposal 09-04/07, ratified 09-23) | **log₂ domain**: LP, LAD1, LAD2, LE0, LS0 (+0xF) | Ch.3 § 3.5 | the linear forward recurrence underflows (σ = 71 bins → silent), is a loop-carried multiply, and compounds truncation as k² |
| LP ← LP + LE0 (free slope) | LP steps toward **LPT** (+0x9) at rate LE0 ≥ 0 | Ch.5 § 5.3.2, CR5-L1 | continuity without [S] writes; cannot run away |
| CR3-C2 (two update classes) | **CR5-I1** (per-slot mask) | Ch.5 § 5.10 | level and phase need separate control |
| CR3-C3 (test origin inside the profile) | **CR5-R1** (empty sweeps after reset; ROM port loads the test origin) | Ch.5 § 5.8 | no special logic in the profile |
| MiSTer HDMI core as starting code (Ch.1 § 1.3) | **prior art only; regenerate** | Ch.4 § 4.2.1 | GPL vs MIT Layer 3 |
| ISSP as the parameter write path (Ch.1 § 1.8) | **JTAG memory-mapped master**; ISSP for probes/knobs | Ch.5 § 5.7 | hundreds of slots need addressable writes |
| "AXI-Stream-style input switch" (Ch.1 § 1.9) | **four-port memory-mapped switch with ownership** | Ch.5 § 5.5 | several sources play at once |
| Camera maps to δφ, ψ as positions | camera writes **velocities** through OMD1/OMD2 (no [S] writes) | Ch.5 § 5.9 | § 5.3.3 identity |
| Ch.2 § 2.5 "35-clock per-bin budget", "~17 cycles" | 2,083 clocks vs 2,048 bins; 35-clock margin; 16-clock depth is latency | Ch.2 v1.1 | profile amanuensis's correction |
| Ch.2 amplitude Q10.14 | Q1.31 | Ch.2 v1.1 | C5G artifact; Free Precision Floor |
| Upper / Lower PTSG | L1 pipeline / L2 Formation / L4 Formation (outside WPMS) | Ch.3 § 3.1 | ecosystem vocabulary; 09-04 ruling |

---

## Decision Points / 決定点

Compact form; each row names the chapter section that holds the full reasoning. / 簡潔形。詳しい推論は各章の該当節にある。

| # | Point | Alternatives | Chosen | Rationale |
|---|---|---|---|---|
| DP-1 | Owner of f → φ | A: L4 · B: L2 page · C: host | **Only phase/log integers cross the boundary; L4 converts** (C3-D1) | the profile's insight: cost is one reciprocal MAC anywhere; the decisive question is who knows Fs and when f changes |
| DP-2 | Place of L4 | inside WPMS (Upper PTSG) · outside | **Outside**, as a verification tool first | L4's functions are many; keep the earliest-sound path short (architect) |
| DP-3 | Amplitude representation | linear geometric (ratified) · log₂ | **log₂**, level + shape split — *retracting the customer's own ratified proposal* | underflow: γ = 1e-4 gives a₀ ≈ 3×10⁻⁴⁶ → Q1.31 0 → silent; loop-carried multiply; 0.58 % bias even when representable. Log: exact integers, adders only |
| DP-4 | Log-domain formats | one format · per-slot formats | LP, LE0 Q6.26 · LAD1 Q8.24 · LAD2 Q2.30 · LS0 Q12.20 · internal 54-bit Q23.30 | range for LS0, resolution for LAD2 and slow decays; alignment shifts are wiring |
| DP-5 | Block selection | Mode W (window) · Mode T (table-direct) | **Mode T** (profile's recommendation; customer concurs) | three times cheaper; N_min ≈ 32 |
| DP-6 | Closing a sample | sweep-end token · synchronized strobe | **Strobe** | no extra lane; empty sweeps close at zero |
| DP-7 | Packet boundary gap g | tolerate · require 0 | **Require g = 0** (CR3-T1) | full-load slack is 7 clocks; g = 1 consumes it all |
| DP-8 | Master of L3 | divide clk_sys · audio domain | **Audio domain**; strobe S_m = F_m − 1 SCLK; stability-window handoff | 100 MHz / 48 kHz is not an integer; 1-period compute latency reaches the wire in 1.031 periods |
| DP-9 | Master gain | linear multiplier · log adder | **MG in log₂, one adder**, target + slew; soft mute | exact, no DSP, constant-dB/s fades |
| DP-10 | MiSTer HDMI blocks | copy · regenerate | **Regenerate** from datasheet + Ch.4 | license boundary; itself an Open Prompt demonstration |
| DP-11 | Latency claim | "1 sample" unqualified · defined intervals | **Defined intervals**, sink reported separately | honest publication (architect: also useful as publicity) |
| DP-12 | Update granularity | two classes · per-slot mask | **16-bit slot mask + RT.OUT bit** | level vs phase vs frequency are independent concerns |
| DP-13 | Level continuity | writer-side slope + readback · Formation-side target glide | **Formation glide** (CR5-L1) | a missed update parks the level instead of letting it run away |
| DP-14 | Host write path | ISSP · JTAG memory-mapped master | **JTAG MM master**; ISSP for probes | addressable writes; vendor IP instantiated, not copied |
| DP-15 | Test origin | profile logic · ROM port | **ROM port** (port 3), ISMCE-editable preset | reset restores the regression anchor |
| DP-16 | Input switch | single selectable source · multi-port with ownership | **Four ports, ownership per block** | host composes, camera modulates, HPS later |
| DP-17 | Camera template | positions (δφ, ψ) · velocities | **Velocities**, no [S] writes | δφ̇ ≡ 2πΔf, ψ̇ ≡ 2πα (verified) |

---

## Naming Map / 名称対応

| Earlier name | Current name | Notes |
|---|---|---|
| A0 (+0x2) | **LP** | Q6.26, log₂ level, [S] |
| AR1 (+0x3) | **LAD1** | Q8.24, first difference of the shape |
| AR2 (+0x4) | **LAD2** | Q2.30, second difference |
| E0 (+0x5) | **LE0** | Ch.3: slope; Ch.5 (CR5-L1): rate ≥ 0 |
| reserved (+0x9) | **LPT** | Q6.26 level target (CR5-L1) |
| reserved (+0xF) | **LS0** | Q12.20 shape offset at k = 0 (CR3-A1) |
| Upper PTSG | L4 Formation | outside WPMS |
| Lower PTSG | L2 Formation | = PTSG-WPMS-Formation |
| "sequence-modulation pipeline processor" (Ch.1 § 1.7) | L1 difference engine + L2 Formation | |
| "phase accumulator φ_k" (Ch.2) | evaluated phase Φ_k(n) | no per-bin state |
| "AXI-Stream-style input switch" (Ch.1 § 1.9) | four-port input switch | Ch.5 § 5.5 |

Symbols: S_m L3 strobe · F_m I2S frame boundary · Δ_pre = 1 SCLK · T_min = 2,083 · g packet-boundary gap · T_wake · D_L1 · MG master gain · G coarse gain · N_p, P packet length and count.

---

## Evidence — the Oracle / 根拠——オラクル

`wpms_layer1_oracle.py` reproduces every [Evidence: oracle] number of Ch.2 v1.1 – Ch.5 and checks it against the chapter: **18 checks, all PASS, about 3 s** (Python 3; numpy only for CH4-CREST). A deliberately wrong expectation produces FAIL and exit status 1. The file also contains readable **reference models** — `exp2_q131`, `l1_amplitude`, `l1_phase`, `step_toward`, `gaussian_slots` — usable as golden models for testbenches.

`wpms_layer1_oracle.py` は第 2 章 v1.1〜第 5 章の [Evidence: oracle] の数値をすべて再現し、章の値と照合する。18 項目すべて PASS、約 3 秒。参照モデルはテストベンチの黄金モデルとして使える。

| Check | Certifies |
|---|---|
| CH2-CLOCK, CH2-WIDTH | 2,083 / 35 / 19; Q1.71 → Q1.63; Q12.63 / Q13.63 / Q15.63 |
| CH3-ORIGIN | OM0 = 89,120,571; OMD1 = 350; LP = −2,948,988; 255.653 s period |
| CH3-UNDERFLOW, CH3-LINBIAS | the linear domain silences σ = 71; 0.58 % bias at σ = 224 |
| CH3-LOGEXACT, CH3-PHASE | exact forward differences; 54-bit bound; zero phase drift |
| CH3-EXP2, **CH3-E2E** | ≤ 12 LSB, ≤ 2⁻²⁴ relative; **σ = 71 plays: 927 audible bins** |
| CH3-BUDGET, CH3-QFMT | slack 7 / 0; legal loads for g = 0…3; slot resolutions |
| CH4-CREST, CH4-MG, CH4-LATENCY | 36.1 / 5.6 / 12.2 dB; 13,933 → 1.000 s fade; 21.484 µs |
| CH5-VELOCITY, CH5-GLIDE, CH5-MASK, CH5-MAP | δφ̇ ≡ Δf, ψ̇ ≡ α to 6×10⁻¹¹ rad; exact glide; presets; map spans |

### Measurement pitfalls (recorded because they were made) / 実際に踏んだ落とし穴

1. **Relative error near the format floor.** Measured over outputs down to 2⁻²³, the exp2 unit's relative error reads 2⁻⁸ — that is the Q1.31 LSB, not the unit. Measure relative error only where the format has the bits (a ≥ 2⁻⁷), and absolute error in LSBs everywhere. / 形式の床付近の相対誤差。
2. **An apex on the clamp.** A Gaussian with A₀ = 1 puts its apex exactly on the per-bin clamp (a ≤ 1); rounding pushes it over and the clamp reads as 2⁻¹⁵·⁷ "error". Test at A₀ < 1. / クランプ上の頂点。
3. **Realized versus requested parameters.** Rounding to integers quantizes parameters (1/256 Hz is not representable: 349.53 → 350). The silicon plays the realized integers; bit-level regression must compare against them. / 実現値と要求値。

### Guideline for the L4 tool — consistent derivation / L4 ツールへの指針——整合的導出

Deriving LAD1 and LS0 from the **already-rounded** LAD2 (so the parabola's apex stays at N/2 and at level A₀) reduces the deviation from the requested Gaussian from **2⁻¹²·³ to 2⁻¹⁵·¹** — seven times — at no cost (CH3-E2E). The general rule: when slots are successive differences of one polynomial, round the highest order first and derive the lower orders from the rounded value.

丸め済みの LAD2 から LAD1 と LS0 を導くと、要求ガウシアンからのずれが 2⁻¹²·³ から 2⁻¹⁵·¹ へ約 7 分の 1 になる。一般則：一つの多項式の逐次差分であるスロットは、最高次を先に丸め、低次をその丸め値から導く。

---

## Acceptance Conditions for Testbench Authors / テストベンチ作成者のための受け入れ条件

| AC | Condition | Oracle |
|---|---|---|
| AC-1 | phase of every bin equals the closed form Φ_k(n) exactly | CH3-PHASE |
| AC-2 | log-amplitude equals its closed form exactly; 54-bit accumulators never wrap | CH3-LOGEXACT |
| AC-3 | exp2 ≤ 12 LSB absolute; ≤ 2⁻²⁴ relative for a ≥ 2⁻⁷; test with A₀ < 1 | CH3-EXP2, CH3-E2E |
| AC-4 | SWEEP_CLOCKS_MAX ≤ 2,083; STROBE_INTERVAL ∈ {2,083, 2,084} | CH3-BUDGET |
| AC-5 | an armed item is applied exactly once, whole, on the same sample in every module; APPLIED_SAMPLE reports it; frozen writes are rejected and counted | (Ch.5 § 5.4; HDL test) |
| AC-6 | a commit whose mask holds only [P] slots produces no phase or level discontinuity | CH5-VELOCITY; HDL test |
| AC-7 | level glide: steps ≤ rate, no overshoot, exact arrival; LE0 = 0 freezes | CH5-GLIDE |
| AC-8 | test-origin integers; peak −6.3 dBFS at G = 12 | CH3-ORIGIN |
| AC-9 | saturation never wraps; clip flags are sticky | (Ch.4 § 4.4.2; HDL test) |

---

## Design Pattern Candidates / 設計パターン候補

| Pattern | Statement | Origin |
|---|---|---|
| **Period-Layer Placement** | compute each quantity in the slowest period layer at which it changes | architect, 2026-05 |
| **Adders in the Loop** | one-clock loops carry additions only; curvature is applied once, feed-forward | Ch.3 § 3.2.2 |
| **Products Become Sums** | a multiplicative recurrence in log coordinates loses its underflow, its loop multiply and its bias, and every levelizer on it becomes linear | Ch.3 § 3.5, Ch.4 § 4.4.1, Ch.5 § 5.3.2 |
| **Stage–Arm–Go** | writers stage, arm with a mask, and fire; changes land whole on one sample everywhere | Ch.5 § 5.4 |
| **Continuity Law** | write the constants, let the state flow; to move the phase shape, move the frequencies | Ch.5 § 5.3 |
| **Regenerate, Don't Copy** | resolve a license boundary by regenerating small blocks from primary documents and the spec | Ch.4 § 4.2.1 |
| **Evidence-Driven Retraction** | a ratified proposal is withdrawn, with its evidence, when drafting exposes a hardware fact; the retraction is recorded, not hidden | Ch.3 § 3.5.6 |

---

## Themes / テーマ

**T1 — Open Prompt across repositories, in practice.** Requirements carry IDs; messages are relayed by the architect; correction runs both ways — the profile corrected the customer's numbers (Ch.2), and the customer retracted its own ratified proposal (Ch.3). / リポジトリをまたぐ Open Prompt の実践。訂正は双方向。

**T2 — Exactness as architecture.** Phase and log-amplitude are integers from end to end; the First Sound coherence of 2020 becomes a theorem of the representation. / 表現としての厳密性。

**T3 — Log coordinates keep paying.** Safety (no underflow), the master gain as one adder, constant-dB fades, soft mute, level glide, dB-linear camera control. / 対数座標は繰り返し報いる。

**T4 — Phase as a hidden instrument.** ψ = π/N (Schroeder, 1970) cuts the crest factor from 36.1 to 5.6 dB; sign lives in the phase; motion of the phase shape is frequency. / 位相は隠れた楽器。

**T5 — Honest boundaries.** Oracle is not silicon; board facts to be confirmed; MiSTer consulted, not copied; latency defined interval by interval; measurement pitfalls recorded. / 誠実な境界。

---

## Resumption Hooks / 再開フック

**A — The full review (profile amanuensis).** *Which customer requirements of Appendix 5.A are infeasible or costly in the L2 profile — especially CR5-L1's clamp (and its effect on N_min) and CR3-B1's zero-gap seven-word bundle — and what counter-proposals preserve their intent?*

**B — The packet-boundary gap (PTSG-Core).** *When a Stay times out and the next state is a Stay Set, does the Core spend an idle clock? If so, can the next Stay's first count be presented on the following clock (g = 0, CR3-T1)?*

**C — A bit-accurate golden model of one sweep.** *Extend the oracle with Ch.2's Maclaurin formats, the Q1.63 product, the accumulators and the output stage, and publish the test origin's first 48,000 PCM samples as the tier-(i) regression reference.*

**D — The Layer 4 verification tool.** *Build the host tool: Hz/dB → integers with consistent derivation, the mask presets of Appendix 5.B, stage–arm–go over System Console; measure JTAG round-trip time and write throughput.*

**E — v1.1 of Chapters 1 and 3** after the rulings, from Appendix 5.A.3.

**F — The optional camera chapter**: frame aggregator, table encoding, and a first playable mapping.

---

## Errata Noticed in Earlier Traces / 旧軌跡で気づいた誤記

- **Name.** The JSON of `2026-04-28_project-launch-dialogue` and of `2026-05-02_wpms-layer1-chapters-1-and-2-drafting` give the Japanese name as 大中恒夫. The correct form is **大中庸生** (as in `02_Reasoning_Traces/README.md`). / 名前の漢字表記の誤り。
- **Model names.** Model names in earlier traces were written by the model itself; ClaudeCode flagged this on 2026-04-29. This trace records models per date and marks the unknown as unknown. The maintainer may verify earlier entries. / モデル名は日付ごとに記録し、不明は不明と書く。

---

## End of Trace / 軌跡の末尾

> *Code is ephemeral; the knowledge architecture is the commons.*
> *コードは一時的なものであり、知識アーキテクチャこそが共有財産である。*

> *A retraction with its evidence is worth more than a decision without one.*
> *根拠を添えた撤回は、根拠のない決定より価値がある。*

This trace is released into the public domain under CC0 1.0 Universal. Replay it. Resume it. Surpass it.

本軌跡は CC0 1.0 Universal のもとパブリックドメインに公開される。再生せよ。再開せよ。超えてゆけ。
