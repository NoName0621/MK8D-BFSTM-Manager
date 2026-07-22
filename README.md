# 🎵 MK8D BFSTM Manager

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)
![Status](https://img.shields.io/badge/Status-Beta--Active-orange.svg)
[![Japanese README](https://img.shields.io/badge/Language-%E6%97%A5%E6%9C%AC%E8%AA%9E-red)](README_JP.md)
[![GitHub Stars](https://img.shields.io/github/stars/NoName0621/MK8D-BFSTM-Manager?style=social)](https://github.com/NoName0621/MK8D-BFSTM-Manager)

> 🇯🇵 **[日本語のドキュメント (README_JP.md) はこちらをご参照ください。](README_JP.md)**

> ⚠️ **Notice / Work in Progress**:  
> This application is currently in early active development (**Beta**). Some features, audio conversions, or file detections may be incomplete or encounter unstable behavior. Please make sure to back up your game files before applying mods. Bug reports and feedback are highly appreciated!

---

**MK8D BFSTM Manager** is a modern GUI application for managing, previewing, and converting custom BGM & SFX (BFSTM) audio mods for **Mario Kart 8** and **Mario Kart 8 Deluxe** (Cemu / Hardware Consoles).

---

## ⭐ Support the Project (Give a Star!)

If you find this tool helpful or useful for your custom audio mods, please consider giving this repository a **⭐ Star** on GitHub!  
It helps the project gain visibility and supports future updates & improvements.

---

## 📖 Detailed Usage Guide

### 🕹️ 1. Direct Management for Cemu (PC Emulator)

1. Launch the app and navigate to the **`⚙️ Settings`** tab in the sidebar.
2. Under `Root Game / mlc01 Path`, select your Cemu `mlc01` directory (e.g. `I:\cemu\mlc01\usr\title`) and click `💾 Save Settings`.
3. Open the **`🎮 Game Mod Manager`** tab.
4. Select your target category (`Update`, `Base`, or `DLC`). Your BGM and SFX files will be listed with active status badges.
5. Click `Apply Mod...` for any track and select your custom `.bfstm` file.
   - **Automatic Protection**: Original game files are automatically backed up before any modifications.
   - **Multi-path Sync**: All related aliases across Update and Base paths are updated together to prevent game resets.
6. Click `Restore` anytime to revert to the original audio instantly.

---

### 🎮 2. Creating Custom Mods for Real Hardware (Wii U / Nintendo Switch)

1. Navigate to the **`🔄 Audio Converter`** tab in the sidebar.
2. Select your source audio file (.mp3, .wav, .flac, .ogg, etc.) under `Input File`.
3. Select your target course or SFX from the `🎯 Replace Target BGM / SE` dropdown menu.
4. **Timeline & Trimming**:
   - Enable `✂️ Audio Trimming` to specify custom start/end playback boundaries.
   - Enable `🔁 Loop Points` to adjust seamless in-game loop start and end sample values.
5. Click `⚡ Convert & Save to custom_sound_mods`.
6. Copy the generated `.bfstm` file from the `custom_sound_mods/` folder to your hardware SD card:

   - **Wii U (SDCafiine)**:
     ```text
     sd:/sdcafiine/00050000/1010eb00/content/audio/stream/ [Place .bfstm here]
     ```
   - **Nintendo Switch (Atmosphère / MK8DX)**:
     ```text
     sd:/atmosphere/contents/0100152000022000/romfs/stream/ [Place .bfstm here]
     ```

---

## ✨ Features

- 🎮 **Non-destructive Game Mod Management**:
  - Automatically backs up original game audio and seamlessly applies/restores custom `.bfstm` mods without damaging game files.
- 🔊 **Full BGM & SE (SFX) Support**:
  - Customize not only course background music (BGM) but also sound effects (Star invincible music, Goal fanfares, Countdown signals, etc.).
- 🎚️ **Integrated Dual-Pointer Timeline & Trim Editor**:
  - Dual-pointer sliders to slice custom audio ranges and set exact loop points with sample-rate calculation (44100 / 48000 / 32000 Hz).
- 🎧 **Built-in BFSTM / WAV Preview Player**:
  - Listen to `.bfstm` files directly inside the application with safe default volume controls.
- ⚡ **Asynchronous & Fast $O(1)$ Search**:
  - Threaded background index scanning ensures a lag-free UI, avoiding any "Not Responding" freezes.
- 🌐 **Multilingual Support (i18n)**:
  - English 🇺🇸 (Default) and Japanese 🇯🇵 with persistent language settings.

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- `VGAudioCLI.exe` (Place inside the `tools/` directory)

### Installation & Run

1. Clone this repository:
   ```cmd
   git clone https://github.com/NoName0621/MK8D-BFSTM-Manager.git
   cd MK8D-BFSTM-Manager
   ```

2. Install dependencies:
   ```cmd
   pip install customtkinter pygame-ce
   ```

3. Launch the application:
   ```cmd
   python main.py
   ```

---

## 🛠️ Requirements

- `customtkinter`
- `pygame-ce`
- [VGAudio](https://github.com/Thealexbarney/VGAudio) (`VGAudioCLI.exe`)

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

Developed with ❤️ by **NoName0621**
