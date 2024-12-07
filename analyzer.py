import pandas as pd

# CSVファイルの読み込み
file_path = "cleaned_file.csv"
data = pd.read_csv(file_path)

# データの確認
# print(data.head())

# ジャンルやアーティストごとの再生回数を分析
genre_counts = data['Genre'].value_counts().head(5)
# artist_play_counts = data.groupby('Album Artist')['Play Count'].sum()

print("ジャンルごとの再生回数:\n", genre_counts)
# print("アーティストごとの再生回数:\n", artist_play_counts)

# 年を抽出
data['Year'] = pd.to_datetime(data['Release Date']).dt.year

# 10年ごとの年代を計算
data['Decade'] = (data['Year'] // 10) * 10  # 10年ごとの年代を求める

decade_counts = data['Decade'].value_counts().sort_index()

# 結果を表示
print(decade_counts)

# 最も多い年代を取得
most_common_decade = decade_counts.idxmax()

# メッセージを作成
print(f"あなたは{most_common_decade}年代の曲をよく聴きます。")

# アーティスト登場回数をカウント
decade_artist_counts = data['Album Artist'].value_counts().head(5)

# 結果を表示
print(decade_artist_counts)

