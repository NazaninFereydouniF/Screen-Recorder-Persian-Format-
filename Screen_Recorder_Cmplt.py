import os  
import time  
import threading  

import cv2  
import numpy as np  
import customtkinter as ctk  
import mss  
import sounddevice as sd  
import soundfile as sf  

# ---------------- تنظیمات ----------------  
OUTPUT_DIR = "recordings"  
FPS = 15.0  
AUDIO_RATE = 44100  
CHANNELS = 1  

os.makedirs(OUTPUT_DIR, exist_ok=True)  


class ScreenRecorder:  
    def __init__(self):  
        self.recording = False  
        self.video_writer = None  
        self.audio_frames = []  
        self.audio_stream = None  
        self.video_thread = None  
        self.audio_thread = None  
        self.wav_path = None  
        self.video_path = None  

    # ---------- ضبط تصویر ----------  
    def _record_video(self):  
        with mss.mss() as sct:  
            monitor = sct.monitors[1]  # مانیتور اصلی  
            width = monitor["width"]  
            height = monitor["height"]  

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")  
            self.video_writer = cv2.VideoWriter(  
                self.video_path, fourcc, FPS, (width, height)  
            )  

            frame_interval = 1.0 / FPS  
            next_time = time.time()  
            while self.recording:  
                now = time.time()  
                if now < next_time:  
                    time.sleep(max(0, next_time - now))  
                    continue  
                next_time += frame_interval  

                img = np.array(sct.grab(monitor))  # BGRA  
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  
                self.video_writer.write(frame)  

            self.video_writer.release()  
            self.video_writer = None  

    # ---------- ضبط صدا ----------  
    def _audio_callback(self, indata, frames, time_info, status):  
        if self.recording:  
            self.audio_frames.append(indata.copy())  

    def _record_audio(self):  
        with sd.InputStream(  
            samplerate=AUDIO_RATE,  
            channels=CHANNELS,  
            callback=self._audio_callback,  
        ):  
            while self.recording:  
                time.sleep(0.05)  

    # ---------- شروع و توقف ----------  
    def start(self):  
        if self.recording:  
            return  
        ts = time.strftime("%Y%m%d_%H%M%S")  
        self.video_path = os.path.join(OUTPUT_DIR, f"video_{ts}.mp4")  
        self.wav_path = os.path.join(OUTPUT_DIR, f"audio_{ts}.wav")  
        self.audio_frames = []  
        self.recording = True  

        self.video_thread = threading.Thread(target=self._record_video, daemon=True)  
        self.audio_thread = threading.Thread(target=self._record_audio, daemon=True)  
        self.video_thread.start()  
        self.audio_thread.start()  

    def stop(self):  
        if not self.recording:  
            return  
        self.recording = False  
        self.video_thread.join(timeout=5)  
        self.audio_thread.join(timeout=5)  

        # ذخیره صدا  
        if self.audio_frames:  
            audio_data = np.concatenate(self.audio_f