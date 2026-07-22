import os
import wave
import glob
import logging
import pygame

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class AudioPlayer:
    """pygame.mixer を使用した音声再生・プレビュー制御クラス"""

    def __init__(self, temp_dir="temp"):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.temp_dir = os.path.join(self.base_dir, temp_dir)
        self.current_file = None
        self.is_paused = False
        self.volume = 0.3
        
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)
            pygame.mixer.music.set_volume(self.volume)
        except Exception as e:
            logging.error(f"Pygame Mixer 初期化失敗: {e}")

    def get_audio_duration(self, file_path: str) -> float:
        """
        指定された音声ファイル (WAV, MP3, BFSTM等) の長さ (秒) を高精度で全自動取得
        """
        if not file_path or not os.path.exists(file_path):
            return 0.0

        ext = os.path.splitext(file_path)[1].lower()

        # 1. WAV ファイルの標準ヘッダー解析
        if ext == ".wav":
            try:
                with wave.open(file_path, 'rb') as wf:
                    frames = wf.getnframes()
                    rate = wf.getframerate()
                    if rate > 0:
                        return frames / float(rate)
            except Exception:
                pass

        # 2. BFSTM ファイルのバイナリ解析
        if ext == ".bfstm":
            from converter import VGAudioConverter
            info = VGAudioConverter.get_bfstm_info(file_path)
            if info.get("duration_sec", 0.0) > 0:
                return info["duration_sec"]

        # 3. Pygame Sound での測定 (MP3, OGG 等)
        try:
            sound = pygame.mixer.Sound(file_path)
            dur = sound.get_length()
            if dur > 0:
                return dur
        except Exception:
            pass

        # 4. ファイルサイズからの概算
        try:
            size_bytes = os.path.getsize(file_path)
            # 一般的な 16bit 44.1kHz ステレオ WAV 相当 (176,400 bytes/sec)
            return max(1.0, size_bytes / 176400.0)
        except Exception:
            return 0.0

    def load_and_play(self, file_path: str, start_sec: float = 0.0, volume: float = None) -> tuple[bool, str]:
        if not os.path.exists(file_path):
            return False, f"再生対象のファイルが存在しません: {file_path}"

        try:
            self.stop()
            pygame.mixer.music.load(file_path)
            if volume is not None:
                self.set_volume(volume)
            else:
                pygame.mixer.music.set_volume(self.volume)
            
            pygame.mixer.music.play(start=start_sec)
            self.current_file = file_path
            self.is_paused = False
            return True, "再生開始"
        except Exception as e:
            return False, f"音声再生エラー: {str(e)}"

    def pause(self):
        if pygame.mixer.music.get_busy() and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True

    def unpause(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False

    def toggle_play_pause(self):
        if self.is_paused:
            self.unpause()
        elif pygame.mixer.music.get_busy():
            self.pause()

    def stop(self):
        try:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
        except Exception as e:
            logging.warning(f"Stop 時のエラー: {e}")
        self.is_paused = False
        self.current_file = None

    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
        try:
            if pygame.mixer.get_init():
                pygame.mixer.music.set_volume(self.volume)
        except Exception as e:
            logging.warning(f"音量設定エラー: {e}")

    def is_playing(self) -> bool:
        return pygame.mixer.get_init() is not None and pygame.mixer.music.get_busy() and not self.is_paused

    def get_current_file(self) -> str:
        return self.current_file

    def clear_temp_cache(self):
        self.stop()
        if os.path.exists(self.temp_dir):
            wav_files = glob.glob(os.path.join(self.temp_dir, "*.wav"))
            for f in wav_files:
                try:
                    os.remove(f)
                except Exception as e:
                    logging.warning(f"キャッシュファイル削除失敗 ({f}): {e}")
