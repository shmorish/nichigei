# Image to Music - 画像から音楽を生成

画像から円を検出し、その位置情報をMax/MSPで音楽に変換するプロジェクト。

## ファイル構成

- **synth_128_working.maxpat** - Max/MSPパッチ（128個の円から約2-3分の音楽を生成）
- **extract_circles_to_json.py** - 画像から円を検出してJSON形式で保存
- **generate_synth_128_working.py** - Max/MSPパッチを自動生成
- **data/circles_data.json** - 検出された565個の円のデータ
- **data/image.png** - 元画像

## 画像→音楽のマッピング

| 画像の特徴 | 音楽パラメータ |
|-----------|---------------|
| Y座標（上→下） | ピッチ（高音→低音） |
| 時系列 | 登場順（上から順に鳴る） |
| 円の大きさ | 音の長さ |

## 使い方

### 前提条件

- Python 3.x
- Max/MSP 8
- 必要なライブラリ:
  ```bash
  pip install opencv-python numpy
  git clone https://github.com/shakfu/py2max.git
  ```

### 新しい画像から音楽を生成する場合

1. 画像から円データを抽出:
   ```bash
   python3 extract_circles_to_json.py
   ```

2. Max/MSPパッチを生成:
   ```bash
   PYTHONPATH=py2max python3 generate_synth_128_working.py
   ```

### Max/MSPで音楽を再生

1. Max/MSPで `synth_128_working.maxpat` を開く
2. **BPM** ボックスに `120` と入力してEnter
3. **Filter Cutoff** ボックスに `0` と入力してEnter
4. **ezdac~**（スピーカーアイコン）をクリックしてDSP ON
5. **toggle**（Start/Stop）をクリック
6. 音楽が再生されます！

## パラメータ調整

Max/MSPパッチ内で調整可能：

- **BPM** - テンポ（推奨: 100-180）
- **Filter Cutoff** - フィルターの明るさ
  - 0: LFOのみで揺らぐ
  - 500-1000: 暗めの音色
  - 1500-2500: 明るめの音色
