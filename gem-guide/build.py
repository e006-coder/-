"""src/ を1枚のHTMLにまとめる。
 dist/artifact.html … claude.ai Artifact 用（<html>等の骨組みなし）
 index.html          … そのまま静的ホスティングできる完全版
"""
from pathlib import Path
root = Path(__file__).parent
shell = (root/'src/shell.html').read_text()
body = shell.replace('/*DATA*/', (root/'src/data.js').read_text()).replace('/*APP*/', (root/'src/app.js').read_text())
(root/'dist').mkdir(exist_ok=True)
(root/'dist/artifact.html').write_text(body)
(root/'index.html').write_text('<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
