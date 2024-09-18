import numpy as np
import matplotlib.pyplot as plt
from scipy.io.wavfile import read, write
from scipy.fftpack import fft, ifft

# パラメーター
input_file = "sample/crown-athlete_650.wav"
output_file = "output/crown_athlete_650.wav"
n_cylinders = 6 #number of cylinders
rpm = 2000# revolutions per minute
f_0 = (rpm / 60) * (n_cylinders / 2)
K = 18 # number of harmonics
N_m = n_cylinders * n_cylinders
generate_length = 5
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
    #ak, bk = compute_fourier_coefficients(engine_data, 1 / sample_rate, M, K)
    ak, bk = calculate_spectrum(engine_data, sample_rate, f_0, K)

    # 機械音の合成
    t = np.arange(0, generate_length, 1/sample_rate)
    f_t = np.zeros_like(t)
    for i in range(len(t)):
        #f_t[i] = f_0 * np.sin(2 * np.pi * i / len(t))
        f_t [i] = rpm
    
    mechanical_sound = np.zeros_like(t)
    #mechanical_sound = np.fft.ifft(np.fft.fft(engine_data)) # これは当然再現できる
    for k in range(1, K+1):
        mechanical_sound += ak[k-1] * np.cos(2.0 * np.pi * k * f_t * t ) + bk[k-1] * np.sin(2.0 * np.pi * k * f_t * t ) 
    
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
            #print(idx[:5])

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
    return a_k, b_k


def synthesize_combustion_sound(sample_rate):
    t = np.arange(0, generate_length, 1/sample_rate)
    combustion_sound = np.random.normal(0, 1, len(t))
    envelope = np.exp(-3 * t)  # 例としての包絡線
    
    print("Combustion sound synthesized")
    return combustion_sound * envelope

def combine_sounds(mechanical_sound, combustion_sound, mechanical_amplitude):
    combined_sound = mechanical_sound + mechanical_amplitude * combustion_sound
    return combined_sound

def main():
    engine_data, sample_rate = read_wave_file(input_file)
    print("Loaded Data :")
    print(f"length : {len(engine_data)}")
    print(f"sample rate : {sample_rate}")

    mechanical_amplitude = 0.1  # 燃焼音の振幅
    
    # 機械音の合成
    mechanical_sound = synthesize_mechanical_sound(engine_data, sample_rate)

    # 燃焼音の合成
    #combustion_sound = synthesize_combustion_sound(sample_rate)
    # エンジン音の合成
    combustion_sound = np.zeros_like(mechanical_sound)
    engine_sound = combine_sounds(mechanical_sound, combustion_sound, mechanical_amplitude)
    engine_sound /= np.max(np.abs(engine_sound))

    max_int = np.iinfo(np.int16).max
    output_engine_sound = (engine_sound * max_int).astype(np.int16)
    print(output_engine_sound[:10])

    write(output_file, sample_rate, output_engine_sound)
    print(f"エンジン音を保存しました -> {output_file}")

if __name__ == "__main__":
    main()