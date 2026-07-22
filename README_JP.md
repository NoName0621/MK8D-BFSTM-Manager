# 🎵 MK8D BFSTM Manager (日本語版ドキュメント)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Beta--開発中-orange.svg)
[![English README](https://img.shields.io/badge/Language-English-blue)](README.md)

> ⚠️ **ご注意 / 開発中（ベータ版）**:  
> 本ツールは現在初期開発の段階 (**ベータ版**) であり、一部の機能・ファイル検出・音声変換において不完全な部分や不安定な動作が含まれる場合があります。ご使用の際は、念のため大切なゲームデータのバックアップを取ることを推奨いたします。不具合報告や改善のご提案は大歓迎です！

---

**MK8D BFSTM Manager** は、マリオカート8 および マリオカート8 デラックス (Cemu / 実機 Switch & Wii U) のカスタム BGM ＆ SE (効果音) 音声 Mod を安全かつ快適に管理・試聴・変換できるモダンな GUI アプリケーションです。

---

## ⭐ プロジェクトの応援 (Star をお願いします！)

このツールが役に立ちましたら、ぜひ GitHub リポジトリの **⭐ Star** を押していただけると嬉しいです！開発の大きな励みになります。

---

## 📖 詳しい使い方 (Usage Guide)

### 🕹️ 1. Cemu (PC エミュレータ) での直接管理・書き換え手順

1. アプリを起動し、サイドバーの **`⚙️ Settings` (設定)** タブを開きます。
2. `Root Game / mlc01 パス` 項目で、Cemu の `mlc01` ディレクトリ (例: `I:\cemu\mlc01\usr\title`) を選択し、`💾 設定を保存` を押します。
3. サイドバーの **`🎮 Game Mod Manager`** タブを開きます。
4. 対象カテゴリ (`Update` / `Base` / `DLC`) を選択すると、BGM および SE が一覧表示されます。
5. 変更したい音源の `Modを適用...` ボタンを押し、用意した `.bfstm` ファイルを選択します。
   - **自動保護**: 初回適用時にオリジナルのゲーム音源が全自動でバックアップ保存されます。
   - **一括書き換え**: 関連するすべてのエイリアスファイルや Update / Base 階層も一括更新されるため、タイトル画面に戻っても元の曲に戻りません。
6. 元の音源に戻したい場合は `元に戻す` ボタンを押すだけで一瞬で復元されます。

---

### 🎮 2. 実機 (Wii U / Nintendo Switch) 用 Mod ファイルの作成手順

1. アプリのサイドバーから **`🔄 Audio Converter` (相互変換ツール)** タブを開きます。
2. `入力ファイル` に Mod 化したいお好みの音楽ファイル (.mp3, .wav, .flac, .ogg 等) を指定します。
3. `🎯 置き換え対象の BGM / SE を選択` ドロップダウンから、置き換えたいコース曲や効果音（例: `マリオサーキット` や `スター無敵音`）を選択します。
4. **タイムライン ＆ トリミング編集**:
   - `✂️ 曲の範囲指定（切り出しトリミング）` を有効化すると、曲の好きな区間だけを切り出せます。
   - `🔁 ループ設定` を有効化すると、ゲーム内で途切れなくループ再生されるサンプルの開始・終了位置を指定できます。
5. `⚡ custom_sound_mods へ変換・保存する` を実行します。
6. `custom_sound_mods/` フォルダ内に作成された `.bfstm` ファイルを、実機 SD カードの Mod 用フォルダへ配置します：

   - **Wii U (SDCafiine の場合)**:
     ```text
     sd:/sdcafiine/00050000/1010eb00/content/audio/stream/ [ここに .bfstm を配置]
     ```
   - **Nintendo Switch (Atmosphère の場合 / MK8DX)**:
     ```text
     sd:/atmosphere/contents/0100152000022000/romfs/stream/ [ここに .bfstm を配置]
     ```

---

## ✨ 主な機能

- 🎮 **非破壊のゲーム Mod 管理**:
  - ゲーム内のオリジナル音源を全自動でバックアップ保護し、ワンクリックで独自の `.bfstm` Mod 音声の適用・復元・再適用が行えます。
- 🔊 **BGM ＆ SE (効果音) のフル対応**:
  - レース中のコース BGM だけでなく、スター無敵曲、1位ゴールファンファーレ、表彰台ジングル、ハイライトリプレイ演出などの効果音・演出音 Mod にも完全対応。
- 🎚️ **統合デュアルポインター タイムライン ＆ 範囲切り出し**:
  - 曲の開始・終了位置のトリミング切り出しや、ゲーム内ループポイント（ループ開始・終了サンプル数）をタイムラインバーで直感的に調整可能。
- 🎧 **BFSTM / WAV 内蔵試聴プレイヤー**:
  - VGAudioCLI を利用し、アプリ内で安全な音量で直接 `.bfstm` の試聴再生が可能です。
- ⚡ **高速 $O(1)$ ファイルスキャン ＆ フリーズゼロの非同期処理**:
  - バックグラウンドスレッド処理により、画面切替やファイル探索時に「応答なし」にならずサクサク軽快に動作します。
- 🌐 **多言語対応 (English 🇺🇸 / 日本語 🇯🇵)**:
  - 英語と日本語の表示切り替えに対応。設定内容は永久保存されます。

---

## 🚀 起動・開発手順

### 必要な環境
- Python 3.10 以上
- `VGAudioCLI.exe` (`tools/` フォルダ内に配置)

### 起動手順

1. リポジトリのクローンまたはダウンロード:
   ```cmd
   git clone https://github.com/NoName0621/MK8D-BFSTM-Manager.git
   cd MK8D-BFSTM-Manager
   ```

2. 必要なライブラリのインストール:
   ```cmd
   pip install customtkinter pygame-ce
   ```

3. アプリの起動:
   ```cmd
   python main.py
   ```

---

## 🛠️ 依存ライブラリ

- `customtkinter`
- `pygame-ce`
- [VGAudio](https://github.com/Thealexbarney/VGAudio) (`VGAudioCLI.exe`)

---

## 📄 ライセンス

本プロジェクトは **MIT ライセンス** のもとで公開されています。詳細は [LICENSE](LICENSE) をご確認ください。

Developed with ❤️ by **NoName0621**
