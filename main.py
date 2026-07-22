import os
import json
import re
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk

from converter import VGAudioConverter
from player import AudioPlayer
from mod_manager import ModManager

# CustomTkinter テーマ設定
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# 🌐 多言語 i18n 辞書 (デフォルト: English 🇺🇸 / 日本語 🇯🇵)
TRANSLATIONS = {
    "en": {
        "app_title": "BFSTM Audio Manager - Mario Kart 8 / 8DX Mod Tool",
        "tab_mod_mgr": "🎮 Game Mod Manager",
        "tab_db": "📚 BGM / SE Database",
        "tab_player": "🎧 Audio Player",
        "tab_converter": "🔄 Audio Converter",
        "tab_settings": "⚙️ Settings",
        "tab_credits": "ℹ️ Credits",
        
        "vgaudio_ok": "✅ VGAudioCLI Ready",
        "vgaudio_ng": "⚠️ VGAudioCLI.exe Not Found",
        "recheck": "Recheck / Browse...",

        # Mod Manager
        "mod_title": "Game BGM & SE Mod Manager",
        "target_cat": "🎯 Target Category:",
        "filter_label": "🔍 Filter:",
        "filter_all": "🌐 Show All",
        "filter_bgm": "🎵 BGM Only",
        "filter_se": "🔊 SE (SFX) Only",
        "stream_path": "📍 Active Stream Path:",
        "no_stream_path": "📍 Active Stream Path: (Not Found - Please set Game Directory in Settings)",
        "restore_all": "⏪ Restore All Originals",
        "reapply_all": "⏩ Reapply All Mods",
        "no_folder_warn": "⚠️ Please configure Game Directory in Settings",
        "status_orig": "🟢 Original",
        "status_mod": "🔵 Modded",
        "status_not_found": "⚪ Not Found",
        "btn_listen": "▶ Listen",
        "btn_apply": "Apply Mod...",
        "btn_restore": "Restore",
        "btn_reapply": "Reapply Mod",
        "time_fmt": "⏱️ Time:",
        "loop_on": "🔁 Loop ON",
        "loop_off": "🛑 Loop OFF",
        "summary_fmt": "Showing: {total} (Found: {found}) | Protected: {protected} | Modded: {modded}",

        # Database
        "db_title": "Mario Kart 8 / 8DX BGM & SE Database",
        "db_search_ph": "Search course, SE name, or filename...",
        "db_all_cat": "All Categories",
        "db_copy_btn": "Copy Filename",
        "db_apply_btn": "Apply as Mod...",
        "db_copied": "Copied to clipboard:",

        # Audio Player
        "player_title": "BFSTM Audio Preview Player",
        "player_ph": "Select .bfstm or .wav file to preview...",
        "browse": "Browse...",
        "player_no_file": "🎵 No File Selected",
        "player_desc": "Press play to convert to temp WAV and preview",
        "play_pause": "▶ Play / ⏸ Pause",
        "stop": "⏹ Stop",
        "volume": "🔊 Volume:",
        "clean_cache": "🧹 Clean Preview Cache",

        # Converter
        "conv_title": "BFSTM Converter & Audio Range Timeline Editor",
        "conv_in_lbl": "Input File:",
        "conv_in_ph": "Select source file (.wav, .mp3, .bfstm, etc.)",
        "conv_preset_lbl": "🎯 Replace Target BGM / SE:",
        "conv_preset_none": "(Save with custom filename)",
        "conv_out_lbl": "Output File:",
        "conv_out_ph": "Save destination path (.bfstm)",
        "conv_timeline_title": "🎚️ Integrated Audio Timeline (Start / End Handles)",
        "conv_sr": "Sample Rate:",
        "conv_auto_len": "⏱️ Duration:",
        "conv_trim_switch": "✂️ Enable Audio Trimming (Range Slicing)",
        "conv_start_pos": "🔴 Start Pos:",
        "conv_end_pos": "🔵 End Pos:",
        "conv_loop_switch": "🔁 Enable Loop Points (Game Loop Segment)",
        "conv_lstart_pos": "🟢 Loop Start:",
        "conv_lend_pos": "🟣 Loop End:",
        "conv_run_btn": "⚡ Convert & Save to custom_sound_mods",

        # Settings
        "settings_title": "⚙️ Settings & Environment Configuration",
        "game_dir_sec": "🎮 Game Directory Settings (Cemu / Game Files)",
        "game_dir_lbl": "Root Game / mlc01 Path:",
        "game_dir_ph": "Path to Cemu mlc01 or title/00050000/1010eb00...",
        "lang_sec": "🌐 Language Settings / 言語設定",
        "lang_lbl": "Display Language:",
        "save_settings_btn": "💾 Save Settings",
        "settings_saved": "Settings saved successfully!",

        # Credits
        "credits_title": "ℹ️ Credits & Project Information",
        "developed_by": "👨‍💻 Developed by: NoName0621",
        "repo_lbl": "🔗 GitHub Repository:",
        "repo_url": "https://github.com/NoName0621/MK8D-BFSTM-Manager",
        "open_repo_btn": "🌐 Open GitHub & Give a ⭐ Star!",
        "star_req_msg": "⭐ If you find this project helpful, please consider giving it a Star on GitHub to support development!",
        "credits_desc": "MK8D BFSTM Manager is an open-source tool for managing, previewing, and converting audio mods for Mario Kart 8 and 8 Deluxe."
    },
    "ja": {
        "app_title": "BFSTM Audio Manager - マリオカート8/8DX BGM & SE Mod Manager",
        "tab_mod_mgr": "🎮 ゲーム Mod 管理",
        "tab_db": "📚 BGM / SE データベース",
        "tab_player": "🎧 BFSTM 試聴",
        "tab_converter": "🔄 相互変換ツール",
        "tab_settings": "⚙️ 設定",
        "tab_credits": "ℹ️ クレジット",
        
        "vgaudio_ok": "✅ VGAudioCLI 準備完了",
        "vgaudio_ng": "⚠️ VGAudioCLI.exe 未配置",
        "recheck": "再検索 / パス指定",

        # Mod Manager
        "mod_title": "ゲーム BGM ＆ SE Mod 管理",
        "target_cat": "🎯 対象カテゴリ:",
        "filter_label": "🔍 表示フィルター:",
        "filter_all": "🌐 すべて表示",
        "filter_bgm": "🎵 BGMのみ",
        "filter_se": "🔊 SE（効果音）のみ",
        "stream_path": "📍 読み取り中の Stream パス:",
        "no_stream_path": "📍 読み取り中の Stream パス: (未設定 - 「設定」画面でゲームフォルダを指定してください)",
        "restore_all": "⏪ 全てオリジナルに復元",
        "reapply_all": "⏩ 全て Mod に再適用",
        "no_folder_warn": "⚠️ 設定画面でゲームフォルダ (Cemu mlc01 など) を選択してください",
        "status_orig": "🟢 オリジナル",
        "status_mod": "🔵 Mod適用中",
        "status_not_found": "⚪ フォルダ内未検出",
        "btn_listen": "▶ 試聴",
        "btn_apply": "Modを適用...",
        "btn_restore": "元に戻す",
        "btn_reapply": "Modに戻す",
        "time_fmt": "⏱️ 時間:",
        "loop_on": "🔁 ループ有効",
        "loop_off": "🛑 ループ無効",
        "summary_fmt": "表示中: {total} 件 (検出: {found} 件) | バックアップ保護: {protected} 件 | Mod適用中: {modded} 件",

        # Database
        "db_title": "マリオカート8 / 8DX BGM & SE データベース",
        "db_search_ph": "コース名・SE名・ファイル名で検索...",
        "db_all_cat": "すべてのカテゴリ",
        "db_copy_btn": "ファイル名コピー",
        "db_apply_btn": "Modとして適用...",
        "db_copied": "クリップボードにコピーしました:",

        # Audio Player
        "player_title": "BFSTM 音声プレビュー再生 (BGM / SE 対応)",
        "player_ph": "試聴したい .bfstm または .wav ファイルを選択...",
        "browse": "ファイル選択...",
        "player_no_file": "🎵 ファイルが選択されていません",
        "player_desc": "再生ボタンを押すと、WAVへ一時変換して再生します",
        "play_pause": "▶ 再生 / ⏸ 一時停止",
        "stop": "⏹ 停止",
        "volume": "🔊 音量:",
        "clean_cache": "🧹 試聴キャッシュを消去",

        # Converter
        "conv_title": "BFSTM 相互変換 ・ オーディオ範囲 ＆ タイムライン編集",
        "conv_in_lbl": "入力ファイル:",
        "conv_in_ph": "変換元ファイルを選択 (.wav, .mp3, .bfstm etc.)",
        "conv_preset_lbl": "🎯 置き換え対象の BGM / SE を選択:",
        "conv_preset_none": "(自由なファイル名で保存)",
        "conv_out_lbl": "出力ファイル:",
        "conv_out_ph": "保存先ファイル名 (.bfstm または .wav)",
        "conv_timeline_title": "🎚️ 統合オーディオタイムライン (開始・終了 ポインターコントロール)",
        "conv_sr": "周波数:",
        "conv_auto_len": "⏱️ 自動計測時間:",
        "conv_trim_switch": "✂️ 曲の範囲指定（切り出しトリミング）を有効化",
        "conv_start_pos": "🔴 開始位置:",
        "conv_end_pos": "🔵 終了位置:",
        "conv_loop_switch": "🔁 ループ設定（ゲーム内リピート再生範囲）を有効化",
        "conv_lstart_pos": "🟢 ループ開始:",
        "conv_lend_pos": "🟣 ループ終了:",
        "conv_run_btn": "⚡ custom_sound_mods へ変換・保存する",

        # Settings
        "settings_title": "⚙️ 環境設定 ＆ ゲームフォルダ指定",
        "game_dir_sec": "🎮 ゲームフォルダ設定 (Cemu / ゲームファイル参照)",
        "game_dir_lbl": "Root Game / mlc01 パス:",
        "game_dir_ph": "Cemu mlc01 や title/00050000/1010eb00 へのパス...",
        "lang_sec": "🌐 Language Settings / 言語設定",
        "lang_lbl": "表示言語 (Display Language):",
        "save_settings_btn": "💾 設定を保存",
        "settings_saved": "設定を正常に保存しました！",

        # Credits
        "credits_title": "ℹ️ クレジット ＆ プロジェクト情報",
        "developed_by": "👨‍💻 開発者: NoName0621",
        "repo_lbl": "🔗 GitHub リポジトリ:",
        "repo_url": "https://github.com/NoName0621/MK8D-BFSTM-Manager",
        "open_repo_btn": "🌐 GitHub ページを開いて ⭐ Star を押す！",
        "star_req_msg": "⭐ このツールを気に入っていただけましたら、ぜひ GitHub で Star (⭐) をお願いします！開発の大きな励みになります。",
        "credits_desc": "MK8D BFSTM Manager は、マリオカート8 および 8 デラックスの BGM / SE 音声 Mod を安全かつ快適に作成・管理・編集できるオープンソースツールです。"
    }
}


def parse_time_to_samples(time_input: str, sample_rate: int = 44100) -> int:
    if not time_input:
        return 0

    s = str(time_input).strip()

    if ":" in s:
        parts = s.split(":")
        try:
            if len(parts) == 2:
                mins = float(parts[0])
                secs = float(parts[1])
                total_seconds = mins * 60.0 + secs
                return int(total_seconds * sample_rate)
            elif len(parts) == 3:
                hrs = float(parts[0])
                mins = float(parts[1])
                secs = float(parts[2])
                total_seconds = hrs * 3600.0 + mins * 60.0 + secs
                return int(total_seconds * sample_rate)
        except ValueError:
            pass

    if "." in s:
        try:
            total_seconds = float(s)
            return int(total_seconds * sample_rate)
        except ValueError:
            pass

    try:
        return int(s)
    except ValueError:
        return 0


def seconds_to_time_str(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    mins = int(seconds // 60)
    secs = seconds % 60
    return f"{mins:02d}:{secs:04.1f}"


class BFSTMManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # モジュール初期化
        self.converter = VGAudioConverter()
        self.player = AudioPlayer()
        self.mod_manager = ModManager()
        self.bgm_database = self.load_database()

        # デフォルト言語設定 (デフォルト: en)
        self.lang = self.mod_manager.language if self.mod_manager.language in TRANSLATIONS else "en"

        self.title(self.tr("app_title"))
        self.geometry("1320 x 920")
        self.minsize(1050, 720)

        # 出力用フォルダ custom_sound_mods の自動生成
        self.custom_mods_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "custom_sound_mods")
        os.makedirs(self.custom_mods_dir, exist_ok=True)

        # フィルタ状態: "ALL", "BGM", "SE"
        self.active_type_filter = "ALL"
        self.is_refreshing_list = False

        self.input_audio_duration = 180.0
        self.is_updating_sliders = False

        # レイアウト構築
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        self.create_sidebar()
        self.create_main_container()

        # 初期描画・状態更新
        self.show_view("mod_manager")
        self.check_vgaudio_status()

    def tr(self, key: str) -> str:
        """多言語ヘルパー"""
        lang_dict = TRANSLATIONS.get(self.lang, TRANSLATIONS["en"])
        return lang_dict.get(key, TRANSLATIONS["en"].get(key, key))

    def load_database(self) -> list:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bgm_database.json")
        if os.path.exists(db_path):
            try:
                with open(db_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Database load error: {e}")
        return []

    def check_vgaudio_status(self):
        if self.converter.is_available():
            cli_path = self.converter.get_cli_path()
            self.vgaudio_status_label.configure(
                text=f"{self.tr('vgaudio_ok')}\n({os.path.basename(cli_path)})",
                text_color="#4CAF50"
            )
        else:
            self.vgaudio_status_label.configure(
                text=f"{self.tr('vgaudio_ng')}\n(tools/VGAudioCLI.exe)",
                text_color="#FF9800"
            )

    # ------------------------------------------------------------------
    # サイドバー
    # ------------------------------------------------------------------
    def create_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1)

        logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="🎵 BFSTM Manager",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        logo_label.grid(row=0, column=0, padx=20, pady=(20, 5))

        sub_logo = ctk.CTkLabel(
            self.sidebar_frame,
            text="Mario Kart 8 / 8DX Mod Tool",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        sub_logo.grid(row=1, column=0, padx=20, pady=(0, 20))

        self.btn_mod_mgr = ctk.CTkButton(
            self.sidebar_frame,
            text=self.tr("tab_mod_mgr"),
            anchor="w",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=lambda: self.show_view("mod_manager")
        )
        self.btn_mod_mgr.grid(row=2, column=0, padx=15, pady=4, sticky="ew")

        self.btn_db = ctk.CTkButton(
            self.sidebar_frame,
            text=self.tr("tab_db"),
            anchor="w",
            font=ctk.CTkFont(size=13),
            command=lambda: self.show_view("db")
        )
        self.btn_db.grid(row=3, column=0, padx=15, pady=4, sticky="ew")

        self.btn_player = ctk.CTkButton(
            self.sidebar_frame,
            text=self.tr("tab_player"),
            anchor="w",
            font=ctk.CTkFont(size=13),
            command=lambda: self.show_view("player")
        )
        self.btn_player.grid(row=4, column=0, padx=15, pady=4, sticky="ew")

        self.btn_converter = ctk.CTkButton(
            self.sidebar_frame,
            text=self.tr("tab_converter"),
            anchor="w",
            font=ctk.CTkFont(size=13),
            command=lambda: self.show_view("converter")
        )
        self.btn_converter.grid(row=5, column=0, padx=15, pady=4, sticky="ew")

        self.btn_settings = ctk.CTkButton(
            self.sidebar_frame,
            text=self.tr("tab_settings"),
            anchor="w",
            font=ctk.CTkFont(size=13),
            command=lambda: self.show_view("settings")
        )
        self.btn_settings.grid(row=6, column=0, padx=15, pady=4, sticky="ew")

        self.btn_credits = ctk.CTkButton(
            self.sidebar_frame,
            text=self.tr("tab_credits"),
            anchor="w",
            font=ctk.CTkFont(size=13),
            command=lambda: self.show_view("credits")
        )
        self.btn_credits.grid(row=7, column=0, padx=15, pady=4, sticky="ew")

        self.status_box = ctk.CTkFrame(self.sidebar_frame, fg_color="#1E1E24")
        self.status_box.grid(row=10, column=0, padx=15, pady=20, sticky="ew")

        self.vgaudio_status_label = ctk.CTkLabel(
            self.status_box,
            text="...",
            font=ctk.CTkFont(size=11),
            justify="center"
        )
        self.vgaudio_status_label.pack(padx=10, pady=10)

        self.btn_recheck = ctk.CTkButton(
            self.status_box,
            text=self.tr("recheck"),
            font=ctk.CTkFont(size=11),
            height=24,
            command=self.select_custom_cli
        )
        self.btn_recheck.pack(padx=10, pady=(0, 10))

    def select_custom_cli(self):
        file_path = filedialog.askopenfilename(
            title="VGAudioCLI.exe",
            filetypes=[("Executable Files", "*.exe"), ("All Files", "*.*")]
        )
        if file_path:
            self.converter.custom_cli_path = file_path
            self.check_vgaudio_status()

    # ------------------------------------------------------------------
    # メイン表示エリア切替
    # ------------------------------------------------------------------
    def create_main_container(self):
        self.main_container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=15, pady=15)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        self.views = {}
        self.views["mod_manager"] = self.build_mod_manager_view()
        self.views["db"] = self.build_database_view()
        self.views["player"] = self.build_player_view()
        self.views["converter"] = self.build_converter_view()
        self.views["settings"] = self.build_settings_view()
        self.views["credits"] = self.build_credits_view()

    def show_view(self, view_name: str):
        for name, view_frame in self.views.items():
            if name == view_name:
                view_frame.grid(row=0, column=0, sticky="nsew")
            else:
                view_frame.grid_forget()

        active_color = "#1F6AA5"
        inactive_color = "transparent"

        self.btn_mod_mgr.configure(fg_color=active_color if view_name == "mod_manager" else inactive_color)
        self.btn_db.configure(fg_color=active_color if view_name == "db" else inactive_color)
        self.btn_player.configure(fg_color=active_color if view_name == "player" else inactive_color)
        self.btn_converter.configure(fg_color=active_color if view_name == "converter" else inactive_color)
        self.btn_settings.configure(fg_color=active_color if view_name == "settings" else inactive_color)
        self.btn_credits.configure(fg_color=active_color if view_name == "credits" else inactive_color)

        if view_name == "mod_manager":
            self.refresh_mod_manager_list()

    # ------------------------------------------------------------------
    # View 1: ゲーム Mod 管理
    # ------------------------------------------------------------------
    def build_mod_manager_view(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            frame,
            text=self.tr("mod_title"),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        hdr_frame = ctk.CTkFrame(frame, corner_radius=10)
        hdr_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        hdr_frame.grid_columnconfigure(1, weight=1)

        lbl_target = ctk.CTkLabel(hdr_frame, text=self.tr("target_cat"), font=ctk.CTkFont(size=12, weight="bold"))
        lbl_target.grid(row=0, column=0, padx=15, pady=8, sticky="w")

        self.target_seg_btn = ctk.CTkSegmentedButton(
            hdr_frame,
            values=["⚡ Update (0005000e)", "🎮 Base (00050000)", "📦 DLC (0005000c)", "📂 Custom Stream"],
            command=self.on_target_type_changed
        )
        self.target_seg_btn.grid(row=0, column=1, columnspan=2, padx=(10, 15), pady=8, sticky="w")

        type_map_reverse = {"UPDATE": "⚡ Update (0005000e)", "BASE": "🎮 Base (00050000)", "DLC": "📦 DLC (0005000c)", "CUSTOM": "📂 Custom Stream"}
        self.target_seg_btn.set(type_map_reverse.get(self.mod_manager.target_type, "⚡ Update (0005000e)"))

        lbl_filter_type = ctk.CTkLabel(hdr_frame, text=self.tr("filter_label"), font=ctk.CTkFont(size=12, weight="bold"))
        lbl_filter_type.grid(row=1, column=0, padx=15, pady=4, sticky="w")

        self.type_filter_seg_btn = ctk.CTkSegmentedButton(
            hdr_frame,
            values=[self.tr("filter_all"), self.tr("filter_bgm"), self.tr("filter_se")],
            command=self.on_type_filter_changed
        )
        self.type_filter_seg_btn.grid(row=1, column=1, columnspan=2, padx=(10, 15), pady=4, sticky="w")
        self.type_filter_seg_btn.set(self.tr("filter_all"))

        self.resolved_path_lbl = ctk.CTkLabel(
            hdr_frame,
            text=self.tr("no_stream_path"),
            font=ctk.CTkFont(size=11),
            text_color="#64B5F6",
            anchor="w"
        )
        self.resolved_path_lbl.grid(row=2, column=0, columnspan=3, padx=15, pady=(4, 10), sticky="w")

        ctrl_bar = ctk.CTkFrame(hdr_frame, fg_color="transparent")
        ctrl_bar.grid(row=3, column=0, columnspan=3, sticky="ew", padx=15, pady=(0, 10))
        ctrl_bar.grid_columnconfigure(0, weight=1)

        self.mod_summary_lbl = ctk.CTkLabel(
            ctrl_bar,
            text="...",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.mod_summary_lbl.grid(row=0, column=0, sticky="w")

        btn_restore_all = ctk.CTkButton(
            ctrl_bar,
            text=self.tr("restore_all"),
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#D32F2F",
            hover_color="#9A0007",
            width=160,
            height=30,
            command=self.restore_all_originals_click
        )
        btn_restore_all.grid(row=0, column=1, padx=5)

        btn_reapply_all = ctk.CTkButton(
            ctrl_bar,
            text=self.tr("reapply_all"),
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#1F6AA5",
            width=160,
            height=30,
            command=self.reapply_all_mods_click
        )
        btn_reapply_all.grid(row=0, column=2, padx=5)

        self.mod_scroll_frame = ctk.CTkScrollableFrame(frame, label_text="BGM / SE List")
        self.mod_scroll_frame.grid(row=2, column=0, sticky="nsew")
        self.mod_scroll_frame.grid_columnconfigure(1, weight=1)

        return frame

    def on_type_filter_changed(self, value: str):
        if value in ["🎵 BGM Only", "🎵 BGMのみ"]:
            self.active_type_filter = "BGM"
        elif value in ["🔊 SE (SFX) Only", "🔊 SE（効果音）のみ"]:
            self.active_type_filter = "SE"
        else:
            self.active_type_filter = "ALL"

        self.refresh_mod_manager_list()

    def on_target_type_changed(self, value: str):
        type_map = {
            "⚡ Update (0005000e)": "UPDATE",
            "🎮 Base (00050000)": "BASE",
            "📦 DLC (0005000c)": "DLC",
            "📂 Custom Stream": "CUSTOM"
        }
        target_type = type_map.get(value, "UPDATE")
        root_path = self.mod_manager.root_game_dir
        self.mod_manager.set_target_type(target_type, root_path)
        self.refresh_mod_manager_list()

    def refresh_mod_manager_list(self):
        if self.is_refreshing_list:
            return

        for child in self.mod_scroll_frame.winfo_children():
            child.destroy()

        active_stream_dir = self.mod_manager.game_dir
        if active_stream_dir:
            self.resolved_path_lbl.configure(text=f"{self.tr('stream_path')} {active_stream_dir}")
        else:
            self.resolved_path_lbl.configure(text=self.tr('no_stream_path'))

        if not active_stream_dir or not os.path.exists(active_stream_dir):
            lbl = ctk.CTkLabel(
                self.mod_scroll_frame,
                text=self.tr('no_folder_warn'),
                text_color="gray"
            )
            lbl.pack(pady=30)
            self.mod_summary_lbl.configure(text="No game directory")
            return

        self.mod_summary_lbl.configure(text="⏳ Scanning directory index...")
        self.is_refreshing_list = True

        def bg_scan_worker():
            if not self.mod_manager._index_built:
                self.mod_manager.rebuild_file_index()

            filtered_items = []
            for item in self.bgm_database:
                item_type = item.get("type", "BGM")
                if self.active_type_filter == "ALL":
                    filtered_items.append(item)
                elif self.active_type_filter == "BGM" and item_type == "BGM":
                    filtered_items.append(item)
                elif self.active_type_filter == "SE" and item_type == "SE":
                    filtered_items.append(item)

            row_data_list = []
            backed_up_count = 0
            modded_count = 0
            found_count = 0

            for item in filtered_items:
                fname = item.get("filename")
                aliases = item.get("aliases", [])
                status = self.mod_manager.get_file_status(fname, aliases)
                has_orig = self.mod_manager.has_original_backup(fname)
                has_mod = self.mod_manager.has_mod_backup(fname)
                item_type = item.get("type", "BGM")

                bfstm_meta = {"duration_str": "--:--", "has_loop": False}
                if status != ModManager.STATUS_NOT_FOUND:
                    bfstm_meta = self.mod_manager.get_bgm_metadata(fname, aliases)
                    found_count += 1

                if has_orig:
                    backed_up_count += 1
                if status == ModManager.STATUS_MODDED:
                    modded_count += 1

                row_data_list.append({
                    "item": item,
                    "status": status,
                    "has_orig": has_orig,
                    "has_mod": has_mod,
                    "bfstm_meta": bfstm_meta,
                    "item_type": item_type
                })

            summary_text = self.tr("summary_fmt").format(
                total=len(filtered_items),
                found=found_count,
                protected=backed_up_count,
                modded=modded_count
            )
            
            self.after(0, lambda: self._render_mod_rows_main_thread(row_data_list, summary_text))

        threading.Thread(target=bg_scan_worker, daemon=True).start()

    def _render_mod_rows_main_thread(self, row_data_list: list, summary_text: str):
        for idx, row in enumerate(row_data_list):
            item = row["item"]
            fname = item.get("filename")
            aliases = item.get("aliases", [])
            status = row["status"]
            has_orig = row["has_orig"]
            has_mod = row["has_mod"]
            bfstm_meta = row["bfstm_meta"]
            item_type = row["item_type"]

            row_frame = ctk.CTkFrame(self.mod_scroll_frame, fg_color="#2B2B36" if idx % 2 == 0 else "#23232C")
            row_frame.pack(fill="x", padx=5, pady=4)
            row_frame.grid_columnconfigure(1, weight=1)

            badge_text = self.tr("status_orig")
            badge_color = "#2E7D32"
            if status == ModManager.STATUS_MODDED:
                badge_text = self.tr("status_mod")
                badge_color = "#1565C0"
            elif status == ModManager.STATUS_NOT_FOUND:
                badge_text = self.tr("status_not_found")
                badge_color = "#424242"

            lbl_badge = ctk.CTkLabel(
                row_frame,
                text=badge_text,
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=badge_color,
                corner_radius=6,
                width=110
            )
            lbl_badge.grid(row=0, column=0, padx=10, pady=10)

            info_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            type_icon = "🎵 [BGM]" if item_type == "BGM" else "🔊 [SE]"
            title_name = item.get('course_name_en') if self.lang == "en" else item.get('course_name_ja')
            title_str = f"{type_icon} {title_name}"
            lbl_title = ctk.CTkLabel(info_frame, text=title_str, font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
            lbl_title.pack(anchor="w")

            loop_str = self.tr("loop_on") if bfstm_meta.get("has_loop") else self.tr("loop_off")
            duration_str = bfstm_meta.get("duration_str", "--:--")
            
            sub_text = f"{fname} | {self.tr('time_fmt')} {duration_str} | {loop_str}"
            lbl_sub = ctk.CTkLabel(
                info_frame,
                text=sub_text,
                font=ctk.CTkFont(size=11),
                text_color="#B0BEC5",
                anchor="w"
            )
            lbl_sub.pack(anchor="w")

            btn_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
            btn_frame.grid(row=0, column=2, padx=10, pady=10)

            btn_listen = ctk.CTkButton(
                btn_frame,
                text=self.tr("btn_listen"),
                font=ctk.CTkFont(size=11, weight="bold"),
                fg_color="#00838F",
                hover_color="#005662",
                width=65,
                height=28,
                state="normal" if status != ModManager.STATUS_NOT_FOUND else "disabled",
                command=lambda f=fname, a=aliases: self.play_game_bgm_direct(f, a)
            )
            btn_listen.pack(side="left", padx=3)

            btn_apply = ctk.CTkButton(
                btn_frame,
                text=self.tr("btn_apply"),
                font=ctk.CTkFont(size=11),
                width=90,
                height=28,
                command=lambda f=fname, a=aliases: self.apply_mod_dialog(f, a)
            )
            btn_apply.pack(side="left", padx=3)

            btn_restore = ctk.CTkButton(
                btn_frame,
                text=self.tr("btn_restore"),
                font=ctk.CTkFont(size=11),
                fg_color="#D32F2F",
                hover_color="#9A0007",
                width=75,
                height=28,
                state="normal" if has_orig else "disabled",
                command=lambda f=fname, a=aliases: self.restore_original_click(f, a)
            )
            btn_restore.pack(side="left", padx=3)

            btn_reapply = ctk.CTkButton(
                btn_frame,
                text=self.tr("btn_reapply"),
                font=ctk.CTkFont(size=11),
                fg_color="#283593",
                width=75,
                height=28,
                state="normal" if has_mod else "disabled",
                command=lambda f=fname, a=aliases: self.reapply_mod_click(f, a)
            )
            btn_reapply.pack(side="left", padx=3)

        self.mod_summary_lbl.configure(text=summary_text)
        self.is_refreshing_list = False

    def play_game_bgm_direct(self, filename: str, aliases: list = None):
        file_path = self.mod_manager.get_game_file_path(filename, aliases)
        if not file_path or not os.path.exists(file_path):
            messagebox.showwarning("Warning", f"Target file not found: {filename}")
            return

        self.show_view("player")
        self.player_filepath_entry.delete(0, tk.END)
        self.player_filepath_entry.insert(0, file_path)
        self.player_track_name.configure(text=f"🎵 {os.path.basename(file_path)}")
        self.player_status_lbl.configure(text="Ready to play")

        self.toggle_play_preview()

    def apply_mod_dialog(self, filename: str, aliases: list = None):
        initial_dir = self.custom_mods_dir if os.path.exists(self.custom_mods_dir) else ""
        mod_path = filedialog.askopenfilename(
            title=f"Select Mod (.bfstm) for {filename}",
            initialdir=initial_dir,
            filetypes=[("BFSTM Audio", "*.bfstm"), ("All Files", "*.*")]
        )
        if mod_path:
            ok, msg = self.mod_manager.apply_mod(filename, mod_path, aliases)
            if ok:
                messagebox.showinfo("Success", msg)
                self.refresh_mod_manager_list()
            else:
                messagebox.showerror("Error", msg)

    def restore_original_click(self, filename: str, aliases: list = None):
        ok, msg = self.mod_manager.restore_original(filename, aliases)
        if ok:
            messagebox.showinfo("Success", msg)
            self.refresh_mod_manager_list()
        else:
            messagebox.showerror("Error", msg)

    def reapply_mod_click(self, filename: str, aliases: list = None):
        ok, msg = self.mod_manager.reapply_mod(filename, aliases)
        if ok:
            messagebox.showinfo("Success", msg)
            self.refresh_mod_manager_list()
        else:
            messagebox.showerror("Error", msg)

    def restore_all_originals_click(self):
        if not messagebox.askyesno("Confirm Restore", "Restore all backed-up original sound files?"):
            return
        succ, fail = self.mod_manager.restore_all_originals(self.bgm_database)
        messagebox.showinfo("Restore Completed", f"Results:\nSuccess: {succ}\nFailed: {fail}")
        self.refresh_mod_manager_list()

    def reapply_all_mods_click(self):
        if not messagebox.askyesno("Confirm Reapply", "Reapply all saved Mod sound files?"):
            return
        succ, fail = self.mod_manager.reapply_all_mods(self.bgm_database)
        messagebox.showinfo("Reapply Completed", f"Results:\nSuccess: {succ}\nFailed: {fail}")
        self.refresh_mod_manager_list()

    # ------------------------------------------------------------------
    # View 2: BGM / SE データベース
    # ------------------------------------------------------------------
    def build_database_view(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            frame,
            text=self.tr("db_title"),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        search_frame = ctk.CTkFrame(frame)
        search_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        search_frame.grid_columnconfigure(0, weight=1)

        self.db_search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text=self.tr("db_search_ph"),
            font=ctk.CTkFont(size=13)
        )
        self.db_search_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.db_search_entry.bind("<KeyRelease>", lambda e: self.filter_database())

        self.db_type_seg_btn = ctk.CTkSegmentedButton(
            search_frame,
            values=[self.tr("filter_all"), self.tr("filter_bgm"), self.tr("filter_se")],
            command=lambda v: self.filter_database()
        )
        self.db_type_seg_btn.grid(row=0, column=1, padx=10, pady=10)
        self.db_type_seg_btn.set(self.tr("filter_all"))

        self.category_option = ctk.CTkOptionMenu(
            search_frame,
            values=[self.tr("db_all_cat"), "Nitro (MK8)", "Retro", "DLC / Booster Course Pass", "System Menu", "SE (効果音)"],
            command=lambda v: self.filter_database()
        )
        self.category_option.grid(row=0, column=2, padx=10, pady=10)

        self.db_scroll_frame = ctk.CTkScrollableFrame(frame, label_text="BGM / SE List")
        self.db_scroll_frame.grid(row=2, column=0, sticky="nsew")
        self.db_scroll_frame.grid_columnconfigure(1, weight=1)

        self.render_db_items(self.bgm_database)
        return frame

    def filter_database(self):
        query = self.db_search_entry.get().strip().lower()
        selected_cat = self.category_option.get()
        selected_type = self.db_type_seg_btn.get()

        filtered = []
        for item in self.bgm_database:
            item_type = item.get("type", "BGM")

            if selected_type in ["🎵 BGM Only", "🎵 BGMのみ"] and item_type != "BGM":
                continue
            if selected_type in ["🔊 SE (SFX) Only", "🔊 SE（効果音）のみ"] and item_type != "SE":
                continue

            if selected_cat != self.tr("db_all_cat") and item.get("category") != selected_cat:
                continue

            match = False
            if query in item.get("course_name_ja", "").lower() or query in item.get("course_name_en", "").lower():
                match = True
            elif query in item.get("filename", "").lower() or query in item.get("id", "").lower():
                match = True

            if not query or match:
                filtered.append(item)

        self.render_db_items(filtered)

    def render_db_items(self, items: list):
        for child in self.db_scroll_frame.winfo_children():
            child.destroy()

        if not items:
            no_item_label = ctk.CTkLabel(self.db_scroll_frame, text="No items found.", text_color="gray")
            no_item_label.pack(pady=20)
            return

        for idx, item in enumerate(items):
            item_frame = ctk.CTkFrame(self.db_scroll_frame, fg_color="#2B2B36" if idx % 2 == 0 else "#23232C")
            item_frame.pack(fill="x", padx=5, pady=3)
            item_frame.grid_columnconfigure(1, weight=1)

            item_type = item.get("type", "BGM")
            badge_color = "#1F6AA5" if item_type == "BGM" else "#E65100"

            cat_label = ctk.CTkLabel(
                item_frame,
                text=f"{'🎵' if item_type == 'BGM' else '🔊'} {item.get('category', 'General')}",
                font=ctk.CTkFont(size=10, weight="bold"),
                fg_color=badge_color,
                corner_radius=6,
                width=110
            )
            cat_label.grid(row=0, column=0, padx=10, pady=10)

            info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
            info_frame.grid(row=0, column=1, padx=10, pady=5, sticky="w")

            title_name = f"{item.get('course_name_en')} / {item.get('course_name_ja')}" if self.lang == "en" else f"{item.get('course_name_ja')} ({item.get('course_name_en')})"
            title_lbl = ctk.CTkLabel(info_frame, text=title_name, font=ctk.CTkFont(size=13, weight="bold"), anchor="w")
            title_lbl.pack(anchor="w")

            file_lbl = ctk.CTkLabel(
                info_frame,
                text=f"Filename: {item.get('filename')} | {item.get('description')}",
                font=ctk.CTkFont(size=11),
                text_color="gray",
                anchor="w"
            )
            file_lbl.pack(anchor="w")

            btn_box = ctk.CTkFrame(item_frame, fg_color="transparent")
            btn_box.grid(row=0, column=2, padx=10, pady=10)

            btn_copy = ctk.CTkButton(
                btn_box,
                text=self.tr("db_copy_btn"),
                font=ctk.CTkFont(size=11),
                width=110,
                height=28,
                command=lambda fname=item.get('filename'): self.copy_to_clipboard(fname)
            )
            btn_copy.pack(side="left", padx=3)

            btn_game_apply = ctk.CTkButton(
                btn_box,
                text=self.tr("db_apply_btn"),
                font=ctk.CTkFont(size=11),
                fg_color="#2E7D32",
                hover_color="#1B5E20",
                width=110,
                height=28,
                command=lambda fname=item.get('filename'), aliases=item.get('aliases', []): self.apply_mod_dialog(fname, aliases)
            )
            btn_game_apply.pack(side="left", padx=3)

    def copy_to_clipboard(self, text: str):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copied", f"{self.tr('db_copied')}\n{text}")

    # ------------------------------------------------------------------
    # View 3: BFSTM 試聴プレイヤー
    # ------------------------------------------------------------------
    def build_player_view(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            frame,
            text=self.tr("player_title"),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 15))

        card = ctk.CTkFrame(frame, corner_radius=12)
        card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(2, weight=1)

        file_sec = ctk.CTkFrame(card, fg_color="transparent")
        file_sec.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        file_sec.grid_columnconfigure(0, weight=1)

        self.player_filepath_entry = ctk.CTkEntry(
            file_sec,
            placeholder_text=self.tr("player_ph"),
            font=ctk.CTkFont(size=13)
        )
        self.player_filepath_entry.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        btn_browse = ctk.CTkButton(
            file_sec,
            text=self.tr("browse"),
            width=120,
            command=self.browse_preview_file
        )
        btn_browse.grid(row=0, column=1)

        self.player_info_frame = ctk.CTkFrame(card, fg_color="#1E1E26", corner_radius=10)
        self.player_info_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=10)

        self.player_track_name = ctk.CTkLabel(
            self.player_info_frame,
            text=self.tr("player_no_file"),
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.player_track_name.pack(pady=(20, 5))

        self.player_status_lbl = ctk.CTkLabel(
            self.player_info_frame,
            text=self.tr("player_desc"),
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.player_status_lbl.pack(pady=(0, 20))

        ctrl_frame = ctk.CTkFrame(card, fg_color="transparent")
        ctrl_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=30)
        ctrl_frame.grid_columnconfigure(1, weight=1)

        btn_play_pause = ctk.CTkButton(
            ctrl_frame,
            text=self.tr("play_pause"),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=160,
            command=self.toggle_play_preview
        )
        btn_play_pause.grid(row=0, column=0, padx=10)

        btn_stop = ctk.CTkButton(
            ctrl_frame,
            text=self.tr("stop"),
            font=ctk.CTkFont(size=14),
            height=40,
            width=100,
            fg_color="#D32F2F",
            hover_color="#9A0007",
            command=self.stop_preview
        )
        btn_stop.grid(row=0, column=1, padx=10, sticky="w")

        vol_frame = ctk.CTkFrame(ctrl_frame, fg_color="transparent")
        vol_frame.grid(row=0, column=2, padx=10, sticky="e")

        vol_lbl = ctk.CTkLabel(vol_frame, text=self.tr("volume"), font=ctk.CTkFont(size=12))
        vol_lbl.pack(side="left", padx=5)

        self.vol_slider = ctk.CTkSlider(
            vol_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=100,
            width=150,
            command=self.on_volume_change
        )
        self.vol_slider.set(0.3)
        self.vol_slider.pack(side="left", padx=5)

        btn_clean_cache = ctk.CTkButton(
            card,
            text=self.tr("clean_cache"),
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            border_width=1,
            border_color="gray",
            command=self.clean_preview_cache
        )
        btn_clean_cache.grid(row=4, column=0, pady=(0, 20))

        return frame

    def browse_preview_file(self):
        path = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[("BFSTM / WAV Files", "*.bfstm;*.wav"), ("All Files", "*.*")]
        )
        if path:
            self.player_filepath_entry.delete(0, tk.END)
            self.player_filepath_entry.insert(0, path)
            self.player_track_name.configure(text=f"🎵 {os.path.basename(path)}")
            self.player_status_lbl.configure(text="Ready to play")

    def toggle_play_preview(self):
        input_path = self.player_filepath_entry.get().strip()
        if not input_path or not os.path.exists(input_path):
            messagebox.showwarning("Warning", "Please select a valid file.")
            return

        if self.player.current_file and self.player.current_file.endswith(".wav"):
            self.player.toggle_play_pause()
            if self.player.is_paused:
                self.player_status_lbl.configure(text="⏸ Paused")
            else:
                self.player_status_lbl.configure(text="▶ Playing...")
            return

        if input_path.lower().endswith(".bfstm"):
            if not self.converter.is_available():
                messagebox.showerror("Error", "VGAudioCLI.exe is required to preview BFSTM.")
                return

            self.player_status_lbl.configure(text="⏳ Converting BFSTM to temp WAV...")

            def run_preview_convert():
                temp_wav = os.path.join("temp", "preview_cache.wav")
                success, msg = self.converter.convert(input_path, temp_wav)

                if success:
                    self.player.load_and_play(temp_wav, volume=self.vol_slider.get())
                    self.player_status_lbl.configure(text="▶ Playing preview...")
                else:
                    self.player_status_lbl.configure(text=f"❌ Failed: {msg}")
                    messagebox.showerror("Error", msg)

            threading.Thread(target=run_preview_convert, daemon=True).start()

        elif input_path.lower().endswith(".wav"):
            self.player.load_and_play(input_path, volume=self.vol_slider.get())
            self.player_status_lbl.configure(text="▶ Playing preview...")

    def stop_preview(self):
        self.player.stop()
        self.player_status_lbl.configure(text="⏹ Stopped")

    def on_volume_change(self, value):
        self.player.set_volume(value)

    def clean_preview_cache(self):
        self.player.clear_temp_cache()
        messagebox.showinfo("Cache Cleared", "Temporary preview files removed.")

    # ------------------------------------------------------------------
    # View 4: BFSTM 相互変換ツール
    # ------------------------------------------------------------------
    def build_converter_view(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            frame,
            text=self.tr("conv_title"),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 10))

        scroll_card = ctk.CTkScrollableFrame(frame, corner_radius=12)
        scroll_card.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scroll_card.grid_columnconfigure(0, weight=1)

        in_frame = ctk.CTkFrame(scroll_card, fg_color="transparent")
        in_frame.pack(fill="x", padx=15, pady=(15, 6))
        in_frame.grid_columnconfigure(1, weight=1)

        lbl_in = ctk.CTkLabel(in_frame, text=self.tr("conv_in_lbl"), font=ctk.CTkFont(size=13, weight="bold"))
        lbl_in.grid(row=0, column=0, padx=(0, 10), sticky="w")

        self.conv_in_entry = ctk.CTkEntry(in_frame, placeholder_text=self.tr("conv_in_ph"))
        self.conv_in_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.conv_in_entry.bind("<KeyRelease>", lambda e: self.on_conv_input_path_changed())

        btn_in = ctk.CTkButton(in_frame, text=self.tr("browse"), width=90, command=self.browse_conv_input)
        btn_in.grid(row=0, column=2)

        player_ctrl_bar = ctk.CTkFrame(scroll_card, fg_color="#1E1E26", corner_radius=8)
        player_ctrl_bar.pack(fill="x", padx=15, pady=(0, 10))

        self.conv_player_status_lbl = ctk.CTkLabel(
            player_ctrl_bar,
            text="🎵 Audio Player: No file selected",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.conv_player_status_lbl.pack(side="left", padx=15, pady=8)

        btn_play_full = ctk.CTkButton(
            player_ctrl_bar,
            text="▶ Play Input",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=110,
            height=26,
            fg_color="#00838F",
            command=self.play_conv_input_full
        )
        btn_play_full.pack(side="left", padx=3)

        btn_play_trimmed = ctk.CTkButton(
            player_ctrl_bar,
            text="✂️ Test Range",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=130,
            height=26,
            fg_color="#6A1B9A",
            command=self.play_conv_input_trimmed
        )
        btn_play_trimmed.pack(side="left", padx=3)

        btn_stop_conv_play = ctk.CTkButton(
            player_ctrl_bar,
            text=self.tr("stop"),
            font=ctk.CTkFont(size=11),
            width=60,
            height=26,
            fg_color="#D32F2F",
            command=self.stop_preview
        )
        btn_stop_conv_play.pack(side="left", padx=3)

        lbl_conv_vol = ctk.CTkLabel(player_ctrl_bar, text=self.tr("volume"), font=ctk.CTkFont(size=11))
        lbl_conv_vol.pack(side="left", padx=(15, 3))

        self.conv_vol_slider = ctk.CTkSlider(
            player_ctrl_bar,
            from_=0.0,
            to=1.0,
            number_of_steps=100,
            width=110,
            command=self.on_volume_change
        )
        self.conv_vol_slider.set(0.3)
        self.conv_vol_slider.pack(side="left", padx=3)

        preset_frame = ctk.CTkFrame(scroll_card, fg_color="#1E1E26", corner_radius=10)
        preset_frame.pack(fill="x", padx=15, pady=(4, 8))
        preset_frame.grid_columnconfigure(1, weight=1)

        lbl_preset = ctk.CTkLabel(
            preset_frame,
            text=self.tr("conv_preset_lbl"),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        lbl_preset.grid(row=0, column=0, padx=12, pady=10, sticky="w")

        self.preset_options = [self.tr("conv_preset_none")]
        self.preset_filename_map = {}

        for item in self.bgm_database:
            item_type = item.get("type", "BGM")
            title_name = item.get('course_name_en') if self.lang == "en" else item.get('course_name_ja')
            display_name = f"{'🎵' if item_type == 'BGM' else '🔊'} {title_name} [{item.get('filename')}]"
            self.preset_options.append(display_name)
            self.preset_filename_map[display_name] = item.get("filename")

        self.bgm_preset_dropdown = ctk.CTkOptionMenu(
            preset_frame,
            values=self.preset_options,
            font=ctk.CTkFont(size=12),
            command=self.on_bgm_preset_selected
        )
        self.bgm_preset_dropdown.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        out_frame = ctk.CTkFrame(scroll_card, fg_color="transparent")
        out_frame.pack(fill="x", padx=15, pady=6)
        out_frame.grid_columnconfigure(1, weight=1)

        lbl_out = ctk.CTkLabel(out_frame, text=self.tr("conv_out_lbl"), font=ctk.CTkFont(size=13, weight="bold"))
        lbl_out.grid(row=0, column=0, padx=(0, 10), sticky="w")

        default_output_path = os.path.join(self.custom_mods_dir, "custom_bgm.bfstm")
        self.conv_out_entry = ctk.CTkEntry(out_frame, placeholder_text=self.tr("conv_out_ph"))
        self.conv_out_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.conv_out_entry.insert(0, default_output_path)

        btn_out = ctk.CTkButton(out_frame, text=self.tr("browse"), width=90, command=self.browse_conv_output)
        btn_out.grid(row=0, column=2)

        timeline_card = ctk.CTkFrame(scroll_card, fg_color="#1E1E26", corner_radius=12)
        timeline_card.pack(fill="x", padx=15, pady=10)

        timeline_hdr = ctk.CTkFrame(timeline_card, fg_color="transparent")
        timeline_hdr.pack(fill="x", padx=15, pady=(12, 6))

        lbl_card_title = ctk.CTkLabel(
            timeline_hdr,
            text=self.tr("conv_timeline_title"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_card_title.pack(side="left")

        lbl_sr = ctk.CTkLabel(timeline_hdr, text=self.tr("conv_sr"), font=ctk.CTkFont(size=11))
        lbl_sr.pack(side="left", padx=(25, 5))

        self.sample_rate_option = ctk.CTkOptionMenu(
            timeline_hdr,
            values=["44100 Hz", "48000 Hz", "32000 Hz"],
            width=110,
            height=24,
            command=lambda v: self.recalculate_all_timeline_samples()
        )
        self.sample_rate_option.pack(side="left")

        self.audio_length_lbl = ctk.CTkLabel(
            timeline_hdr,
            text=f"{self.tr('conv_auto_len')} --:--",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#81D4FA"
        )
        self.audio_length_lbl.pack(side="right", padx=10)

        trim_sec_frame = ctk.CTkFrame(timeline_card, fg_color="#252532", corner_radius=10)
        trim_sec_frame.pack(fill="x", padx=15, pady=8)

        self.trim_switch = ctk.CTkSwitch(
            trim_sec_frame,
            text=self.tr("conv_trim_switch"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_trim_inputs
        )
        self.trim_switch.pack(anchor="w", padx=12, pady=(10, 6))

        trim_controls_frame = ctk.CTkFrame(trim_sec_frame, fg_color="transparent")
        trim_controls_frame.pack(fill="x", padx=12, pady=(0, 10))
        trim_controls_frame.grid_columnconfigure(1, weight=1)

        lbl_tstart = ctk.CTkLabel(trim_controls_frame, text=self.tr("conv_start_pos"), font=ctk.CTkFont(size=11, weight="bold"), text_color="#FF5252")
        lbl_tstart.grid(row=0, column=0, padx=5, pady=4, sticky="w")

        self.trim_start_slider = ctk.CTkSlider(
            trim_controls_frame,
            from_=0.0,
            to=self.input_audio_duration,
            number_of_steps=1000,
            button_color="#FF5252",
            button_hover_color="#FF1744",
            progress_color="#FF5252",
            command=self.on_start_slider_moved
        )
        self.trim_start_slider.grid(row=0, column=1, padx=10, pady=4, sticky="ew")
        self.trim_start_slider.set(0.0)

        self.trim_start_entry = ctk.CTkEntry(trim_controls_frame, width=110, placeholder_text="00:00.0")
        self.trim_start_entry.grid(row=0, column=2, padx=5, pady=4)
        self.trim_start_entry.insert(0, "00:00.0")
        self.trim_start_entry.bind("<KeyRelease>", lambda e: self.on_start_entry_changed())

        lbl_tend = ctk.CTkLabel(trim_controls_frame, text=self.tr("conv_end_pos"), font=ctk.CTkFont(size=11, weight="bold"), text_color="#29B6F6")
        lbl_tend.grid(row=1, column=0, padx=5, pady=4, sticky="w")

        self.trim_end_slider = ctk.CTkSlider(
            trim_controls_frame,
            from_=0.0,
            to=self.input_audio_duration,
            number_of_steps=1000,
            button_color="#29B6F6",
            button_hover_color="#00B0FF",
            progress_color="#29B6F6",
            command=self.on_end_slider_moved
        )
        self.trim_end_slider.grid(row=1, column=1, padx=10, pady=4, sticky="ew")
        self.trim_end_slider.set(self.input_audio_duration)

        self.trim_end_entry = ctk.CTkEntry(trim_controls_frame, width=110, placeholder_text="05:00.0")
        self.trim_end_entry.grid(row=1, column=2, padx=5, pady=4)
        self.trim_end_entry.insert(0, seconds_to_time_str(self.input_audio_duration))
        self.trim_end_entry.bind("<KeyRelease>", lambda e: self.on_end_entry_changed())

        loop_sec_frame = ctk.CTkFrame(timeline_card, fg_color="#252532", corner_radius=10)
        loop_sec_frame.pack(fill="x", padx=15, pady=(4, 12))

        self.loop_switch = ctk.CTkSwitch(
            loop_sec_frame,
            text=self.tr("conv_loop_switch"),
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.toggle_loop_inputs
        )
        self.loop_switch.pack(anchor="w", padx=12, pady=(10, 6))

        loop_controls_frame = ctk.CTkFrame(loop_sec_frame, fg_color="transparent")
        loop_controls_frame.pack(fill="x", padx=12, pady=(0, 10))
        loop_controls_frame.grid_columnconfigure(1, weight=1)

        lbl_lstart = ctk.CTkLabel(loop_controls_frame, text=self.tr("conv_lstart_pos"), font=ctk.CTkFont(size=11, weight="bold"), text_color="#00E676")
        lbl_lstart.grid(row=0, column=0, padx=5, pady=4, sticky="w")

        self.loop_start_slider = ctk.CTkSlider(
            loop_controls_frame,
            from_=0.0,
            to=self.input_audio_duration,
            number_of_steps=1000,
            button_color="#00E676",
            button_hover_color="#00C853",
            progress_color="#00E676",
            command=self.on_loop_start_slider_moved
        )
        self.loop_start_slider.grid(row=0, column=1, padx=10, pady=4, sticky="ew")
        self.loop_start_slider.set(0.0)

        self.loop_start_entry = ctk.CTkEntry(loop_controls_frame, width=110, placeholder_text="0")
        self.loop_start_entry.grid(row=0, column=2, padx=5, pady=4)
        self.loop_start_entry.insert(0, "0")
        self.loop_start_entry.bind("<KeyRelease>", lambda e: self.on_loop_start_entry_changed())

        lbl_lend = ctk.CTkLabel(loop_controls_frame, text=self.tr("conv_lend_pos"), font=ctk.CTkFont(size=11, weight="bold"), text_color="#AB47BC")
        lbl_lend.grid(row=1, column=0, padx=5, pady=4, sticky="w")

        self.loop_end_slider = ctk.CTkSlider(
            loop_controls_frame,
            from_=0.0,
            to=self.input_audio_duration,
            number_of_steps=1000,
            button_color="#AB47BC",
            button_hover_color="#8E24AA",
            progress_color="#AB47BC",
            command=self.on_loop_end_slider_moved
        )
        self.loop_end_slider.grid(row=1, column=1, padx=10, pady=4, sticky="ew")
        self.loop_end_slider.set(self.input_audio_duration)

        self.loop_end_entry = ctk.CTkEntry(loop_controls_frame, width=110, placeholder_text="2450000")
        self.loop_end_entry.grid(row=1, column=2, padx=5, pady=4)
        self.loop_end_entry.insert(0, str(parse_time_to_samples(seconds_to_time_str(self.input_audio_duration), 44100)))
        self.loop_end_entry.bind("<KeyRelease>", lambda e: self.on_loop_end_entry_changed())

        self.timeline_summary_lbl = ctk.CTkLabel(
            timeline_card,
            text="💡 Calculation Results...",
            font=ctk.CTkFont(size=11),
            text_color="#90CAF9"
        )
        self.timeline_summary_lbl.pack(anchor="w", padx=15, pady=(0, 12))

        self.toggle_trim_inputs()
        self.toggle_loop_inputs()

        self.btn_run_conv = ctk.CTkButton(
            scroll_card,
            text=self.tr("conv_run_btn"),
            font=ctk.CTkFont(size=15, weight="bold"),
            height=45,
            fg_color="#2E7D32",
            hover_color="#1B5E20",
            command=self.execute_conversion
        )
        self.btn_run_conv.pack(fill="x", padx=15, pady=12)

        self.log_textbox = ctk.CTkTextbox(scroll_card, height=120, font=ctk.CTkFont(family="Consolas", size=11))
        self.log_textbox.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.log_textbox.insert(tk.END, "--- Console Output ---\n")

        return frame

    def on_bgm_preset_selected(self, selected_display_name: str):
        filename = self.preset_filename_map.get(selected_display_name)
        if filename:
            target_path = os.path.join(self.custom_mods_dir, filename)
            self.conv_out_entry.delete(0, tk.END)
            self.conv_out_entry.insert(0, target_path)
            self.append_log(f"🎯 Output set to: '{filename}' ({selected_display_name})")

    def get_selected_sample_rate(self) -> int:
        val = self.sample_rate_option.get()
        if "48000" in val:
            return 48000
        elif "32000" in val:
            return 32000
        return 44100

    def toggle_trim_inputs(self):
        state = "normal" if self.trim_switch.get() == 1 else "disabled"
        self.trim_start_entry.configure(state=state)
        self.trim_end_entry.configure(state=state)
        self.trim_start_slider.configure(state=state)
        self.trim_end_slider.configure(state=state)
        self.recalculate_all_timeline_samples()

    def toggle_loop_inputs(self):
        state = "normal" if self.loop_switch.get() == 1 else "disabled"
        self.loop_start_entry.configure(state=state)
        self.loop_end_entry.configure(state=state)
        self.loop_start_slider.configure(state=state)
        self.loop_end_slider.configure(state=state)
        self.recalculate_all_timeline_samples()

    def on_start_slider_moved(self, value: float):
        if self.is_updating_sliders:
            return
        self.is_updating_sliders = True
        self.trim_start_entry.delete(0, tk.END)
        self.trim_start_entry.insert(0, seconds_to_time_str(value))
        self.recalculate_all_timeline_samples()
        self.is_updating_sliders = False

    def on_end_slider_moved(self, value: float):
        if self.is_updating_sliders:
            return
        self.is_updating_sliders = True
        self.trim_end_entry.delete(0, tk.END)
        self.trim_end_entry.insert(0, seconds_to_time_str(value))
        self.recalculate_all_timeline_samples()
        self.is_updating_sliders = False

    def on_start_entry_changed(self):
        if self.is_updating_sliders:
            return
        sr = self.get_selected_sample_rate()
        samples = parse_time_to_samples(self.trim_start_entry.get(), sr)
        sec = samples / float(sr)
        self.is_updating_sliders = True
        self.trim_start_slider.set(min(sec, self.input_audio_duration))
        self.recalculate_all_timeline_samples()
        self.is_updating_sliders = False

    def on_end_entry_changed(self):
        if self.is_updating_sliders:
            return
        sr = self.get_selected_sample_rate()
        samples = parse_time_to_samples(self.trim_end_entry.get(), sr)
        sec = samples / float(sr)
        self.is_updating_sliders = True
        self.trim_end_slider.set(min(sec, self.input_audio_duration))
        self.recalculate_all_timeline_samples()
        self.is_updating_sliders = False

    def on_loop_start_slider_moved(self, value: float):
        if self.is_updating_sliders:
            return
        self.is_updating_sliders = True
        sr = self.get_selected_sample_rate()
        samples = int(value * sr)
        self.loop_start_entry.delete(0, tk.END)
        self.loop_start_entry.insert(0, str(samples))
        self.recalculate_all_timeline_samples()
        self.is_updating_sliders = False

    def on_loop_end_slider_moved(self, value: float):
        if self.is_updating_sliders:
            return
        self.is_updating_sliders = True
        sr = self.get_selected_sample_rate()
        samples = int(value * sr)
        self.loop_end_entry.delete(0, tk.END)
        self.loop_end_entry.insert(0, str(samples))
        self.recalculate_all_timeline_samples()
        self.is_updating_sliders = False

    def on_loop_start_entry_changed(self):
        if self.is_updating_sliders:
            return
        sr = self.get_selected_sample_rate()
        samples = parse_time_to_samples(self.loop_start_entry.get(), sr)
        sec = samples / float(sr)
        self.is_updating_sliders = True
        self.loop_start_slider.set(min(sec, self.input_audio_duration))
        self.recalculate_all_timeline_samples()
        self.is_updating_sliders = False

    def on_loop_end_entry_changed(self):
        if self.is_updating_sliders:
            return
        sr = self.get_selected_sample_rate()
        samples = parse_time_to_samples(self.loop_end_entry.get(), sr)
        sec = samples / float(sr)
        self.is_updating_sliders = True
        self.loop_end_slider.set(min(sec, self.input_audio_duration))
        self.recalculate_all_timeline_samples()
        self.is_updating_sliders = False

    def recalculate_all_timeline_samples(self):
        sr = self.get_selected_sample_rate()

        t_start = parse_time_to_samples(self.trim_start_entry.get(), sr) if self.trim_switch.get() == 1 else 0
        t_end = parse_time_to_samples(self.trim_end_entry.get(), sr) if self.trim_switch.get() == 1 else int(self.input_audio_duration * sr)

        l_start = parse_time_to_samples(self.loop_start_entry.get(), sr) if self.loop_switch.get() == 1 else 0
        l_end = parse_time_to_samples(self.loop_end_entry.get(), sr) if self.loop_switch.get() == 1 else int(self.input_audio_duration * sr)

        trim_info = f"Trim: {t_start:,} - {t_end:,} samples" if self.trim_switch.get() == 1 else "Trim: Disabled"
        loop_info = f"Loop: {l_start:,} - {l_end:,} samples" if self.loop_switch.get() == 1 else "Loop: Disabled"

        self.timeline_summary_lbl.configure(
            text=f"💡 Calculated ({sr} Hz): {trim_info} | {loop_info}"
        )

    def on_conv_input_path_changed(self):
        path = self.conv_in_entry.get().strip()
        if path and os.path.exists(path):
            self.update_input_audio_info(path)

    def browse_conv_input(self):
        path = filedialog.askopenfilename(
            title="Select audio file",
            filetypes=[("Audio Files", "*.wav;*.mp3;*.flac;*.ogg;*.bfstm"), ("All Files", "*.*")]
        )
        if path:
            self.conv_in_entry.delete(0, tk.END)
            self.conv_in_entry.insert(0, path)

            base_filename = os.path.basename(path)
            base_name, _ = os.path.splitext(base_filename)
            
            if self.bgm_preset_dropdown.get() == self.tr("conv_preset_none"):
                target_path = os.path.join(self.custom_mods_dir, f"{base_name}.bfstm")
                self.conv_out_entry.delete(0, tk.END)
                self.conv_out_entry.insert(0, target_path)

            self.update_input_audio_info(path)

    def update_input_audio_info(self, file_path: str):
        dur = self.player.get_audio_duration(file_path)
        if dur <= 0:
            dur = 180.0

        self.input_audio_duration = dur
        self.audio_length_lbl.configure(text=f"{self.tr('conv_auto_len')} {seconds_to_time_str(dur)} ({dur:.1f}s)")
        self.conv_player_status_lbl.configure(text=f"🎵 {os.path.basename(file_path)} ({seconds_to_time_str(dur)})")

        self.is_updating_sliders = True

        self.trim_start_slider.configure(to=dur)
        self.trim_end_slider.configure(to=dur)
        self.trim_start_slider.set(0.0)
        self.trim_end_slider.set(dur)

        self.trim_start_entry.delete(0, tk.END)
        self.trim_start_entry.insert(0, "00:00.0")

        self.trim_end_entry.delete(0, tk.END)
        self.trim_end_entry.insert(0, seconds_to_time_str(dur))

        self.loop_start_slider.configure(to=dur)
        self.loop_end_slider.configure(to=dur)
        self.loop_start_slider.set(0.0)
        self.loop_end_slider.set(dur)

        sr = self.get_selected_sample_rate()
        self.loop_start_entry.delete(0, tk.END)
        self.loop_start_entry.insert(0, "0")

        self.loop_end_entry.delete(0, tk.END)
        self.loop_end_entry.insert(0, str(int(dur * sr)))

        self.is_updating_sliders = False
        self.recalculate_all_timeline_samples()

    def play_conv_input_full(self):
        in_path = self.conv_in_entry.get().strip()
        if not in_path or not os.path.exists(in_path):
            messagebox.showwarning("Warning", "Select input file.")
            return
        self.play_conv_input_at(0.0)

    def play_conv_input_trimmed(self):
        in_path = self.conv_in_entry.get().strip()
        if not in_path or not os.path.exists(in_path):
            messagebox.showwarning("Warning", "Select input file.")
            return

        sr = self.get_selected_sample_rate()
        start_samples = parse_time_to_samples(self.trim_start_entry.get(), sr)
        start_sec = start_samples / float(sr)
        self.play_conv_input_at(start_sec)

    def play_conv_input_at(self, start_sec: float):
        in_path = self.conv_in_entry.get().strip()
        target_path = in_path

        if in_path.lower().endswith(".bfstm"):
            temp_wav = os.path.join("temp", "conv_preview.wav")
            ok, msg = self.converter.convert(in_path, temp_wav)
            if ok:
                target_path = temp_wav
            else:
                messagebox.showerror("Error", msg)
                return

        vol = self.conv_vol_slider.get()
        self.player.load_and_play(target_path, start_sec=start_sec, volume=vol)
        self.conv_player_status_lbl.configure(
            text=f"▶ Playing: {os.path.basename(in_path)} (Start: {seconds_to_time_str(start_sec)})"
        )

    def browse_conv_output(self):
        path = filedialog.asksaveasfilename(
            title="Save Output File",
            initialdir=self.custom_mods_dir,
            filetypes=[("BFSTM Audio", "*.bfstm"), ("WAV Audio", "*.wav"), ("All Files", "*.*")]
        )
        if path:
            self.conv_out_entry.delete(0, tk.END)
            self.conv_out_entry.insert(0, path)

    def append_log(self, text: str):
        self.log_textbox.insert(tk.END, text + "\n")
        self.log_textbox.see(tk.END)

    def execute_conversion(self):
        in_path = self.conv_in_entry.get().strip()
        out_path = self.conv_out_entry.get().strip()

        if not in_path or not os.path.exists(in_path):
            messagebox.showwarning("Warning", "Valid input file is required.")
            return

        if not out_path:
            messagebox.showwarning("Warning", "Destination path is required.")
            return

        if not self.converter.is_available():
            messagebox.showerror("Error", "VGAudioCLI.exe not found.")
            return

        sr = self.get_selected_sample_rate()
        enable_trim = (self.trim_switch.get() == 1)
        trim_start = 0
        trim_end = 0

        if enable_trim:
            trim_start = parse_time_to_samples(self.trim_start_entry.get(), sr)
            trim_end = parse_time_to_samples(self.trim_end_entry.get(), sr)

            if trim_end <= trim_start:
                messagebox.showwarning("Warning", "End time must be greater than start time.")
                return

        enable_loop = (self.loop_switch.get() == 1)
        loop_start = 0
        loop_end = 0

        if enable_loop and out_path.lower().endswith(".bfstm"):
            try:
                loop_start = parse_time_to_samples(self.loop_start_entry.get(), sr)
                loop_end = parse_time_to_samples(self.loop_end_entry.get(), sr)
                if loop_end <= loop_start:
                    messagebox.showwarning("Warning", "Loop end must be greater than loop start.")
                    return
            except ValueError:
                messagebox.showerror("Error", "Check loop point input values.")
                return

        self.btn_run_conv.configure(state="disabled", text="⏳ Converting...")
        self.append_log(f"\n[Start] Conversion: {os.path.basename(in_path)} -> {os.path.basename(out_path)}")

        def worker():
            success, msg = self.converter.convert(
                in_path,
                out_path,
                enable_loop=enable_loop,
                loop_start=loop_start,
                loop_end=loop_end,
                enable_trim=enable_trim,
                trim_start=trim_start,
                trim_end=trim_end
            )

            self.after(0, lambda: self.on_conversion_finished(success, msg))

        threading.Thread(target=worker, daemon=True).start()

    def on_conversion_finished(self, success: bool, msg: str):
        self.btn_run_conv.configure(state="normal", text=self.tr("conv_run_btn"))
        if success:
            self.append_log(f"[Success] {msg}")
            messagebox.showinfo("Completed", msg)
        else:
            self.append_log(f"[Failed] {msg}")
            messagebox.showerror("Error", msg)

    # ------------------------------------------------------------------
    # View 5: ⚙️ Settings (設定) 画面
    # ------------------------------------------------------------------
    def build_settings_view(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            frame,
            text=self.tr("settings_title"),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 15))

        card = ctk.CTkFrame(frame, corner_radius=12)
        card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        card.grid_columnconfigure(0, weight=1)

        gsec = ctk.CTkFrame(card, fg_color="#1E1E26", corner_radius=10)
        gsec.pack(fill="x", padx=20, pady=15)
        gsec.grid_columnconfigure(1, weight=1)

        lbl_gtitle = ctk.CTkLabel(
            gsec,
            text=self.tr("game_dir_sec"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#81D4FA"
        )
        lbl_gtitle.grid(row=0, column=0, columnspan=3, padx=15, pady=(12, 6), sticky="w")

        lbl_gpath = ctk.CTkLabel(gsec, text=self.tr("game_dir_lbl"), font=ctk.CTkFont(size=12, weight="bold"))
        lbl_gpath.grid(row=1, column=0, padx=15, pady=10, sticky="w")

        self.setting_gdir_entry = ctk.CTkEntry(
            gsec,
            placeholder_text=self.tr("game_dir_ph"),
            font=ctk.CTkFont(size=12)
        )
        self.setting_gdir_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        if self.mod_manager.root_game_dir:
            self.setting_gdir_entry.insert(0, self.mod_manager.root_game_dir)

        btn_browse_setting = ctk.CTkButton(
            gsec,
            text=self.tr("browse"),
            width=110,
            command=self.browse_settings_game_dir
        )
        btn_browse_setting.grid(row=1, column=2, padx=(0, 15), pady=10)

        lsec = ctk.CTkFrame(card, fg_color="#1E1E26", corner_radius=10)
        lsec.pack(fill="x", padx=20, pady=15)
        lsec.grid_columnconfigure(1, weight=1)

        lbl_ltitle = ctk.CTkLabel(
            lsec,
            text=self.tr("lang_sec"),
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#A5D6A7"
        )
        lbl_ltitle.grid(row=0, column=0, columnspan=2, padx=15, pady=(12, 6), sticky="w")

        lbl_lselect = ctk.CTkLabel(lsec, text=self.tr("lang_lbl"), font=ctk.CTkFont(size=12, weight="bold"))
        lbl_lselect.grid(row=1, column=0, padx=15, pady=10, sticky="w")

        self.lang_option_menu = ctk.CTkOptionMenu(
            lsec,
            values=["English 🇺🇸", "日本語 🇯🇵"],
            font=ctk.CTkFont(size=12),
            width=180
        )
        self.lang_option_menu.grid(row=1, column=1, padx=10, pady=10, sticky="w")
        self.lang_option_menu.set("English 🇺🇸" if self.lang == "en" else "日本語 🇯🇵")

        btn_save_settings = ctk.CTkButton(
            card,
            text=self.tr("save_settings_btn"),
            font=ctk.CTkFont(size=15, weight="bold"),
            height=42,
            fg_color="#1F6AA5",
            command=self.save_all_settings
        )
        btn_save_settings.pack(fill="x", padx=20, pady=25)

        return frame

    def browse_settings_game_dir(self):
        path = filedialog.askdirectory(title="Select Cemu mlc01 or title folder")
        if path:
            self.setting_gdir_entry.delete(0, tk.END)
            self.setting_gdir_entry.insert(0, path)

    def save_all_settings(self):
        new_gdir = self.setting_gdir_entry.get().strip()
        type_map = {
            "⚡ Update (0005000e)": "UPDATE",
            "🎮 Base (00050000)": "BASE",
            "📦 DLC (0005000c)": "DLC",
            "📂 Custom Stream": "CUSTOM"
        }
        current_type = type_map.get(self.target_seg_btn.get(), "UPDATE")
        self.mod_manager.set_target_type(current_type, new_gdir)

        selected_lang_str = self.lang_option_menu.get()
        new_lang = "en" if "English" in selected_lang_str else "ja"
        self.lang = new_lang
        self.mod_manager.set_language(new_lang)

        self.apply_language_ui_update()
        messagebox.showinfo("Settings Saved", self.tr("settings_saved"))

    # ------------------------------------------------------------------
    # View 6: ℹ️ Credits (クレジット ＆ GitHub Star 要求) 画面
    # ------------------------------------------------------------------
    def build_credits_view(self) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            frame,
            text=self.tr("credits_title"),
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(0, 15))

        card = ctk.CTkFrame(frame, corner_radius=12)
        card.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        card.grid_columnconfigure(0, weight=1)

        csec = ctk.CTkFrame(card, fg_color="#1E1E26", corner_radius=10)
        csec.pack(fill="x", padx=25, pady=15)
        csec.grid_columnconfigure(0, weight=1)

        lbl_app_name = ctk.CTkLabel(
            csec,
            text="🎵 MK8D BFSTM Manager",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#64B5F6"
        )
        lbl_app_name.pack(pady=(20, 5))

        lbl_dev = ctk.CTkLabel(
            csec,
            text=self.tr("developed_by"),
            font=ctk.CTkFont(size=14, weight="bold")
        )
        lbl_dev.pack(pady=5)

        lbl_desc = ctk.CTkLabel(
            csec,
            text=self.tr("credits_desc"),
            font=ctk.CTkFont(size=12),
            text_color="gray",
            wraplength=700
        )
        lbl_desc.pack(pady=(5, 15))

        # ⭐ GitHub Star 促進カード
        star_card = ctk.CTkFrame(csec, fg_color="#2E2A12", corner_radius=8, border_width=1, border_color="#FFD54F")
        star_card.pack(fill="x", padx=20, pady=10)

        lbl_star_msg = ctk.CTkLabel(
            star_card,
            text=self.tr("star_req_msg"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FFEE58",
            wraplength=650
        )
        lbl_star_msg.pack(padx=15, pady=12)

        repo_frame = ctk.CTkFrame(csec, fg_color="#272736", corner_radius=8)
        repo_frame.pack(fill="x", padx=20, pady=(5, 15))
        repo_frame.grid_columnconfigure(1, weight=1)

        lbl_repo_title = ctk.CTkLabel(
            repo_frame,
            text=self.tr("repo_lbl"),
            font=ctk.CTkFont(size=12, weight="bold")
        )
        lbl_repo_title.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        lbl_repo_url = ctk.CTkLabel(
            repo_frame,
            text=self.tr("repo_url"),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#81D4FA"
        )
        lbl_repo_url.grid(row=0, column=1, padx=5, pady=12, sticky="w")

        btn_open_repo = ctk.CTkButton(
            csec,
            text=self.tr("open_repo_btn"),
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            fg_color="#F57F17",
            hover_color="#F57C00",
            command=lambda: webbrowser.open(self.tr("repo_url"))
        )
        btn_open_repo.pack(pady=(0, 20))

        return frame

    def apply_language_ui_update(self):
        self.title(self.tr("app_title"))

        self.btn_mod_mgr.configure(text=self.tr("tab_mod_mgr"))
        self.btn_db.configure(text=self.tr("tab_db"))
        self.btn_player.configure(text=self.tr("tab_player"))
        self.btn_converter.configure(text=self.tr("tab_converter"))
        self.btn_settings.configure(text=self.tr("tab_settings"))
        self.btn_credits.configure(text=self.tr("tab_credits"))
        self.btn_recheck.configure(text=self.tr("recheck"))

        for child in self.main_container.winfo_children():
            child.destroy()

        self.views = {}
        self.views["mod_manager"] = self.build_mod_manager_view()
        self.views["db"] = self.build_database_view()
        self.views["player"] = self.build_player_view()
        self.views["converter"] = self.build_converter_view()
        self.views["settings"] = self.build_settings_view()
        self.views["credits"] = self.build_credits_view()

        self.show_view("settings")


if __name__ == "__main__":
    app = BFSTMManagerApp()
    app.mainloop()
