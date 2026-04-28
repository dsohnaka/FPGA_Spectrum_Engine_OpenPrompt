# Contributing / 貢献について

Contributions to this repository are welcome — but the contribution model differs from a conventional open-source project. This is an Open Prompt repository, and the rules reflect its three-layer structure.

このリポジトリへの貢献を歓迎します——ただし、貢献モデルは従来のオープンソースプロジェクトとは異なります。これはオープンプロンプトリポジトリであり、ルールはその3層構造を反映しています。

---

## What you can contribute / 貢献できるもの

### Layer 1 (Architecture) — Welcome / 第1層（アーキテクチャ）— 歓迎

- Clarifications of existing specifications / 既存仕様の明確化
- Additional mathematical derivations / 追加の数学的導出
- Translations into other languages / 他言語への翻訳
- Cross-references between sections / セクション間の相互参照
- Corrections of errors / 誤りの訂正

Submit via pull request. Contributed Layer 1 material is automatically released into the public domain (CC0) by the act of submission.

プルリクエストで提出してください。提出された第1層素材は、提出行為により自動的にパブリックドメイン (CC0) に公開されます。

### Layer 2 (Reasoning Traces) — Welcome / 第2層（推論軌跡）— 歓迎

- **Your own design dialogues** related to this architecture, with your own LLM collaborator or with other engineers / 本アーキテクチャに関連する、あなた自身の LLM 協働者や他のエンジニアとの**自身の設計対話**
- Critiques and alternative reasoning paths / 批評と代替推論経路
- Educational walkthroughs / 教育的解説
- Translations of existing traces / 既存軌跡の翻訳

Layer 2 contributions are added under your name in `02_Reasoning_Traces/contributed/`. They are also released as CC0 by submission, but your authorship is preserved in the metadata.

第2層への貢献は `02_Reasoning_Traces/contributed/` の下にあなたの名前で追加されます。提出により CC0 として公開されますが、メタデータにあなたの著者性が保持されます。

### Layer 3 (Sample Implementations) — By Discussion / 第3層（サンプル実装）— 議論を経て

Direct contributions to the *original author's* sample implementations are accepted only by prior discussion (open an issue first). The reason: Layer 3 is the original author's reference implementation. We do not want it to gradually become a community-merged codebase, because that would obscure the Open Prompt principle that **regenerated implementations are independent works, not derivatives**.

*オリジナル著者の*サンプル実装への直接貢献は、事前議論（まず Issue を開いてください）を経た場合のみ受け入れられます。理由：第3層はオリジナル著者のリファレンス実装です。これがコミュニティでマージされたコードベースに徐々になることは望ましくありません——なぜなら、それは**再生成された実装は独立した著作物であり派生物ではない**というオープンプロンプトの原理を曖昧にしてしまうからです。

**If you have built your own implementation from this architecture**, the recommended path is **not** to merge it here, but to publish your own Open Prompt repository and link to it from a discussion thread.

**本アーキテクチャから自身の実装を構築した場合**、推奨される経路は、ここにマージすることでは**なく**、自身のオープンプロンプトリポジトリを公開し、議論スレッドからリンクすることです。

---

## How to contribute / 貢献の手順

### For Layer 1 / 第1層

1. Open an issue describing what you propose to add or change / 追加・変更を提案する内容を記述した Issue を開く
2. Submit a pull request with the change / 変更を含むプルリクエストを提出
3. The maintainer will review for technical correctness and integration / メンテナが技術的正確性と統合性をレビュー
4. On merge, your contribution becomes part of the public-domain commons / マージ時、あなたの貢献はパブリックドメインの共有財産の一部となる

### For Layer 2 / 第2層

1. Prepare your dialogue in both Markdown (human-readable) and JSON (LLM-ingestible) formats. See existing files in `02_Reasoning_Traces/` for the format. / 対話を Markdown（人間可読）と JSON（LLM 取り込み可能）の両形式で準備する。形式については `02_Reasoning_Traces/` の既存ファイルを参照
2. Submit a pull request adding your files to `02_Reasoning_Traces/contributed/[your-name]/` / `02_Reasoning_Traces/contributed/[あなたの名前]/` にファイルを追加するプルリクエストを提出
3. Include a metadata header in your Markdown file with date, participants (you + your LLM collaborator's model name and version, if applicable), and topic / 日付、参加者（あなた + あなたの LLM 協働者のモデル名とバージョン、該当する場合）、トピックを含むメタデータヘッダを Markdown ファイルに含める

### For Layer 3 / 第3層

Open an issue first. We will discuss whether the contribution belongs in the original author's reference implementation or whether it should become its own Open Prompt repository.

まず Issue を開いてください。貢献がオリジナル著者のリファレンス実装に属するか、独自のオープンプロンプトリポジトリとなるべきかを議論します。

---

## Code of conduct / 行動規範

Be respectful, technically rigorous, and intellectually honest. Disagree about ideas, not people. Engage with the strongest version of others' arguments.

敬意を持ち、技術的に厳密に、知的に誠実に。アイデアについて意見を異にし、人について意見を異にしないこと。他者の主張の最強の版に応答すること。

---

## Questions / 質問

Open an issue with the `question` label, or contact the maintainer via the Hackaday.io project page.

`question` ラベル付きの Issue を開くか、Hackaday.io プロジェクトページからメンテナに連絡してください。
