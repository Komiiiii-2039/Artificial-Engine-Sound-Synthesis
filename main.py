import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from scipy.fftpack import fft, ifft

n_cylinders = 6 #number of cylinders
rpm = 2000 # revolutions per minute
f_0 = rpm * (n_cylinders / 2)* 60
K = 100 # number of harmonics
N_m = n_cylinders * n_cylinders
T = 0.5
M = 10


# Waveファイルからデータを読み取る関数
def read_wave_file(file_path):
    sample_rate, data= read(file_path)
    # ステレオデータをモノラルに変換
    if len(data.shape) > 1:
        data = data.mean(axis=1)
    return data, sample_rate  # 10秒間のデータを使用

def synthesize_mechanical_sound(engine_data, sample_rate):
    # フーリエ係数のサンプリング
    ak, bk = compute_fourier_coefficients(engine_data, 1 / sample_rate, M, K)

    print("ak")
    print(ak)
    print("bk")
    print(bk)

    # 機械音の合成
    t = np.arange(0, T, 1/sample_rate)
    mechanical_sound = np.zeros_like(t)
    #rpmを0から4000まで線型に変化させる（１０秒間）
    for k in range(1, K+1):
        mechanical_sound += ak[k-1] * np.cos(2.0 * np.pi * k * f_0 * t / N_m) + bk[k-1] * np.sin(2.0 * np.pi * k * f_0 * t / N_m) 
    
    print("Mechanical sound synthesized")
    
    return mechanical_sound

def compute_fourier_coefficients(p, T, M, K):
    div = 100
    N = len(p)  # データ点数
    a_k = np.zeros(K)  # a_k を格納する配列
    b_k = np.zeros(K)  # b_k を格納する配列

    h = T / div  # step
    x = np.linspace(0, T, div + 1)

    for k in range(1, K + 1):
        a_sum_k = 0
        b_sum_k = 0
        
        for m in range(1, M + 1):
            # インデックスを整数に変換
            idx = np.clip(np.round((1/T) * (x + (m - 1) * T)).astype(int), 0, N-1) #このインデックスがおかしい
            print(idx[:5])

            # シンプソンの定理で積分
            y_cos = p[idx] * np.cos(2 * np.pi * k * x / T)
            a_sum_k += h / 3 * np.sum(y_cos[0:-1:2] + 4 * y_cos[1::2] + y_cos[2::2])
            
            y_sin = p[idx] * np.sin(2 * np.pi * k * x / T)
            b_sum_k += h / 3 * np.sum(y_sin[0:-1:2] + 4 * y_sin[1::2] + y_sin[2::2])
             
        # 平均を取る
        a_k[k-1] = a_sum_k / M / T
        b_k[k-1] = b_sum_k / M / T
    
    return a_k, b_k

def calculate_spectrum(data, fs, f0, K):
    N = len(data)
    Y = np.fft.fft(data)
    
    a_k = np.zeros(K)
    b_k = np.zeros(K)
    
    for k in range(1, K+1):
        a_k[k-1] = 2 * np.real(Y[k-1])
        b_k[k-1] = 2 * np.imag(Y[k-1])
    
    #print("Y")
    #print(Y[:10])
    #print("a_k")
    #print(a_k)
    #print("b_k")
    #print(b_k)
    return a_k, b_k


def synthesize_combustion_sound(sample_rate):
    t = np.arange(0, T, 1/sample_rate)
    combustion_sound = np.random.normal(0, 1, len(t))
    envelope = np.exp(-3 * t)  # 例としての包絡線
    
    print("Combustion sound synthesized")
    return combustion_sound * envelope

def combine_sounds(mechanical_sound, combustion_sound, mechanical_amplitude):
    combined_sound = mechanical_sound + mechanical_amplitude * combustion_sound
    return combined_sound

def main():
    engine_data, sample_rate = read_wave_file('sample/lfa_original.wav')
    mechanical_amplitude = 0.1  # 燃焼音の振幅
    
    mechanical_sound = synthesize_mechanical_sound(engine_data, sample_rate)
    #combustion_sound = synthesize_combustion_sound(sample_rate)
    combustion_sound = np.zeros_like(mechanical_sound)
    engine_sound = combine_sounds(mechanical_sound, combustion_sound, mechanical_amplitude)
    
    write('lfa_generated_engine_sound.wav', sample_rate, np.int16(engine_sound * 32767))
    print("エンジン音を保存しました")

if __name__ == "__main__":
    main()