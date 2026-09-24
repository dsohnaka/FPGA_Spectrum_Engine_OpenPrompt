# WPMS Synthesizer — Layer 1 Specification
# Chapter 5: The Boundary — Inbox Protocol, Input Switch and Address Map
# WPMS シンセサイザー — 第1層仕様書
# 第5章：境界——inbox プロトコル、入力スイッチ、アドレスマップ

> **License: CC0 1.0 Universal (Public Domain)**
> **ライセンス：CC0 1.0 Universal（パブリックドメイン）**

*v1.0 DRAFT · 2026-09-24 · WPMS / FPGA Spectrum Engine amanuensis (customer side).*
*Depends on: Ch.1 v1.0 (§ 1.8, § 1.9), Ch.3 v1.0 DRAFT (C3-D1 Fixed; CR3-xx), Ch.4 v1.0 DRAFT; PTSG-WPMS-Formation L2 Formation Register Map v0.2 § 5.1 (inbox). This chapter completes the Layer 1 v1.0 draft. Appendix 5.A consolidates every customer requirement and every v1.1 alignment item of Chapters 1–5 for the full review by the PTSG-WPMS-Formation amanuensis.*

*本章で第 1 層 v1.0 草案が一巡する。付録 5.A に、第 1〜5 章の顧客要求と v1.1 整合項目をすべて集約し、PTSG-WPMS-Formation 祐筆殿の通読に供する。*

**Legend / 凡例:** **[Fixed]** · **[CR5-xx]** customer requirement to the L2 profile · **[Arena]** · **[Evidence: oracle]** (Python, *not silicon*)

---

## 5.0 Reading guide / 読み方

C3-D1 made the boundary of WPMS a wall that only integers cross. This chapter specifies the door in that wall: **what a writer may write, when it takes effect, who may write what, and at which address.** Three ideas carry the chapter:

C3-D1 は WPMS の境界を「整数だけが越える壁」にした。本章はその壁の扉を仕様する：**書き手が何を書けるか、いつ効くか、誰が何を書けるか、どの番地か。** 三つの考えが章を支える：

1. **Stage, arm, go.** Writers stage values, arm them with a slot mask, and fire; every armed change lands whole, in one sample, in every module at once (§ 5.4). / **置く、構える、放つ。**
2. **The continuity law.** Writing a [P] slot is continuous; writing an [S] slot is a re-seed. Level glides and phase-shape motion are both reachable through [P] slots alone (§ 5.3). / **連続性の法則。**
3. **Ownership by block.** Several sources — the host tool, the camera, later the HPS — may play at once, each on its own packets, through one switch (§ 5.5). / **ブロック単位の所有。**

---

## 5.1 Role and Boundary / 役割と境界

### Owned / 所有

- The boundary protocol (staging, commit mask, arm, GO, application timing, acknowledgement) / 境界プロトコル
- The input switch: source ports, ownership, arbitration, rejection accounting / 入力スイッチ
- The external address map, including the global registers of Ch.3 and Ch.4 / 外部アドレスマップ
- The host path (JTAG), the role of ISSP and ISMCE, the board buttons / ホスト経路、ISSP と ISMCE の役割、基板ボタン
- The test-origin source, and the contract between the camera mapper and the switch / テスト原点ソース、カメラ写像器とスイッチの契約

### Not owned / 所有しない

- How the L2 Formation copies the inbox into its shadow page and commits (PTSG-WPMS-Formation, Deliverable 3) / L2 の複製と commit の実現
- The camera driver and frame aggregator (optional camera chapter) / カメラドライバとフレーム集計器
- The L4 verification tool and its unit conversions (Layer 4) / L4 検証ツールと単位換算

---

## 5.2 The Boundary in One Paragraph / 境界を一段落で **[Fixed]**

Every writer writes **integers in the page's own block format** into a per-module **inbox** (register map v0.2 § 5.1), attaches a **slot mask**, and **arms** the block. A **GO** event applies every armed item of that writer, in every module, at **one sample boundary**. Nothing a writer does is ever observed half-done by L1. Hz, dB and linear gains never cross (C3-D1); their conversion belongs to the writer.

書き手はすべて、**ページのブロック形式の整数**をモジュールごとの **inbox** に書き、**スロットマスク**を添えてブロックを**構える**。**GO** がその書き手の構えた項目を、全モジュールで、**一つのサンプル境界**に適用する。書き手の操作が L1 に半端に見えることはない。Hz・dB・線形ゲインは越えない（C3-D1）。

---

## 5.3 The Continuity Law / 連続性の法則 **[Fixed; requires CR5-L1]**

### 5.3.1 [S] and [P] / 状態と定数

| Kind | Slots | Writing it means |
|---|---|---|
| **[S]** sample-advanced state | PH0, PHD1, PHD2, LP | **re-seed**: phase or level jumps to the written value. For note-on or a deliberate reset. |
| **[P]** per-packet constant | N, TAG, OM0, OMD1, OMD2, LAD1, LAD2, LS0, LE0, **LPT**, RT.OUT | **retune**: phase and level continue from where they are. |

Frequency changes through OM\* are **phase-continuous for every bin** (Ch.3 § 3.4.3: [S] slots keep integrating; only their increments change). Shape changes through LAD1, LAD2, LS0 are amplitude-shape steps, small when the change is small.

### 5.3.2 Level glide — the levelizer in the page / レベルの滑走——ページの中のレベラー **[CR5-L1]**

A level set by writing LP is a jump. To make level continuous without writing [S], this chapter asks the L2 profile for one behaviour:

LP を書いてのレベル設定は跳躍である。[S] を書かずにレベルを連続にするため、本章は L2 プロファイルに一つの振る舞いを求める：

```
per packet, once per sample:   LP ← LP + clamp( LPT − LP, −LE0, +LE0 )
```

- **LPT** (new, **+0x9**, Q6.26, [P]) is the level target; **LE0** (+0x5) becomes a **non-negative rate** (Q6.26 log₂ per sample), no longer a free slope. / LPT は目標、LE0 は非負の速度。
- LP reaches LPT exactly and stops. LE0 = 0 freezes the level. / LP は LPT に正確に到達して止まる。
- **A decay is a target**: LPT = −32 (below the per-bin clamp) with LE0 = the decay rate gives an exponential decay that ends in exact silence. An attack is LPT = the peak level with LE0 = the attack rate. A dB-linear ADSR is a sequence of (LPT, LE0) pairs written as [P] retunes at segment boundaries. / 減衰は目標である。dB 線形の ADSR は (LPT, LE0) の組の列。
- It cannot run away: unlike a free slope, a missed update leaves the level parked at its target. / 暴走しない。

This is the same law as the master gain of Ch.4 § 4.4.1, applied per packet. It supersedes Ch.3 § 3.5.2's `LP ← LP + LE0` (Ch.3 v1.1). It uses the reserved slot +0x9, which v0.2 and Ch.3 both marked "third-order phase — not needed"; +0xD stays reserved.

これは第 4 章 § 4.4.1 のマスターゲインと同じ法則をパケットごとに適用したもの。第 3 章 § 3.5.2 の `LP ← LP + LE0` を置き換える（第 3 章 v1.1）。予約スロット +0x9 を使い、+0xD は予約のまま残す。

### 5.3.3 Moving the phase shape is shaping the frequencies / 位相の形を動かすことは周波数を形づくること

Ch.1 § 1.4's phase shape (δφ, ψ) lives in [S] slots, so setting it is a re-seed. But **moving** it continuously needs no [S] write at all: a phase gradient moving at v rad/s adds k·v·t to bin k, which is a frequency offset of k·v/2π — exactly Δf. Likewise ψ moving at w rad/s is exactly α. **[Evidence: oracle]** Over 300 random (v, w, k, n), the two formulations agree to 6×10⁻¹¹ rad (floating-point rounding).

第 1 章 § 1.4 の位相の形（δφ, ψ）は [S] スロットにあり、それを「設定する」のは再播種である。しかし連続に「動かす」には [S] の書き込みは一切いらない：v rad/s で動く位相勾配はビン k に k·v·t を加え、それは周波数オフセット k·v/2π——まさに Δf である。同様に w rad/s で動く ψ はまさに α である。

```
d(δφ)/dt = v   ≡   Δf += v / 2π      (OMD1 += v/2π · 2³²/Fs)
d(ψ)/dt  = w   ≡   α  += w / 2π      (OMD1 += w/2π · 2³²/Fs ;  OMD2 += 2·w/2π · 2³²/Fs)
```

In WPMS, **the velocity of the phase shape and the shape of the frequencies are one coordinate.** A continuous controller moves the packet's group delay and chirp by writing [P] frequency slots, and when it stops, the phase shape stays where it drifted. This is what makes camera control click-free (§ 5.9).

WPMS では、**位相の形の速度と周波数の形は同じ座標である。** 連続制御器は [P] の周波数スロットを書くことで波束の群遅延とチャープを動かし、止めれば位相の形はそこに留まる。

---

## 5.4 Stage, Arm, Go / 置く、構える、放つ **[Fixed; requires CR5-I1…I3, S1]**

### 5.4.1 Items / 項目

Per module there are nine armable items: **eight blocks** (16 slots + RT.OUT each) and **one sweep word** (which blocks play, in what order).

### 5.4.2 Protocol / 手順

1. **Stage.** Write slot values into the inbox block and RT.OUT into its staging word. Any subset, any order. / 置く。
2. **Arm.** Write COMMIT[b] with a **slot mask** (bit *i* = slot +0x*i*; bit 16 = RT.OUT) and the arm bit. Masked slots will replace the page's values; unmasked slots continue untouched. Mask bits 13 and 14 are ignored: +0xD is reserved and +0xE (CUR) is internal to the L2 Formation, so neither is writable through the inbox. Retune and re-seed are simply two masks (Appendix 5.B lists the presets). While armed, the block is **frozen**: further writes to it are rejected and counted. / 構える。マスク外のスロットはそのまま続く。構えている間は凍結。
3. **Go.** Write GO. Every item armed by *this writer's port* (§ 5.5), in every module, is applied at the same sample boundary. A single block may instead be armed with **go-now**, which arms and fires that block alone. / 放つ。
4. **Acknowledge.** When the L2 Formations have taken the items, the switch clears the armed bits, unfreezes the blocks, and publishes **APPLIED_SEQ** (which GO) and **APPLIED_SAMPLE** (the sample index *n* of the first sweep that plays the new values). / 受領。

### 5.4.3 Timing / 時間

A GO is latched and handed to all Formations **on the next synchronized strobe** (the same event for every module, Ch.4 § 4.3.2). During that sweep each Formation copies its armed items into its shadow page; they take effect from the following sweep. Hence:

- **GO → first sweep playing it: ≤ 2 sample periods** (≤ 41.7 µs; add Ch.4 § 4.8 for the wire), with all modules and all items of the GO landing on the **same** sample. / GO から新しい値を演奏する最初の掃引まで 2 周期以内、全モジュール・全項目が同一サンプルに着地。
- **Exactly once.** An armed item is never applied twice and never partially. The coherence invariant CR3-C1 continues from each re-seed. / ちょうど一度。

### 5.4.4 The sweep word / 掃引語

`SWEEP = [3:0] P (0…8) | [27:4] order: eight 3-bit block indices, first packet first`. Armed and fired like a block. Changing P or the order is how packets are added to or removed from the sweep without touching the L2 program. The per-sweep limits of Ch.3 § 3.3 and the timing budget of Ch.3 § 3.7 are the writer's responsibility; the switch rejects Σ N > NMAX when it can compute it (N of all listed blocks staged or active).

---

## 5.5 The Input Switch / 入力スイッチ **[Fixed]**

### 5.5.1 Ports / ポート

The switch presents **the same address map (§ 5.6) on each of four ports**. The port a transaction arrives on *is* its source identity; no source field is carried in the data.

| Port | Source | First implementation |
|---|---|---|
| **0** | Host — the L4 verification tool over JTAG (§ 5.7) | yes |
| **1** | Camera mapper (§ 5.9) | optional extension |
| **2** | HPS, through the lightweight HPS-to-FPGA bridge | reserved (intermediate-layer phase) |
| **3** | Built-in ROM — test origin and power-on preset (§ 5.8) | yes |

Transactions from different ports are serialized by the switch (round-robin; a single-cycle write never waits more than three others). Reads are allowed from every port to every address.

### 5.5.2 Ownership / 所有

Each block and each module's sweep word has an **owner port** (2 bits), set only from port 0 or 3. A write, arm or GO from a non-owner is rejected and counted in **REJECT[port]**, so a mis-aimed controller is visible rather than silent. GO from port *p* fires only items owned by *p*; **GO_ALL** (port 0 or 3 only) fires every armed item. Changing an owner disarms that item.

Typical use: the host owns the sweep words and composes the music; the camera owns one or two blocks and modulates them; the host can take any block back at any time.

各ブロックと各モジュールの掃引語に**所有ポート**がある（ポート 0 と 3 だけが設定可）。非所有者の書込・構え・GO は拒否され REJECT に数えられるので、狙いを誤った制御器は黙って失敗せず目に見える。典型的には、ホストが掃引語を所有して曲を組み立て、カメラが一つ二つのブロックを所有して変調する。

---

## 5.6 Address Map / アドレスマップ **[Fixed]**

32-bit registers, **word addresses** (byte address = 4 × word address). Identical on every port. The map is bus-neutral: the reference bindings are Avalon-MM for port 0 (JTAG master) and AXI4-Lite for port 2 (HPS bridge), joined by standard adapters.

### 5.6.1 Global region `0x000–0x0FF`

| Word | Name | Access | Content |
|---|---|---|---|
| 0x000 | ID | R | 0x57504D53 ("WPMS") |
| 0x001 | VERSION | R | Layer 1 map version |
| 0x002 | CONFIG | R | [3:0] M modules · [7:4] blocks per page (8) · [23:8] NMAX (2,048) |
| 0x003 | PORT_ID | R | the port this read arrived on |
| 0x008 | GO | W | bit 0 GO (port-scoped) · bit 1 GO_ALL (ports 0, 3) |
| 0x009 | GO_SEQ | R | count of accepted GO events |
| 0x00A | APPLIED_SEQ | R | GO_SEQ of the last fully applied GO |
| 0x00B | APPLIED_SAMPLE | R | low 32 bits of *n* of the first sweep playing it |
| 0x00C / 0x00D | SAMPLE_LO / HI | R | 64-bit sample counter *n* (reading LO latches HI) |
| 0x010 | MG_TARGET | RW | Q6.26 log₂, ≤ 0 (Ch.4 § 4.4.1) |
| 0x011 | MG_RATE | RW | Q6.26 per sample, ≥ 0; default 13,933 (60 dB/s) |
| 0x012 | MG | R | current master gain |
| 0x013 | G_CTRL | RW | [3:0] G override · [4] override enable (Ch.4 § 4.4.2) |
| 0x014 | G_EFF | R | effective G |
| 0x015 | MUTE | RW | [0] soft mute, OR-ed with DIP[3] (Ch.4 § 4.4.5) |
| 0x016 | CLIP | R/W1C | [0] L · [1] R, sticky |
| 0x018 | STROBE_INTERVAL | R | clk_sys clocks between the last two strobes (2,083 / 2,084) |
| 0x019 | STROBE_MINMAX | R/W-clear | [15:0] min · [31:16] max |
| 0x01C | TEST_ORIGIN | W | write 1 = KEY[1] (§ 5.8) |
| 0x020 + m | OWNER[m] | RW (ports 0, 3) | [15:0] owner of blocks 0–7 (2 bits each) · [17:16] owner of the sweep word |
| 0x030 + p | REJECT[p] | R/W1C | rejected transactions from port *p* |
| 0x040 | INSPECT_SEL | RW | [3:0] module · [15:4] bin position in the sweep (Ch.1 § 1.8 inspector) |
| 0x041–0x043 | INSPECT_φ / L / a | R | Q0.32 phase · log₂ amplitude · Q1.31 amplitude of the selected bin, last sweep |

### 5.6.2 Module region `0x200 + 0x100·m` (m = 0 … M−1)

| Offset | Name | Access | Content |
|---|---|---|---|
| +0x00–0x7F | INBOX[b][i] | RW (owner; frozen while armed) | block *b* at +0x10·b, slot *i* at +i — **same format as the page block** (v0.2 § 3.1, with CR3-A1 and CR5-L1 names) |
| +0x80–0x87 | RTOUT[b] | RW (owner) | staged RT.OUT of block *b* |
| +0x88–0x8F | COMMIT[b] | W: [15:0] slot mask · [16] RT.OUT · [30] arm · [31] go-now; R: pending mask, armed | |
| +0x90 | SWEEP | RW (owner) | staged sweep word (§ 5.4.4) |
| +0x91 | SWEEP_COMMIT | W: [30] arm · [31] go-now; R: armed | |
| +0x92 | SWEEP_ACTIVE | R | sweep word in effect |
| +0x98 | SWEEP_CLOCKS | R | clk_sys clocks from strobe to the last accumulated product (Ch.4 § 4.9) |
| +0x99 | SWEEP_CLOCKS_MAX | R/W-clear | worst case since clear — the live left side of Ch.3 § 3.7 |

Span: Compact (M = 2) ends at 0x3FF; Extended (M = 10) at 0xBFF. The block offsets of the inbox are the page's offsets, so a controller that knows the page format already knows the inbox.

---

## 5.7 The Host Path / ホスト経路 **[Fixed]**

- **Writes: a JTAG-reachable memory-mapped master on port 0.** Reference: the vendor's JTAG-to-Avalon master bridge, driven from System Console by the L4 verification tool. It is vendor IP instantiated in the design, not source copied into Layer 3, so the MIT boundary of Ch.4 § 4.2.1 is kept. A Virtual-JTAG custom protocol is an Arena alternative. / 書込は JTAG から届くメモリマップドマスター。ベンダー IP のインスタンス化であり、第 3 層へのソース複製ではない。
- **ISSP stays required, for probes and a few direct knobs**: CLIP, MG, G_EFF, STROBE_INTERVAL, SWEEP_CLOCKS, the inspector. ISSP is no longer the parameter write path; with hundreds of slots, addressable writes are the right tool. / ISSP はプローブと少数の直接つまみとして必須のまま。パラメータ書込経路ではなくなる。
- **ISMCE edits the built-in ROM** (§ 5.8) and the camera mapping table (§ 5.9). This gives Ch.1 § 1.8's third interface its first real job. / ISMCE は内蔵 ROM とカメラ写像表を編集する。
- **Honest bandwidth.** The JTAG port is a verification channel. Round trips are of the order of milliseconds with USB-Blaster-class cables (to be measured, Layer 4); it is suitable for composing and for slow automation, not for 1 kHz musical control. That rate belongs to port 2 in the intermediate-layer phase. Because of stage–arm–go, host latency and jitter never produce partial updates — only later ones. / JTAG は検証チャネル。1 kHz の音楽的制御はポート 2 の役目。置く・構える・放つにより、ホストの遅延やジッタが半端な更新を生むことはない。

---

## 5.8 Buttons, Switches and the Built-in ROM / ボタン、スイッチ、内蔵 ROM **[Fixed]**

| Control | Function (Ch.1 § 1.8 remapped) |
|---|---|
| **KEY[0]** | **GO_ALL** — the physical "commit" button (Ch.1: "parameter snapshot trigger") |
| **KEY[1]** | **Test origin** — port 3 replays the ROM |
| DIP[1:0] | G ∈ {0, 4, 8, 12} (Ch.4) |
| DIP[2] | reset hold |
| DIP[3] | soft mute (Ch.4) |

**The ROM (port 3)** holds a short list of (address, data) writes ending in GO_ALL. Its initial content is the **test origin**: module 0 block 0 = the Dirichlet block of Ch.3 § 3.10 (with LPT = LP and LE0 = 0), full mask; module 0 SWEEP = {P = 1, order 0}; every other module SWEEP = {P = 0}; MG_TARGET = 0; all owners = port 0. It is replayed **after reset** and on **KEY[1]**. After reset the Formations start with empty sweeps (CR5-R1), so the ROM is the only source of the first sound.

ISMCE may overwrite the ROM with any preset — a power-on "music-box pattern" — until the next reconfiguration restores the test origin. The regression anchor therefore always survives a power cycle.

**内蔵 ROM（ポート 3）**は GO_ALL で終わる短い書込列を持ち、初期内容はテスト原点。リセット後と KEY[1] で再生する。ISMCE で任意のプリセット——電源投入時の「オルゴールの植立」——に書き換えられるが、再コンフィギュレーションでテスト原点に戻るので、回帰の錨は電源の入れ直しを越えて必ず残る。

---

## 5.9 The Camera Mapper Contract (optional extension) / カメラ写像器の契約（オプション拡張） **[Fixed]**

The camera subsystem of Ch.1 § 1.9 stays a Spin-Off-Ready Subsystem. Its only contract with WPMS is **port 1**: it writes owned inbox blocks, arms them, and fires port-scoped GO — exactly like any other writer.

第 1 章 § 1.9 のカメラサブシステムは暖簾分け準備済みのまま。WPMS との契約は**ポート 1**のみ。

**Mapper.** Once per frame the six aggregates *g* = (cx, cy, σx², σy², diff, mean) enter an affine map held in a small table (one M10K, ISMCE-editable). Each table row targets one (module, block, slot):

```
value = base + Σ_j c_j · g_j      (integer; modular slots wrap, signed slots saturate)
```

≤ 16 rows × 6 terms per frame — one DSP block or a short PTSG loop at 30 fps. After writing, the mapper arms the touched blocks with the mask of the slots it wrote and fires GO.

**Default template — continuity-respecting.** Ch.1's template is kept in spirit, re-expressed through § 5.3 so that the camera **never writes an [S] slot**:

| Aggregate | Ch.1 target | Written slots | Why |
|---|---|---|---|
| cx | α | OMD1, OMD2 | frequency curvature ([P]) |
| cy | β | LAD1 | spectral tilt ([P]) |
| σx² | γ | LS0, LAD1, LAD2 | packet width ([P]), coherently |
| σy² | δφ | OMD1 | **as δφ velocity** ≡ Δf offset (§ 5.3.3) |
| diff | ψ | OMD1, OMD2 | **as ψ velocity** ≡ α offset (§ 5.3.3) — motion drives motion |
| mean | A₀ | LPT (with a table-set LE0) | **level glide** (§ 5.3.2), no zipper at frame rate |

Every mapping is linear in slot space because every slot is linear in Ch.1's parameters once level is in log₂ — with N fixed per block, γ, for example, moves LS0, LAD1 and LAD2 by fixed coefficients (−N²/(4 ln 2), (N−1)/ln 2, −2/ln 2). The table is a template to be played with; the detailed camera chapter owns the aggregator and the table encoding.

---

## 5.10 Customer Requirements to the L2 Profile / L2 プロファイルへの顧客要求

These refine the inbox of register map v0.2 § 5.1 and replace CR3-C2 and CR3-C3.

| ID | Requirement | Replaces / why |
|---|---|---|
| **CR5-I1** | **Masked copy.** For each armed block, copy into the shadow page exactly the slots set in its 16-bit mask, and RT.OUT if bit 16 is set; leave every other slot of the page block untouched (it continues). The mask and the staged RT.OUT are readable by the datapath (location in the L2 address space: the profile's). | replaces CR3-C2's two classes; § 5.3 |
| **CR5-I2** | **One sweep, all modules.** When the switch raises *inbox-ready* on a synchronized strobe, every Formation copies all of its armed items during that sweep, so that they take effect from the next sweep — the same sweep index in every module. If a full copy (8 blocks × 16 slots + sweep word) cannot fit one sweep, the profile states the bound in sweeps; APPLIED semantics are unchanged. | § 5.4.3 |
| **CR5-I3** | **inbox-taken is required**, not optional: one lane per Formation, asserted when its copy is complete. The switch uses it to unfreeze blocks and publish APPLIED_SEQ / APPLIED_SAMPLE. | v0.2 § 5.1 made it optional |
| **CR5-S1** | **Sweep word.** The Formation plays P packets in the order given by the active sweep word; the sweep word is an armable inbox item with the same exactly-once semantics. | § 5.4.4 |
| **CR5-L1** | **Level glide.** Per packet, once per sample: `LP ← LP + clamp(LPT − LP, −LE0, +LE0)`; LPT at +0x9 (Q6.26, [P]); LE0 (+0x5) is a non-negative rate. Replaces `LP ← LP + LE0`. | § 5.3.2; supersedes part of CR3-A1 |
| **CR5-R1** | **Reset state.** After reset every Formation runs empty sweeps (P = 0) and accepts the inbox; the test origin is loaded by the switch's ROM port. | replaces CR3-C3; no test-origin logic in the profile |

---

## 5.11 Implementation Arena / 実装アリーナ

| Item | This chapter | Preserved alternative |
|---|---|---|
| JTAG write path | JTAG-to-Avalon master bridge | Virtual-JTAG custom protocol |
| Port arbitration | round-robin | fixed priority (host first) |
| Frozen-while-armed | reject and count | double-buffered staging (writer may prepare the next change while one is armed) |
| Group scope of GO | per port | per group bitmap (several atomic groups per port) |
| Live readback | none (the writer knows what it wrote) | snapshot of active block values on request, for tools that re-seed relative to the current phase |
| Camera mapper | affine table | PTSG program; non-linear curves in the table |
| Shape glide | none (LAD\*/LS0 step) | targets and rates for shape slots, as CR5-L1 does for level |

---

## 5.12 Open Questions / 未解決問題

| Question | Resolution path |
|---|---|
| Whether CR5-L1's clamp fits the profile's ISA and per-packet budget (N_min) | PTSG-WPMS-Formation, full review |
| Copy bound of CR5-I2 in sweeps | PTSG-WPMS-Formation |
| JTAG round-trip time and write throughput | Layer 4 |
| HPS port (AXI bridge, driver) | intermediate-layer phase |
| Camera aggregator and table encoding | optional camera chapter |

---

## 5.13 Decisions of this Chapter / 本章の決定事項

| ID | Decision | Status |
|---|---|---|
| C5-D1 | Stage–arm–go: masked items applied exactly once, at one sample boundary, in all modules; APPLIED_SEQ / APPLIED_SAMPLE | Fixed, with CR5-I1…I3 |
| C5-D2 | Continuity law: [P] writes continuous, [S] writes re-seed; the [S]/[P] table of § 5.3.1 | Fixed |
| C5-D3 | Level glide by LPT and rate LE0 | Fixed, with CR5-L1 |
| C5-D4 | Phase-shape velocity ≡ frequency shape (δφ̇ ≡ 2πΔf, ψ̇ ≡ 2πα) | Fixed (mathematical fact) |
| C5-D5 | Input switch: four ports, same map, port = source | Fixed |
| C5-D6 | Ownership per block and per sweep word; REJECT counters; GO per port, GO_ALL for ports 0 and 3 | Fixed |
| C5-D7 | Address map § 5.6 | Fixed |
| C5-D8 | Host path: JTAG memory-mapped master for writes; ISSP for probes and knobs; ISMCE for ROM and camera table | Fixed |
| C5-D9 | KEY[0] = GO_ALL; KEY[1] = test origin; ROM port replays after reset | Fixed |
| C5-D10 | Camera mapper: affine table on port 1; default template writes no [S] slot | Fixed |

---

## Appendix 5.A — Consolidated Review Sheet for the Full Read / 付録 5.A——通読用の集約表

### 5.A.1 All customer requirements to PTSG-WPMS-Formation (Chapters 3 and 5)

| ID | Short name | Chapter | State |
|---|---|---|---|
| CR3-A1 | Log-domain amplitude slots (LP, LAD1, LAD2, LE0; LS0 at +0xF) | 3 § 3.5.3 | active; LE0 meaning refined by CR5-L1 |
| CR3-B1 | Packet-start bundle, zero gap (7 words + RT.OUT) | 3 § 3.8 | active |
| CR3-B2 | L1 reads nothing else | 3 § 3.8 | active (adopted by the profile) |
| CR3-R1 | RT.OUT in the bundle | 3 § 3.8 | active |
| CR3-T1 | Zero-gap packet boundaries (g = 0) | 3 § 3.7 | active |
| CR3-T2 | Strobe wake ≤ 4 clocks | 3 § 3.7, 4 § 4.3 | active |
| CR3-T3 | Lanes to L1: packet_start, bin_valid, K | 3 § 3.8 | active |
| CR3-C1 | Coherence invariant: one advance per sample per packet | 3 § 3.4.3 | active |
| CR3-C2 | Update classes | 3 § 3.8 | **replaced by CR5-I1** |
| CR3-C3 | Test-origin block in the profile | 3 § 3.8 | **replaced by CR5-R1** |
| CR3-M1 | One Formation per module | 3 § 3.8 | active |
| CR5-I1 | Masked copy | 5 § 5.10 | active |
| CR5-I2 | One sweep, all modules | 5 § 5.10 | active |
| CR5-I3 | inbox-taken required | 5 § 5.10 | active |
| CR5-S1 | Sweep word | 5 § 5.10 | active |
| CR5-L1 | Level glide (LPT at +0x9) | 5 § 5.10 | active |
| CR5-R1 | Reset state: empty sweeps | 5 § 5.10 | active |

Ruling state: C3-D1 Fixed (2026-09-24). The log-domain amplitude (C3-D4, CR3-A1) and the relay of these requirements are to be ruled at the full review.

### 5.A.2 Slot map after all requests (for register map v0.3)

| Offset | Name | Kind | Q | L1 bundle |
|---|---|---|---|---|
| +0x0 | N | [P] | integer | — |
| +0x1 | TAG | [P] | integer | — |
| +0x2 | LP | [S] | Q6.26 | yes |
| +0x3 | LAD1 | [P] | Q8.24 | yes |
| +0x4 | LAD2 | [P] | Q2.30 | yes |
| +0x5 | LE0 (rate ≥ 0) | [P] | Q6.26 | — |
| +0x6 | PH0 | [S] | Q0.32 mod | yes |
| +0x7 | PHD1 | [S] | Q0.32 mod | yes |
| +0x8 | PHD2 | [S] | Q0.32 mod | yes |
| +0x9 | **LPT** | [P] | Q6.26 | — |
| +0xA | OM0 | [P] | Q0.32 mod | — |
| +0xB | OMD1 | [P] | Q0.32 mod | — |
| +0xC | OMD2 | [P] | Q0.32 mod | — |
| +0xD | reserved | | | |
| +0xE | CUR | (block 0, Mode T) | integer | — |
| +0xF | **LS0** | [P] | Q12.20 | yes |

Per-packet advance: three phase ADDs and one level step-toward (CR5-L1).

### 5.A.3 v1.1 alignment items for Chapters 1–4

| Chapter | Item |
|---|---|
| Ch.1 § 1.3 | MiSTer framework as prior art, not starting code (Ch.4 C4-D11) |
| Ch.1 § 1.6 | amplitude: 32-bit, produced by exp2 from log₂ (Ch.2 v1.1, Ch.3) |
| Ch.1 § 1.7 | amplitude recurrence in log₂ coordinates; the processor = L1 difference engine + L2 Formation |
| Ch.1 § 1.8 | JTAG memory-mapped port for writes; ISSP for probes/knobs; ISMCE for ROM and camera table; KEY[0] = GO_ALL; DIP[3] = soft mute; G override |
| Ch.1 § 1.9 | "AXI-Stream-style switch" → four-port memory-mapped switch with ownership; template re-expressed per § 5.9 |
| Ch.1 § 1.10 | multi-packet superposition is now in scope (Ch.3 § 3.3) |
| Ch.2 | (v1.1 issued) |
| Ch.3 § 3.5.2, § 3.5.3, § 3.10 | LE0 as rate; LPT at +0x9; test-origin block gains LPT = LP |
| Ch.3 § 3.5.4 | add MG: `L_k = ℓ + s_k + MG` (Ch.4) |
| Ch.3 § 3.8 | mark CR3-C2, CR3-C3 as replaced |
| Ch.4 | none known |

---

## Appendix 5.B — Mask Presets (non-normative) / マスク既定値（非規範）

| Preset | Mask (slots) | Use |
|---|---|---|
| RETUNE | 0x9E3B — all [P] (+0x0, 0x1, 0x3, 0x4, 0x5, 0x9, 0xA, 0xB, 0xC, 0xF) + RT.OUT | change anything without a click |
| RESEED | 0x9FFF — every writable slot + RT.OUT | note-on with defined phase and level |
| LEVEL | 0x0220 — +0x5, +0x9 | glide to a new level |
| PITCH | 0x1C00 — +0xA, +0xB, +0xC | phase-continuous frequency change |
| PHASE_RESET | 0x01C0 — +0x6, +0x7, +0x8 | re-align the phase shape (clicks by nature) |

---

## End of Chapter 5 / 第 5 章の末尾

> *Code is ephemeral; the knowledge architecture is the commons.*
> *コードは一時的なものであり、知識アーキテクチャこそが共有財産である。*

> *Write the constants; let the state flow. To move the shape of the phase, move the frequencies.*
> *定数を書き、状態は流れるにまかせよ。位相の形を動かしたければ、周波数を動かせ。*

This chapter is released into the public domain under CC0 1.0 Universal. With it, the WPMS Synthesizer Layer 1 specification (Chapters 1–5) is complete as a v1.0 draft, ready for the full review.

本章は CC0 1.0 Universal のもとパブリックドメインに公開される。本章をもって WPMS シンセサイザー第 1 層仕様（第 1〜5 章）は v1.0 草案として一巡し、通読の準備が整った。
