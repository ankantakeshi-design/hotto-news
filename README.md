# ほっとニュース

心が温まるニュース、希望が持てるニュース、くすっと笑えるニュースを、
日本と世界から毎朝お届けする小さなサイトです。

- 公開先: https://hotto-news.pages.dev/
- 構成: index.html（表示）＋ data.js（その日のニュースデータ）＋ build_static.py（静的記事の生成）
- 更新: 毎朝、data.js を差し替え（前日分は archive へ）→ `python3 build_static.py` を実行 → data.js と index.html の両方を push
- 静的記事: JS を実行しない AI クローラー向けに、その日の記事（見出し＋本文）を index.html 内の
  `<!-- static-articles:start -->` 〜 `<!-- static-articles:end -->`（noscript 内）にも持たせている。
  この区間は build_static.py が data.js から生成するので、手で編集しない。
  人間の見た目（見出し一覧＋ポップアップ）は従来どおり JS 描画。
- 心体調整塾のコンテンツサイトの一つ
