import os
import wave
import struct
import subprocess
import logging
import pygame

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class VGAudioConverter:
    """VGAudioCLI.exe を利用して BFSTM / WAV などの相互変換を行う変換クラス"""

    def __init__(self, tools_dir="tools", custom_cli_path=None):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.tools_dir = os.path.join(self.base_dir, tools_dir)
        self.temp_dir = os.path.join(self.base_dir, "temp")
        self.custom_cli_path = custom_cli_path
        os.makedirs(self.temp_dir, exist_ok=True)

    def get_cli_path(self):
        if self.custom_cli_path and os.path.isfile(self.custom_cli_path):
            return self.custom_cli_path
        
        default_path = os.path.join(self.tools_dir, "VGAudioCLI.exe")
        if os.path.isfile(default_path):
            return default_path
        
        alt_path = os.path.join(os.getcwd(), "tools", "VGAudioCLI.exe")
        if os.path.isfile(alt_path):
            return alt_path
            
        return None

    def is_available(self):
        path = self.get_cli_path()
        return path is not None and os.path.exists(path)

    @staticmethod
    def get_bfstm_info(file_path: str) -> dict:
        info = {
            "exists": False,
            "has_loop": False,
            "sample_rate": 44100,
            "total_samples": 0,
            "loop_start": 0,
            "loop_end": 0,
            "duration_sec": 0.0,
            "duration_str": "--:--"
        }

        if not file_path or not os.path.exists(file_path):
            return info

        info["exists"] = True

        try:
            with open(file_path, "rb") as f:
                data = f.read(512)

            magic = data[0:4]
            if magic in [b"FSTM", b"CSTM", b"RSTM"]:
                endian = ">" if data[4:6] == b"\xfe\xff" else "<"
                info_pos = data.find(b"INFO")
                if info_pos != -1 and len(data) >= info_pos + 40:
                    is_loop = (data[info_pos + 0x18] != 0) if len(data) > info_pos + 0x18 else False
                    sample_rate = struct.unpack(endian + "I", data[info_pos + 0x1C:info_pos + 0x20])[0] if len(data) >= info_pos + 0x20 else 44100
                    loop_start = struct.unpack(endian + "I", data[info_pos + 0x20:info_pos + 0x24])[0] if len(data) >= info_pos + 0x24 else 0
                    total_samples = struct.unpack(endian + "I", data[info_pos + 0x24:info_pos + 0x28])[0] if len(data) >= info_pos + 0x28 else 0

                    if sample_rate > 0:
                        duration_sec = total_samples / float(sample_rate)
                        mins = int(duration_sec // 60)
                        secs = int(duration_sec % 60)

                        info["has_loop"] = bool(is_loop)
                        info["sample_rate"] = sample_rate
                        info["total_samples"] = total_samples
                        info["loop_start"] = loop_start
                        info["loop_end"] = total_samples if is_loop else 0
                        info["duration_sec"] = duration_sec
                        info["duration_str"] = f"{mins:02d}:{secs:02d}"
                        return info

        except Exception as e:
            logging.warning(f"BFSTM ヘッダー解析失敗 ({file_path}): {e}")

        try:
            size_mb = os.path.getsize(file_path) / (1024 * 1024)
            est_sec = size_mb * 30.0
            mins = int(est_sec // 60)
            secs = int(est_sec % 60)
            info["duration_str"] = f"~{mins:02d}:{secs:02d}"
            info["has_loop"] = True
        except Exception:
            pass

        return info

    def _prepare_intermediate_wav(self, input_path: str, enable_trim: bool, trim_start: int, trim_end: int, target_sr: int = 44100) -> tuple[str, int]:
        """
        MP3/OGG等の非WAV音源のデコード、および指定サンプル範囲の切り出しを完全処理した中間 WAV を生成。
        返り値: (中間WAVのパス, 中間WAVの総サンプル数)
        """
        temp_wav = os.path.join(self.temp_dir, "intermediate_trimmed.wav")
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass

        actual_input = input_path
        if input_path.lower().endswith(".bfstm"):
            decompressed_wav = os.path.join(self.temp_dir, "temp_decompressed.wav")
            cli = self.get_cli_path()
            if cli:
                subprocess.run([cli, "-i", input_path, "-o", decompressed_wav], capture_output=True)
                if os.path.exists(decompressed_wav):
                    actual_input = decompressed_wav

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=target_sr, size=-16, channels=2)

            sound = pygame.mixer.Sound(actual_input)
            raw_bytes = sound.get_raw()

            bytes_per_sample = 4  # 16-bit stereo = 4 bytes per frame
            total_samples = len(raw_bytes) // bytes_per_sample

            start_idx = 0
            end_idx = total_samples

            if enable_trim:
                start_idx = max(0, min(trim_start, total_samples))
                end_idx = max(start_idx, min(trim_end, total_samples))

            sliced_bytes = raw_bytes[start_idx * bytes_per_sample : end_idx * bytes_per_sample]
            out_samples = len(sliced_bytes) // bytes_per_sample

            with wave.open(temp_wav, "wb") as wf:
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(target_sr)
                wf.writeframes(sliced_bytes)

            if os.path.exists(temp_wav) and os.path.getsize(temp_wav) > 44:
                return temp_wav, out_samples

        except Exception as e:
            logging.warning(f"Pygame での切り出しWAV生成スキップ/例外: {e}")

        # フォールバック: WAVファイル直接読み込み
        if actual_input.lower().endswith(".wav"):
            try:
                with wave.open(actual_input, 'rb') as wf:
                    return actual_input, wf.getnframes()
            except Exception:
                pass

        return actual_input, 0

    def convert(
        self,
        input_path: str,
        output_path: str,
        enable_loop: bool = False,
        loop_start: int = 0,
        loop_end: int = 0,
        enable_trim: bool = False,
        trim_start: int = 0,
        trim_end: int = 0
    ) -> tuple[bool, str]:
        cli_path = self.get_cli_path()
        if not cli_path:
            return False, "VGAudioCLI.exe が見つかりません。'tools' フォルダに配置してください。"

        if not os.path.isfile(input_path):
            return False, f"入力ファイルが存在しません: {input_path}"

        out_dir = os.path.dirname(os.path.abspath(output_path))
        if not os.path.exists(out_dir):
            os.makedirs(out_dir, exist_ok=True)

        # トリミングまたは非WAV入力の場合は中間 WAV を生成し、実際の総サンプル数を取得
        target_input, actual_total_samples = self._prepare_intermediate_wav(input_path, enable_trim, trim_start, trim_end)

        cmd = [cli_path, "-i", target_input, "-o", output_path]

        if output_path.lower().endswith(".bfstm"):
            if enable_loop:
                # 🎯 ループポイントが実データサンプル数を超えないように自動安全アジャスト (クランプ)
                eff_lstart = max(0, loop_start)
                eff_lend = loop_end

                # トリミングが行われた場合、相対オフセット補正
                if enable_trim and eff_lend > (trim_end - trim_start):
                    eff_lend = trim_end - trim_start

                if actual_total_samples > 0:
                    eff_lstart = min(eff_lstart, actual_total_samples - 1)
                    eff_lend = min(eff_lend, actual_total_samples - 1)

                if eff_lend > eff_lstart:
                    cmd.extend(["-l", f"{eff_lstart}-{eff_lend}"])
                else:
                    cmd.append("--no-loop")
            else:
                cmd.append("--no-loop")

        logging.info(f"変換実行コマンド: {' '.join(cmd)}")

        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                startupinfo=startupinfo,
                check=False
            )

            if result.returncode == 0 and os.path.exists(output_path):
                return True, f"変換完了: {output_path}"
            else:
                err_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                if not err_msg:
                    err_msg = f"終了コード: {result.returncode}"
                return False, f"VGAudioCLI エラー: {err_msg}"

        except Exception as e:
            return False, f"変換処理中に例外が発生しました: {str(e)}"
