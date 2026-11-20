#!/usr/bin/env python3
"""ほっとニュース: data.js から静的記事HTML（noscript）を生成し、index.html に差し込む。

目的: JS を実行しない AI クローラーにも、その日の記事（見出し＋本文）が読めるようにする。
人間の見た目（見出し一覧＋ポップアップ）は従来どおり JS 描画のまま変えない。

毎朝の更新手順:
  1. data.js を新しい内容に差し替える
  2. python3 build_static.py を実行する（このスクリプトが index.html の
     <!-- static-articles:start --> 〜 <!-- static-articles:end --> の間を再生成する）
  3. data.js と index.html の両方を GitHub に push する
"""
import html
import json
import pathlib
import subprocess
import sys

BASE = pathlib.Path(__file__).resolve().parent
START = "<!-- static-articles:start -->"
END = "<!-- static-articles:end -->"
ANCHOR = '  <section class="omake" id="omakeBox" hidden>'


def load_data():
    js = (
        "global.window={}; require(process.argv[1]);"
        "process.stdout.write(JSON.stringify(window.NEWS_DATA))"
    )
    out = subprocess.run(
        ["node", "-e", js, str(BASE / "data.js")],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def esc(s):
    return html.escape(s or "", quote=True)


def build_block(d):
    lines = [START, "<noscript>", '<section class="static-articles" aria-label="今日のニュース全文">']
    lines.append(f'  <h2>{esc(d.get("dateLabel", ""))}のニュース（全文）</h2>')
    for cat in d.get("categories", []):
        lines.append('  <div class="cat-head">')
        lines.append(f'    <span class="icon" aria-hidden="true">{esc(cat.get("icon", ""))}</span>')
        lines.append(f'    <h2>{esc(cat.get("name", ""))}</h2>')
        lines.append('    <span class="rule"></span>')
        lines.append('  </div>')
        for it in cat.get("items", []):
            area_cls = "area jp" if it.get("area") == "日本" else "area"
            lines.append("  <article>")
            lines.append(f'    <span class="{area_cls}">{esc(it.get("area", ""))}</span>')
            lines.append(f'    <h3>{esc(it.get("title", ""))}</h3>')
            lines.append(f'    <p>{esc(it.get("body", ""))}</p>')
            lines.append(
                '    <p class="more"><a href="{}" target="_blank" rel="noopener noreferrer">元の記事を読む →</a>'
                ' <span class="src">（{}）</span></p>'.format(esc(it.get("url", "")), esc(it.get("source", "")))
            )
            lines.append("  </article>")
    lines.append("</section>")
    lines.append("</noscript>")
    lines.append(END)
    return "\n".join(lines)


def main():
    d = load_data()
    block = build_block(d)
    p = BASE / "index.html"
    src = p.read_text(encoding="utf-8")
    if START in src and END in src:
        pre, rest = src.split(START, 1)
        _, post = rest.split(END, 1)
        src = pre + block + post
    else:
        if ANCHOR not in src:
            sys.exit("anchor not found in index.html")
        src = src.replace(ANCHOR, block + "\n\n" + ANCHOR, 1)
    p.write_text(src, encoding="utf-8")
    n = sum(len(c.get("items", [])) for c in d.get("categories", []))
    print(f"static articles updated: date={d.get('dateISO')} items={n}")


if __name__ == "__main__":
    main()
