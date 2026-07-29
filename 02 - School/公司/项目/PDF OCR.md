---
created: 2026-07-29T11:35
updated: 2026-07-29T11:39
---
1. 进入目录：` D:\Tutorials\Python`
2. 输入命令：
```powershell
cd D:\Tutorials\Python
& .\.venv-mineru\Scripts\Activate.ps1
$env:MINERU_MODEL_SOURCE = "modelscope"
$env:NO_PROXY = "localhost,127.0.0.1,::1"
$env:no_proxy = "localhost,127.0.0.1,::1"

# 手动改pdf名称
& D:\Work\projects\ontology-builder\.venv\Scripts\python.exe `
  .\pdf_ocr_md\scan_pdf_to_searchable.py `
  -i "D:\Work\projects\ontology-builder-work\rocket-engine-ontology\input\pdf\液体推进剂火箭发动机设计_split" `
  -o "D:\Work\projects\ontology-builder-work\rocket-engine-ontology\input\pdf\液体推进剂火箭发动机设计-searchable.pdf" `
  --model-source modelscope
	
& D:\Work\projects\ontology-builder\.venv\Scripts\python.exe `
  .\faithful_builder.py init `
  --pdf ".\input\pdf\液体推进剂火箭发动机设计-searchable.pdf" `
  --chapter "1" `
  --title "液体火箭发动机简介" `
  --start-page 9 `
  --end-page 39 `
  --slug "chapter01"
  # 命名组成 {slug}-{title}-faithful.md
	```