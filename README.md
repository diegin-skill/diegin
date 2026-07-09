# 杩繘路DGEN 鈥?AI 鍏ㄥ煙甯搁┗鑷垜杩唬杩涘寲绯荤粺

> 鍦烘櫙鏃犲叧 路 寮€绠卞嵆鐢?路 鍙殢闇€鎵╁睍

---

## 涓€鍙ヨ瘽

**杩繘鏄?AI Agent 鐨勬搷浣滅郴缁熺骇杩涘寲灞傘€?* 姣忔鍥炲鍓嶈嚜鍔ㄩ妫€鈥旀嫤鎴敊璇€斿己鍖栨垚鍔熲€旇嚜涓昏繘鍖栥€備笉缁戝畾妯″瀷銆佸钩鍙版垨涓氬姟鍦烘櫙銆?

---

## 鏍稿績鍥涘師鍒?

| 瀹堜笁 | 鏀讳竷 | 涓€浜屼笉杩囦笁 | 涓句竴鍙嶄笁 |
|:---|:---|:---|:---|
| 璐熷悜绾犻敊 | 姝ｅ悜寮哄寲 | 绗?3 娆￠€氱煡鐢ㄦ埛 | 璺ㄥ煙娉涘寲 |

---

## 蹇€熷紑濮?

### 鏂瑰紡 A锛氱函 Markdown锛堟帹鑽?路 闆朵緷璧?路 30 绉掔敓鏁堬級

鍛婅瘔浣犵殑 AI锛?

```
璇疯鍙?SKILL.md锛屼箣鍚庢墍鏈夊洖澶嶆墽琛岃凯杩涢妫€锛岃緭鍑?[DGEN] 鏍囪銆?
```

閫傜敤浜?**Codex / Claude / ChatGPT / 浠讳綍 AI Agent**銆?

### 鏂瑰紡 B锛歅ython 寮曟搸

```bash
cd engine && uv run python call_diegin.py activate
uv run python call_diegin.py check   # 姣忔鍥炲鍓?
```

### 鏂瑰紡 C锛氳嚜鍔ㄥ寲寮曟搸

```bash
python scripts/dgen_evolve.py   # 鍒涘缓鍋ュ悍搴﹀熀绾匡紝寮€濮嬭嚜鍔ㄩ棴鐜?
```

---

## 鑷姩鍖栭棴鐜?

杩繘涓嶆槸"鎵嬪姩瀹氳鍒?锛岃€屾槸鑷姩杩涘寲锛?

```
dgen_evolve.py 鈫?鑷姩瑙傚療 鈫?鑷姩鎻愯 鈫?鐢ㄦ埛纭 鈫?鍐欏叆瑙勫垯 鈫?trail 褰掓。
```

棣栨鍚姩锛?
```bash
python scripts/dgen_evolve.py
```

---

## 娣诲姞鏂伴鍩?

鍦?`engine/evo/rules/domain_rules/` 涓嬪垱寤?JSON 鏂囦欢锛屽紩鎿庤嚜鍔ㄥ彂鐜般€?

---

## 鐩綍

```
diegin-skill/
鈹溾攢鈹€ SKILL.md               猸?鏍稿績鎶€鑳藉畾涔?
鈹溾攢鈹€ README.md              鏈枃浠?
鈹溾攢鈹€ engine/                Python 杩繘寮曟搸
鈹?  鈹斺攢鈹€ evo/rules/
鈹?      鈹溾攢鈹€ interception_rules.json  10 鏉＄郴缁熺骇瑙勫垯
鈹?      鈹溾攢鈹€ success_patterns.json     6 鏉＄郴缁熺骇妯″紡
鈹?      鈹斺攢鈹€ domain_rules/            浣犵殑棰嗗煙瑙勫垯鍖?
鈹溾攢鈹€ scripts/               鑷姩鍖栧紩鎿?
鈹溾攢鈹€ workspace/             杩愯鏃舵ā鏉?
鈹溾攢鈹€ plugin/                OpenClaw 鎻掍欢
鈹斺攢鈹€ config/                閰嶇疆鏂囨。
```

---

## 璁稿彲

Apache 2.0 — 自由使用、修改、分发（保留版权声明）。
Apache 2.0 ? ???????????????????