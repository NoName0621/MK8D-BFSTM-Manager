import os
import json
import shutil
import logging
from converter import VGAudioConverter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ModManager:
    """ゲームフォルダの管理、Mod書き換え、およびバックアップ・復元を扱うマネージャー"""

    STATUS_NOT_FOUND = "NOT_FOUND"        # ゲームフォルダにファイルが存在しない
    STATUS_ORIGINAL = "ORIGINAL"          # オリジナル状態
    STATUS_MODDED = "MODDED"              # Mod適用中

    TITLE_BASE_ID = "00050000"
    TITLE_UPDATE_ID = "0005000e"
    TITLE_DLC_ID = "0005000c"
    GAME_CODE = "1010eb00"

    def __init__(self, settings_file="settings.json", backup_dir="backups"):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.settings_file = os.path.join(self.base_dir, settings_file)
        self.backup_dir = os.path.join(self.base_dir, backup_dir)
        
        self.original_backup_dir = os.path.join(self.backup_dir, "original")
        self.mod_backup_dir = os.path.join(self.backup_dir, "mods")

        os.makedirs(self.original_backup_dir, exist_ok=True)
        os.makedirs(self.mod_backup_dir, exist_ok=True)

        self.root_game_dir = ""
        self.target_type = "UPDATE"
        self.game_dir = ""
        self.content_root_dir = ""
        self.language = "en"  # デフォルト言語は English 🇺🇸

        # 高速化用キャッシュマップ
        self.file_path_index = {}       # filename.lower() -> list of full_paths
        self.metadata_cache = {}        # full_path -> info dict
        self._index_built = False

        self.load_settings()

    def rebuild_file_index(self):
        """ゲームフォルダ全体（Base / Update / DLC / titleルート全域）を 1 回だけ高速横断スキャン"""
        self.file_path_index = {}

        search_roots = []
        if self.game_dir and isinstance(self.game_dir, str) and os.path.exists(self.game_dir):
            search_roots.append(self.game_dir)
            parent_audio = os.path.dirname(self.game_dir)
            if os.path.exists(parent_audio):
                search_roots.append(parent_audio)

        if self.content_root_dir and isinstance(self.content_root_dir, str) and os.path.exists(self.content_root_dir) and self.content_root_dir not in search_roots:
            search_roots.append(self.content_root_dir)

        all_targets = self.detect_available_targets(self.root_game_dir)
        for cat_key in ["BASE", "UPDATE", "DLC"]:
            cat_dir = all_targets.get(cat_key, "")
            if cat_dir and isinstance(cat_dir, str) and os.path.exists(cat_dir):
                if cat_dir not in search_roots:
                    search_roots.append(cat_dir)
                parent_audio = os.path.dirname(cat_dir)
                if os.path.exists(parent_audio) and parent_audio not in search_roots:
                    search_roots.append(parent_audio)

        if self.root_game_dir and isinstance(self.root_game_dir, str) and os.path.exists(self.root_game_dir):
            if self.root_game_dir not in search_roots:
                search_roots.append(self.root_game_dir)

        for root_dir in search_roots:
            try:
                for root, _, files in os.walk(root_dir):
                    for f in files:
                        lower_name = f.lower()
                        full_p = os.path.join(root, f)
                        if lower_name not in self.file_path_index:
                            self.file_path_index[lower_name] = []
                        if full_p not in self.file_path_index[lower_name]:
                            self.file_path_index[lower_name].append(full_p)
            except Exception as e:
                logging.warning(f"Index build error: {e}")

        self._index_built = True

    def auto_find_stream_dir(self, start_path: str) -> str:
        if not start_path or not os.path.exists(start_path):
            return ""

        norm = os.path.normpath(start_path)

        candidates = [
            os.path.join(norm, "content", "audio", "stream"),
            os.path.join(norm, "audio", "stream"),
            os.path.join(norm, "content", "stream"),
            os.path.join(norm, "stream"),
            norm
        ]

        for cand in candidates:
            if os.path.exists(cand) and os.path.isdir(cand):
                files = os.listdir(cand)
                if any(f.lower().endswith(".bfstm") for f in files):
                    return cand

        for root, _, files in os.walk(norm):
            if any(f.lower().endswith(".bfstm") for f in files):
                return root

        return norm

    def detect_available_targets(self, path: str) -> dict:
        result = {
            "BASE": "",
            "UPDATE": "",
            "DLC": "",
            "root_found": False
        }

        if not path:
            return result

        norm = os.path.normpath(path)

        title_root = ""
        if "title" in norm.lower():
            parts = norm.split(os.sep)
            for i, p in enumerate(parts):
                if p.lower() == "title" and i + 2 < len(parts):
                    title_root = os.sep.join(parts[:i+1])
                    break
        elif "0005000" in norm:
            parts = norm.split(os.sep)
            for i, p in enumerate(parts):
                if p.startswith("0005000"):
                    title_root = os.sep.join(parts[:i])
                    break

        if not title_root or not os.path.exists(title_root):
            title_root = norm

        for key, tid in [("BASE", self.TITLE_BASE_ID), ("UPDATE", self.TITLE_UPDATE_ID), ("DLC", self.TITLE_DLC_ID)]:
            candidate_base = os.path.join(title_root, tid, self.GAME_CODE)
            if os.path.exists(candidate_base):
                stream_dir = self.auto_find_stream_dir(candidate_base)
                result[key] = stream_dir
                result["root_found"] = True

        return result

    def set_target_type(self, target_type: str, base_path: str = None):
        self.target_type = target_type
        if base_path:
            self.root_game_dir = base_path

        targets = self.detect_available_targets(self.root_game_dir)
        if target_type in targets and targets[target_type]:
            self.game_dir = targets[target_type]
        else:
            self.game_dir = self.auto_find_stream_dir(self.root_game_dir)

        if self.game_dir:
            norm = os.path.normpath(self.game_dir)
            if "content" in norm.lower():
                parts = norm.split(os.sep)
                for i, p in enumerate(parts):
                    if p.lower() == "content":
                        self.content_root_dir = os.sep.join(parts[:i+1])
                        break
            if not self.content_root_dir:
                self.content_root_dir = os.path.dirname(os.path.dirname(self.game_dir))

        self._index_built = False
        self.save_settings()

    def set_language(self, lang: str):
        self.language = lang
        self.save_settings()

    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.root_game_dir = data.get("root_game_dir", "")
                    self.target_type = data.get("target_type", "UPDATE")
                    self.game_dir = data.get("game_dir", "")
                    self.language = data.get("language", "en")  # デフォルト en
                    
                    if self.root_game_dir and not self.game_dir:
                        self.set_target_type(self.target_type, self.root_game_dir)
            except Exception as e:
                logging.error(f"設定ファイル読み込みエラー: {e}")

    def save_settings(self):
        try:
            with open(self.settings_file, "w", encoding="utf-8") as f:
                json.dump({
                    "root_game_dir": self.root_game_dir,
                    "target_type": self.target_type,
                    "game_dir": self.game_dir,
                    "language": self.language
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"設定ファイル保存エラー: {e}")

    def get_all_matching_game_paths(self, filename: str, aliases: list = None) -> list:
        if not self._index_built:
            self.rebuild_file_index()

        matched_paths = []
        check_names = [filename]
        if aliases:
            for a in aliases:
                if a not in check_names:
                    check_names.append(a)

        for name in check_names:
            lower = name.lower()
            if lower in self.file_path_index:
                for p in self.file_path_index[lower]:
                    if p not in matched_paths:
                        matched_paths.append(p)

        return matched_paths

    def get_game_file_path(self, filename: str, aliases: list = None) -> str:
        all_paths = self.get_all_matching_game_paths(filename, aliases)
        if all_paths:
            return all_paths[0]
        if self.game_dir:
            return os.path.join(self.game_dir, filename)
        return ""

    def get_bgm_metadata(self, filename: str, aliases: list = None) -> dict:
        file_path = self.get_game_file_path(filename, aliases)
        if not file_path or not os.path.exists(file_path):
            return {"exists": False, "duration_str": "--:--", "has_loop": False}

        if file_path in self.metadata_cache:
            return self.metadata_cache[file_path]

        info = VGAudioConverter.get_bfstm_info(file_path)
        self.metadata_cache[file_path] = info
        return info

    def has_original_backup(self, filename: str) -> bool:
        backup_path = os.path.join(self.original_backup_dir, filename)
        return os.path.exists(backup_path)

    def has_mod_backup(self, filename: str) -> bool:
        mod_path = os.path.join(self.mod_backup_dir, filename)
        return os.path.exists(mod_path)

    def get_file_status(self, filename: str, aliases: list = None) -> str:
        target_path = self.get_game_file_path(filename, aliases)
        if not target_path or not os.path.exists(target_path):
            return self.STATUS_NOT_FOUND

        orig_backup = os.path.join(self.original_backup_dir, filename)
        mod_backup = os.path.join(self.mod_backup_dir, filename)

        if os.path.exists(mod_backup):
            if os.path.exists(orig_backup):
                if os.path.getsize(target_path) == os.path.getsize(mod_backup):
                    return self.STATUS_MODDED

        return self.STATUS_ORIGINAL

    def apply_mod(self, filename: str, mod_file_path: str, aliases: list = None) -> tuple[bool, str]:
        if not self.game_dir or not os.path.exists(self.game_dir):
            return False, "Game directory is not set or does not exist." if self.language == "en" else "ゲームフォルダが指定されていないか、存在しません。"

        if not os.path.exists(mod_file_path):
            return False, f"Mod file not found: {mod_file_path}" if self.language == "en" else f"指定された Mod ファイルが見つかりません: {mod_file_path}"

        target_paths = self.get_all_matching_game_paths(filename, aliases)
        if not target_paths:
            default_p = os.path.join(self.game_dir, filename)
            target_paths = [default_p]

        orig_backup_path = os.path.join(self.original_backup_dir, filename)
        mod_backup_path = os.path.join(self.mod_backup_dir, filename)

        try:
            if os.path.exists(target_paths[0]) and not os.path.exists(orig_backup_path):
                shutil.copy2(target_paths[0], orig_backup_path)
                logging.info(f"Original backup created: {orig_backup_path}")

            shutil.copy2(mod_file_path, mod_backup_path)

            applied_count = 0
            for path in target_paths:
                out_dir = os.path.dirname(path)
                os.makedirs(out_dir, exist_ok=True)
                shutil.copy2(mod_file_path, path)
                applied_count += 1
                logging.info(f"Mod applied: {path}")

            self._index_built = False
            self.metadata_cache.clear()
            msg = f"Applied Mod to '{filename}' ({applied_count} locations updated, original protected)." if self.language == "en" else f"「{filename}」に Mod を適用しました。（関連 {applied_count} 箇所を一括更新・オリジナル保護済み）"
            return True, msg

        except Exception as e:
            return False, f"Error applying Mod: {str(e)}" if self.language == "en" else f"Mod 適用中にエラーが発生しました: {str(e)}"

    def restore_original(self, filename: str, aliases: list = None) -> tuple[bool, str]:
        orig_backup_path = os.path.join(self.original_backup_dir, filename)
        if not os.path.exists(orig_backup_path):
            return False, f"Original backup for '{filename}' does not exist." if self.language == "en" else f"「{filename}」のオリジナルバックアップが存在しません。"

        target_paths = self.get_all_matching_game_paths(filename, aliases)
        if not target_paths and self.game_dir:
            target_paths = [os.path.join(self.game_dir, filename)]

        try:
            restored_count = 0
            for path in target_paths:
                shutil.copy2(orig_backup_path, path)
                restored_count += 1
                logging.info(f"Original restored: {path}")

            self._index_built = False
            self.metadata_cache.clear()
            msg = f"Restored '{filename}' to original audio ({restored_count} locations)." if self.language == "en" else f"「{filename}」をオリジナルの音声に戻しました。（{restored_count} 箇所復元）"
            return True, msg
        except Exception as e:
            return False, f"Restore error: {str(e)}" if self.language == "en" else f"オリジナル復元エラー: {str(e)}"

    def reapply_mod(self, filename: str, aliases: list = None) -> tuple[bool, str]:
        mod_backup_path = os.path.join(self.mod_backup_dir, filename)
        if not os.path.exists(mod_backup_path):
            return False, f"Mod backup for '{filename}' does not exist." if self.language == "en" else f"「{filename}」の Mod バックアップが存在しません。"

        target_paths = self.get_all_matching_game_paths(filename, aliases)
        if not target_paths and self.game_dir:
            target_paths = [os.path.join(self.game_dir, filename)]

        try:
            reapplied_count = 0
            for path in target_paths:
                shutil.copy2(mod_backup_path, path)
                reapplied_count += 1
                logging.info(f"Mod reapplied: {path}")

            self._index_built = False
            self.metadata_cache.clear()
            msg = f"Reapplied Mod to '{filename}' ({reapplied_count} locations)." if self.language == "en" else f"「{filename}」に Mod を再適用しました。（{reapplied_count} 箇所更新）"
            return True, msg
        except Exception as e:
            return False, f"Reapply error: {str(e)}" if self.language == "en" else f"Mod 再適用エラー: {str(e)}"

    def restore_all_originals(self, db_items: list) -> tuple[int, int]:
        success_count = 0
        fail_count = 0

        for item in db_items:
            fname = item.get("filename")
            aliases = item.get("aliases", [])
            if fname and self.has_original_backup(fname):
                ok, _ = self.restore_original(fname, aliases)
                if ok:
                    success_count += 1
                else:
                    fail_count += 1

        self._index_built = False
        self.metadata_cache.clear()
        return success_count, fail_count

    def reapply_all_mods(self, db_items: list) -> tuple[int, int]:
        success_count = 0
        fail_count = 0

        for item in db_items:
            fname = item.get("filename")
            aliases = item.get("aliases", [])
            if fname and self.has_mod_backup(fname):
                ok, _ = self.reapply_mod(fname, aliases)
                if ok:
                    success_count += 1
                else:
                    fail_count += 1

        self._index_built = False
        self.metadata_cache.clear()
        return success_count, fail_count
