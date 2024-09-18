import numpy as np
import soundfile as sf
import sounddevice as sd
import threading
import time
import tkinter as tk
from tkinter import ttk

# パラメータ設定
grain_time = 300.0       # 単位：ミリ秒
envelope_time = 50.0     # 単位：ミリ秒
clip_margin = 0.1        # クリップを避けるための閾値
variance = 0.05          # ランダム性
rev = 0.0                # アクセルの値（0.0〜1.0）

# オーディオファイルの読み込み
filename = 'sample/lfa_original.wav'  # エンジン音のファイルパスを指定してください
data, samplerate = sf.read(filename)

# モノラルに変換
if data.ndim > 1:
    data = np.mean(data, axis=1)

# グレインのサイズを計算
grain_size = int(grain_time / 1000.0 * samplerate)
envelope_size = int(envelope_time / 1000.0 * samplerate)

# グレインの境界を検出
samples = len(data)
grain_indices = [0]

index = grain_size
while index < samples:
    found = False
    for r in range(grain_size // 2):
        right = index - r
        if right >= samples:
            continue
        if abs(data[right]) < clip_margin:
            index = right
            found = True
            break
    if not found:
        index += grain_size
        continue
    grain_indices.append(index)
    index += grain_size

# グレインをコピーしエンベロープを適用
grains = []
for i in range(len(grain_indices)):
    index = grain_indices[i]
    if i + 1 < len(grain_indices):
        next_index = grain_indices[i + 1]
    else:
        next_index = samples
    grain_data = data[index:next_index]

    # エンベロープの適用
    fade_in = np.linspace(0, 1, envelope_size)
    fade_out = np.linspace(1, 0, envelope_size)
    envelope = np.ones_like(grain_data)
    envelope[:envelope_size] *= fade_in
    envelope[-envelope_size:] *= fade_out
    grain_data *= envelope
    grains.append(grain_data)

# グレインをスケジュールし再生するクラス
class GrainPlayer(threading.Thread):
    def __init__(self, grains, samplerate):
        threading.Thread.__init__(self)
        self.grains = grains
        self.samplerate = samplerate
        self.grain_schedule = []
        self.current_grain = None
        self.playing = False
        self.stream = None
        self.lock = threading.Lock()

    def run(self):
        # オーディオストリームの開始
        self.stream = sd.OutputStream(samplerate=self.samplerate, channels=1, callback=self.callback)
        self.stream.start()
        self.playing = True
        while self.playing:
            self.schedule_grains()
            time.sleep(0.01)  # 10ミリ秒待機

    def stop(self):
        self.playing = False
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def schedule_grains(self):
        with self.lock:
            # 必要なだけグレインをスケジュール
            while len(self.grain_schedule) < max(1, int(2 * 0.1 / (grain_time / 1000.0))):
                # アクセルの値とランダム性に基づいてグレインを選択
                index = int(len(self.grains) * (rev + (np.random.rand() * 2 - 1) * variance))
                index = np.clip(index, 0, len(self.grains) - 1)
                self.grain_schedule.append(self.grains[index])

    def callback(self, outdata, frames, time_info, status):
        with self.lock:
            if self.current_grain is None or len(self.current_grain) == 0:
                if self.grain_schedule:
                    self.current_grain = self.grain_schedule.pop(0)
                else:
                    outdata[:] = np.zeros((frames, 1))
                    return
            chunk = self.current_grain[:frames]
            outdata[:len(chunk), 0] = chunk
            if len(chunk) < frames:
                remaining = frames - len(chunk)
                if self.grain_schedule:
                    self.current_grain = self.grain_schedule.pop(0)
                    next_chunk = self.current_grain[:remaining]
                    outdata[len(chunk):len(chunk)+len(next_chunk), 0] = next_chunk
                    self.current_grain = self.current_grain[remaining:]
                else:
                    outdata[len(chunk):, 0] = 0
                    self.current_grain = np.array([])
            else:
                self.current_grain = self.current_grain[frames:]

# GUIの設定
def on_rev_change(value):
    global rev
    rev = float(value)

root = tk.Tk()
root.title("Granular Engine Sound")

rev_slider = ttk.Scale(root, from_=0.0, to=1.0, orient='horizontal', command=on_rev_change)
rev_slider.pack()

player = GrainPlayer(grains, samplerate)
player.start()

root.mainloop()

player.stop()