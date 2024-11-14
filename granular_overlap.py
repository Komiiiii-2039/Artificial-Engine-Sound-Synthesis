import numpy as np
import soundfile as sf
import sounddevice as sd
import threading
import time
import tkinter as tk
from tkinter import ttk

# パラメータ設定
grain_time = 300.0       # 単位：ミリ秒
envelope_time = 150.0     # 単位：ミリ秒（オーバーラップ量に影響）
clip_margin = 0.8       # クリップを避けるための閾値
variance = 0.00          # ランダム性

# オーディオファイルの読み込み
filename = 'sample/audi_a4_clip.wav'  # エンジン音のファイルパスを指定してください
data, samplerate = sf.read(filename)

# モノラルに変換
if data.ndim > 1:
    data = np.mean(data, axis=1)

# clipの閾値を可視化
print(f"Max amplitude: {np.max(abs(data))}")
print(f"Min amplitude: {np.min(abs(data))}")
print(f"Mean amplitude: {np.mean(abs(data))}")

import matplotlib.pyplot as plt

#plt.hist(abs(data), bins=100)
#plt.title("Amplitude Histogram")
#plt.xlabel("Amplitude")
#plt.ylabel("Frequency")
#plt.show()

#----------------グレインを作成--------------------------
# グレインのサイズを計算
grain_size = int(grain_time / 1000.0 * samplerate)      # グレインの長さ（サンプル数）
envelope_size = int(envelope_time / 1000.0 * samplerate)  # エンベロープの長さ（サンプル数）

# グレインの境界を設定
grain_step = grain_size - envelope_size  # オーバーラップするためのステップサイズ

# グレインを抽出しエンベロープを適用
grains = []
index = 0
while index + grain_size <= len(data):
    grain_data = data[index:index + grain_size].copy()
    # エンベロープの適用
    envelope = np.ones(grain_size)
    fade_in = np.linspace(0, 1, envelope_size)
    fade_out = np.linspace(1, 0, envelope_size)
    envelope[:envelope_size] *= fade_in
    envelope[-envelope_size:] *= fade_out
    grain_data *= envelope
    grains.append(grain_data)
    index += grain_step  # 次のグレインへ移動

#--------------------------------------------------------------

#-----------------グレインを再生するクラス-------------------------
class GrainPlayer(threading.Thread):
    def __init__(self, grains, samplerate):
        threading.Thread.__init__(self)
        self.grains = grains
        self.samplerate = samplerate
        self.playing = False
        self.stream = None
        self.lock = threading.Lock()
        self.target_rev = 0.0
        self.current_rev = 0.0
        self.buffer = np.array([])
        self.buffer_lock = threading.Lock()
        self.grain_interval = (grain_step / self.samplerate)

    def run(self):
        # オーディオストリームの開始
        self.stream = sd.OutputStream(samplerate=self.samplerate, channels=1, callback=self.callback)
        self.stream.start()
        self.playing = True
        while self.playing:
            # current_revをtarget_revに向かって徐々に変化させる
            with self.lock:
                if self.current_rev < self.target_rev:
                    self.current_rev = min(self.current_rev + 0.02, self.target_rev)
                elif self.current_rev > self.target_rev:
                    self.current_rev = max(self.current_rev - 0.02, self.target_rev)
                current_rev = self.current_rev

            # グレインの選択
            index = int(len(self.grains) * (current_rev + np.random.uniform(-1, 1) * variance))
            index = np.clip(index, 0, len(self.grains) - 1)
            grain = self.grains[index]

            # バッファにグレインをオーバーラップ・アドで追加
            with self.buffer_lock:
                buffer_len = len(self.buffer)
                overlap_len = min(envelope_size, buffer_len)
                if overlap_len > 0:
                    # オーバーラップ部分を加算
                    self.buffer[-overlap_len:] += grain[:overlap_len]
                    # 非オーバーラップ部分を追加
                    self.buffer = np.concatenate((self.buffer, grain[overlap_len:]))
                else:
                    # バッファが空の場合はそのまま追加
                    self.buffer = np.concatenate((self.buffer, grain))

            # グレイン間の待機時間を調整
            time.sleep(self.grain_interval)

    def stop(self):
        self.playing = False
        if self.stream:
            self.stream.stop()
            self.stream.close()

    def set_target_rev(self, value):
        with self.lock:
            self.target_rev = value

    def callback(self, outdata, frames, time_info, status):
        with self.buffer_lock:
            if len(self.buffer) >= frames:
                outdata[:, 0] = self.buffer[:frames]
                self.buffer = self.buffer[frames:]
            else:
                outdata[:len(self.buffer), 0] = self.buffer
                outdata[len(self.buffer):, 0] = 0
                self.buffer = np.array([])

# GUIの設定
def on_rev_change(value):
    player.set_target_rev(float(value))

root = tk.Tk()
root.title("Granular Engine Sound")

# ラベルを追加
rev_label = ttk.Label(root, text="rev_target")
rev_label.pack()

rev_slider = ttk.Scale(root, from_=0.0, to=1.0, orient='horizontal', command=on_rev_change)
rev_slider.pack()

player = GrainPlayer(grains, samplerate)
player.start()

root.mainloop()

player.stop()