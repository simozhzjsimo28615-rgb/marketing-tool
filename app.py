from flask import Flask, request, jsonify, render_template_string
import re, random

app = Flask(__name__)

GREETINGS = {
    "formal": ["تحية طيبة،", "السلام عليكم ورحمة الله،", "عميلنا العزيز،"],
    "friendly": ["مرحباً! 👋", "أهلاً بك!", "كيف حالك؟"],
    "short": [""],
    "catchy": ["🔥 انتباه!", "⚡ لا تفوّت!", "🚀 اكتشف الآن!"]
}
CLOSINGS = {
    "formal": ["وتفضلوا بقبول فائق الاحترام.", "مع خالص التقدير."],
    "friendly": ["دمت بود! 😊", "بانتظار ردك!"],
    "short": [""],
    "catchy": ["سارع الآن! ⏳", "العرض محدود!", "اطلب اليوم! 🎁"]
}
POWER = {
    "formal": ["بكل احترافية", "بأعلى معايير الجودة"],
    "friendly": ["بكل حب", "بكل بساطة"],
    "short": [""],
    "catchy": ["حصرياً 🔥", "مجاناً 🎁", "بدون منافس 💎"]
}

def clean(t): return re.sub(r'\s+', ' ', t).strip()
def split(t): return [p.strip() for p in re.split(r'[.!?؟،]+', t) if p.strip()]

def transform(text, style):
    text = clean(text)
    if not text: return ""
    sents = split(text)
    r = []
    if style == "formal":
        r.append(random.choice(GREETINGS["formal"])); r.append("")
        for i, s in enumerate(sents):
            r.append(("نود أن نحيطكم علماً بأن " if i==0 else "كما نلفت انتباهكم إلى أن ") + s + ".")
        r.append(""); r.append(random.choice(CLOSINGS["formal"]))
    elif style == "friendly":
        r.append(random.choice(GREETINGS["friendly"])); r.append("")
        for s in sents: r.append("تعرف إيش؟ " + s + " 😍")
        r.append(""); r.append(random.choice(CLOSINGS["friendly"]))
    elif style == "short":
        r.append(". ".join(sents[:2]) + ("." if not sents[:2][-1].endswith('.') else ""))
    elif style == "catchy":
        r.append(random.choice(GREETINGS["catchy"])); r.append("")
        for s in sents:
            words = s.split()
            if len(words) > 3:
                words[random.randint(0,len(words)-1)] = words[random.randint(0,len(words)-1)].upper()
            r.append(" ".join(words) + "!")
        r.append(""); r.append(random.choice(POWER["catchy"])); r.append(random.choice(CLOSINGS["catchy"]))
    return "\n".join(r)

HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>منشئ المحتوى التسويقي</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Segoe UI',Tahoma,sans-serif;background:linear-gradient(135deg,#667eea,#764ba2);min-height:100vh;padding:20px;color:#333}
.container{max-width:750px;margin:0 auto}
.header{text-align:center;color:#fff;margin-bottom:25px}
.header h1{font-size:2em;margin-bottom:8px;text-shadow:0 2px 10px rgba(0,0,0,.3)}
.header p{opacity:.9;font-size:.95em}
.card{background:#fff;border-radius:20px;padding:25px;box-shadow:0 20px 60px rgba(0,0,0,.3);margin-bottom:20px}
.card h2{font-size:1.2em;margin-bottom:15px;color:#667eea}
textarea{width:100%;min-height:120px;padding:15px;border:2px solid #e0e0e0;border-radius:12px;font-size:1em;font-family:inherit;resize:vertical;line-height:1.6}
textarea:focus{outline:none;border-color:#667eea;box-shadow:0 0 0 4px rgba(102,126,234,.15)}
.styles{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin:18px 0}
.style-btn{padding:14px;border:2px solid #e0e0e0;background:#fff;border-radius:12px;cursor:pointer;font-family:inherit;font-size:.95em;font-weight:600;transition:.2s}
.style-btn.active{background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border-color:transparent;box-shadow:0 8px 20px rgba(102,126,234,.4)}
.action{width:100%;padding:17px;background:linear-gradient(135deg,#667eea,#764ba2);color:#fff;border:none;border-radius:12px;font-size:1.15em;font-weight:700;cursor:pointer;font-family:inherit;box-shadow:0 10px 30px rgba(102,126,234,.4)}
.action:active{transform:scale(.98)}
.result{background:#f8f9ff;border:2px dashed #667eea;border-radius:12px;padding:20px;min-height:130px;white-space:pre-wrap;line-height:1.8;font-size:1.05em;position:relative}
.result:empty::before{content:"النتيجة ستظهر هنا...";color:#999}
.copy{position:absolute;top:10px;left:10px;background:#667eea;color:#fff;border:none;padding:7px 14px;border-radius:8px;cursor:pointer;font-family:inherit;font-size:.85em;font-weight:600;display:none}
.copy.show{display:block}
.toast{position:fixed;bottom:30px;left:50%;transform:translateX(-50%) translateY(100px);background:#10b981;color:#fff;padding:12px 25px;border-radius:25px;font-weight:600;transition:.3s;box-shadow:0 10px 30px rgba(16,185,129,.4)}
.toast.show{transform:translateX(-50%) translateY(0)}
</style>
</head>
<body>
<div class="container">
<div class="header"><h1>✍️ منشئ المحتوى التسويقي</h1><p>حوّل نصوصك إلى محتوى احترافي بضغطة واحدة</p></div>
<div class="card"><h2>📝 النص الأصلي</h2><textarea id="input" placeholder="اكتب أو الصق نصك هنا..."></textarea></div>
<div class="card">
<h2>🎨 اختر الأسلوب</h2>
<div class="styles">
<button class="style-btn active" data-style="formal">🎩 رسمي</button>
<button class="style-btn" data-style="friendly">😊 ودّي</button>
<button class="style-btn" data-style="short">⚡ مختصر</button>
<button class="style-btn" data-style="catchy">🔥 جذاب</button>
</div>
<button class="action" id="genBtn">✨ إعادة صياغة</button>
</div>
<div class="card">
<h2>📄 النتيجة</h2>
<div class="result"><button class="copy" id="copyBtn">📋 نسخ</button><span id="out"></span></div>
</div>
</div>
<div class="toast" id="toast">✅ تم النسخ!</div>
<script>
var style='formal';
document.querySelectorAll('.style-btn').forEach(function(b){
  b.onclick=function(){
    document.querySelectorAll('.style-btn').forEach(function(x){x.classList.remove('active')});
    b.classList.add('active');style=b.dataset.style;
  };
});
document.getElementById('genBtn').onclick=async function(){
  var t=document.getElementById('input').value.trim();
  if(!t){alert('اكتب نصاً أولاً');return}
  var btn=this;btn.disabled=true;btn.textContent='⏳ جاري الصياغة...';
  try{
    var r=await fetch('/api/transform',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({text:t,style:style})});
    var d=await r.json();
    document.getElementById('out').textContent=d.result;
    document.getElementById('copyBtn').classList.add('show');
  }catch(e){alert('خطأ في الاتصال')}
  btn.disabled=false;btn.textContent='✨ إعادة صياغة';
};
document.getElementById('copyBtn').onclick=function(){
  var t=document.getElementById('out').textContent;
  if(navigator.clipboard){navigator.clipboard.writeText(t)}
  var to=document.getElementById('toast');to.classList.add('show');
  setTimeout(function(){to.classList.remove('show')},2000);
};
</script>
</body>
</html>
"""

@app.route('/')
def index(): return render_template_string(HTML)

@app.route('/api/transform', methods=['POST'])
def api():
    d = request.get_json()
    return jsonify({'result': transform(d.get('text',''), d.get('style','formal'))})

if __name__ == '__main__':
    print("="*50)
    print("✍️  منشئ المحتوى التسويقي")
    print("افتح: http://localhost:5555")
    print("="*50)
    app.run(host='0.0.0.0', port=int(__import__("os").environ.get("PORT", 5555)))
