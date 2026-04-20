import base64, hashlib, markdown

# Read methodology
with open('D:/maki-second-brain/03-Projects/AI-Training-Methodology/AI-Second-Brain-Methodology-v2.md', 'r', encoding='utf-8') as f:
    md = f.read()

# Simple SC to TC
pairs = [('与','與'),('设','設'),('产','產'),('团','團'),('经','經'),('质','質'),('体','體'),
    ('个','個'),('对','對'),('进','進'),('动','動'),('发','發'),('应','應'),('这','這'),
    ('实','實'),('际','際'),('运','運'),('专','專'),('业','業'),('练','練'),('记','記'),
    ('录','錄'),('构','構'),('术','術'),('测','測'),('试','試'),('认','認'),('证','證'),
    ('过','過'),('关','關'),('键','鍵'),('词','詞'),('数','據'),('远','遠'),('础','礎'),
    ('码','碼'),('级','級'),('层','層'),('间','間'),('维','維'),('护','護'),('类','類'),
    ('项','項'),('线','線'),('决','決'),('统','統'),('义','義'),('长','長'),('门','門'),
    ('传','傳'),('从','從'),('开','開'),('创','創'),('备','備'),('讨','討'),('论','論'),
    ('赖','賴'),('视','視'),('规','規'),('划','劃'),('历','歷'),('网','網'),('页','頁'),
    ('库','庫'),('并','並'),('来','來'),('后','後'),('监','監'),('机','機'),('执','執'),
    ('时','時'),('战','戰'),('还','還'),('让','讓'),('两','兩'),('馈','饋'),('纠','糾'),
    ('错','錯'),('问','問'),('题','題'),('负','負'),('责','責'),('忆','憶'),('现','現'),
    ('觉','覺'),('调','調'),('优','優'),('为','為'),('带','帶'),('资','資'),('场','場'),
    ('块','塊'),('无','無'),('碍','礙'),('脑','腦'),('训','訓'),('够','夠'),('声','聲')]

tc = md
for s, t in pairs:
    tc = tc.replace(s, t)

html_content = markdown.markdown(tc, extensions=['tables', 'fenced_code'])
encoded = base64.b64encode(html_content.encode('utf-8')).decode('ascii')
pwd_hash = '83503f696e4535c1ed5260f3bc23dfd17f64a2da4a03839be41d2cea4eed101c'

page = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Second Brain</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Noto Sans TC','Inter',sans-serif;color:#2c3e50;background:#fff;line-height:1.8}}
#login{{display:flex;align-items:center;justify-content:center;min-height:100vh;background:#f7f9fc}}
.login-box{{text-align:center;max-width:400px;padding:40px}}
.login-box h1{{font-size:28px;color:#1a2744;margin-bottom:8px}}
.login-box p{{color:#666;margin-bottom:24px;font-size:14px}}
.login-box input{{width:100%;padding:12px 16px;border:2px solid #ddd;border-radius:8px;font-size:16px;outline:none}}
.login-box input:focus{{border-color:#2c6fbb}}
.login-box button{{margin-top:12px;padding:12px 40px;background:#2c6fbb;color:#fff;border:none;border-radius:8px;font-size:15px;font-weight:600;cursor:pointer}}
.login-error{{color:#e74c3c;margin-top:12px;font-size:13px;display:none}}
#content{{display:none;max-width:900px;margin:0 auto;padding:40px 24px}}
#content h1{{font-size:26px;color:#1a2744;margin:32px 0 12px;border-bottom:2px solid #2c6fbb;padding-bottom:8px}}
#content h2{{font-size:20px;color:#1a2744;margin:28px 0 10px}}
#content h3{{font-size:16px;color:#333;margin:20px 0 8px}}
#content p{{margin:8px 0;font-size:14px}}
#content ul,#content ol{{margin:8px 0 8px 24px;font-size:14px}}
#content table{{border-collapse:collapse;width:100%;margin:12px 0;font-size:13px}}
#content th,#content td{{border:1px solid #ddd;padding:8px 12px;text-align:left}}
#content th{{background:#f0f4f8}}
#content blockquote{{border-left:3px solid #2c6fbb;padding:8px 16px;margin:12px 0;background:#f7f9fc;color:#555;font-style:italic}}
#content code{{background:#f0f4f8;padding:1px 6px;border-radius:3px;font-size:13px}}
#content pre{{background:#1a2744;color:#e0e6ff;padding:16px;border-radius:8px;overflow-x:auto;margin:12px 0}}
#content pre code{{background:none;color:inherit}}
#content hr{{border:none;border-top:1px solid #eee;margin:24px 0}}
@media(max-width:768px){{#content{{padding:20px 16px}}}}
</style>
</head>
<body>
<div id="login">
<div class="login-box">
<h1>AI Second Brain</h1>
<p>此文件需要授權密碼</p>
<input type="password" id="pwd" placeholder="請輸入密碼" onkeypress="if(event.key==='Enter')unlock()">
<br><button onclick="unlock()">進入</button>
<div class="login-error" id="err">密碼錯誤，請重新輸入</div>
</div>
</div>
<div id="content"></div>
<script>
const H="{pwd_hash}";
const D="{encoded}";
async function sha256(m){{const e=new TextEncoder().encode(m);const h=await crypto.subtle.digest('SHA-256',e);return Array.from(new Uint8Array(h)).map(b=>b.toString(16).padStart(2,'0')).join('')}}
async function unlock(){{const p=document.getElementById('pwd').value;const h=await sha256(p);if(h===H){{document.getElementById('login').style.display='none';const c=document.getElementById('content');c.innerHTML=new TextDecoder().decode(Uint8Array.from(atob(D),c=>c.charCodeAt(0)));c.style.display='block'}}else{{document.getElementById('err').style.display='block';document.getElementById('pwd').value=''}}}}
</script>
</body>
</html>"""

with open('D:/maki-workspace/demos/ai-methodology/index.html', 'w', encoding='utf-8') as f:
    f.write(page)
print(f'Done! Encoded content: {len(encoded)} chars')
