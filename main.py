import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from scipy.fftpack import fft, ifft

# Waveファイルからデータを読み取る関数
def read_wave_file(file_path):
    sample_rate, data = read(file_path)
    # ステレオデータをモノラルに変換
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    return sample_rate, data[0: int(sample_rate * 3)]  # 10秒間のデータを使用

def synthesize_mechanical_sound(engine_data, sample_rate):
    # フーリエ係数のサンプリング
    M = len(engine_data)
    ak = np.zeros(M)
    bk = np.zeros(M)
    print("Number of samples: ", M)
    
    for k in range(M):
        ak[k] = np.mean(engine_data * np.cos(2 * np.pi * k * np.arange(M) / M))
        bk[k] = np.mean(engine_data * np.sin(2 * np.pi * k * np.arange(M) / M))
        if(k % 1000 == 0):
            print("Fourier coefficient calculated: ", k)
    
    # 機械音の合成
    t = np.linspace(0, M / sample_rate, M, endpoint=False)
    mechanical_sound = np.zeros_like(t)
    for k in range(M):
        mechanical_sound += ak[k] * np.cos(2 * np.pi * k * t) + bk[k] * np.sin(2 * np.pi * k * t)
    
    print("Mechanical sound synthesized")
    
    return mechanical_sound

def synthesize_combustion_sound(duration, sample_rate):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    combustion_sound = np.random.normal(0, 1, len(t))
    envelope = np.exp(-3 * t)  # 例としての包絡線
    
    print("Combustion sound synthesized")
    return combustion_sound * envelope

def combine_sounds(mechanical_sound, combustion_sound, mechanical_amplitude):
    combined_sound = mechanical_sound + mechanical_amplitude * combustion_sound
    return combined_sound / np.max(np.abs(combined_sound))

def main():
    sample_rate, engine_data = read_wave_file('sample/lfa.wav')
    duration = len(engine_data) / sample_rate  # 継続時間 (秒)
    mechanical_amplitude = 0.1  # 燃焼音の振幅
    
    mechanical_sound = synthesize_mechanical_sound(engine_data, sample_rate)
    combustion_sound = synthesize_combustion_sound(duration, sample_rate)
    engine_sound = combine_sounds(mechanical_sound, combustion_sound, mechanical_amplitude)
    
    write('engine_sound.wav', sample_rate, np.int16(engine_sound * 32767))
    print("エンジン音を 'engine_sound.wav' に保存しました")

if __name__ == "__main__":
    main()