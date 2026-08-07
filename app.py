from flask import Flask, render_template_string, request, jsonify, session
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'darkstore_secret_key_change_this_786'

# CONFIG - CHANGE THESE
ADMIN_PASSWORD = "darkstore786"
WHATSAPP_NUMBER = "923303257478"  # Updated number

# Data file paths
DATA_FILE = 'store_data.json'

# Default data
default_data = {
    'products': [
        {"id": "p_demo1", "name": "Starter Pack", "desc": "Basic bundle to get going. Free forever.", 
         "type": "free", "price": "", "images": [], "videos": [], "soldOut": False},
        {"id": "p_demo2", "name": "Pro Bundle", "desc": "Full premium bundle with extra content.", 
         "type": "paid", "price": "Rs. 1500", "images": [], "videos": [], "soldOut": False}
    ],
    'orders': [],
    'votes': {"trusted": 84, "not": 1}
}

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except:
            return default_data.copy()
    return default_data.copy()

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# HTML TEMPLATE
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DARK STORE</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#0a0a0d;
    --surface:#151318;
    --surface2:#1e1a22;
    --gold:#d4a017;
    --gold-bright:#f0c341;
    --red:#c0392b;
    --teal:#1a9c8c;
    --text:#ece7dd;
    --muted:#8b8577;
    --line:#2c2730;
  }
  *{box-sizing:border-box; margin:0; padding:0;}
  body{
    background:var(--bg);
    color:var(--text);
    font-family:'Inter',sans-serif;
    min-height:100vh;
    position:relative;
    overflow-x:hidden;
  }
  body::before{
    content:'';
    position:fixed; inset:0; z-index:-3;
    background-image:
      linear-gradient(rgba(212,160,23,0.05) 1px, transparent 1px),
      linear-gradient(90deg, rgba(212,160,23,0.05) 1px, transparent 1px);
    background-size:42px 42px;
    mask-image:radial-gradient(circle at 50% 0%, black, transparent 75%);
    animation:gridDrift 30s linear infinite;
  }
  @keyframes gridDrift{0%{background-position:0 0, 0 0;}100%{background-position:42px 84px, 42px 84px;}}
  body::after{
    content:'';
    position:fixed; inset:0; z-index:-2;
    background-image:
      radial-gradient(ellipse 700px 500px at 12% 8%, rgba(212,160,23,0.10), transparent 60%),
      radial-gradient(ellipse 600px 500px at 88% 30%, rgba(26,156,140,0.09), transparent 60%),
      radial-gradient(ellipse 500px 400px at 50% 95%, rgba(192,57,43,0.07), transparent 60%);
    animation:glowShift 14s ease-in-out infinite alternate;
  }
  @keyframes glowShift{
    0%{transform:translate(0,0) scale(1);}
    100%{transform:translate(-2%,2%) scale(1.06);}
  }
  .particles{position:fixed; inset:0; z-index:-1; pointer-events:none; overflow:hidden;}
  .particles span{
    position:absolute; bottom:-10px; width:2px; height:2px; border-radius:50%;
    background:var(--gold); opacity:0.5; box-shadow:0 0 6px var(--gold);
    animation:floatUp linear infinite;
  }
  @keyframes floatUp{
    0%{transform:translateY(0) translateX(0); opacity:0;}
    10%{opacity:0.6;}
    90%{opacity:0.4;}
    100%{transform:translateY(-100vh) translateX(20px); opacity:0;}
  }
  .mono{font-family:'JetBrains Mono',monospace;}
  header{
    padding:22px 28px;
    display:flex; align-items:center; justify-content:space-between;
    border-bottom:1px solid var(--line);
    position:sticky; top:0; z-index:50;
    background:rgba(10,10,13,0.65); backdrop-filter:blur(14px) saturate(140%);
    box-shadow:0 1px 0 rgba(212,160,23,0.08);
  }
  .brand{
    font-family:'Bebas Neue', sans-serif;
    font-size:32px; letter-spacing:3px; color:var(--gold-bright);
    display:flex; align-items:center; gap:10px;
  }
  .brand .dot{width:9px;height:9px;border-radius:50%;background:var(--red); box-shadow:0 0 10px var(--red); animation:pulse 2s infinite;}
  @keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.3;}}
  .tagline{font-size:11px; color:var(--muted); letter-spacing:2px; text-transform:uppercase; margin-top:2px;}
  nav{display:flex; align-items:center; gap:10px;}
  nav button{
    background:rgba(255,255,255,0.02); border:1px solid var(--line); color:var(--text);
    padding:10px 20px; font-family:'JetBrains Mono',monospace; font-size:12px;
    letter-spacing:1px; cursor:pointer; border-radius:4px; transition:.25s;
  }
  nav button:hover{border-color:var(--gold); color:var(--gold-bright); box-shadow:0 0 16px rgba(212,160,23,0.25); transform:translateY(-1px);}
  .count-pill{
    background:var(--red); color:#fff; border-radius:10px; padding:1px 6px; font-size:10px; margin-left:6px;
  }

  .hero{
    padding:64px 24px 44px; text-align:center; border-bottom:1px solid var(--line);
  }
  .hero h1{
    font-family:'Bebas Neue'; font-size:clamp(40px,8vw,80px); letter-spacing:4px;
    line-height:1;
    background:linear-gradient(100deg, var(--text) 30%, var(--gold-bright) 45%, var(--text) 60%);
    background-size:220% auto;
    -webkit-background-clip:text; background-clip:text; color:transparent;
    animation:shine 5s linear infinite;
  }
  @keyframes shine{0%{background-position:0% 0;}100%{background-position:-220% 0;}}
  .hero h1 span{
    background:linear-gradient(100deg, var(--gold-bright), #fff6d8, var(--gold-bright));
    -webkit-background-clip:text; background-clip:text; color:transparent;
  }
  .hero p{color:var(--muted); margin-top:14px; font-size:13px; letter-spacing:2px;}

  .trust-box{
    max-width:520px; margin:0 auto; padding:20px 22px; background:var(--surface);
    border:1px solid var(--line); border-radius:8px; position:relative;
  }
  .trust-head{display:flex; justify-content:space-between; align-items:center; font-size:11px; letter-spacing:2px; color:var(--muted); margin-bottom:10px;}
  .trust-count{color:var(--gold-bright);}
  .trust-bar{
    height:12px; border-radius:6px; overflow:hidden; background:rgba(192,57,43,0.35);
    border:1px solid var(--line); display:flex;
  }
  .trust-fill{
    height:100%; background:linear-gradient(90deg, var(--teal), #2fd6bd);
    width:84%; transition:width .5s ease; box-shadow:0 0 10px rgba(26,156,140,0.6);
  }
  .trust-labels{display:flex; justify-content:space-between; margin-top:8px; font-size:11px; letter-spacing:1px;}
  .t-good{color:var(--teal);}
  .t-bad{color:var(--red);}
  .trust-actions{display:flex; gap:10px; margin-top:16px;}
  .vote-btn{
    flex:1; padding:11px; border-radius:6px; border:1px solid var(--line); background:rgba(255,255,255,0.02);
    color:var(--text); font-size:12px; font-weight:700; letter-spacing:1px; cursor:pointer; transition:.25s;
  }
  .vote-btn:active{transform:scale(0.96);}
  .vote-btn.good:hover{border-color:var(--teal); color:var(--teal); background:rgba(26,156,140,0.08); box-shadow:0 4px 16px rgba(26,156,140,0.2);}
  .vote-btn.bad:hover{border-color:var(--red); color:#ff6b5b; background:rgba(192,57,43,0.08); box-shadow:0 4px 16px rgba(192,57,43,0.2);}
  .trust-thanks{
    display:none; text-align:center; margin-top:14px; color:var(--gold-bright);
    font-size:11px; letter-spacing:2px;
  }
  .voted .trust-actions{display:none;}
  .voted .trust-thanks{display:block;}

  .filters{
    display:flex; gap:10px; justify-content:center; padding:24px; flex-wrap:wrap;
  }
  .filters button{
    background:rgba(255,255,255,0.02); border:1px solid var(--line); color:var(--muted);
    padding:9px 18px; border-radius:22px; font-size:12px; letter-spacing:1.5px; cursor:pointer;
    font-family:'JetBrains Mono',monospace; transition:.25s;
  }
  .filters button:hover{border-color:rgba(212,160,23,0.4); color:var(--text);}
  .filters button.active{background:var(--gold); color:#161116; border-color:var(--gold); font-weight:700; box-shadow:0 4px 14px rgba(212,160,23,0.25);}

  .grid{
    display:grid; grid-template-columns:repeat(auto-fill,minmax(240px,1fr));
    gap:20px; padding:10px 24px 80px; max-width:1400px; margin:0 auto;
  }
  .card{
    background:linear-gradient(180deg, rgba(30,26,34,0.9), rgba(21,19,24,0.95));
    border:1px solid var(--line); border-radius:10px; overflow:hidden;
    position:relative; transition:.3s cubic-bezier(.2,.8,.2,1); display:flex; flex-direction:column;
    backdrop-filter:blur(6px);
  }
  .card::before{
    content:''; position:absolute; top:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg, var(--gold), var(--teal)); opacity:0; transition:.3s;
  }
  .card:hover{transform:translateY(-6px); border-color:rgba(212,160,23,0.4); box-shadow:0 16px 36px rgba(0,0,0,.55), 0 0 0 1px rgba(212,160,23,0.08);}
  .card:hover::before{opacity:1;}
  .card .media{width:100%; height:180px; background:#0d0c10; display:flex; align-items:center; justify-content:center; overflow:hidden; position:relative;}
  .card .media::after{content:''; position:absolute; inset:0; background:linear-gradient(180deg, transparent 60%, rgba(0,0,0,0.35));}
  .card .media img, .card .media video{width:100%; height:100%; object-fit:cover; transition:.4s;}
  .card:hover .media img, .card:hover .media video{transform:scale(1.06);}
  .stamp{
    position:absolute; top:12px; right:-30px; transform:rotate(35deg);
    padding:4px 40px; font-family:'JetBrains Mono'; font-size:11px; font-weight:700;
    letter-spacing:2px; z-index:5;
  }
  .stamp.free{background:var(--teal); color:#04211d;}
  .stamp.paid{background:var(--red); color:#2a0f0b;}
  .card.sold-out .media{filter:grayscale(0.8) brightness(0.5);}
  .sold-badge{
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%) rotate(-10deg);
    background:rgba(0,0,0,0.75); border:2px solid var(--red); color:#ff6b5b;
    font-family:'Bebas Neue'; font-size:22px; letter-spacing:3px; padding:6px 18px;
    z-index:6; border-radius:4px; box-shadow:0 0 20px rgba(192,57,43,0.4);
  }
  .buy-btn:disabled{
    background:rgba(255,255,255,0.06); color:var(--muted); cursor:not-allowed;
    box-shadow:none; transform:none !important;
  }
  .buy-btn.dl-btn{background:linear-gradient(135deg, var(--teal), #12796d); box-shadow:0 4px 14px rgba(26,156,140,0.15);}
  .buy-btn.dl-btn:hover{background:linear-gradient(135deg, #2fd6bd, var(--teal)); box-shadow:0 8px 22px rgba(26,156,140,0.35);}
  .card-body .price.approval-note{font-size:10px; color:var(--muted); font-family:'JetBrains Mono';}
  .card-body{padding:16px; display:flex; flex-direction:column; gap:8px; flex:1;}
  .card-body h3{font-size:16px; font-weight:600;}
  .card-body .price{color:var(--gold-bright); font-family:'JetBrains Mono'; font-size:14px;}
  .card-body p{color:var(--muted); font-size:12px; line-height:1.5; flex:1;}
  .buy-btn{
    margin-top:8px; background:linear-gradient(135deg, var(--gold), #b98410); color:#161116; border:none; padding:11px;
    font-weight:700; letter-spacing:1px; font-size:12px; border-radius:5px; cursor:pointer;
    display:flex; align-items:center; justify-content:center; gap:8px; transition:.25s;
    box-shadow:0 4px 14px rgba(212,160,23,0.15);
  }
  .buy-btn:hover{background:linear-gradient(135deg, var(--gold-bright), var(--gold)); transform:translateY(-2px); box-shadow:0 8px 22px rgba(212,160,23,0.35);}
  .rm-btn{
    position:absolute; top:8px; left:8px; background:rgba(192,57,43,0.85); color:#fff; border:none;
    width:26px; height:26px; border-radius:50%; cursor:pointer; font-size:14px; z-index:6; display:none;
  }
  .so-btn{
    position:absolute; top:8px; left:40px; background:rgba(60,55,45,0.9); color:#fff; border:none;
    width:26px; height:26px; border-radius:50%; cursor:pointer; font-size:12px; z-index:6; display:none;
  }
  .admin-on .rm-btn, .admin-on .so-btn{display:block;}

  .empty{grid-column:1/-1; text-align:center; color:var(--muted); padding:60px 20px;}

  /* Uptime Status */
  .uptime-bar {
    max-width:520px; margin:12px auto 0; padding:8px 22px; background:var(--surface);
    border:1px solid var(--line); border-radius:8px; display:flex; align-items:center; justify-content:space-between;
    font-size:11px; font-family:'JetBrains Mono'; color:var(--muted);
  }
  .uptime-bar .uptime-status {
    display:flex; align-items:center; gap:6px;
  }
  .uptime-bar .uptime-dot {
    width:8px; height:8px; border-radius:50%; display:inline-block;
  }
  .uptime-bar .uptime-dot.online { background:#2ecc71; box-shadow:0 0 10px #2ecc71; animation:blink 2s infinite; }
  .uptime-bar .uptime-dot.offline { background:var(--red); box-shadow:0 0 10px var(--red); }
  .uptime-bar .uptime-label { letter-spacing:1px; }

  /* Modal */
  .overlay{
    position:fixed; inset:0; background:rgba(5,5,7,0.85); backdrop-filter:blur(4px);
    display:none; align-items:center; justify-content:center; z-index:100; padding:20px;
  }
  .overlay.show{display:flex;}
  .modal{
    background:var(--surface2); border:1px solid var(--gold); border-radius:8px; padding:28px;
    width:100%; max-width:440px; max-height:88vh; overflow-y:auto;
  }
  .modal.modal-wide{max-width:560px;}
  .modal h2{font-family:'Bebas Neue'; letter-spacing:2px; color:var(--gold-bright); font-size:26px; margin-bottom:16px;}

  .login-modal{
    position:relative; text-align:center; border:1px solid transparent; overflow:visible;
    background:
      linear-gradient(var(--surface2), var(--surface2)) padding-box,
      linear-gradient(130deg, var(--gold), var(--teal), var(--gold)) border-box;
    border:1px solid transparent; background-size:100% 100%, 250% 250%;
    animation:borderFlow 5s ease infinite;
  }
  @keyframes borderFlow{0%{background-position:0 0, 0% 50%;}100%{background-position:0 0, 200% 50%;}}
  .login-lock{
    width:60px; height:60px; margin:0 auto 14px; border-radius:50%;
    background:radial-gradient(circle, rgba(212,160,23,0.18), transparent 70%);
    display:flex; align-items:center; justify-content:center; font-size:26px;
    border:1px solid rgba(212,160,23,0.35); box-shadow:0 0 20px rgba(212,160,23,0.15);
    animation:lockPulse 2.2s ease-in-out infinite;
  }
  @keyframes lockPulse{0%,100%{box-shadow:0 0 14px rgba(212,160,23,0.15);}50%{box-shadow:0 0 26px rgba(212,160,23,0.4);}}
  .login-modal h2{text-align:center; margin-bottom:4px;}
  .login-sub{color:var(--muted); font-size:11px; letter-spacing:2px; margin-bottom:20px; font-family:'JetBrains Mono';}
  .login-modal .field input{text-align:center; letter-spacing:3px; font-size:15px;}

  .approval-modal{text-align:center;}
  .approval-item{color:var(--text); font-size:13px; margin-bottom:16px; font-weight:600;}
  .key-box{
    display:flex; align-items:center; justify-content:space-between; gap:10px;
    background:var(--bg); border:1px solid var(--gold); border-radius:6px; padding:12px 14px;
    margin-bottom:14px;
  }
  .key-text{
    font-family:'JetBrains Mono'; font-size:18px; letter-spacing:3px; color:var(--gold-bright); font-weight:700;
  }
  .copy-btn{
    background:rgba(212,160,23,0.12); border:1px solid var(--gold); color:var(--gold-bright);
    padding:7px 12px; border-radius:4px; font-size:10px; letter-spacing:1px; cursor:pointer; transition:.2s;
    font-family:'JetBrains Mono'; font-weight:700;
  }
  .copy-btn:hover{background:var(--gold); color:#161116;}
  .approval-note{color:var(--muted); font-size:11px; line-height:1.5; margin-bottom:6px;}
  .field{margin-bottom:14px;}
  .field label{display:block; font-size:11px; color:var(--muted); letter-spacing:1px; margin-bottom:6px; text-transform:uppercase;}
  .field input[type=text], .field input[type=number], .field input[type=password], .field textarea{
    width:100%; background:var(--bg); border:1px solid var(--line); color:var(--text);
    padding:10px; border-radius:4px; font-family:'Inter'; font-size:13px;
  }
  .field textarea{resize:vertical; min-height:60px;}
  .field input[type=file]{width:100%; font-size:12px; color:var(--muted);}
  .radio-row{display:flex; gap:14px; font-size:13px;}
  .radio-row label{display:flex; align-items:center; gap:6px; color:var(--text); text-transform:none; font-size:13px;}
  .thumbs{display:flex; gap:6px; margin-top:6px; flex-wrap:wrap;}
  .thumbs img, .thumbs video{width:50px; height:50px; object-fit:cover; border-radius:4px; border:1px solid var(--line);}
  .modal-actions{display:flex; gap:10px; margin-top:18px;}
  .modal-actions button{
    flex:1; padding:12px; border:none; border-radius:6px; font-weight:700; letter-spacing:1px;
    font-size:12px; cursor:pointer; transition:.2s;
  }
  .modal-actions button:active{transform:scale(0.96);}
  .btn-primary{background:linear-gradient(135deg, var(--gold), #b98410); color:#161116; box-shadow:0 4px 14px rgba(212,160,23,0.2);}
  .btn-primary:hover{background:linear-gradient(135deg, var(--gold-bright), var(--gold)); box-shadow:0 6px 18px rgba(212,160,23,0.35); transform:translateY(-1px);}
  .btn-ghost{background:transparent; border:1px solid var(--line) !important; color:var(--muted);}
  .btn-ghost:hover{color:var(--text); border-color:var(--text) !important;}
  .err{color:var(--red); font-size:12px; margin-top:8px; display:none;}

  .admin-panel-list{margin-top:20px; border-top:1px solid var(--line); padding-top:14px;}
  .admin-panel-list h3{font-size:12px; letter-spacing:1px; color:var(--muted); margin-bottom:10px; text-transform:uppercase;}
  .admin-badge{
    position:fixed; bottom:20px; right:20px; background:var(--red); color:#fff; padding:8px 14px;
    border-radius:20px; font-size:11px; font-family:'JetBrains Mono'; letter-spacing:1px; z-index:60;
    display:none; align-items:center; gap:8px; cursor:pointer;
  }
  .admin-badge.show{display:flex;}

  .orders-filters{display:flex; gap:8px; margin-bottom:14px; flex-wrap:wrap;}
  .orders-filters button{
    background:rgba(255,255,255,0.02); border:1px solid var(--line); color:var(--muted);
    padding:6px 14px; border-radius:16px; font-size:11px; letter-spacing:1px; cursor:pointer;
    font-family:'JetBrains Mono',monospace; transition:.2s;
  }
  .orders-filters button.active{background:var(--gold); color:#161116; border-color:var(--gold); font-weight:700;}
  .order-card{
    border:1px solid var(--line); border-radius:6px; padding:12px 14px; margin-bottom:10px;
    background:var(--bg); text-align:left;
  }
  .order-card .o-top{display:flex; align-items:center; justify-content:space-between; gap:8px; margin-bottom:4px;}
  .order-card .o-name{font-weight:700; font-size:13px;}
  .order-card .o-key{font-family:'JetBrains Mono'; color:var(--gold-bright); letter-spacing:2px; font-size:13px; margin-bottom:4px;}
  .order-card .o-meta{font-size:11px; color:var(--muted); margin-bottom:10px;}
  .order-card .o-actions{display:flex; gap:8px;}
  .order-card .o-actions button{
    flex:1; padding:9px; border:none; border-radius:5px; font-size:11px; font-weight:700; letter-spacing:0.5px;
    cursor:pointer; font-family:'JetBrains Mono'; transition:.2s;
  }
  .order-card .o-actions button:active{transform:scale(0.96);}
  .o-approve{background:var(--teal); color:#04211d;}
  .o-approve:hover{background:#2fd6bd;}
  .o-reject{background:var(--red); color:#fff;}
  .o-reject:hover{background:#e0453a;}
  .o-remove{background:rgba(255,255,255,0.06); color:var(--muted);}
  .o-remove:hover{color:var(--text);}
  .order-status{font-size:10px; letter-spacing:1px; padding:3px 9px; border-radius:10px; white-space:nowrap; font-family:'JetBrains Mono';}
  .status-pending{background:rgba(212,160,23,0.15); color:var(--gold-bright); border:1px solid rgba(212,160,23,0.35);}
  .status-approved{background:rgba(26,156,140,0.15); color:var(--teal); border:1px solid rgba(26,156,140,0.35);}
  .status-rejected{background:rgba(192,57,43,0.15); color:#ff6b5b; border:1px solid rgba(192,57,43,0.35);}
  .orders-empty{text-align:center; color:var(--muted); padding:40px 10px; font-size:12px;}

  /* Product Detail Modal */
  .detail-modal .detail-content {
    text-align:left;
  }
  .detail-modal .detail-content .detail-media {
    width:100%; max-height:300px; overflow:hidden; border-radius:8px; margin-bottom:16px;
    background:#0d0c10;
  }
  .detail-modal .detail-content .detail-media img, 
  .detail-modal .detail-content .detail-media video {
    width:100%; max-height:300px; object-fit:cover;
  }
  .detail-modal .detail-content .detail-title {
    font-size:20px; font-weight:700; color:var(--gold-bright); margin-bottom:6px;
  }
  .detail-modal .detail-content .detail-price {
    font-size:16px; font-family:'JetBrains Mono'; color:var(--teal); margin-bottom:8px;
  }
  .detail-modal .detail-content .detail-desc {
    color:var(--muted); font-size:14px; line-height:1.6; margin-bottom:12px;
  }
  .detail-modal .detail-content .detail-meta {
    display:flex; gap:12px; flex-wrap:wrap; font-size:12px; color:var(--muted);
    border-top:1px solid var(--line); padding-top:12px; margin-top:6px;
  }
  .detail-modal .detail-content .detail-meta span {
    background:var(--bg); padding:4px 12px; border-radius:12px;
  }

  .product-detail-btn {
    background:var(--bg); border:1px solid var(--line); color:var(--text);
    padding:4px 12px; border-radius:12px; font-size:10px; cursor:pointer;
    transition:.2s; font-family:'JetBrains Mono';
  }
  .product-detail-btn:hover {
    border-color:var(--gold); color:var(--gold-bright);
  }

  footer{
    text-align:center; padding:34px; color:var(--muted); font-size:11px; letter-spacing:2px;
    border-top:1px solid var(--line); font-family:'JetBrains Mono';
  }
  footer .fdot{color:var(--gold); margin:0 8px;}

  #splash{
    position:fixed; inset:0; z-index:999; background:#000;
    display:flex; flex-direction:column; align-items:center; justify-content:center;
    cursor:pointer; overflow:hidden;
    transition:opacity .6s ease, visibility .6s ease;
  }
  #splash.hide{opacity:0; visibility:hidden; pointer-events:none;}
  #splash::before{
    content:''; position:absolute; inset:0;
    background:
      repeating-linear-gradient(0deg, rgba(212,160,23,0.03) 0px, transparent 2px, transparent 4px),
      radial-gradient(circle at 50% 50%, rgba(212,160,23,0.08), transparent 60%);
    animation:scan 6s linear infinite;
  }
  @keyframes scan{0%{background-position:0 0;}100%{background-position:0 200px;}}
  .splash-lock{font-size:38px; margin-bottom:18px; opacity:0; animation:fadeIn .6s ease .1s forwards;}
  .splash-title{
    font-family:'Bebas Neue'; font-size:clamp(46px,11vw,110px); letter-spacing:6px;
    color:var(--gold-bright);
    text-shadow:0 0 18px rgba(240,195,65,0.5), 0 0 40px rgba(240,195,65,0.25);
    opacity:0; transform:translateY(14px);
    animation:fadeIn .7s ease .3s forwards, flicker 3.5s ease-in-out 1.4s infinite;
    position:relative;
  }
  .splash-title::after{
    content:'DARK STORE'; position:absolute; left:2px; top:0; color:var(--teal);
    opacity:0.5; mix-blend-mode:screen; animation:glitchShift 4s infinite;
  }
  @keyframes glitchShift{
    0%,92%,100%{clip-path:inset(0 0 0 0); transform:translate(0,0);}
    93%{clip-path:inset(10% 0 60% 0); transform:translate(-3px,0);}
    95%{clip-path:inset(60% 0 5% 0); transform:translate(3px,0);}
    97%{clip-path:inset(30% 0 40% 0); transform:translate(-2px,0);}
  }
  @keyframes flicker{0%,96%,100%{opacity:1;}97%{opacity:0.7;}98%{opacity:1;}}
  @keyframes fadeIn{to{opacity:1; transform:translateY(0);}}
  .splash-sub{
    font-family:'JetBrains Mono'; font-size:12px; letter-spacing:4px; color:var(--muted);
    margin-top:16px; opacity:0; animation:fadeIn .6s ease 1s forwards; text-transform:uppercase;
  }
  .splash-hint{
    position:absolute; bottom:36px; font-family:'JetBrains Mono'; font-size:11px;
    color:var(--muted); letter-spacing:2px; opacity:0; animation:fadeIn .6s ease 1.8s forwards, blink 1.6s ease-in-out 2.4s infinite;
  }
  @keyframes blink{0%,100%{opacity:.4;}50%{opacity:1;}}
  .splash-bars{display:flex; gap:4px; margin-top:22px; height:22px; align-items:flex-end; opacity:0; animation:fadeIn .5s ease .8s forwards;}
  .splash-bars span{width:4px; background:var(--gold); animation:eq 1s ease-in-out infinite;}
  .splash-bars span:nth-child(1){animation-delay:0s; height:8px;}
  .splash-bars span:nth-child(2){animation-delay:.15s; height:16px;}
  .splash-bars span:nth-child(3){animation-delay:.3s; height:22px;}
  .splash-bars span:nth-child(4){animation-delay:.1s; height:12px;}
  .splash-bars span:nth-child(5){animation-delay:.25s; height:18px;}
  @keyframes eq{0%,100%{transform:scaleY(0.4);}50%{transform:scaleY(1);}}

  @media (max-width:600px){
    header{padding:16px; flex-wrap:wrap; gap:10px;}
    .brand{font-size:24px;}
    nav button{padding:8px 14px; font-size:11px;}
    .hero{padding:40px 16px 28px;}
    .hero h1{letter-spacing:2px;}
    .trust-box{margin:0 16px; padding:16px;}
    .trust-actions{flex-direction:column;}
    .filters{padding:16px; gap:8px;}
    .filters button{padding:7px 14px; font-size:11px;}
    .grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr)); gap:12px; padding:6px 16px 60px;}
    .card .media{height:130px;}
    .card-body{padding:12px;}
    .card-body h3{font-size:14px;}
    .modal{padding:20px; max-width:94vw;}
    .admin-badge{right:12px; bottom:12px; font-size:10px; padding:7px 12px;}
    .splash-title{letter-spacing:3px;}
    .uptime-bar{flex-wrap:wrap; gap:6px; justify-content:center;}
  }
  @media (max-width:360px){
    .grid{grid-template-columns:repeat(auto-fill,minmax(130px,1fr));}
  }
</style>
</head>
<body>

<div class="particles" id="particles"></div>

<div id="splash">
  <div class="splash-lock">🔒</div>
  <div class="splash-title">DARK STORE</div>
  <div class="splash-bars"><span></span><span></span><span></span><span></span><span></span></div>
  <div class="splash-sub">// tap anywhere to enter //</div>
  <div class="splash-hint">SOUND ON RECOMMENDED</div>
</div>

<header>
  <div>
    <div class="brand"><span class="dot"></span>DARK STORE</div>
    <div class="tagline">buy quiet. buy fast.</div>
  </div>
  <nav>
    <button id="ordersBtn" style="display:none;">ORDERS<span class="count-pill" id="ordersCount"></span></button>
    <button id="adminBtn">ADMIN</button>
  </nav>
</header>

<section class="hero">
  <h1>EVERYTHING HAS A <span>PRICE</span>.<br>SOME OF IT IS FREE.</h1>
  <p class="mono">TAP ANY ITEM → BUY ON WHATSAPP INSTANTLY</p>
</section>

<!-- Uptime Status Bar -->
<div class="uptime-bar" id="uptimeBar">
  <span class="uptime-status">
    <span class="uptime-dot online" id="uptimeDot"></span>
    <span class="uptime-label" id="uptimeLabel">SYSTEM ONLINE</span>
  </span>
  <span id="uptimeTime">⏱ 100% UPTIME</span>
</div>

<section class="trust-box">
  <div class="trust-head">
    <span class="mono">STORE TRUST SCORE</span>
    <span class="trust-count mono" id="trustCount"></span>
  </div>
  <div class="trust-bar">
    <div class="trust-fill" id="trustFill"></div>
  </div>
  <div class="trust-labels mono">
    <span class="t-good" id="trustPct">84% TRUSTED</span>
    <span class="t-bad" id="notPct">1% NOT TRUSTED</span>
  </div>
  <div class="trust-actions" id="trustActions">
    <button class="vote-btn good" onclick="castVote('trusted')">✅ Trusted</button>
    <button class="vote-btn bad" onclick="castVote('not')">❌ Not Trusted</button>
  </div>
  <div class="trust-thanks mono" id="trustThanks">✓ THANKS FOR YOUR VOTE</div>
</section>

<div class="filters">
  <button class="active" data-filter="all">ALL</button>
  <button data-filter="free">FREE</button>
  <button data-filter="paid">PAID</button>
</div>

<div class="grid" id="grid"></div>

<footer>DARK STORE <span class="fdot">●</span> SINGLE FILE BUILD <span class="fdot">●</span> HOST ANYWHERE</footer>

<div class="admin-badge" id="adminBadge">🔓 ADMIN MODE — TAP TO EXIT</div>

<!-- Admin Login Modal -->
<div class="overlay" id="loginOverlay">
  <div class="modal login-modal">
    <div class="login-lock">🔐</div>
    <h2>ADMIN ACCESS</h2>
    <div class="login-sub">RESTRICTED AREA — AUTHORIZED ONLY</div>
    <div class="field">
      <label>Password</label>
      <input type="password" id="loginPass" placeholder="• • • • • • • •">
    </div>
    <div class="err" id="loginErr">✕ ACCESS DENIED — WRONG PASSWORD</div>
    <div class="modal-actions">
      <button class="btn-ghost" onclick="closeLogin()">Cancel</button>
      <button class="btn-primary" onclick="tryLogin()">🔓 Unlock</button>
    </div>
  </div>
</div>

<!-- Add Product Modal -->
<div class="overlay" id="addOverlay">
  <div class="modal">
    <h2>ADD ITEM</h2>
    <div class="field">
      <label>Full Name / Title</label>
      <input type="text" id="pName" placeholder="Item name">
    </div>
    <div class="field">
      <label>Description</label>
      <textarea id="pDesc" placeholder="Short description"></textarea>
    </div>
    <div class="field">
      <label>Type</label>
      <div class="radio-row">
        <label><input type="radio" name="ptype" value="free" checked> Free</label>
        <label><input type="radio" name="ptype" value="paid"> Paid</label>
      </div>
    </div>
    <div class="field" id="priceField">
      <label>Price</label>
      <input type="text" id="pPrice" placeholder="e.g. Rs. 500">
    </div>
    <div class="field" id="downloadField">
      <label>Download Link (optional)</label>
      <input type="text" id="pDownloadLink" placeholder="https://... (e.g. Google Drive link)">
      <label style="margin-top:10px;">Or Upload a File to Download (optional)</label>
      <input type="file" id="pDownloadFile">
      <div class="mono" id="downloadFileName" style="font-size:11px; color:var(--muted); margin-top:4px;"></div>
    </div>
    <div class="field">
      <label>Photos (up to 3)</label>
      <input type="file" id="pImages" accept="image/*" multiple>
      <div class="thumbs" id="imgThumbs"></div>
    </div>
    <div class="field">
      <label>Videos (up to 2)</label>
      <input type="file" id="pVideos" accept="video/*" multiple>
      <div class="thumbs" id="vidThumbs"></div>
    </div>
    <div class="field">
      <label class="radio-row" style="text-transform:none;"><input type="checkbox" id="pSoldOut"> Mark as Sold Out</label>
    </div>
    <div class="err" id="addErr"></div>
    <div class="modal-actions">
      <button class="btn-ghost" onclick="closeAdd()">Cancel</button>
      <button class="btn-primary" onclick="saveProduct()">Post Item</button>
    </div>
  </div>
</div>

<!-- Approval Key Modal -->
<div class="overlay" id="approvalOverlay">
  <div class="modal login-modal approval-modal">
    <div class="login-lock approval-lock">🗝️</div>
    <h2>ORDER SUBMITTED</h2>
    <div class="login-sub">AWAITING SELLER APPROVAL</div>
    <p class="approval-item" id="approvalItemName">—</p>
    <div class="key-box">
      <span class="key-text" id="approvalKeyText">— — — —</span>
      <button class="copy-btn" onclick="copyApprovalKey()" id="copyBtn">COPY</button>
    </div>
    <p class="approval-note">Keep this key — it confirms and approves your order once the seller replies on WhatsApp.</p>
    <div class="modal-actions">
      <button class="btn-ghost" onclick="closeApproval()">Close</button>
      <button class="btn-primary" onclick="resendApprovalWhatsApp()">💬 Reopen WhatsApp</button>
    </div>
  </div>
</div>

<!-- Product Detail Modal -->
<div class="overlay" id="detailOverlay">
  <div class="modal modal-wide detail-modal">
    <h2>📦 PRODUCT DETAILS</h2>
    <div class="detail-content" id="detailContent">
      <div class="detail-media" id="detailMedia"></div>
      <div class="detail-title" id="detailTitle">—</div>
      <div class="detail-price" id="detailPrice">—</div>
      <div class="detail-desc" id="detailDesc">—</div>
      <div class="detail-meta" id="detailMeta"></div>
    </div>
    <div class="modal-actions">
      <button class="btn-ghost" onclick="closeDetail()">Close</button>
      <button class="btn-primary" id="detailActionBtn">💬 Buy on WhatsApp</button>
    </div>
  </div>
</div>

<!-- Orders Panel -->
<div class="overlay" id="ordersOverlay">
  <div class="modal modal-wide">
    <h2>ORDER APPROVALS</h2>
    <div class="orders-filters" id="ordersFilters">
      <button class="active" data-ofilter="all">ALL</button>
      <button data-ofilter="pending">PENDING</button>
      <button data-ofilter="approved">APPROVED</button>
      <button data-ofilter="rejected">REJECTED</button>
    </div>
    <div id="ordersList"></div>
    <div class="modal-actions">
      <button class="btn-ghost" onclick="closeOrders()">Close</button>
    </div>
  </div>
</div>

<script>
const API_BASE = '';
const ADMIN_PASSWORD = "darkstore786";
const WHATSAPP_NUMBER = "923303257478";

let isAdmin = false;
let currentFilter = "all";
let currentOrderFilter = "all";
let pendingImages = [];
let pendingVideos = [];
let products = [];
let orders = [];
let votes = {trusted: 84, not: 1};
let detailProductId = null;

async function loadData() {
    try {
        const res = await fetch('/api/data');
        const data = await res.json();
        products = data.products || [];
        orders = data.orders || [];
        votes = data.votes || {trusted: 84, not: 1};
        render();
        renderTrust();
        updateOrdersCount();
        updateUptime();
    } catch(e) {
        console.error('Failed to load data:', e);
        products = [];
        render();
    }
}

function cryptoId(){ return 'p_'+Math.random().toString(36).slice(2,10)+Date.now().toString(36); }

/* ---------- UPTIME ---------- */
function updateUptime() {
    const dot = document.getElementById('uptimeDot');
    const label = document.getElementById('uptimeLabel');
    const time = document.getElementById('uptimeTime');
    dot.className = 'uptime-dot online';
    label.textContent = 'SYSTEM ONLINE';
    time.textContent = '⏱ 100% UPTIME';
}
setInterval(updateUptime, 30000);

/* ---------- PARTICLES ---------- */
(function initParticles(){
  const box = document.getElementById('particles');
  const n = window.innerWidth < 500 ? 14 : 26;
  for(let i=0;i<n;i++){
    const s = document.createElement('span');
    const left = Math.random()*100;
    const dur = 10 + Math.random()*14;
    const delay = Math.random()*14;
    s.style.left = left+'vw';
    s.style.animationDuration = dur+'s';
    s.style.animationDelay = delay+'s';
    box.appendChild(s);
  }
})();

/* ---------- TRUST VOTE ---------- */
function renderTrust(){
  const total = votes.trusted + votes.not;
  const goodPct = total ? Math.round((votes.trusted/total)*100) : 0;
  const badPct = total ? (100 - goodPct) : 0;
  document.getElementById('trustFill').style.width = goodPct+'%';
  document.getElementById('trustPct').textContent = goodPct+'% TRUSTED';
  document.getElementById('notPct').textContent = badPct+'% NOT TRUSTED';
  document.getElementById('trustCount').textContent = total+' VOTES';
}

async function castVote(kind){
  if(localStorage.getItem('ds_voted')) return;
  try {
    const res = await fetch('/api/vote', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({kind})
    });
    if(res.ok) {
      const data = await res.json();
      votes = data.votes;
      localStorage.setItem('ds_voted', kind);
      document.getElementById('trustActions').closest('.trust-box').classList.add('voted');
      renderTrust();
    }
  } catch(e) {
    console.error('Vote failed:', e);
  }
}

if(localStorage.getItem('ds_voted')){
  document.querySelector('.trust-box').classList.add('voted');
}

/* ---------- SOUND ---------- */
let audioCtx;
function clickSound(){
  try{
    audioCtx = audioCtx || new (window.AudioContext||window.webkitAudioContext)();
    const o = audioCtx.createOscillator();
    const g = audioCtx.createGain();
    o.type = 'square';
    o.frequency.setValueAtTime(520, audioCtx.currentTime);
    o.frequency.exponentialRampToValueAtTime(120, audioCtx.currentTime+0.12);
    g.gain.setValueAtTime(0.08, audioCtx.currentTime);
    g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime+0.15);
    o.connect(g); g.connect(audioCtx.destination);
    o.start(); o.stop(audioCtx.currentTime+0.15);
  }catch(e){}
}
document.addEventListener('click', (e)=>{
  if(e.target.closest('button') || e.target.closest('.card')) clickSound();
}, true);

/* ---------- INTRO ---------- */
function playJingle(){
  try{
    audioCtx = audioCtx || new (window.AudioContext||window.webkitAudioContext)();
    const notes = [
      {f:196.00, t:0.00, d:0.18, type:'sawtooth', g:0.05},
      {f:233.08, t:0.18, d:0.18, type:'sawtooth', g:0.05},
      {f:293.66, t:0.36, d:0.18, type:'sawtooth', g:0.06},
      {f:349.23, t:0.54, d:0.30, type:'sawtooth', g:0.07},
      {f:392.00, t:0.84, d:0.55, type:'square',   g:0.06},
    ];
    notes.forEach(n=>{
      const o = audioCtx.createOscillator();
      const g = audioCtx.createGain();
      o.type = n.type;
      o.frequency.setValueAtTime(n.f, audioCtx.currentTime + n.t);
      g.gain.setValueAtTime(0.0001, audioCtx.currentTime + n.t);
      g.gain.exponentialRampToValueAtTime(n.g, audioCtx.currentTime + n.t + 0.03);
      g.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + n.t + n.d);
      o.connect(g); g.connect(audioCtx.destination);
      o.start(audioCtx.currentTime + n.t);
      o.stop(audioCtx.currentTime + n.t + n.d + 0.02);
    });
    const sub = audioCtx.createOscillator();
    const subG = audioCtx.createGain();
    sub.type='sine'; sub.frequency.setValueAtTime(60, audioCtx.currentTime);
    subG.gain.setValueAtTime(0.001, audioCtx.currentTime);
    subG.gain.exponentialRampToValueAtTime(0.18, audioCtx.currentTime+0.05);
    subG.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime+1.3);
    sub.connect(subG); subG.connect(audioCtx.destination);
    sub.start(); sub.stop(audioCtx.currentTime+1.3);
  }catch(e){}
}
function welcomeVoice(){
  try{
    speechSynthesis.cancel();
    const u = new SpeechSynthesisUtterance("Welcome... to Dark Store.");
    u.rate = 0.82; u.pitch = 0.6; u.volume = 1;
    const pick = speechSynthesis.getVoices().find(v=>/male|david|daniel|george/i.test(v.name));
    if(pick) u.voice = pick;
    speechSynthesis.speak(u);
  }catch(e){}
}
function enterSite(){
  if(hasEntered) return;
  hasEntered = true;
  const splash = document.getElementById('splash');
  tryPlaySound();
  splash.classList.add('hide');
  splash.removeEventListener('click', enterSite);
}
function tryPlaySound(){
  try{
    audioCtx = audioCtx || new (window.AudioContext||window.webkitAudioContext)();
    audioCtx.resume().catch(()=>{});
    playJingle();
    setTimeout(welcomeVoice, 950);
  }catch(e){}
}
let hasEntered = false;
window.addEventListener('DOMContentLoaded', ()=>{
  setTimeout(enterSite, 2600);
});
['click','touchstart','keydown','scroll'].forEach(evt=>{
  document.addEventListener(evt, enterSite, {once:true, passive:true});
});
document.getElementById('splash').addEventListener('click', enterSite, {once:true});

/* ---------- RENDER ---------- */
function render(){
  const grid = document.getElementById('grid');
  grid.classList.toggle('admin-on', isAdmin);
  const list = products.filter(p => currentFilter==='all' ? true : p.type===currentFilter);
  if(list.length===0){
    grid.innerHTML = '<div class="empty mono">NO ITEMS YET' + (isAdmin ? ' — TAP "ADD POST" TO CREATE ONE' : '') + '</div>';
    return;
  }
  grid.innerHTML = list.map(p => {
    const soldOut = !!p.soldOut;
    let actionBtn;
    if(soldOut){
      actionBtn = `<button class="buy-btn" disabled>🚫 SOLD OUT</button>`;
    } else if(p.type==='free'){
      actionBtn = `<button class="buy-btn dl-btn" onclick="downloadItem('${p.id}')">⬇ DOWNLOAD</button>`;
    } else {
      actionBtn = `<button class="buy-btn" onclick="buyItem('${p.id}')">💬 BUY ON WHATSAPP</button>`;
    }
    return `
    <div class="card ${soldOut ? 'sold-out':''}" data-id="${p.id}" onclick="showDetail('${p.id}')">
      ${isAdmin ? `<button class="rm-btn" onclick="event.stopPropagation();removeProduct('${p.id}')">✕</button>` : ''}
      ${isAdmin ? `<button class="so-btn" onclick="event.stopPropagation();toggleSoldOut('${p.id}')" title="Toggle sold out">${soldOut ? '✅' : '🚫'}</button>` : ''}
      <div class="stamp ${p.type}">${p.type}</div>
      ${soldOut ? `<div class="sold-badge">SOLD OUT</div>` : ''}
      <div class="media">
        ${p.images && p.images[0] ? `<img src="${p.images[0]}">` : (p.videos && p.videos[0] ? `<video src="${p.videos[0]}" muted></video>` : `<span class="mono" style="color:var(--muted);font-size:11px;">NO PREVIEW</span>`)}
      </div>
      <div class="card-body">
        <h3>${escapeHtml(p.name)}</h3>
        ${p.type==='paid' ? `<div class="price">${escapeHtml(p.price||'Contact for price')}</div><div class="price approval-note">Buy generates an approval key, sent via WhatsApp</div>` : `<div class="price">FREE</div>`}
        <p>${escapeHtml(p.desc||'')}</p>
        ${actionBtn}
        <button class="product-detail-btn" onclick="event.stopPropagation();showDetail('${p.id}')">🔍 View Details</button>
      </div>
    </div>
  `}).join('');
}
function escapeHtml(s){ const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }

/* ---------- PRODUCT DETAIL ---------- */
function showDetail(id){
  const p = products.find(x=>x.id===id);
  if(!p) return;
  detailProductId = id;
  const media = document.getElementById('detailMedia');
  if(p.images && p.images[0]) {
    media.innerHTML = `<img src="${p.images[0]}">`;
  } else if(p.videos && p.videos[0]) {
    media.innerHTML = `<video src="${p.videos[0]}" controls></video>`;
  } else {
    media.innerHTML = `<div style="padding:40px;text-align:center;color:var(--muted);">NO PREVIEW</div>`;
  }
  document.getElementById('detailTitle').textContent = p.name;
  document.getElementById('detailPrice').textContent = p.type==='paid' ? p.price||'Contact for price' : 'FREE';
  document.getElementById('detailDesc').textContent = p.desc||'No description available.';
  document.getElementById('detailMeta').innerHTML = `
    <span>Type: ${p.type.toUpperCase()}</span>
    <span>${p.soldOut ? '🚫 SOLD OUT' : '✅ AVAILABLE'}</span>
    ${p.downloadLink ? `<span>🔗 Download Link Available</span>` : ''}
    ${p.downloadFile ? `<span>📁 File Attachment Available</span>` : ''}
  `;
  const actionBtn = document.getElementById('detailActionBtn');
  if(p.soldOut) {
    actionBtn.textContent = '🚫 SOLD OUT';
    actionBtn.disabled = true;
    actionBtn.style.opacity = '0.5';
    actionBtn.style.cursor = 'not-allowed';
  } else if(p.type==='free') {
    actionBtn.textContent = '⬇ DOWNLOAD';
    actionBtn.disabled = false;
    actionBtn.style.opacity = '1';
    actionBtn.style.cursor = 'pointer';
    actionBtn.onclick = () => { closeDetail(); downloadItem(id); };
  } else {
    actionBtn.textContent = '💬 BUY ON WHATSAPP';
    actionBtn.disabled = false;
    actionBtn.style.opacity = '1';
    actionBtn.style.cursor = 'pointer';
    actionBtn.onclick = () => { closeDetail(); buyItem(id); };
  }
  document.getElementById('detailOverlay').classList.add('show');
}
function closeDetail(){ document.getElementById('detailOverlay').classList.remove('show'); }

function openWhatsApp(text){
  const url = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;
  const a = document.createElement('a');
  a.href = url;
  a.target = '_blank';
  a.rel = 'noopener';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

function generateKey(){
  const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
  let key='';
  for(let i=0;i<8;i++){
    if(i===4) key+='-';
    key += chars[Math.floor(Math.random()*chars.length)];
  }
  return key;
}

let lastApprovalMsg = '';

async function buyItem(id){
  const p = products.find(x=>x.id===id);
  if(!p || p.soldOut) return;
  const key = generateKey();
  
  try {
    const res = await fetch('/api/order', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        productId: p.id,
        productName: p.name,
        price: p.price || '',
        key: key
      })
    });
    if(res.ok) {
      const data = await res.json();
      orders = data.orders || [];
      updateOrdersCount();

      const msg = `Hi, I want to buy: ${p.name} (${p.price||'Contact for price'})\nApproval Key: ${key}\nPlease confirm and approve my order.`;
      lastApprovalMsg = msg;

      document.getElementById('approvalItemName').textContent = p.name;
      document.getElementById('approvalKeyText').textContent = key;
      document.getElementById('approvalOverlay').classList.add('show');

      openWhatsApp(msg);
    }
  } catch(e) {
    alert('Error creating order');
  }
}

function closeApproval(){ document.getElementById('approvalOverlay').classList.remove('show'); }
function resendApprovalWhatsApp(){ if(lastApprovalMsg) openWhatsApp(lastApprovalMsg); }
function copyApprovalKey(){
  const key = document.getElementById('approvalKeyText').textContent;
  const btn = document.getElementById('copyBtn');
  navigator.clipboard.writeText(key).then(()=>{
    btn.textContent = '✓ COPIED';
    setTimeout(()=>{ btn.textContent = 'COPY'; }, 1500);
  }).catch(()=>{});
}

function updateOrdersCount(){
  const pending = orders.filter(o => !o.status || o.status==='pending').length;
  const el = document.getElementById('ordersCount');
  el.textContent = pending>0 ? pending : '';
  el.style.display = pending>0 ? 'inline-block' : 'none';
}

function renderOrders(){
  const list_orders = orders.filter(o => currentOrderFilter==='all' ? true : (o.status||'pending')===currentOrderFilter);
  const list = document.getElementById('ordersList');
  if(list_orders.length===0){
    list.innerHTML = '<div class="orders-empty mono">NO ORDERS IN THIS VIEW</div>';
    return;
  }
  list.innerHTML = list_orders.map(o=>{
    const status = o.status || 'pending';
    const statusClass = status==='approved' ? 'status-approved' : (status==='rejected' ? 'status-rejected' : 'status-pending');
    const time = new Date(o.time).toLocaleString();
    const actions = status==='pending'
      ? `<div class="o-actions">
           <button class="o-approve" onclick="setOrderStatus('${o.id}','approved')">✅ Approve</button>
           <button class="o-reject" onclick="setOrderStatus('${o.id}','rejected')">❌ Reject</button>
         </div>`
      : `<div class="o-actions">
           <button class="o-remove" onclick="removeOrder('${o.id}')">🗑 Remove</button>
         </div>`;
    return `
      <div class="order-card">
        <div class="o-top">
          <span class="o-name">${escapeHtml(o.productName)}${o.price ? ' — '+escapeHtml(o.price) : ''}</span>
          <span class="order-status ${statusClass}">${status.toUpperCase()}</span>
        </div>
        <div class="o-key">KEY: ${o.key}</div>
        <div class="o-meta">${time}</div>
        ${actions}
      </div>
    `;
  }).join('');
}

async function setOrderStatus(id, status){
  try {
    const res = await fetch(`/api/order/${id}`, {
      method: 'PUT',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({status})
    });
    if(res.ok) {
      const data = await res.json();
      orders = data.orders || [];
      updateOrdersCount();
      renderOrders();
    }
  } catch(e) {
    alert('Error updating order');
  }
}

async function removeOrder(id){
  try {
    const res = await fetch(`/api/order/${id}`, { method: 'DELETE' });
    if(res.ok) {
      const data = await res.json();
      orders = data.orders || [];
      updateOrdersCount();
      renderOrders();
    }
  } catch(e) {
    alert('Error removing order');
  }
}

function openOrders(){
  if(!isAdmin) return;
  renderOrders();
  document.getElementById('ordersOverlay').classList.add('show');
}
function closeOrders(){ document.getElementById('ordersOverlay').classList.remove('show'); }

document.getElementById('ordersBtn').addEventListener('click', openOrders);
document.querySelectorAll('#ordersFilters button').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    document.querySelectorAll('#ordersFilters button').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    currentOrderFilter = btn.dataset.ofilter;
    renderOrders();
  });
});

async function downloadItem(id){
  const p = products.find(x=>x.id===id);
  if(!p || p.soldOut) return;
  if(p.downloadFile){
    const a = document.createElement('a');
    a.href = p.downloadFile;
    a.download = p.downloadFileName || (p.name.replace(/\s+/g,'_') + '_file');
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  } else if(p.downloadLink){
    window.open(p.downloadLink, '_blank', 'noopener');
  } else {
    alert('No download file or link has been added for this item yet.');
  }
}

async function toggleSoldOut(id){
  try {
    const res = await fetch(`/api/product/${id}/soldout`, { method: 'PUT' });
    if(res.ok) {
      const data = await res.json();
      products = data.products || [];
      render();
    }
  } catch(e) {
    alert('Error toggling sold out');
  }
}

document.querySelectorAll('.filters button').forEach(btn=>{
  btn.addEventListener('click', ()=>{
    document.querySelectorAll('.filters button').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    render();
  });
});

/* ---------- ADMIN ---------- */
const adminBtn = document.getElementById('adminBtn');
const ordersBtn = document.getElementById('ordersBtn');
const loginOverlay = document.getElementById('loginOverlay');
const adminBadge = document.getElementById('adminBadge');

adminBtn.addEventListener('click', ()=>{
  if(isAdmin){ openAdd(); } else { loginOverlay.classList.add('show'); document.getElementById('loginPass').value=''; document.getElementById('loginErr').style.display='none'; }
});
function closeLogin(){ loginOverlay.classList.remove('show'); }

async function tryLogin(){
  const val = document.getElementById('loginPass').value;
  try {
    const res = await fetch('/api/login', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({password: val})
    });
    if(res.ok) {
      isAdmin = true;
      closeLogin();
      adminBadge.classList.add('show');
      adminBtn.textContent = 'ADD POST';
      ordersBtn.style.display = 'inline-flex';
      render();
      await loadData();
    } else {
      document.getElementById('loginErr').style.display='block';
    }
  } catch(e) {
    document.getElementById('loginErr').style.display='block';
  }
}

adminBadge.addEventListener('click', async ()=>{
  isAdmin = false;
  adminBadge.classList.remove('show');
  adminBtn.textContent = 'ADMIN';
  ordersBtn.style.display = 'none';
  render();
  await fetch('/api/logout', { method: 'POST' });
});

/* ---------- ADD PRODUCT ---------- */
const addOverlay = document.getElementById('addOverlay');
let pendingDownloadFile = null;
let pendingDownloadFileName = '';

function openAdd(){
  pendingImages = []; pendingVideos = []; pendingDownloadFile = null; pendingDownloadFileName = '';
  document.getElementById('pName').value='';
  document.getElementById('pDesc').value='';
  document.getElementById('pPrice').value='';
  document.getElementById('pDownloadLink').value='';
  document.getElementById('pDownloadFile').value='';
  document.getElementById('downloadFileName').textContent='';
  document.getElementById('imgThumbs').innerHTML='';
  document.getElementById('vidThumbs').innerHTML='';
  document.getElementById('pSoldOut').checked = false;
  document.getElementById('addErr').style.display='none';
  document.querySelector('input[name=ptype][value=free]').checked = true;
  document.getElementById('downloadField').style.display='block';
  document.getElementById('priceField').style.display='none';
  addOverlay.classList.add('show');
}
function closeAdd(){ addOverlay.classList.remove('show'); }

document.getElementById('pDownloadFile').addEventListener('change', (e)=>{
  const f = e.target.files[0];
  if(!f) return;
  const reader = new FileReader();
  reader.onload = ()=>{
    pendingDownloadFile = reader.result;
    pendingDownloadFileName = f.name;
    document.getElementById('downloadFileName').textContent = '✓ ' + f.name;
  };
  reader.readAsDataURL(f);
});

document.getElementById('pImages').addEventListener('change', (e)=>{
  const files = Array.from(e.target.files).slice(0,3);
  pendingImages = [];
  const thumbs = document.getElementById('imgThumbs');
  thumbs.innerHTML='';
  files.forEach(f=>{
    const reader = new FileReader();
    reader.onload = ()=>{
      pendingImages.push(reader.result);
      const img = document.createElement('img');
      img.src = reader.result;
      thumbs.appendChild(img);
    };
    reader.readAsDataURL(f);
  });
});
document.getElementById('pVideos').addEventListener('change', (e)=>{
  const files = Array.from(e.target.files).slice(0,2);
  pendingVideos = [];
  const thumbs = document.getElementById('vidThumbs');
  thumbs.innerHTML='';
  files.forEach(f=>{
    const reader = new FileReader();
    reader.onload = ()=>{
      pendingVideos.push(reader.result);
      const v = document.createElement('video');
      v.src = reader.result; v.muted = true;
      thumbs.appendChild(v);
    };
    reader.readAsDataURL(f);
  });
});

async function saveProduct(){
  const name = document.getElementById('pName').value.trim();
  const desc = document.getElementById('pDesc').value.trim();
  const type = document.querySelector('input[name=ptype]:checked').value;
  const price = document.getElementById('pPrice').value.trim();
  const downloadLink = document.getElementById('pDownloadLink').value.trim();
  const soldOut = document.getElementById('pSoldOut').checked;
  const errBox = document.getElementById('addErr');
  if(!name){ errBox.textContent = 'Please enter a name.'; errBox.style.display='block'; return; }
  if(type==='paid' && !price){ errBox.textContent = 'Please enter a price for paid items.'; errBox.style.display='block'; return; }
  
  try {
    const res = await fetch('/api/product', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        name, desc, type, price, soldOut,
        downloadLink: type==='free' ? downloadLink : '',
        downloadFile: type==='free' ? pendingDownloadFile : null,
        downloadFileName: type==='free' ? pendingDownloadFileName : '',
        images: pendingImages.slice(0,3),
        videos: pendingVideos.slice(0,2)
      })
    });
    if(res.ok) {
      const data = await res.json();
      products = data.products || [];
      closeAdd();
      render();
    } else {
      errBox.textContent = 'Error saving product.';
      errBox.style.display='block';
    }
  } catch(e) {
    errBox.textContent = 'Network error.';
    errBox.style.display='block';
  }
}

async function removeProduct(id){
  if(!confirm('Remove this item?')) return;
  try {
    const res = await fetch(`/api/product/${id}`, { method: 'DELETE' });
    if(res.ok) {
      const data = await res.json();
      products = data.products || [];
      render();
    }
  } catch(e) {
    alert('Error removing product');
  }
}

document.querySelectorAll('input[name=ptype]').forEach(r=>{
  r.addEventListener('change', ()=>{
    const isPaid = document.querySelector('input[name=ptype]:checked').value==='paid';
    document.getElementById('priceField').style.display = isPaid ? 'block':'none';
    document.getElementById('downloadField').style.display = isPaid ? 'none':'block';
  });
});

loadData();
updateOrdersCount();
</script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

# API Routes
@app.route('/api/data')
def get_data():
    data = load_data()
    return jsonify({
        'products': data['products'],
        'orders': data['orders'],
        'votes': data['votes']
    })

@app.route('/api/product', methods=['POST'])
def add_product():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    data_obj = load_data()
    new_product = {
        'id': 'p_' + str(uuid.uuid4())[:8],
        'name': data.get('name'),
        'desc': data.get('desc', ''),
        'type': data.get('type', 'free'),
        'price': data.get('price', ''),
        'images': data.get('images', []),
        'videos': data.get('videos', []),
        'soldOut': data.get('soldOut', False),
        'downloadLink': data.get('downloadLink', ''),
        'downloadFile': data.get('downloadFile', ''),
        'downloadFileName': data.get('downloadFileName', '')
    }
    data_obj['products'].insert(0, new_product)
    save_data(data_obj)
    return jsonify({'success': True, 'products': data_obj['products']})

@app.route('/api/product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    data['products'] = [p for p in data['products'] if p['id'] != product_id]
    save_data(data)
    return jsonify({'success': True, 'products': data['products']})

@app.route('/api/product/<product_id>/soldout', methods=['PUT'])
def toggle_soldout(product_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    for p in data['products']:
        if p['id'] == product_id:
            p['soldOut'] = not p.get('soldOut', False)
            save_data(data)
            return jsonify({'success': True, 'products': data['products']})
    return jsonify({'error': 'Product not found'}), 404

@app.route('/api/order', methods=['POST'])
def create_order():
    data = request.json
    data_obj = load_data()
    new_order = {
        'id': 'o_' + str(uuid.uuid4())[:8],
        'productId': data.get('productId'),
        'productName': data.get('productName'),
        'price': data.get('price', ''),
        'key': data.get('key'),
        'time': datetime.now().isoformat(),
        'status': 'pending'
    }
    data_obj['orders'].insert(0, new_order)
    save_data(data_obj)
    return jsonify({'success': True, 'orders': data_obj['orders']})

@app.route('/api/order/<order_id>', methods=['PUT', 'DELETE'])
def update_order(order_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = load_data()
    if request.method == 'PUT':
        status = request.json.get('status')
        for o in data['orders']:
            if o['id'] == order_id:
                o['status'] = status
                save_data(data)
                return jsonify({'success': True, 'orders': data['orders']})
    elif request.method == 'DELETE':
        data['orders'] = [o for o in data['orders'] if o['id'] != order_id]
        save_data(data)
        return jsonify({'success': True, 'orders': data['orders']})
    return jsonify({'error': 'Order not found'}), 404

@app.route('/api/vote', methods=['POST'])
def cast_vote():
    data = load_data()
    kind = request.json.get('kind')
    if kind in data['votes']:
        data['votes'][kind] += 1
        save_data(data)
        return jsonify({'success': True, 'votes': data['votes']})
    return jsonify({'error': 'Invalid vote'}), 400

@app.route('/api/login', methods=['POST'])
def login():
    password = request.json.get('password')
    if password == ADMIN_PASSWORD:
        session['admin'] = True
        return jsonify({'success': True})
    return jsonify({'error': 'Invalid password'}), 401

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('admin', None)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
