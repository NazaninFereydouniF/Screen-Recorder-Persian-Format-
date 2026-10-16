# HZ ScreenRecorder 🎥

Lightweight screen + microphone recorder with a modern CustomTkinter GUI.
Captures the full screen, records mic audio, and merges them into one MP4.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 🖥️ Full-screen recording (20 FPS)
- 🎙️ Microphone recording (44.1 kHz, mono)
- 🔗 Auto-merge to `output_final.mp4` (H.264 + AAC)
- ⏱️ Live recording timer
- 🖌️ Dark-mode GUI with CustomTkinter
- 🧊 Non-freezing UI + error popups

## 🛠️ Built With

`Python` · `CustomTkinter` · `PyAutoGUI` · `OpenCV` · `PyAudio` · `MoviePy` · `NumPy`

## 📋 Requirements

- Python 3.8+
- FFmpeg installed and in PATH ([ffmpeg.org](https://ffmpeg.org/download.html))
- Working microphone

```bash
pip install customtkinter pyautogui numpy opencv-python pyaudio moviepy
```

> Windows: if PyAudio fails, install a prebuilt wheel from
> `lfd.uci.edu/~gohlke/pythonlibs/#pyaudio`.
>
> MoviePy v2: use `from moviepy import VideoFileClip, AudioFileClip`.

## 🚀 Usage

```bash
python "ScreenRecorder(VS code).py"
```

1. Click **Start Recording**
2. Click **Stop Recording** → wait for `Saving...`
3. Done → `output_final.mp4`

```
output_video.mp4  # raw video
output_audio.wav  # raw audio
output_final.mp4  # merged result
```

## ⚙️ Config

```python
self.FPS = 20                 # video fps
# audio: 44100 Hz, mono, chunk 1024
self.root.geometry("400x300") # window size
```

Change theme at the top of the file:

```python
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")
```

## 🧠 How It Works

- Thread 1: screenshots → OpenCV writer (`mp4v`)
- Thread 2: PyAudio stream → frame list → WAV
- On stop: threads join, WAV saved, MoviePy merges A/V
- Timer and save-status poll via `root.after()` (thread-safe UI)

## 🔮 Roadmap

- Timestamped filenames (no overwrite)
- Pause / Resume
- Region capture + system audio
- Replace PyAutoGUI with `mss` for higher FPS

## 🤝 Contributing

PRs welcome! Open an issue first for major changes.

## 📄 License

MIT — see [LICENSE](LICENSE) for details.
