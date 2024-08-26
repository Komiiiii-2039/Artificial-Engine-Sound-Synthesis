import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from scipy.fftpack import fft, ifft

# Waveファイルからデータを読み取る関数
def read_wave_file(file_path):
    sample_rate, data= read(file_path)
    # ステレオデータをモノラルに変換
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    return data, sample_rate  # 10秒間のデータを使用

# wavから読んだデータをfftしてプロットする
data_output, sapmle_rate_output = read_wave_file("porsche_911_generated_engine_sound.wav")
data_input, sample_rate_input = read_wave_file("sample/porsche_911_original.wav")
N_output = len(data_output)
N_input = len(data_input)

fft_output = fft(data_output)
fft_input = fft(data_input)

fft_fs_output = np.fft.fftfreq(N_output, d=1/sapmle_rate_output)
fft_fs_input = np.fft.fftfreq(N_input, d=1/sample_rate_input)

plt.plot(fft_fs_output, np.abs(fft_output), label="output", zorder=1)
plt.plot(fft_fs_input, np.abs(fft_input), label="input", zorder=2)
plt.legend()
plt.show()