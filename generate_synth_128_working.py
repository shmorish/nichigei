import sys
import json
sys.path.insert(0, 'py2max')

from py2max import Patcher

# JSONデータを読み込む
with open("data/circles_data.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

circles = data['circles']

# 128個にサンプリング
step = len(circles) // 128
selected_circles = [circles[i * step] for i in range(128)]

print(f"全{len(circles)}個から128個にサンプリング")

# Patcherを作成
p = Patcher('synth_128_working.maxpat')

# === UI ===
p.add_comment('Image to Music - SYNTH Edition (Fixed)!', x=50, y=20)
p.add_comment('BPM', x=50, y=50)
bpm = p.add_intbox(x=100, y=50)

p.add_comment('Start/Stop', x=200, y=50)
toggle = p.add_textbox('toggle', x=270, y=50)

p.add_comment('Beat:', x=370, y=50)
position = p.add_intbox(x=420, y=50)

p.add_comment('Filter Cutoff', x=520, y=50)
filter_cutoff = p.add_intbox(x=620, y=50)

# === BPM to ms ===
bpm_calc = p.add_textbox('expr 60000 / $i1', x=100, y=80)

# === Metro & Counter ===
metro = p.add_textbox('metro 500', x=200, y=90)
counter = p.add_textbox('counter 0 0 127', x=200, y=130)

# === 4拍子判定 ===
beat_mod = p.add_textbox('% 4', x=320, y=130)

# === LFO（フィルター用） ===
p.add_comment('=== LFO ===', x=520, y=90)
lfo = p.add_textbox('cycle~ 0.25', x=520, y=120)
lfo_scale = p.add_textbox('*~ 1500.', x=520, y=160)
lfo_offset = p.add_textbox('+~ 2000.', x=520, y=200)

# === メロディ部分 ===
p.add_comment('=== SYNTH MELODY ===', x=50, y=160)

# sel for pitch（0から127まで）
sel_args = ' '.join([str(i) for i in range(128)])
sel_pitch = p.add_textbox(f'sel {sel_args}', x=50, y=190)

# 128個のピッチmessage
pitch_messages = []
for i, circle in enumerate(selected_circles):
    y_norm = circle['y_normalized']
    pitch = int(48 + (1 - y_norm) * 24)
    x_pos = 50 + (i % 16) * 35
    y_pos = 220 + (i // 16) * 30
    msg = p.add_message(str(pitch), x=x_pos, y=y_pos)
    pitch_messages.append(msg)

# メロディ音生成（3オシレーター）
mtof_mel = p.add_textbox('mtof', x=50, y=350)

# オシレーター1（中心）
cycle_mel1 = p.add_textbox('cycle~', x=50, y=390)

# オシレーター2（+5セント）
plus_detune = p.add_textbox('* 1.003', x=150, y=390)
cycle_mel2 = p.add_textbox('cycle~', x=150, y=430)

# オシレーター3（-5セント）
minus_detune = p.add_textbox('* 0.997', x=250, y=390)
cycle_mel3 = p.add_textbox('cycle~', x=250, y=430)

# 3つを合成
add_osc1 = p.add_textbox('+~', x=50, y=470)
add_osc2 = p.add_textbox('+~', x=50, y=505)

# フィルター（ローパス）
filter_mel = p.add_textbox('svf~ lowpass', x=50, y=540)

# エンベロープ
env_mel_msg = p.add_message('1, 0 150', x=200, y=350)
env_mel = p.add_textbox('line~', x=200, y=390)

# フィルターエンベロープ
env_filt_msg = p.add_message('4000, 800 150', x=350, y=350)
env_filt = p.add_textbox('line~', x=350, y=390)
add_filt = p.add_textbox('+~', x=520, y=240)

# 音量調整
mult_mel = p.add_textbox('*~', x=50, y=580)
mult_mel_vol = p.add_textbox('*~ 0.3', x=50, y=620)

# === ベース部分 ===
p.add_comment('=== SYNTH BASS ===', x=700, y=350)
minus12 = p.add_textbox('- 12', x=700, y=380)
mtof_bass = p.add_textbox('mtof', x=700, y=410)

# 矩形波2つをデチューン
rect_bass1 = p.add_textbox('rect~ 0.5', x=700, y=450)
detune_bass = p.add_textbox('* 1.005', x=800, y=410)
rect_bass2 = p.add_textbox('rect~ 0.5', x=800, y=450)
add_bass = p.add_textbox('+~', x=700, y=490)

# フィルター
filter_bass = p.add_textbox('svf~ lowpass', x=700, y=530)
bass_cutoff = p.add_message('600', x=800, y=530)

env_bass_msg = p.add_message('0.8, 0 180', x=900, y=410)
env_bass = p.add_textbox('line~', x=900, y=450)

mult_bass = p.add_textbox('*~', x=700, y=570)
mult_bass_vol = p.add_textbox('*~ 0.4', x=700, y=610)

# === ハイハット ===
p.add_comment('=== HI-HAT ===', x=450, y=350)
hihat_sel = p.add_textbox('sel 0 1 2 3', x=450, y=380)
hihat_msg0 = p.add_message('1', x=450, y=410)
hihat_msg1 = p.add_message('0.4', x=490, y=410)
hihat_msg2 = p.add_message('0.7', x=530, y=410)
hihat_msg3 = p.add_message('0.4', x=570, y=410)

noise = p.add_textbox('noise~', x=450, y=450)
hihat_filt = p.add_textbox('svf~ highpass 8000', x=450, y=485)
env_hihat_msg = p.add_message('1, 0 80', x=600, y=410)
env_hihat = p.add_textbox('line~', x=600, y=450)
mult_hihat = p.add_textbox('*~', x=450, y=525)
mult_hihat_vol = p.add_textbox('*~', x=450, y=560)

# === キック ===
p.add_comment('=== KICK ===', x=900, y=600)
kick_sel = p.add_textbox('sel 0 1 2 3', x=900, y=1270)
kick_msg0 = p.add_message('1', x=900, y=660)
kick_msg1 = p.add_message('0', x=940, y=660)
kick_msg2 = p.add_message('0.7', x=980, y=660)
kick_msg3 = p.add_message('0', x=1020, y=660)

# ピッチエンベロープ
kick_env_msg = p.add_message('80, 40 200', x=900, y=700)
kick_pitch_env = p.add_textbox('line~', x=900, y=735)
cycle_kick = p.add_textbox('cycle~', x=900, y=770)

env_kick_msg = p.add_message('1, 0 250', x=1000, y=700)
env_kick = p.add_textbox('line~', x=1000, y=735)
mult_kick = p.add_textbox('*~', x=900, y=810)
mult_kick_vol = p.add_textbox('*~', x=900, y=850)

# === ミックス ===
mix1 = p.add_textbox('+~', x=50, y=690)
mix2 = p.add_textbox('+~', x=50, y=725)
mix3 = p.add_textbox('+~', x=50, y=760)

master = p.add_textbox('*~ 0.25', x=50, y=795)
dac = p.add_textbox('ezdac~', x=50, y=835)

# === 接続 ===
# コントロール
p.link(bpm, bpm_calc)
p.link(bpm_calc, metro, inlet=1)
p.link(toggle, metro)
p.link(metro, counter)
p.link(counter, position)
p.link(counter, beat_mod)

# LFO
p.link(lfo, lfo_scale)
p.link(lfo_scale, lfo_offset)
p.link(lfo_offset, add_filt, inlet=0)

# メロディ - selを使用
p.link(counter, sel_pitch)
p.link(counter, env_mel_msg)
p.link(counter, env_filt_msg)

# selの各outletから対応するmessageへ
for i, msg in enumerate(pitch_messages):
    p.link(sel_pitch, msg, outlet=i)
    p.link(msg, mtof_mel)
    p.link(msg, minus12)

# 3オシレーター
p.link(mtof_mel, cycle_mel1)
p.link(mtof_mel, plus_detune)
p.link(plus_detune, cycle_mel2)
p.link(mtof_mel, minus_detune)
p.link(minus_detune, cycle_mel3)

# 合成
p.link(cycle_mel1, add_osc1, inlet=0)
p.link(cycle_mel2, add_osc1, inlet=1)
p.link(add_osc1, add_osc2, inlet=0)
p.link(cycle_mel3, add_osc2, inlet=1)

# フィルター
p.link(env_filt_msg, env_filt)
p.link(env_filt, add_filt, inlet=1)
p.link(filter_cutoff, add_filt, inlet=1)
p.link(add_osc2, filter_mel, inlet=0)
p.link(add_filt, filter_mel, inlet=1)

# エンベロープ
p.link(env_mel_msg, env_mel)
p.link(filter_mel, mult_mel, inlet=0)
p.link(env_mel, mult_mel, inlet=1)
p.link(mult_mel, mult_mel_vol)

# ベース
p.link(minus12, mtof_bass)
p.link(mtof_bass, rect_bass1)
p.link(mtof_bass, detune_bass)
p.link(detune_bass, rect_bass2)
p.link(rect_bass1, add_bass, inlet=0)
p.link(rect_bass2, add_bass, inlet=1)
p.link(add_bass, filter_bass, inlet=0)
p.link(bass_cutoff, filter_bass, inlet=1)
p.link(counter, env_bass_msg)
p.link(env_bass_msg, env_bass)
p.link(filter_bass, mult_bass, inlet=0)
p.link(env_bass, mult_bass, inlet=1)
p.link(mult_bass, mult_bass_vol)

# ハイハット
p.link(beat_mod, hihat_sel)
p.link(hihat_sel, hihat_msg0, outlet=0)
p.link(hihat_sel, hihat_msg1, outlet=1)
p.link(hihat_sel, hihat_msg2, outlet=2)
p.link(hihat_sel, hihat_msg3, outlet=3)
p.link(counter, env_hihat_msg)
p.link(noise, hihat_filt)
p.link(hihat_filt, mult_hihat, inlet=0)
p.link(env_hihat_msg, env_hihat)
p.link(env_hihat, mult_hihat, inlet=1)
p.link(mult_hihat, mult_hihat_vol, inlet=0)
for msg in [hihat_msg0, hihat_msg1, hihat_msg2, hihat_msg3]:
    p.link(msg, mult_hihat_vol, inlet=1)

# キック
p.link(beat_mod, kick_sel)
p.link(kick_sel, kick_msg0, outlet=0)
p.link(kick_sel, kick_msg1, outlet=1)
p.link(kick_sel, kick_msg2, outlet=2)
p.link(kick_sel, kick_msg3, outlet=3)
p.link(counter, kick_env_msg)
p.link(counter, env_kick_msg)
p.link(kick_env_msg, kick_pitch_env)
p.link(kick_pitch_env, cycle_kick)
p.link(cycle_kick, mult_kick, inlet=0)
p.link(env_kick_msg, env_kick)
p.link(env_kick, mult_kick, inlet=1)
p.link(mult_kick, mult_kick_vol, inlet=0)
for msg in [kick_msg0, kick_msg1, kick_msg2, kick_msg3]:
    p.link(msg, mult_kick_vol, inlet=1)

# ミックス
p.link(mult_mel_vol, mix1, inlet=0)
p.link(mult_bass_vol, mix1, inlet=1)
p.link(mix1, mix2, inlet=0)
p.link(mult_hihat_vol, mix2, inlet=1)
p.link(mix2, mix3, inlet=0)
p.link(mult_kick_vol, mix3, inlet=1)
p.link(mix3, master)
p.link(master, dac, inlet=0)
p.link(master, dac, inlet=1)

p.save()

print(f"\nシンセ版（修正）を生成: synth_128_working.maxpat")
print(f"\n特徴:")
print("🎹 selector → sel オブジェクトに修正")
print("🎛️  3オシレーターでユニゾン効果")
print("🎸 フィルターでシンセサイザー風の音色")
print("💥 LFOで自動的にフィルタースイープ")
print("\n使い方:")
print("1. BPMに 120 と入力")
print("2. Filter Cutoffに 0 と入力")
print("3. ezdac~をON")
print("4. toggleをクリック")
