import cv2
import numpy as np
import json

# 画像を読み込む
image_path = "data/image.png"
image = cv2.imread(image_path)
if image is None:
    raise ValueError(f"画像が読み込めませんでした: {image_path}")

height, width = image.shape[:2]
print(f"画像サイズ: {width}x{height}")

# グレー領域のマスクを作成（コンクリート壁の色を検出）
hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# コンクリート壁の色範囲を定義（グレー系）
lower_gray = np.array([0, 0, 100])      # H, S, V
upper_gray = np.array([180, 60, 220])   # H, S, V

# マスクを作成
gray_mask = cv2.inRange(hsv_image, lower_gray, upper_gray)

# モルフォロジー処理でノイズ除去と領域の整形
kernel = np.ones((7, 7), np.uint8)
gray_mask = cv2.morphologyEx(gray_mask, cv2.MORPH_CLOSE, kernel)
gray_mask = cv2.morphologyEx(gray_mask, cv2.MORPH_OPEN, kernel)

# グレースケール変換
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# マスクを適用してグレー領域のみを抽出
gray_masked = cv2.bitwise_and(gray, gray, mask=gray_mask)

# 前処理: より強力なノイズ除去
denoised = cv2.bilateralFilter(gray_masked, 9, 75, 75)
denoised = cv2.medianBlur(denoised, 5)

# コントラスト強調
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
enhanced = clahe.apply(denoised)

# ガウシアンブラーで滑らかに
blurred = cv2.GaussianBlur(enhanced, (7, 7), 2)

# エッジ検出
edges = cv2.Canny(blurred, 30, 100)

# 長い線を除去
horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (80, 1))
horizontal_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)

vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 80))
vertical_lines = cv2.morphologyEx(edges, cv2.MORPH_OPEN, vertical_kernel, iterations=1)

diagonal_size = 15
diagonal_kernel1 = np.eye(diagonal_size, dtype=np.uint8)
diagonal_lines1 = cv2.morphologyEx(edges, cv2.MORPH_OPEN, diagonal_kernel1, iterations=1)

diagonal_kernel2 = np.flip(np.eye(diagonal_size, dtype=np.uint8), axis=1)
diagonal_lines2 = cv2.morphologyEx(edges, cv2.MORPH_OPEN, diagonal_kernel2, iterations=1)

# すべての線を結合
all_lines = cv2.bitwise_or(horizontal_lines, vertical_lines)
all_lines = cv2.bitwise_or(all_lines, diagonal_lines1)
all_lines = cv2.bitwise_or(all_lines, diagonal_lines2)

# 線を膨張させて確実に除去
all_lines = cv2.dilate(all_lines, np.ones((5, 5), np.uint8), iterations=2)

# エッジから線を除去
edges_filtered = cv2.subtract(edges, all_lines)

# Hough円検出 - 複数のパラメータセットを試行
params_list = [
    {"minDist": 10, "param1": 100, "param2": 10, "minR": 4, "maxR": 10},
    {"minDist": 8, "param1": 80, "param2": 12, "minR": 4, "maxR": 12},
    {"minDist": 12, "param1": 120, "param2": 8, "minR": 4, "maxR": 10},
    {"minDist": 10, "param1": 90, "param2": 11, "minR": 4, "maxR": 10},
    {"minDist": 8, "param1": 100, "param2": 9, "minR": 4, "maxR": 10},
]

best_circles = None
best_count = 0

print("\n円検出を実行中...")
for i, params in enumerate(params_list):
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=params["minDist"],
        param1=params["param1"],
        param2=params["param2"],
        minRadius=params["minR"],
        maxRadius=params["maxR"]
    )

    count = len(circles[0]) if circles is not None else 0
    print(f"パラメータセット{i+1}: {count}個の円を検出")

    # 多すぎず、少なすぎず、良いバランスのものを選択
    if 200 <= count <= 800:
        if count > best_count:
            best_count = count
            best_circles = circles
    elif best_circles is None and count > 0 and count < 1500:
        best_count = count
        best_circles = circles

# データを格納するリスト
circles_data = []

# 検出された円の処理
if best_circles is not None:
    circles = np.uint16(np.around(best_circles))
    print(f"\n総検出数: {len(circles[0])}個の円")

    # グレー領域内の円のみをフィルタリング
    valid_circles = []
    for circle in circles[0, :]:
        cx = circle[0]
        cy = circle[1]
        radius = circle[2]

        # その位置がグレーマスク内にあるかチェック
        if 0 <= cy < gray_mask.shape[0] and 0 <= cx < gray_mask.shape[1]:
            if gray_mask[cy, cx] > 0:  # マスク内の場合のみ
                valid_circles.append(circle)

    print(f"グレー領域内の円: {len(valid_circles)}個")

    # 密集している円を除外（近すぎる円を削除）
    filtered_circles = []
    for i, circle1 in enumerate(valid_circles):
        cx1, cy1, r1 = circle1[0], circle1[1], circle1[2]
        is_too_close = False

        # すでに追加されている円との距離をチェック
        for circle2 in filtered_circles:
            cx2, cy2, r2 = int(circle2[0]), int(circle2[1]), int(circle2[2])
            distance = np.sqrt((int(cx1) - cx2)**2 + (int(cy1) - cy2)**2)

            # 円の半径の合計よりも近い場合は密集していると判断
            min_distance = (r1 + r2) * 1.0
            if distance < min_distance:
                is_too_close = True
                break

        if not is_too_close:
            filtered_circles.append(circle1)

    print(f"密集フィルタ後: {len(filtered_circles)}個")
    valid_circles = filtered_circles

    # Y座標でソート（上から下へ時間順に）
    valid_circles = sorted(valid_circles, key=lambda c: c[1])

    # データをJSON形式で保存
    for idx, circle in enumerate(valid_circles):
        cx = int(circle[0])
        cy = int(circle[1])
        radius = int(circle[2])

        # 座標を0-1に正規化
        x_norm = cx / width
        y_norm = cy / height

        circles_data.append({
            "id": idx,
            "x": cx,
            "y": cy,
            "radius": radius,
            "x_normalized": round(x_norm, 4),
            "y_normalized": round(y_norm, 4)
        })

    print(f"最終的な有効な円: {len(valid_circles)}個")

    # 統計情報を表示
    if valid_circles:
        valid_radii = [c[2] for c in valid_circles]
        print(f"平均半径: {np.mean(valid_radii):.2f}px")
        print(f"最小半径: {np.min(valid_radii)}px")
        print(f"最大半径: {np.max(valid_radii)}px")
else:
    print("\n丸が検出されませんでした")

# JSONファイルに保存
output_json = {
    "image_width": width,
    "image_height": height,
    "total_circles": len(circles_data),
    "circles": circles_data
}

output_path = "data/circles_data.json"
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(output_json, f, indent=2, ensure_ascii=False)

print(f"\nデータをJSON形式で保存しました: {output_path}")
