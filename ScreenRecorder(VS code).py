import customtkinter as ctk
import pyautogui
import numpy as np
import cv2
import pyaudio
import wave
import threading
import time
from moviepy.editor import VideoFileClip, AudioFileClip
from tkinter import messagebox

#Main Customtkinter Setting
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class ScreenRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("HZ ScreenRecorder")
        self.root.geometry("400x300")

        self.recording = False
        self.video_writer = None
        self.audio_frames = []
        self.start_time = None

        self.FPS = 20
        self.video_thread = None
        self.audio_thread = None
        self.saving_done = False
        self.save_error = None

        #User Interface
        self.title_label = ctk.CTkLabel(root, text = "Screen Recorder", font = ("Times New Roman", 20))
        self.title_label.pack(pady = 10)

        self.start_button = ctk.CTkButton(root, text = "Start Recording", font = ("Times New Roman", 20), command = self.start_recording)
        self.start_button.pack(pady = 10)

        self.stop_button = ctk.CTkButton(root, text = "Stop Recording", font = ("Times New Roman", 20), command = self.stop_recording, state = ctk.DISABLED)
        self.stop_button.pack(pady = 10)

        self.status_label = ctk.CTkLabel(root, text = "Status: Idle", font = ("Times New Roman", 15))
        self.status_label.pack(pady = 10)

    def start_recording(self):
        self.recording = True
        self.start_button.configure(state = ctk.DISABLED)
        self.stop_button.configure(state = ctk.NORMAL)
        self.status_label.configure(text = "Status: Recording...")

        #Record Video Settings
        first = pyautogui.screenshot()
        w, h = first.size
        w -= w % 2
        h -= h % 2
        self.frame_size = (w, h)
        fource = cv2.VideoWriter_fourcc(*"mp4v")
        self.video_writer = cv2.VideoWriter("output_video.mp4", fource, self.FPS, self.frame_size)

        if not self.video_writer.isOpened():
            messagebox.showerror("Error", "VideoWriter could not be opened")
            self.recording = False
            self.start_button.configure(state = ctk.NORMAL)
            self.stop_button.configure(state = ctk.DISABLED)
            self.status_label.configure(text = "Status: Idle")
            return

        #Microphone Settings
        self.audio_frames = []
        self.audio = pyaudio.PyAudio()
        self.audio_stream = self.audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

        #Thread Recording
        self.start_time = time.time()
        self.video_thread = threading.Thread(target=self.record_screen, daemon=True)
        self.audio_thread = threading.Thread(target=self.record_audio, daemon=True)
        self.video_thread.start()
        self.audio_thread.start()

        #Timer label runs on the main Tkinter thread
        self.update_timer()

    def update_timer(self):
        if self.recording:
            sec = int(time.time() - self.start_time)
            self.status_label.configure(text = f"Status: Recording ...{sec}s")
            self.root.after(500, self.update_timer)

    def record_screen(self):
        #NOTE: no Tkinter calls in this thread (they cause a deadlock)
        frames_written = 0
        w, h = self.frame_size
        while self.recording:
            img = pyautogui.screenshot()
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            frame = np.ascontiguousarray(frame[:h, :w])

            elapsed_time = time.time() - self.start_time
            target = int(elapsed_time * self.FPS) + 1
            while frames_written < target:
                self.video_writer.write(frame)
                frames_written += 1

    def record_audio(self):
        while self.recording:
            data = self.audio_stream.read(1024, exception_on_overflow=False)
            self.audio_frames.append(data)

    def stop_recording(self):
        self.recording = False
        self.stop_button.configure(state = ctk.DISABLED)
        self.status_label.configure(text = "Status: Saving...")

        #Do the slow work in a separate thread so the window stays responsive
        self.saving_done = False
        self.save_error = None
        threading.Thread(target=self.finish_recording, daemon=True).start()
        self.check_finished()

    def finish_recording(self):
        #NOTE: runs in a worker thread, so no Tkinter calls here
        try:
            #Wait for recording threads to finish
            self.video_thread.join()
            self.audio_thread.join()

            #Stop Video Recording
            self.video_writer.release()

            #Stop Audio Recording
            self.audio_stream.stop_stream()
            self.audio_stream.close()
            sample_width = self.audio.get_sample_size(pyaudio.paInt16)
            self.audio.terminate()

            #Microphone Sound Download or Save
            with wave.open("output_audio.wav", "wb") as wf:
                wf.setnchannels(1)
                wf.setsampwidth(sample_width)
                wf.setframerate(44100)
                wf.writeframes(b"".join(self.audio_frames))

            #Combine Sound & Video
            self.combine_audio_video("output_video.mp4", "output_audio.wav", "output_final.mp4")
        except Exception as e:
            self.save_error = e
        finally:
            self.saving_done = True

    def check_finished(self):
        #Runs on the main thread; polls until the worker finishes
        if not self.saving_done:
            self.root.after(200, self.check_finished)
            return

        self.start_button.configure(state = ctk.NORMAL)
        self.status_label.configure(text = "Status: Idle")
        if self.save_error:
            messagebox.showerror("Error", f"Saving failed:\n{self.save_error}")
        else:
            messagebox.showinfo("info", "Recording saved as output_final.mp4")

    def combine_audio_video(self, video_path, audio_path, output_path):
        video_clip = VideoFileClip(video_path)
        audio_clip = AudioFileClip(audio_path)

        #Combine Microphone & Video
        final_clip = video_clip.set_audio(audio_clip)
        final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

        #Close(END)
        video_clip.close()
        audio_clip.close()

if __name__ == "__main__":
    root = ctk.CTk()
    recorder = ScreenRecorder(root)
    root.mainloop()