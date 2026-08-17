from flask import Flask, render_template_string, request, jsonify, session
import json
import os
import uuid
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'darkstore_secret_key_change_this_786'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

ADMIN_PASSWORD = "darkstore786"
WHATSAPP_NUMBER = "923303257478"
DATA_FILE = 'store_data.json'

default_data = {
    'products': [],
    'orders': [],
    'votes': {"trusted": 0, "not": 0},
    'chat_messages': [],
    'users': {},
    'blocked_ips': []
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

def get_client_ip():
    if request.headers.get('X-Forwarded-For'):
        ip = request.headers.get('X-Forwarded-For').split(',')[0]
    else:
        ip = request.remote_addr
    return ip

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
    --chat-bg:#0e0d11;
    --chat-other:#1a1720;
    --chat-self:#2a2533;
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
    padding:18px 24px;
    display:flex; align-items:center; justify-content:space-between;
    border-bottom:1px solid var(--line);
    position:sticky; top:0; z-index:50;
    background:rgba(10,10,13,0.85); backdrop-filter:blur(14px) saturate(140%);
  }
  .brand{
    font-family:'Bebas Neue', sans-serif;
    font-size:28px; letter-spacing:3px; color:var(--gold-bright);
    display:flex; align-items:center; gap:10px;
  }
  .brand .dot{width:8px;height:8px;border-radius:50%;background:var(--red); box-shadow:0 0 10px var(--red); animation:pulse 2s infinite;}
  @keyframes pulse{0%,100%{opacity:1;}50%{opacity:0.3;}}
  .tagline{font-size:10px; color:var(--muted); letter-spacing:2px; text-transform:uppercase; margin-top:2px;}
  nav{display:flex; align-items:center; gap:8px;}
  nav button{
    background:rgba(255,255,255,0.02); border:1px solid var(--line); color:var(--text);
    padding:8px 16px; font-family:'JetBrains Mono',monospace; font-size:11px;
    letter-spacing:1px; cursor:pointer; border-radius:4px; transition:.25s;
  }
  nav button:hover{border-color:var(--gold); color:var(--gold-bright); box-shadow:0 0 16px rgba(212,160,23,0.25);}
  .count-pill{
    background:var(--red); color:#fff; border-radius:10px; padding:1px 6px; font-size:9px; margin-left:5px;
  }

  .hero{
    padding:30px 20px 20px; text-align:center; border-bottom:1px solid var(--line);
  }
  .hero h1{
    font-family:'Bebas Neue'; font-size:clamp(28px,5vw,50px); letter-spacing:3px;
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

  .trust-box{
    max-width:550px; margin:10px auto; padding:16px 20px; background:var(--surface);
    border:1px solid var(--line); border-radius:8px;
  }
  .trust-head{display:flex; justify-content:space-between; align-items:center; font-size:10px; letter-spacing:2px; color:var(--muted); margin-bottom:8px;}
  .trust-count{color:var(--gold-bright);}
  .trust-bar{
    height:12px; border-radius:6px; overflow:hidden; background:rgba(192,57,43,0.35);
    border:1px solid var(--line); display:flex;
  }
  .trust-fill{
    height:100%; background:linear-gradient(90deg, var(--teal), #2fd6bd);
    width:0%; transition:width .8s ease; box-shadow:0 0 10px rgba(26,156,140,0.6);
  }
  .trust-labels{display:flex; justify-content:space-between; margin-top:6px; font-size:10px; letter-spacing:1px;}
  .t-good{color:var(--teal);}
  .t-bad{color:var(--red);}
  .trust-actions{display:flex; gap:8px; margin-top:12px;}
  .vote-btn{
    flex:1; padding:8px; border-radius:6px; border:1px solid var(--line); background:rgba(255,255,255,0.02);
    color:var(--text); font-size:11px; font-weight:700; letter-spacing:1px; cursor:pointer; transition:.25s;
  }
  .vote-btn:active{transform:scale(0.96);}
  .vote-btn.good:hover{border-color:var(--teal); color:var(--teal); background:rgba(26,156,140,0.08);}
  .vote-btn.bad:hover{border-color:var(--red); color:#ff6b5b; background:rgba(192,57,43,0.08);}
  .trust-thanks{
    display:none; text-align:center; margin-top:10px; color:var(--gold-bright);
    font-size:10px; letter-spacing:2px;
  }
  .voted .trust-actions{display:none;}
  .voted .trust-thanks{display:block;}

  .filters{
    display:flex; gap:8px; justify-content:center; padding:12px 20px; flex-wrap:wrap;
  }
  .filters button{
    background:rgba(255,255,255,0.02); border:1px solid var(--line); color:var(--muted);
    padding:6px 14px; border-radius:18px; font-size:10px; letter-spacing:1.5px; cursor:pointer;
    font-family:'JetBrains Mono',monospace; transition:.25s;
  }
  .filters button:hover{border-color:rgba(212,160,23,0.4); color:var(--text);}
  .filters button.active{background:var(--gold); color:#161116; border-color:var(--gold); font-weight:700;}

  .main-wrapper{
    display:flex; gap:20px; padding:10px 20px 30px; max-width:1400px; margin:0 auto;
  }
  
  .products-section{
    flex:2.5;
  }
  
  .chat-section{
    flex:1;
    min-width:260px;
    max-width:350px;
  }
  .chat-container{
    background:var(--surface); border:1px solid var(--line); border-radius:10px;
    overflow:hidden; position:sticky; top:80px;
  }
  .chat-header{
    padding:10px 14px; background:var(--surface2); border-bottom:1px solid var(--line);
    display:flex; align-items:center; gap:8px;
  }
  .chat-header .online-dot{width:7px;height:7px;border-radius:50%;background:var(--teal);animation:pulse 2s infinite;}
  .chat-header h3{font-family:'Bebas Neue'; letter-spacing:2px; color:var(--gold-bright); font-size:16px;}
  .chat-header .user-count{font-size:9px; color:var(--muted); margin-left:auto; font-family:'JetBrains Mono';}
  
  .chat-messages{
    height:280px; overflow-y:auto; padding:10px 14px; background:var(--chat-bg);
    display:flex; flex-direction:column; gap:8px;
  }
  .chat-messages .empty-chat{
    text-align:center; color:var(--muted); padding:30px 0; font-size:10px;
  }
  .msg{
    max-width:85%; padding:8px 12px; border-radius:10px; animation:msgIn .3s ease;
  }
  .msg.self{background:var(--chat-self); align-self:flex-end; border-bottom-right-radius:3px;}
  .msg.other{background:var(--chat-other); align-self:flex-start; border-bottom-left-radius:3px;}
  .msg .msg-user{display:flex; align-items:center; gap:5px; margin-bottom:2px; font-size:9px; font-weight:700;}
  .msg .msg-user img{width:16px;height:16px;border-radius:50%;border:1px solid var(--line);object-fit:cover;}
  .msg .msg-user .uname{color:var(--gold-bright);}
  .msg .msg-user .utime{color:var(--muted); font-weight:400; font-size:7px; margin-left:auto;}
  .msg .msg-text{font-size:11px; line-height:1.5; word-break:break-word;}
  .msg .msg-text a{color:var(--teal); text-decoration:none;}
  .msg .msg-text a:hover{text-decoration:underline;}
  @keyframes msgIn{from{opacity:0;transform:translateY(6px);}to{opacity:1;transform:translateY(0);}}

  .chat-input{
    padding:10px 14px; background:var(--surface2); border-top:1px solid var(--line);
    display:flex; gap:6px;
  }
  .chat-input input[type="text"]{
    flex:1; background:var(--bg); border:1px solid var(--line); color:var(--text);
    padding:6px 10px; border-radius:4px; font-family:'Inter'; font-size:11px;
  }
  .chat-input input[type="text"]:focus{outline:none; border-color:var(--gold);}
  .chat-input button{
    background:linear-gradient(135deg, var(--gold), #b98410); color:#161116; border:none;
    padding:6px 12px; border-radius:4px; font-weight:700; font-size:10px; cursor:pointer;
    transition:.25s; font-family:'JetBrains Mono';
  }
  .chat-input button:hover{background:linear-gradient(135deg, var(--gold-bright), var(--gold));}
  .chat-input button:disabled{opacity:0.5;cursor:not-allowed;}
  .chat-input .file-upload-btn{
    background:rgba(255,255,255,0.02); border:1px solid var(--line); color:var(--muted);
    padding:6px 10px; border-radius:4px; cursor:pointer; transition:.25s;
    font-size:13px;
  }
  .chat-input .file-upload-btn:hover{border-color:var(--gold); color:var(--text);}

  .grid{
    display:grid; grid-template-columns:repeat(auto-fill,minmax(200px,1fr));
    gap:14px;
  }
  .card{
    background:linear-gradient(180deg, rgba(30,26,34,0.9), rgba(21,19,24,0.95));
    border:1px solid var(--line); border-radius:8px; overflow:hidden;
    position:relative; transition:.3s cubic-bezier(.2,.8,.2,1); display:flex; flex-direction:column;
  }
  .card:hover{transform:translateY(-3px); border-color:rgba(212,160,23,0.4); box-shadow:0 10px 24px rgba(0,0,0,.5);}
  .card .media{width:100%; height:140px; background:#0d0c10; display:flex; align-items:center; justify-content:center; overflow:hidden; position:relative;}
  .card .media::after{content:''; position:absolute; inset:0; background:linear-gradient(180deg, transparent 60%, rgba(0,0,0,0.35));}
  .card .media img, .card .media video{width:100%; height:100%; object-fit:cover; transition:.4s;}
  .card:hover .media img, .card:hover .media video{transform:scale(1.05);}
  
  .type-badge{
    position:absolute; top:8px; right:-20px; transform:rotate(35deg);
    padding:2px 30px; font-family:'JetBrains Mono'; font-size:9px; font-weight:700;
    letter-spacing:2px; z-index:5;
  }
  .type-badge.free{background:var(--teal); color:#04211d;}
  .type-badge.paid{background:var(--gold); color:#161116;}
  
  .sold-badge{
    position:absolute; top:50%; left:50%; transform:translate(-50%,-50%) rotate(-10deg);
    background:rgba(0,0,0,0.85); border:2px solid var(--red); color:#ff6b5b;
    font-family:'Bebas Neue'; font-size:18px; letter-spacing:3px; padding:4px 14px;
    z-index:6; border-radius:4px;
  }
  .card.sold-out .media{filter:grayscale(0.8) brightness(0.5);}
  
  .card-body{padding:12px; display:flex; flex-direction:column; gap:5px; flex:1;}
  .card-body h3{font-size:14px; font-weight:600;}
  .card-body .price{color:var(--gold-bright); font-family:'JetBrains Mono'; font-size:12px;}
  .card-body p{color:var(--muted); font-size:10px; line-height:1.5; flex:1;}
  
  .action-btn{
    margin-top:4px; padding:7px; border:none; border-radius:4px;
    font-weight:700; letter-spacing:1px; font-size:10px; cursor:pointer;
    transition:.25s; font-family:'JetBrains Mono';
  }
  .action-btn:disabled{opacity:0.5;cursor:not-allowed;transform:none !important;}
  .action-btn.buy{background:linear-gradient(135deg, var(--gold), #b98410); color:#161116;}
  .action-btn.buy:hover{background:linear-gradient(135deg, var(--gold-bright), var(--gold)); transform:translateY(-1px);}
  .action-btn.download{background:linear-gradient(135deg, var(--teal), #12796d); color:#fff;}
  .action-btn.download:hover{background:linear-gradient(135deg, #2fd6bd, var(--teal)); transform:translateY(-1px);}
  .action-btn.sold{background:rgba(255,255,255,0.06); color:var(--muted);cursor:not-allowed;}
  
  .admin-actions{
    position:absolute; top:6px; left:6px; display:flex; gap:3px; z-index:6;
  }
  .admin-actions button{
    background:rgba(0,0,0,0.8); color:#fff; border:1px solid var(--line);
    width:22px; height:22px; border-radius:50%; cursor:pointer; font-size:10px;
    transition:.2s; display:none; align-items:center; justify-content:center;
  }
  .admin-actions button:hover{background:rgba(192,57,43,0.8);}
  .admin-actions .edit-btn:hover{background:rgba(212,160,23,0.8);}
  .admin-on .admin-actions button{display:flex;}
  
  .empty{grid-column:1/-1; text-align:center; color:var(--muted); padding:30px 20px; font-size:12px;}

  .overlay{
    position:fixed; inset:0; background:rgba(5,5,7,0.85); backdrop-filter:blur(4px);
    display:none; align-items:center; justify-content:center; z-index:100; padding:20px;
  }
  .overlay.show{display:flex;}
  .modal{
    background:var(--surface2); border:1px solid var(--gold); border-radius:8px; padding:20px;
    width:100%; max-width:420px; max-height:88vh; overflow-y:auto;
  }
  .modal h2{font-family:'Bebas Neue'; letter-spacing:2px; color:var(--gold-bright); font-size:22px; margin-bottom:12px;}

  .login-modal{
    position:relative; text-align:center;
    background:
      linear-gradient(var(--surface2), var(--surface2)) padding-box,
      linear-gradient(130deg, var(--gold), var(--teal), var(--gold)) border-box;
    border:1px solid transparent;
  }
  .login-lock{
    width:45px; height:45px; margin:0 auto 10px; border-radius:50%;
    background:radial-gradient(circle, rgba(212,160,23,0.18), transparent 70%);
    display:flex; align-items:center; justify-content:center; font-size:20px;
    border:1px solid rgba(212,160,23,0.35);
  }
  .login-modal h2{text-align:center; margin-bottom:4px;}
  .login-sub{color:var(--muted); font-size:10px; letter-spacing:2px; margin-bottom:14px; font-family:'JetBrains Mono';}

  .profile-preview{width:60px;height:60px;border-radius:50%;margin:8px auto;border:2px solid var(--gold);overflow:hidden;background:var(--bg);}
  .profile-preview img{width:100%;height:100%;object-fit:cover;}
  .profile-preview .placeholder{width:100%;height:100%;display:flex;align-items:center;justify-content:center;font-size:24px;color:var(--muted);}

  .field{margin-bottom:10px;}
  .field label{display:block; font-size:9px; color:var(--muted); letter-spacing:1px; margin-bottom:3px; text-transform:uppercase;}
  .field input[type=text], .field input[type=password], .field input[type=number], .field textarea, .field select{
    width:100%; background:var(--bg); border:1px solid var(--line); color:var(--text);
    padding:7px 10px; border-radius:4px; font-family:'Inter'; font-size:12px;
  }
  .field select option{background:var(--bg);}
  .field textarea{resize:vertical; min-height:45px;}
  .field input[type=file]{width:100%; font-size:10px; color:var(--muted);}
  .thumbs{display:flex; gap:5px; margin-top:4px; flex-wrap:wrap;}
  .thumbs img, .thumbs video{width:45px; height:45px; object-fit:cover; border-radius:4px; border:1px solid var(--line);}
  .modal-actions{display:flex; gap:8px; margin-top:14px;}
  .modal-actions button{
    flex:1; padding:8px; border:none; border-radius:4px; font-weight:700; letter-spacing:1px;
    font-size:10px; cursor:pointer; transition:.2s;
  }
  .modal-actions button:active{transform:scale(0.96);}
  .btn-primary{background:linear-gradient(135deg, var(--gold), #b98410); color:#161116;}
  .btn-primary:hover{background:linear-gradient(135deg, var(--gold-bright), var(--gold));}
  .btn-danger{background:var(--red); color:#fff;}
  .btn-danger:hover{background:#e0453a;}
  .btn-ghost{background:transparent; border:1px solid var(--line) !important; color:var(--muted);}
  .btn-ghost:hover{color:var(--text); border-color:var(--text) !important;}
  .err{color:var(--red); font-size:10px; margin-top:5px; display:none;}

  .admin-badge{
    position:fixed; bottom:16px; right:16px; background:var(--red); color:#fff; padding:5px 10px;
    border-radius:16px; font-size:9px; font-family:'JetBrains Mono'; letter-spacing:1px; z-index:60;
    display:none; align-items:center; gap:5px; cursor:pointer;
  }
  .admin-badge.show{display:flex;}

  .blocked-overlay{
    position:fixed; inset:0; z-index:999; background:rgba(0,0,0,0.92);
    display:none; flex-direction:column; align-items:center; justify-content:center;
    padding:40px; text-align:center;
  }
  .blocked-overlay.show{display:flex;}
  .blocked-overlay h2{color:var(--red); font-family:'Bebas Neue'; font-size:32px; letter-spacing:3px;}
  .blocked-overlay p{color:var(--muted); max-width:400px; line-height:1.8; font-size:12px;}
  .blocked-overlay .reason{color:var(--gold-bright); margin-top:8px; font-family:'JetBrains Mono'; font-size:10px;}

  .blocked-ips-list{margin-top:12px;}
  .blocked-ip-item{
    display:flex; align-items:center; justify-content:space-between;
    padding:5px 8px; background:var(--bg); border:1px solid var(--line);
    border-radius:4px; margin-bottom:4px;
  }
  .blocked-ip-item .ip{font-family:'JetBrains Mono'; font-size:10px; color:var(--red);}
  .blocked-ip-item .unblock-btn{
    background:rgba(255,255,255,0.05); border:1px solid var(--line); color:var(--muted);
    padding:2px 8px; border-radius:4px; cursor:pointer; font-size:9px; font-family:'JetBrains Mono';
  }
  .blocked-ip-item .unblock-btn:hover{border-color:var(--gold); color:var(--text);}

  .orders-filters{display:flex; gap:5px; margin-bottom:10px; flex-wrap:wrap;}
  .orders-filters button{
    background:rgba(255,255,255,0.02); border:1px solid var(--line); color:var(--muted);
    padding:3px 10px; border-radius:12px; font-size:9px; cursor:pointer;
    font-family:'JetBrains Mono'; transition:.2s;
  }
  .orders-filters button.active{background:var(--gold); color:#161116; border-color:var(--gold); font-weight:700;}
  .order-card{
    border:1px solid var(--line); border-radius:4px; padding:8px 10px; margin-bottom:6px;
    background:var(--bg);
  }
  .order-card .o-top{display:flex; align-items:center; justify-content:space-between; gap:6px; flex-wrap:wrap;}
  .order-card .o-name{font-weight:700; font-size:11px;}
  .order-card .o-key{font-family:'JetBrains Mono'; color:var(--gold-bright); font-size:11px;}
  .order-card .o-meta{font-size:9px; color:var(--muted); margin-top:3px;}
  .order-card .o-actions{display:flex; gap:5px; margin-top:5px; flex-wrap:wrap;}
  .order-card .o-actions button{
    padding:4px 10px; border:none; border-radius:3px; font-size:9px; font-weight:700;
    cursor:pointer; font-family:'JetBrains Mono'; transition:.2s;
  }
  .order-card .o-actions button:active{transform:scale(0.96);}
  .o-approve{background:var(--teal); color:#04211d;}
  .o-approve:hover{background:#2fd6bd;}
  .o-reject{background:var(--red); color:#fff;}
  .o-reject:hover{background:#e0453a;}
  .o-remove{background:rgba(255,255,255,0.06); color:var(--muted);}
  .o-remove:hover{color:var(--text);}
  .order-status{font-size:8px; padding:2px 6px; border-radius:6px; font-family:'JetBrains Mono';}
  .status-pending{background:rgba(212,160,23,0.15); color:var(--gold-bright); border:1px solid rgba(212,160,23,0.35);}
  .status-approved{background:rgba(26,156,140,0.15); color:var(--teal); border:1px solid rgba(26,156,140,0.35);}
  .status-rejected{background:rgba(192,57,43,0.15); color:#ff6b5b; border:1px solid rgba(192,57,43,0.35);}
  .orders-empty{text-align:center; color:var(--muted); padding:20px 10px; font-size:10px;}

  .key-box{
    display:flex; align-items:center; justify-content:space-between; gap:8px;
    background:var(--bg); border:1px solid var(--gold); border-radius:4px; padding:8px 12px;
    margin-bottom:10px;
  }
  .key-text{
    font-family:'JetBrains Mono'; font-size:15px; letter-spacing:3px; color:var(--gold-bright); font-weight:700;
  }
  .copy-btn{
    background:rgba(212,160,23,0.12); border:1px solid var(--gold); color:var(--gold-bright);
    padding:4px 8px; border-radius:4px; font-size:9px; cursor:pointer; font-family:'JetBrains Mono'; font-weight:700;
  }
  .copy-btn:hover{background:var(--gold); color:#161116;}

  footer{
    text-align:center; padding:20px; color:var(--muted); font-size:9px; letter-spacing:2px;
    border-top:1px solid var(--line); font-family:'JetBrains Mono';
  }
  footer .fdot{color:var(--gold); margin:0 4px;}

  @media (max-width:900px){
    .main-wrapper{flex-direction:column; padding:10px;}
    .chat-section{min-width:auto; max-width:none;}
    .chat-container{position:static;}
    .chat-messages{height:200px;}
    .grid{grid-template-columns:repeat(auto-fill,minmax(150px,1fr));}
  }
  @media (max-width:600px){
    header{padding:10px 14px; flex-wrap:wrap; gap:6px;}
    .brand{font-size:20px;}
    nav button{padding:5px 10px; font-size:9px;}
    .hero{padding:20px 12px 14px;}
    .hero h1{font-size:clamp(22px,4vw,30px);}
    .grid{grid-template-columns:repeat(auto-fill,minmax(130px,1fr)); gap:8px;}
    .card .media{height:100px;}
    .card-body{padding:8px;}
    .card-body h3{font-size:12px;}
    .modal{padding:14px; max-width:94vw;}
    .trust-box{padding:12px 14px;}
  }

/* =========================
   DARK STORE — NEW MOBILE-FIRST UI
   ========================= */

html{background:#07080b;-webkit-text-size-adjust:100%;scroll-behavior:smooth}
body{
  background:
    radial-gradient(circle at 50% -10%,rgba(0,255,190,.10),transparent 34%),
    radial-gradient(circle at 100% 35%,rgba(120,60,255,.08),transparent 30%),
    #07080b;
  color:#f5f7f8;
}
body::before{
  opacity:.55;
  background-size:32px 32px;
}
body::after{
  background:
    radial-gradient(ellipse 450px 350px at 10% 5%,rgba(0,255,190,.08),transparent 65%),
    radial-gradient(ellipse 400px 350px at 90% 30%,rgba(124,58,237,.07),transparent 65%),
    radial-gradient(ellipse 400px 300px at 50% 100%,rgba(255,40,90,.05),transparent 65%);
}

/* Glass header */
header{
  padding:10px 14px;
  background:rgba(7,8,11,.78);
  border-bottom:1px solid rgba(255,255,255,.08);
  backdrop-filter:blur(20px);
  -webkit-backdrop-filter:blur(20px);
}
.brand{
  font-size:23px;
  letter-spacing:3px;
  color:#fff;
  text-shadow:0 0 18px rgba(0,255,190,.22);
}
.brand .dot{
  width:7px;height:7px;
  background:#00ffc3;
  box-shadow:0 0 12px #00ffc3;
}
.tagline{color:#6f7a82;font-size:8px;letter-spacing:1.8px}
nav button{
  border:1px solid rgba(255,255,255,.10);
  background:rgba(255,255,255,.035);
  border-radius:9px;
  color:#dce3e6;
  min-height:36px;
}
nav button:hover{
  border-color:#00ffc3;
  color:#00ffc3;
  box-shadow:0 0 18px rgba(0,255,195,.12);
}

/* Hero */
.hero{
  padding:28px 14px 18px;
  border-bottom:0;
}
.hero h1{
  font-size:clamp(34px,11vw,56px);
  letter-spacing:4px;
  background:linear-gradient(100deg,#fff 25%,#00ffc3 48%,#fff 70%);
  background-size:220% auto;
  -webkit-background-clip:text;
  background-clip:text;
  text-shadow:0 0 30px rgba(0,255,195,.10);
}
.hero h1 span{
  background:linear-gradient(100deg,#00ffc3,#8b5cf6,#00ffc3);
  -webkit-background-clip:text;
  background-clip:text;
}

/* Trust card */
.trust-box{
  width:calc(100% - 24px);
  max-width:560px;
  margin:0 auto 12px;
  padding:14px;
  background:linear-gradient(145deg,rgba(20,25,29,.92),rgba(11,14,17,.92));
  border:1px solid rgba(255,255,255,.08);
  border-radius:14px;
  box-shadow:0 12px 35px rgba(0,0,0,.28);
}
.trust-head{font-size:9px}
.trust-count{color:#00ffc3}
.trust-bar{
  height:9px;
  border-radius:10px;
  background:#25131a;
  border:0;
}
.trust-fill{
  background:linear-gradient(90deg,#00c99b,#00ffc3)!important;
  box-shadow:0 0 12px rgba(0,255,195,.35);
}
.trust-actions{gap:7px}
.vote-btn{
  min-height:40px;
  border-radius:9px;
  background:rgba(255,255,255,.035);
  border-color:rgba(255,255,255,.08);
}

/* Mobile filter bar */
.filters{
  position:sticky;
  top:57px;
  z-index:40;
  justify-content:flex-start;
  flex-wrap:nowrap;
  overflow-x:auto;
  scrollbar-width:none;
  padding:9px 12px;
  margin:0;
  background:rgba(7,8,11,.78);
  backdrop-filter:blur(18px);
  -webkit-backdrop-filter:blur(18px);
  border-top:1px solid rgba(255,255,255,.04);
  border-bottom:1px solid rgba(255,255,255,.06);
}
.filters::-webkit-scrollbar{display:none}
.filters button{
  flex:0 0 auto;
  min-height:35px;
  padding:7px 17px;
  border-radius:999px;
  background:rgba(255,255,255,.035);
  border-color:rgba(255,255,255,.08);
  color:#7f8b92;
}
.filters button.active{
  background:#00ffc3;
  border-color:#00ffc3;
  color:#04120f;
  box-shadow:0 0 20px rgba(0,255,195,.16);
}

/* Main mobile layout */
.main-wrapper{
  display:block;
  padding:12px 10px 26px;
  max-width:760px;
}
.products-section{width:100%}
.chat-section{
  width:100%;
  max-width:none;
  margin-top:14px;
}
.grid{
  display:grid;
  grid-template-columns:repeat(2,minmax(0,1fr));
  gap:9px;
}

/* Premium product cards */
.card{
  background:linear-gradient(160deg,rgba(24,28,32,.96),rgba(12,14,17,.98));
  border:1px solid rgba(255,255,255,.075);
  border-radius:13px;
  box-shadow:0 8px 25px rgba(0,0,0,.22);
}
.card:active{transform:scale(.985)}
.card .media{
  height:118px;
  background:#090b0e;
}
.card .media img,.card .media video{object-fit:cover}
.card-body{
  padding:10px;
  gap:6px;
}
.card-body h3{
  font-size:12px;
  line-height:1.25;
  color:#f4f6f7;
}
.card-body .price{
  color:#00ffc3;
  font-size:10px;
}
.card-body p{
  color:#768087;
  font-size:8.5px;
  line-height:1.45;
}
.action-btn{
  min-height:38px;
  border-radius:8px;
  padding:8px 6px;
  font-size:8.5px;
}
.action-btn.buy{
  background:linear-gradient(135deg,#00d9a8,#00ffc3);
  color:#03120e;
}
.action-btn.download{
  background:linear-gradient(135deg,#6d4aff,#8b5cf6);
  color:#fff;
}
.type-badge{
  font-size:7px;
  padding:2px 28px;
}
.type-badge.free{background:#00d9a8;color:#03120e}
.type-badge.paid{background:#8b5cf6;color:#fff}

/* Chat as a clean bottom panel */
.chat-container{
  position:static;
  border-radius:14px;
  border:1px solid rgba(255,255,255,.08);
  background:rgba(15,18,21,.95);
  box-shadow:0 10px 35px rgba(0,0,0,.25);
}
.chat-header{
  padding:12px 13px;
  background:rgba(255,255,255,.035);
  border-bottom:1px solid rgba(255,255,255,.07);
}
.chat-header h3{color:#00ffc3;font-size:15px}
.chat-messages{
  height:220px;
  background:#090b0e;
}
.chat-input{
  padding:9px;
  background:rgba(255,255,255,.025);
}
.chat-input input[type="text"]{
  min-height:40px;
  border-radius:8px;
  background:#07080b;
  border-color:rgba(255,255,255,.09);
}
.chat-input button,.chat-input .file-upload-btn{
  min-height:40px;
  border-radius:8px;
}

/* Full-screen mobile modals, easier to use */
.overlay{
  padding:10px;
  align-items:flex-end;
}
.modal{
  width:100%;
  max-width:560px;
  max-height:92vh;
  padding:16px;
  border-radius:16px 16px 10px 10px;
  background:linear-gradient(160deg,#171b1f,#0e1114);
  border-color:rgba(0,255,195,.45);
  box-shadow:0 -10px 45px rgba(0,0,0,.55);
}
.modal h2{
  color:#00ffc3;
}
.field input[type=text],
.field input[type=password],
.field input[type=number],
.field textarea,
.field select{
  min-height:42px;
  border-radius:8px;
  background:#080a0d;
  border-color:rgba(255,255,255,.09);
}
.field textarea{min-height:70px}
.modal-actions button{
  min-height:42px;
  border-radius:8px;
}
.btn-primary{
  background:linear-gradient(135deg,#00d9a8,#00ffc3);
  color:#03120e;
}
.btn-danger{background:#e83b5d}

/* Orders */
.order-card{
  border-radius:9px;
  background:#090b0e;
  border-color:rgba(255,255,255,.07);
}
.orders-filters{
  overflow-x:auto;
  flex-wrap:nowrap;
}
.orders-filters button{
  flex:0 0 auto;
  min-height:34px;
  border-radius:999px;
}

/* Touch devices */
@media (hover:none) and (pointer:coarse){
  button,input,select,textarea{
    touch-action:manipulation;
  }
  .card:hover{transform:none;box-shadow:0 8px 25px rgba(0,0,0,.22)}
  .card:hover .media img,.card:hover .media video{transform:none}
}

@media (max-width:380px){
  header{padding:8px 10px}
  .brand{font-size:18px}
  nav button{padding:6px 8px;font-size:8px}
  .hero{padding:22px 10px 15px}
  .hero h1{font-size:29px}
  .main-wrapper{padding-left:7px;padding-right:7px}
  .grid{gap:7px}
  .card .media{height:100px}
  .card-body{padding:8px}
  .card-body h3{font-size:10.5px}
  .action-btn{min-height:36px;font-size:8px}
}

@media (min-width:601px) and (max-width:900px){
  .main-wrapper{
    max-width:900px;
    margin:auto;
  }
  .grid{grid-template-columns:repeat(3,minmax(0,1fr))}
}


/* ===== FINAL PHONE DESIGN ===== */
body{
  background:
    radial-gradient(700px 420px at 50% -80px,rgba(0,255,190,.16),transparent 60%),
    radial-gradient(500px 420px at -15% 40%,rgba(0,140,255,.10),transparent 65%),
    radial-gradient(500px 420px at 115% 65%,rgba(130,50,255,.12),transparent 65%),
    linear-gradient(145deg,#05070a 0%,#090d12 45%,#050608 100%);
}
body::before{
  background-image:
    linear-gradient(rgba(0,255,195,.035) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,255,195,.035) 1px,transparent 1px);
  background-size:34px 34px;
  mask-image:radial-gradient(circle at 50% 25%,black,transparent 82%);
}
body::after{
  background:
    radial-gradient(circle at 20% 20%,rgba(0,255,195,.09),transparent 24%),
    radial-gradient(circle at 80% 40%,rgba(115,65,255,.09),transparent 26%);
}
header{
  box-shadow:0 8px 30px rgba(0,0,0,.28);
}
.hero{
  position:relative;
  overflow:hidden;
}
.hero::before{
  content:'';
  position:absolute;
  width:180px;height:180px;
  left:50%;top:-120px;
  transform:translateX(-50%);
  border-radius:50%;
  background:rgba(0,255,195,.12);
  filter:blur(45px);
  pointer-events:none;
}
.hero h1{
  position:relative;
  text-shadow:0 0 35px rgba(0,255,195,.14);
}
.card{
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.035),
    0 12px 30px rgba(0,0,0,.28);
}
.card .media{
  background:
    linear-gradient(135deg,rgba(0,255,195,.04),transparent 50%),
    #080b0f;
}
.chat-container{
  box-shadow:0 15px 40px rgba(0,0,0,.38);
}

/* Compact floating chat trigger */
.mobile-chat-trigger{
  display:none;
}
@media(max-width:900px){
  .chat-section{
    position:fixed;
    right:12px;
    bottom:72px;
    z-index:90;
    width:auto;
    margin:0;
  }
  .chat-container{
    display:none;
    width:min(340px,calc(100vw - 24px));
    max-height:62vh;
    overflow:hidden;
  }
  .chat-section.chat-open .chat-container{
    display:block;
  }
  .mobile-chat-trigger{
    display:flex;
    align-items:center;
    justify-content:center;
    gap:6px;
    width:48px;
    height:48px;
    border:1px solid rgba(0,255,195,.55);
    border-radius:50%;
    background:linear-gradient(145deg,#0e211e,#07100f);
    color:#00ffc3;
    box-shadow:0 0 22px rgba(0,255,195,.18),0 8px 25px rgba(0,0,0,.4);
    cursor:pointer;
    font-size:19px;
  }
  .chat-section.chat-open .mobile-chat-trigger{
    width:100%;
    height:36px;
    border-radius:9px;
    margin-top:6px;
    font-size:12px;
  }
  .chat-section.chat-open .mobile-chat-trigger .chat-label{
    display:inline;
  }
  .chat-label{display:none}
  .chat-section.chat-open{
    left:12px;
    right:12px;
  }
  .chat-section.chat-open .chat-container{
    width:100%;
  }
  .chat-messages{height:190px}
}
@media(min-width:901px){
  .chat-section .mobile-chat-trigger{display:none}
}


/* ===== PRODUCT DETAIL + CINEMATIC SPACE BACKGROUND ===== */
body{
  background:
    radial-gradient(circle at 50% -10%,rgba(0,255,205,.13),transparent 27%),
    radial-gradient(circle at 8% 35%,rgba(48,100,255,.12),transparent 25%),
    radial-gradient(circle at 92% 70%,rgba(150,55,255,.12),transparent 28%),
    linear-gradient(145deg,#030509 0%,#080b12 45%,#030407 100%);
}
body::before{
  background-image:
    radial-gradient(circle,rgba(255,255,255,.65) 0 1px,transparent 1.5px),
    radial-gradient(circle,rgba(0,255,205,.45) 0 1px,transparent 1.5px),
    linear-gradient(rgba(0,255,205,.025) 1px,transparent 1px),
    linear-gradient(90deg,rgba(0,255,205,.025) 1px,transparent 1px);
  background-size:97px 113px,173px 149px,34px 34px,34px 34px;
  background-position:17px 9px,61px 41px,0 0,0 0;
  opacity:.65;
  mask-image:linear-gradient(to bottom,black,transparent 92%);
}
body::after{
  background:
    radial-gradient(circle at 25% 15%,rgba(0,255,205,.10),transparent 22%),
    radial-gradient(circle at 78% 28%,rgba(92,76,255,.09),transparent 24%),
    radial-gradient(circle at 50% 95%,rgba(0,130,255,.08),transparent 25%);
  animation:ambientGlow 12s ease-in-out infinite alternate;
}
@keyframes ambientGlow{
  from{opacity:.55;transform:scale(1)}
  to{opacity:.9;transform:scale(1.08)}
}

.product-detail-overlay{
  z-index:300;
  background:rgba(1,3,7,.76);
  backdrop-filter:blur(14px);
  -webkit-backdrop-filter:blur(14px);
  align-items:center;
}
.product-detail-modal{
  width:min(560px,calc(100vw - 20px));
  max-height:92vh;
  overflow:auto;
  position:relative;
  border:1px solid rgba(0,255,205,.22);
  border-radius:20px;
  background:
    linear-gradient(145deg,rgba(19,25,31,.97),rgba(6,9,13,.98));
  box-shadow:0 25px 90px rgba(0,0,0,.72),0 0 45px rgba(0,255,205,.07);
}
.detail-close{
  position:absolute;
  right:10px;
  top:10px;
  z-index:10;
  width:38px;height:38px;
  border-radius:50%;
  border:1px solid rgba(255,255,255,.16);
  background:rgba(0,0,0,.55);
  color:#fff;
  font-size:25px;
  line-height:1;
}
.detail-cover{
  width:100%;
  height:220px;
  display:flex;
  align-items:center;
  justify-content:center;
  overflow:hidden;
  background:
    radial-gradient(circle,rgba(0,255,205,.12),transparent 50%),
    #06090d;
}
.detail-cover img,.detail-cover video{
  width:100%;height:100%;object-fit:cover;
}
.detail-content{padding:17px}
.detail-topline{
  display:flex;align-items:center;justify-content:space-between;gap:10px;
}
.detail-badge{
  padding:5px 10px;border-radius:999px;
  background:#00e0b0;color:#03120e;
  font:700 9px 'JetBrains Mono';
  letter-spacing:1px;
}
.detail-badge.paid{
  background:#8b5cf6;color:#fff;
}
.detail-price{
  color:#00ffc3;
  font:700 12px 'JetBrains Mono';
}
.detail-content h2{
  margin-top:10px;
  font-size:25px;
  letter-spacing:1px;
  color:#fff;
}
.detail-desc{
  margin-top:8px;
  color:#8e9aa2;
  font-size:11px;
  line-height:1.65;
}
.detail-gallery{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:7px;
  margin-top:14px;
}
.detail-gallery img,.detail-gallery video{
  width:100%;height:82px;object-fit:cover;
  border-radius:9px;
  border:1px solid rgba(255,255,255,.08);
  background:#05070a;
}
.detail-info{
  display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:13px;
}
.detail-info div{
  padding:10px;border-radius:9px;
  background:rgba(255,255,255,.035);
  border:1px solid rgba(255,255,255,.06);
}
.detail-info span{
  display:block;color:#66737b;font:8px 'JetBrains Mono';
}
.detail-info b{
  display:block;margin-top:4px;color:#e9eef0;font-size:10px;
}
.detail-actions{
  display:grid;grid-template-columns:1fr;gap:8px;margin-top:13px;
}
.detail-actions button{
  min-height:44px;border:0;border-radius:10px;
  font:700 10px 'JetBrains Mono';
  cursor:pointer;
}
.detail-actions .detail-buy{
  background:linear-gradient(135deg,#00d9a8,#00ffc3);color:#03120e;
}
.detail-actions .detail-download{
  background:linear-gradient(135deg,#6847ff,#9a73ff);color:#fff;
}
@media(max-width:600px){
  .product-detail-overlay{padding:8px;align-items:flex-end}
  .product-detail-modal{
    width:100%;max-height:91vh;border-radius:18px 18px 10px 10px;
  }
  .detail-cover{height:190px}
  .detail-content{padding:14px}
  .detail-content h2{font-size:21px}
  .detail-gallery img,.detail-gallery video{height:70px}
}


/* ===== FINAL RED / GREEN SPAM-STYLE UI ===== */
:root{
  --neon-green:#00ff9d;
  --neon-red:#ff3158;
  --neon-dark:#06100c;
}
body{
  background:
    radial-gradient(ellipse at 15% 10%,rgba(0,255,130,.13),transparent 30%),
    radial-gradient(ellipse at 85% 25%,rgba(255,30,70,.13),transparent 31%),
    radial-gradient(ellipse at 50% 90%,rgba(0,255,170,.07),transparent 35%),
    linear-gradient(135deg,#020604 0%,#080a0b 48%,#090304 100%);
}
body::before{
  background-image:
    linear-gradient(rgba(0,255,130,.045) 1px,transparent 1px),
    linear-gradient(90deg,rgba(255,35,70,.04) 1px,transparent 1px),
    repeating-linear-gradient(0deg,transparent 0 4px,rgba(255,255,255,.018) 5px);
  background-size:30px 30px,30px 30px,100% 6px;
  opacity:.72;
}
body::after{
  background:
    radial-gradient(circle at 12% 55%,rgba(0,255,130,.12),transparent 20%),
    radial-gradient(circle at 88% 60%,rgba(255,35,70,.12),transparent 22%);
  animation:spamPulse 5s ease-in-out infinite alternate;
}
@keyframes spamPulse{
  from{opacity:.45}
  to{opacity:.9}
}

/* Header */
header{
  border-bottom:1px solid rgba(0,255,130,.16);
  box-shadow:0 8px 35px rgba(0,0,0,.4);
}
.brand{
  text-shadow:0 0 15px rgba(0,255,157,.4),2px 0 rgba(255,49,88,.18);
}
.brand .dot{
  background:var(--neon-green);
  box-shadow:0 0 14px var(--neon-green);
}
nav button{
  border-color:rgba(0,255,157,.14);
}
nav button:hover{
  border-color:var(--neon-green);
  color:var(--neon-green);
}

/* Hero */
.hero h1{
  background:linear-gradient(90deg,#fff 0%,var(--neon-green) 35%,#fff 55%,var(--neon-red) 82%,#fff 100%);
  background-size:250% auto;
  -webkit-background-clip:text;
  background-clip:text;
  animation:titleFlow 7s linear infinite;
}
@keyframes titleFlow{
  to{background-position:250% center}
}
.hero p{
  color:#87958f;
}

/* Filter pills */
.filters{
  border-top:1px solid rgba(0,255,157,.07);
  border-bottom:1px solid rgba(255,49,88,.09);
}
.filters button{
  border-color:rgba(255,255,255,.08);
}
.filters button.active{
  background:linear-gradient(135deg,var(--neon-green),#00c879);
  color:#02120b;
  border-color:var(--neon-green);
  box-shadow:0 0 20px rgba(0,255,157,.2);
}

/* Cards */
.card{
  background:
    linear-gradient(145deg,rgba(9,20,15,.96),rgba(17,8,11,.96));
  border-color:rgba(0,255,157,.10);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,.025),
    0 10px 30px rgba(0,0,0,.38);
}
.card:nth-child(3n+2){
  border-color:rgba(255,49,88,.11);
}
.card:hover{
  border-color:rgba(0,255,157,.4);
  box-shadow:0 0 24px rgba(0,255,157,.08),0 15px 35px rgba(0,0,0,.5);
}
.card .media{
  background:
    linear-gradient(135deg,rgba(0,255,157,.06),rgba(255,49,88,.045)),
    #050807;
}
.card-body .price{
  color:var(--neon-green);
}
.action-btn.buy{
  background:linear-gradient(135deg,#00d993,var(--neon-green));
  box-shadow:0 0 12px rgba(0,255,157,.12);
}
.action-btn.download{
  background:linear-gradient(135deg,#ff294f,#c91436);
  box-shadow:0 0 12px rgba(255,49,88,.12);
}

/* ===== CHAT: FULL-SCREEN MOBILE CHAT ===== */
@media(max-width:900px){
  .chat-section{
    position:fixed;
    right:12px;
    bottom:92px;
    left:auto;
    width:auto;
    margin:0;
    z-index:500;
  }
  .mobile-chat-trigger{
    width:48px;
    height:48px;
    border:1px solid rgba(0,255,157,.65);
    background:
      radial-gradient(circle at 35% 30%,rgba(0,255,157,.2),transparent 45%),
      #06120d;
    color:var(--neon-green);
    box-shadow:0 0 20px rgba(0,255,157,.18),0 8px 24px rgba(0,0,0,.45);
    font-size:20px;
  }

  /* Open = entire phone viewport */
  .chat-section.chat-open{
    inset:0;
    width:100vw;
    height:100dvh;
    background:#030606;
    z-index:9999;
  }
  .chat-section.chat-open .chat-container{
    display:flex;
    flex-direction:column;
    position:absolute;
    inset:0;
    width:100%;
    height:100dvh;
    max-height:none;
    border:0;
    border-radius:0;
    box-shadow:none;
    background:#050807;
  }

  /* Dedicated close bar */
  .chat-section.chat-open .mobile-chat-trigger{
    position:absolute;
    top:10px;
    right:10px;
    z-index:20;
    width:40px;
    height:40px;
    border-radius:10px;
    border:1px solid rgba(255,49,88,.55);
    background:rgba(45,5,12,.92);
    color:#ff5574;
    font-size:0;
  }
  .chat-section.chat-open .mobile-chat-trigger::after{
    content:'✕';
    font-size:20px;
  }

  .chat-section.chat-open .chat-header{
    min-height:62px;
    padding:13px 58px 13px 15px;
    border-bottom:1px solid rgba(0,255,157,.16);
    background:
      linear-gradient(90deg,rgba(0,255,157,.08),rgba(255,49,88,.06)),
      #070b09;
  }
  .chat-section.chat-open .chat-header h3{
    color:var(--neon-green);
    font-size:16px;
  }
  .chat-section.chat-open .chat-messages{
    flex:1;
    height:auto;
    min-height:0;
    overflow-y:auto;
    padding:13px;
    background:
      linear-gradient(rgba(0,255,157,.018) 1px,transparent 1px),
      #030605;
    background-size:100% 24px;
  }
  .chat-section.chat-open .chat-input{
    flex-shrink:0;
    padding:10px;
    padding-bottom:max(10px,env(safe-area-inset-bottom));
    border-top:1px solid rgba(255,49,88,.15);
    background:#080b09;
  }
}

/* Desktop remains normal */
@media(min-width:901px){
  .mobile-chat-trigger{display:none!important}
}

/* Detail modal red/green premium treatment */
.product-detail-modal{
  background:
    linear-gradient(145deg,rgba(7,20,14,.98),rgba(19,6,10,.98));
  border-color:rgba(0,255,157,.25);
}
.detail-cover{
  background:
    radial-gradient(circle,rgba(0,255,157,.12),transparent 45%),
    radial-gradient(circle at 80%,rgba(255,49,88,.10),transparent 35%),
    #050807;
}
.detail-buy{
  background:linear-gradient(135deg,#00d993,#00ff9d)!important;
}
.detail-download{
  background:linear-gradient(135deg,#ff3158,#c91436)!important;
}


/* ===== ADMIN PANEL MENU ===== */
.admin-menu-modal{position:relative;max-width:520px;border-color:rgba(0,255,157,.28);background:radial-gradient(circle at 15% 0%,rgba(0,255,157,.10),transparent 30%),radial-gradient(circle at 90% 100%,rgba(255,49,88,.09),transparent 30%),linear-gradient(145deg,#0b1511,#12080c)}
.admin-menu-close{position:absolute;top:10px;right:10px;width:34px;height:34px;border:1px solid rgba(255,49,88,.35);border-radius:9px;background:rgba(255,49,88,.07);color:#ff5471;cursor:pointer}
.admin-menu-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:9px;margin-top:16px}
.admin-menu-item{min-height:120px;padding:13px 8px;border-radius:12px;border:1px solid rgba(255,255,255,.08);background:rgba(255,255,255,.025);color:#fff;cursor:pointer;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px}
.admin-menu-item span{font-size:25px}.admin-menu-item b{font:700 10px 'JetBrains Mono'}.admin-menu-item small{font:8px 'JetBrains Mono';color:#74817d;text-align:center}
.admin-menu-item.add{border-color:rgba(0,255,157,.25)}.admin-menu-item.add b{color:#00ff9d}
.admin-menu-item.orders{border-color:rgba(139,92,246,.25)}.admin-menu-item.orders b{color:#ae8cff}
.admin-menu-item.ip{border-color:rgba(255,49,88,.25)}.admin-menu-item.ip b{color:#ff5574}
.admin-menu-item:active{transform:scale(.97)}
.admin-menu-note{margin-top:12px;padding:9px;border-radius:8px;background:rgba(0,255,157,.035);border:1px solid rgba(0,255,157,.08);color:#68766f;font:8px/1.5 'JetBrains Mono';text-align:center}
@media(max-width:600px){
 .admin-menu-modal{width:calc(100vw - 16px)}
 .admin-menu-grid{grid-template-columns:1fr;gap:7px}
 .admin-menu-item{min-height:62px;display:grid;grid-template-columns:38px 1fr;grid-template-rows:auto auto;text-align:left;padding:9px 12px}
 .admin-menu-item span{grid-row:1/3;font-size:23px;text-align:center}
 .admin-menu-item b{align-self:end}.admin-menu-item small{align-self:start;text-align:left}
}

</style>
</head>
<body>

<div class="particles" id="particles"></div>

<div class="blocked-overlay" id="blockedOverlay">
  <div class="lock-icon">🚫</div>
  <h2>ACCESS DENIED</h2>
  <p>Your IP address has been blocked from accessing this store.</p>
  <p class="reason" id="blockReason">Contact administrator for more information.</p>
</div>

<header>
  <div>
    <div class="brand"><span class="dot"></span>DARK STORE</div>
    <div class="tagline">buy · download · chat</div>
  </div>
  <nav>
    <button id="ordersBtn" style="display:none;">ORDERS<span class="count-pill" id="ordersCount"></span></button>
    <button id="adminBtn">ADMIN</button>
  </nav>
</header>

<section class="hero">
  <h1>DARK <span>STORE</span></h1>
</section>

<section class="trust-box">
  <div class="trust-head">
    <span class="mono">STORE TRUST</span>
    <span class="trust-count mono" id="trustCount"></span>
  </div>
  <div class="trust-bar">
    <div class="trust-fill" id="trustFill"></div>
  </div>
  <div class="trust-labels mono">
    <span class="t-good" id="trustPct">0% TRUSTED</span>
    <span class="t-bad" id="notPct">0% NOT</span>
  </div>
  <div class="trust-actions" id="trustActions">
    <button class="vote-btn good" onclick="castVote('trusted')">✅ Trusted</button>
    <button class="vote-btn bad" onclick="castVote('not')">❌ Not</button>
  </div>
  <div class="trust-thanks mono" id="trustThanks">✓ THANKS FOR YOUR VOTE</div>
</section>

<div class="filters">
  <button class="active" data-filter="all">ALL</button>
  <button data-filter="free">FREE</button>
  <button data-filter="paid">PAID</button>
</div>

<div class="main-wrapper">
  <div class="products-section">
    <div class="grid" id="grid"></div>
  </div>
  
  <div class="chat-section">
     <button class="mobile-chat-trigger" type="button" onclick="this.parentElement.classList.toggle('chat-open')" aria-label="Open chat">💬<span class="chat-label"> CHAT</span></button>
    <div class="chat-container">
      <div class="chat-header">
        <div class="online-dot"></div>
        <h3>💬 CHAT</h3>
        <span class="user-count" id="userCount">0 online</span>
      </div>
      <div class="chat-messages" id="chatMessages">
        <div class="empty-chat mono">No messages yet.</div>
      </div>
      <div class="chat-input">
        <input type="text" id="chatInput" placeholder="Message..." maxlength="500">
        <button class="file-upload-btn" onclick="document.getElementById('chatFileInput').click()">📎</button>
        <input type="file" id="chatFileInput" accept="image/*" style="display:none;">
        <button id="sendChatBtn" onclick="sendChatMessage()">SEND</button>
      </div>
    </div>
  </div>
</div>

<footer>DARK STORE <span class="fdot">●</span> BUILT WITH <span class="fdot">●</span> FLASK</footer>

<div class="admin-badge" id="adminBadge">🔓 ADMIN</div>


<!-- Product Details / Preview Modal -->
<div class="overlay product-detail-overlay" id="productDetailOverlay" onclick="if(event.target===this)closeProductDetails()">
  <div class="product-detail-modal">
    <button class="detail-close" onclick="closeProductDetails()" aria-label="Close">×</button>
    <div class="detail-cover" id="detailCover"></div>
    <div class="detail-content">
      <div class="detail-topline">
        <span class="detail-badge" id="detailType">FREE</span>
        <span class="detail-price" id="detailPrice"></span>
      </div>
      <h2 id="detailName">ITEM</h2>
      <p class="detail-desc" id="detailDesc"></p>
      <div class="detail-gallery" id="detailGallery"></div>
      <div class="detail-info">
        <div><span>TYPE</span><b id="detailType2">FREE</b></div>
        <div><span>STATUS</span><b id="detailStatus">AVAILABLE</b></div>
      </div>
      <div class="detail-actions" id="detailActions"></div>
    </div>
  </div>
</div>


<!-- User Setup Modal -->
<div class="overlay" id="userSetupOverlay">
  <div class="modal user-setup-modal login-modal">
    <div class="login-lock">👤</div>
    <h2>SETUP PROFILE</h2>
    <div class="login-sub">ENTER YOUR NAME & PROFILE PIC</div>
    <div class="profile-preview" id="profilePreview">
      <div class="placeholder">👤</div>
    </div>
    <div class="field">
      <label>Your Name</label>
      <input type="text" id="userNameInput" placeholder="Enter your name..." maxlength="30">
    </div>
    <div class="field">
      <label>Profile Picture</label>
      <input type="file" id="userProfilePic" accept="image/*">
    </div>
    <div class="err" id="userSetupErr"></div>
    <div class="modal-actions">
      <button class="btn-primary" onclick="setupUser()">Join Chat</button>
    </div>
  </div>
</div>

<!-- Admin Login Modal -->
<div class="overlay" id="loginOverlay">
  <div class="modal login-modal">
    <div class="login-lock">🔐</div>
    <h2>ADMIN ACCESS</h2>
    <div class="login-sub">RESTRICTED AREA</div>
    <div class="field">
      <label>Password</label>
      <input type="password" id="loginPass" placeholder="• • • • • • • •">
    </div>
    <div class="err" id="loginErr">✕ WRONG PASSWORD</div>
    <div class="modal-actions">
      <button class="btn-ghost" onclick="closeLogin()">Cancel</button>
      <button class="btn-primary" onclick="tryLogin()">🔓 Unlock</button>
    </div>
  </div>
</div>

<!-- Admin Menu -->
<div class="overlay" id="adminMenuOverlay" onclick="if(event.target===this)closeAdminMenu()">
  <div class="modal admin-menu-modal">
    <button class="admin-menu-close" onclick="closeAdminMenu()">✕</button>
    <div class="login-lock">⚡</div>
    <h2>ADMIN PANEL</h2>
    <div class="login-sub">MANAGE YOUR STORE</div>
    <div class="admin-menu-grid">
      <button class="admin-menu-item add" onclick="adminAddPost()">
        <span>➕</span><b>ADD POST</b><small>New product / item</small>
      </button>
      <button class="admin-menu-item orders" onclick="adminOpenOrders()">
        <span>📦</span><b>ORDERS</b><small>Approve / reject orders</small>
      </button>
      <button class="admin-menu-item ip" onclick="adminOpenIPBlock()">
        <span>🔒</span><b>IP BLOCK</b><small>Manage blocked users</small>
      </button>
    </div>
    <div class="admin-menu-note">Add a post and it will appear in the FREE / PAID store automatically.</div>
  </div>
</div>

<!-- Add/Edit Product Modal -->
<div class="overlay" id="addOverlay">
  <div class="modal">
    <h2 id="productModalTitle">ADD ITEM</h2>
    <div class="field">
      <label>Name / Title</label>
      <input type="text" id="pName" placeholder="Item name">
    </div>
    <div class="field">
      <label>Description</label>
      <textarea id="pDesc" placeholder="Short description"></textarea>
    </div>
    <div class="field">
      <label>Type</label>
      <select id="pType">
        <option value="free">Free</option>
        <option value="paid">Paid</option>
      </select>
    </div>
    <div class="field" id="priceField">
      <label>Price</label>
      <input type="text" id="pPrice" placeholder="e.g. Rs. 500">
    </div>
    <div class="field" id="downloadField">
      <label>Download Link (for free items)</label>
      <input type="text" id="pDownloadLink" placeholder="https://...">
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
      <label><input type="checkbox" id="pSoldOut"> Mark as Sold Out</label>
    </div>
    <div class="err" id="addErr"></div>
    <div class="modal-actions">
      <button class="btn-ghost" onclick="closeAdd()">Cancel</button>
      <button class="btn-primary" onclick="saveProduct()" id="saveProductBtn">Post Item</button>
    </div>
  </div>
</div>

<!-- Approval Key Modal -->
<div class="overlay" id="approvalOverlay">
  <div class="modal login-modal approval-modal">
    <div class="login-lock approval-lock">🗝️</div>
    <h2>ORDER SUBMITTED</h2>
    <div class="login-sub">AWAITING SELLER APPROVAL</div>
    <p class="approval-item" id="approvalItemName" style="color:var(--text);font-size:12px;margin-bottom:10px;">—</p>
    <div class="key-box">
      <span class="key-text" id="approvalKeyText">— — — —</span>
      <button class="copy-btn" onclick="copyApprovalKey()" id="copyBtn">COPY</button>
    </div>
    <p class="approval-note" style="color:var(--muted);font-size:10px;line-height:1.5;margin-bottom:6px;">Keep this key — it confirms your order. Admin will approve it.</p>
    <div class="modal-actions">
      <button class="btn-ghost" onclick="closeApproval()">Close</button>
      <button class="btn-primary" onclick="resendApprovalWhatsApp()">💬 WhatsApp</button>
    </div>
  </div>
</div>

<!-- Orders Panel -->
<div class="overlay" id="ordersOverlay">
  <div class="modal modal-wide" style="max-width:550px;">
    <h2>📦 ORDERS & APPROVALS</h2>
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

<!-- Admin IP Block Panel -->
<div class="overlay" id="ipBlockOverlay">
  <div class="modal modal-wide" style="max-width:450px;">
    <h2>🔒 IP BLOCK</h2>
    <div class="login-sub">Block or unblock users by IP</div>
    <div class="field">
      <label>IP to Block</label>
      <input type="text" id="blockIpInput" placeholder="e.g. 192.168.1.1">
    </div>
    <div class="field">
      <label>Reason</label>
      <input type="text" id="blockReasonInput" placeholder="Why block this IP?">
    </div>
    <div class="modal-actions" style="margin-top:0;">
      <button class="btn-primary" onclick="blockIP()">🚫 Block IP</button>
    </div>
    <div class="err" id="ipBlockErr"></div>
    <div class="blocked-ips-list" id="blockedIpsList"></div>
    <div class="modal-actions">
      <button class="btn-ghost" onclick="closeIPBlock()">Close</button>
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
let editingProductId = null;
let pendingImages = [];
let pendingVideos = [];
let products = [];
let orders = [];
let votes = {trusted: 0, not: 0};
let chatMessages = [];
let users = {};
let currentUser = null;
let chatPollInterval = null;
let blockedIPs = [];
let lastApprovalMsg = '';

async function checkBlocked() {
    try {
        const res = await fetch('/api/check_block');
        const data = await res.json();
        if (data.blocked) {
            document.getElementById('blockedOverlay').classList.add('show');
            document.getElementById('blockReason').textContent = 'Reason: ' + (data.reason || 'No reason provided');
            return true;
        }
        return false;
    } catch(e) { return false; }
}

function checkUserSetup() {
    const saved = localStorage.getItem('ds_user');
    if (saved) {
        try {
            currentUser = JSON.parse(saved);
            document.getElementById('userSetupOverlay').classList.remove('show');
            document.getElementById('chatInput').disabled = false;
            document.getElementById('sendChatBtn').disabled = false;
            loadChat();
            return true;
        } catch(e) {}
    }
    document.getElementById('userSetupOverlay').classList.add('show');
    document.getElementById('chatInput').disabled = true;
    document.getElementById('sendChatBtn').disabled = true;
    return false;
}

document.getElementById('userProfilePic').addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(ev) {
            document.getElementById('profilePreview').innerHTML = `<img src="${ev.target.result}">`;
        };
        reader.readAsDataURL(file);
    }
});

function setupUser() {
    const name = document.getElementById('userNameInput').value.trim();
    const errBox = document.getElementById('userSetupErr');
    if (!name) {
        errBox.textContent = 'Please enter your name.';
        errBox.style.display = 'block';
        return;
    }
    errBox.style.display = 'none';
    
    let profilePic = '';
    const fileInput = document.getElementById('userProfilePic');
    if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = function(e) {
            profilePic = e.target.result;
            completeUserSetup(name, profilePic);
        };
        reader.readAsDataURL(fileInput.files[0]);
    } else {
        completeUserSetup(name, '');
    }
}

function completeUserSetup(name, profilePic) {
    const userId = 'u_' + Math.random().toString(36).slice(2,10);
    currentUser = {
        id: userId,
        name: name,
        profilePic: profilePic || '',
        joined: new Date().toISOString()
    };
    localStorage.setItem('ds_user', JSON.stringify(currentUser));
    
    fetch('/api/user/setup', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(currentUser)
    }).then(() => {
        document.getElementById('userSetupOverlay').classList.remove('show');
        document.getElementById('chatInput').disabled = false;
        document.getElementById('sendChatBtn').disabled = false;
        loadChat();
    });
}

async function loadChat() {
    try {
        const res = await fetch('/api/chat');
        const data = await res.json();
        chatMessages = data.messages || [];
        users = data.users || {};
        renderChat();
        updateUserCount();
    } catch(e) {}
}

function renderChat() {
    const container = document.getElementById('chatMessages');
    if (chatMessages.length === 0) {
        container.innerHTML = '<div class="empty-chat mono">No messages yet.</div>';
        return;
    }
    container.innerHTML = chatMessages.map(msg => {
        const user = users[msg.userId] || {name: 'Unknown', profilePic: ''};
        const isSelf = currentUser && msg.userId === currentUser.id;
        const time = new Date(msg.time).toLocaleTimeString([], {hour:'2-digit', minute:'2-digit'});
        const picHtml = user.profilePic ? `<img src="${user.profilePic}">` : `<span>👤</span>`;
        
        let textHtml = msg.text;
        textHtml = textHtml.replace(/(https?:\/\/[^\s]+)/g, '<a href="$1" target="_blank">$1</a>');
        if (msg.image) {
            textHtml += `<br><img src="${msg.image}" style="max-width:100%;max-height:120px;border-radius:4px;margin-top:4px;">`;
        }
        
        return `
            <div class="msg ${isSelf ? 'self' : 'other'}">
                <div class="msg-user">
                    ${picHtml}
                    <span class="uname">${escapeHtml(user.name)}</span>
                    <span class="utime">${time}</span>
                </div>
                <div class="msg-text">${textHtml}</div>
            </div>
        `;
    }).join('');
    container.scrollTop = container.scrollHeight;
}

function updateUserCount() {
    document.getElementById('userCount').textContent = Object.keys(users).length + ' online';
}

async function sendChatMessage() {
    if (!currentUser) {
        checkUserSetup();
        return;
    }
    const input = document.getElementById('chatInput');
    const text = input.value.trim();
    if (!text) return;
    
    input.value = '';
    document.getElementById('sendChatBtn').disabled = true;
    
    try {
        const res = await fetch('/api/chat/message', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                userId: currentUser.id,
                text: text
            })
        });
        if (res.ok) {
            const data = await res.json();
            chatMessages = data.messages || [];
            users = data.users || {};
            renderChat();
            updateUserCount();
        }
    } catch(e) {}
    document.getElementById('sendChatBtn').disabled = false;
}

document.getElementById('chatInput').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') sendChatMessage();
});

document.getElementById('chatFileInput').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file || !currentUser) return;
    
    const reader = new FileReader();
    reader.onload = async function(ev) {
        try {
            await fetch('/api/chat/message', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    userId: currentUser.id,
                    text: '📷 sent an image',
                    image: ev.target.result
                })
            });
            loadChat();
        } catch(e) {}
    };
    reader.readAsDataURL(file);
    this.value = '';
});

function startChatPolling() {
    if (chatPollInterval) clearInterval(chatPollInterval);
    chatPollInterval = setInterval(async () => {
        if (document.hidden) return;
        try {
            const res = await fetch('/api/chat');
            const data = await res.json();
            if (data.messages && data.messages.length !== chatMessages.length) {
                chatMessages = data.messages;
                users = data.users || {};
                renderChat();
                updateUserCount();
            }
        } catch(e) {}
    }, 3000);
}

function escapeHtml(s){ const d=document.createElement('div'); d.textContent=s||''; return d.innerHTML; }

// ---------- IP BLOCK ----------
async function loadBlockedIPs() {
    try {
        const res = await fetch('/api/blocked_ips');
        const data = await res.json();
        blockedIPs = data.ips || [];
        renderBlockedIPs();
    } catch(e) {}
}

function renderBlockedIPs() {
    const container = document.getElementById('blockedIpsList');
    if (blockedIPs.length === 0) {
        container.innerHTML = '<div class="orders-empty mono">No IPs blocked.</div>';
        return;
    }
    container.innerHTML = blockedIPs.map(item => `
        <div class="blocked-ip-item">
            <span class="ip">${escapeHtml(item.ip)}</span>
            <span style="font-size:9px;color:var(--muted);">${item.reason ? escapeHtml(item.reason) : 'No reason'}</span>
            <button class="unblock-btn" onclick="unblockIP('${escapeHtml(item.ip)}')">Unblock</button>
        </div>
    `).join('');
}

async function blockIP() {
    const ip = document.getElementById('blockIpInput').value.trim();
    const reason = document.getElementById('blockReasonInput').value.trim();
    const errBox = document.getElementById('ipBlockErr');
    if (!ip) {
        errBox.textContent = 'Enter an IP address.';
        errBox.style.display = 'block';
        return;
    }
    errBox.style.display = 'none';
    try {
        const res = await fetch('/api/block_ip', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ip, reason})
        });
        if (res.ok) {
            document.getElementById('blockIpInput').value = '';
            document.getElementById('blockReasonInput').value = '';
            loadBlockedIPs();
        } else {
            const data = await res.json();
            errBox.textContent = data.error || 'Failed to block.';
            errBox.style.display = 'block';
        }
    } catch(e) {
        errBox.textContent = 'Network error.';
        errBox.style.display = 'block';
    }
}

async function unblockIP(ip) {
    try {
        await fetch('/api/unblock_ip', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ip})
        });
        loadBlockedIPs();
    } catch(e) {}
}

function openIPBlock() {
    if (!isAdmin) return;
    loadBlockedIPs();
    document.getElementById('ipBlockOverlay').classList.add('show');
}

function closeIPBlock() {
    document.getElementById('ipBlockOverlay').classList.remove('show');
}

// ---------- LOAD DATA ----------
async function loadData() {
    try {
        const res = await fetch('/api/data');
        const data = await res.json();
        products = data.products || [];
        orders = data.orders || [];
        votes = data.votes || {trusted: 0, not: 0};
        render();
        renderTrust();
        updateOrdersCount();
    } catch(e) {
        products = [];
        render();
    }
}

// ---------- PARTICLES ----------
(function initParticles(){
  const box = document.getElementById('particles');
  const n = window.innerWidth < 500 ? 12 : 20;
  for(let i=0;i<n;i++){
    const s = document.createElement('span');
    s.style.left = Math.random()*100 + 'vw';
    s.style.animationDuration = (10 + Math.random()*12) + 's';
    s.style.animationDelay = (Math.random()*12) + 's';
    box.appendChild(s);
  }
})();

// ---------- TRUST VOTE ----------
function renderTrust(){
  const total = votes.trusted + votes.not;
  const goodPct = total ? Math.round((votes.trusted/total)*100) : 0;
  document.getElementById('trustFill').style.width = goodPct + '%';
  document.getElementById('trustPct').textContent = goodPct + '% TRUSTED';
  document.getElementById('notPct').textContent = (100 - goodPct) + '% NOT';
  document.getElementById('trustCount').textContent = total + ' VOTES';
  
  const fill = document.getElementById('trustFill');
  if (goodPct >= 85) {
    fill.style.background = 'linear-gradient(90deg, var(--teal), #2fd6bd)';
  } else if (goodPct >= 60) {
    fill.style.background = 'linear-gradient(90deg, var(--gold), var(--gold-bright))';
  } else {
    fill.style.background = 'linear-gradient(90deg, var(--red), #e0453a)';
  }
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
  } catch(e) {}
}

if(localStorage.getItem('ds_voted')){
  document.querySelector('.trust-box').classList.add('voted');
}

// ---------- ORDERS ----------
function updateOrdersCount() {
    const pending = orders.filter(o => !o.status || o.status === 'pending').length;
    const el = document.getElementById('ordersCount');
    el.textContent = pending > 0 ? pending : '';
    el.style.display = pending > 0 ? 'inline-block' : 'none';
}

function renderOrders() {
    const list_orders = orders.filter(o => {
        if (currentOrderFilter === 'all') return true;
        return (o.status || 'pending') === currentOrderFilter;
    });
    const list = document.getElementById('ordersList');
    if (list_orders.length === 0) {
        list.innerHTML = '<div class="orders-empty mono">NO ORDERS IN THIS VIEW</div>';
        return;
    }
    list.innerHTML = list_orders.map(o => {
        const status = o.status || 'pending';
        const statusClass = status === 'approved' ? 'status-approved' : (status === 'rejected' ? 'status-rejected' : 'status-pending');
        const time = new Date(o.time).toLocaleString();
        const actions = status === 'pending'
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
                    <span class="o-name">${escapeHtml(o.productName)} ${o.price ? '— '+escapeHtml(o.price) : ''}</span>
                    <span class="order-status ${statusClass}">${status.toUpperCase()}</span>
                </div>
                <div class="o-key">KEY: ${o.key}</div>
                <div class="o-meta">${time} | IP: ${o.ip || 'N/A'}</div>
                ${actions}
            </div>
        `;
    }).join('');
}

async function setOrderStatus(id, status) {
    try {
        const res = await fetch(`/api/order/${id}`, {
            method: 'PUT',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({status})
        });
        if (res.ok) {
            const data = await res.json();
            orders = data.orders || [];
            updateOrdersCount();
            renderOrders();
            loadData();
        }
    } catch(e) {
        alert('Error updating order');
    }
}

async function removeOrder(id) {
    if (!confirm('Remove this order?')) return;
    try {
        const res = await fetch(`/api/order/${id}`, { method: 'DELETE' });
        if (res.ok) {
            const data = await res.json();
            orders = data.orders || [];
            updateOrdersCount();
            renderOrders();
            loadData();
        }
    } catch(e) {
        alert('Error removing order');
    }
}

function openOrders() {
    if (!isAdmin) return;
    renderOrders();
    document.getElementById('ordersOverlay').classList.add('show');
}
function closeOrders() { document.getElementById('ordersOverlay').classList.remove('show'); }

document.getElementById('ordersBtn').addEventListener('click', openOrders);
document.querySelectorAll('#ordersFilters button').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('#ordersFilters button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentOrderFilter = btn.dataset.ofilter;
        renderOrders();
    });
});

// ---------- APPROVAL ----------
function generateKey() {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ23456789';
    let key = '';
    for (let i = 0; i < 8; i++) {
        if (i === 4) key += '-';
        key += chars[Math.floor(Math.random() * chars.length)];
    }
    return key;
}

function copyApprovalKey() {
    const key = document.getElementById('approvalKeyText').textContent;
    const btn = document.getElementById('copyBtn');
    navigator.clipboard.writeText(key).then(() => {
        btn.textContent = '✓ COPIED';
        setTimeout(() => { btn.textContent = 'COPY'; }, 1500);
    }).catch(() => {});
}

function closeApproval() { document.getElementById('approvalOverlay').classList.remove('show'); }
function resendApprovalWhatsApp() { if (lastApprovalMsg) openWhatsApp(lastApprovalMsg); }

function openWhatsApp(text) {
    const url = `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(text)}`;
    window.open(url, '_blank');
}

async function buyItem(id) {
    const p = products.find(x => x.id === id);
    if (!p || p.soldOut) return;
    const key = generateKey();
    
    try {
        const res = await fetch('/api/order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                productId: p.id,
                productName: p.name,
                price: p.price || '',
                key: key,
                type: p.type
            })
        });
        if (res.ok) {
            const data = await res.json();
            orders = data.orders || [];
            updateOrdersCount();

            const msg = `Hi, I want to buy: ${p.name} (${p.price || 'price'})\nApproval Key: ${key}\nPlease confirm and approve my order.`;
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

async function downloadItem(id) {
    const p = products.find(x => x.id === id);
    if (!p || p.soldOut) return;
    
    const key = generateKey();
    try {
        const res = await fetch('/api/order', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                productId: p.id,
                productName: p.name,
                price: 'Free',
                key: key,
                type: 'free'
            })
        });
        if (res.ok) {
            const data = await res.json();
            orders = data.orders || [];
            updateOrdersCount();

            const msg = `Hi, I want to download: ${p.name} (Free)\nApproval Key: ${key}\nPlease approve my download request.`;
            lastApprovalMsg = msg;

            document.getElementById('approvalItemName').textContent = p.name + ' (Free Download)';
            document.getElementById('approvalKeyText').textContent = key;
            document.getElementById('approvalOverlay').classList.add('show');

            openWhatsApp(msg);
        }
    } catch(e) {
        alert('Error creating download request');
    }
}

// ---------- RENDER PRODUCTS ----------
function render() {
    const grid = document.getElementById('grid');
    grid.classList.toggle('admin-on', isAdmin);
    
    const list = products.filter(p => {
        if (currentFilter === 'all') return true;
        return p.type === currentFilter;
    });
    
    if (list.length === 0) {
        grid.innerHTML = '<div class="empty mono">NO ITEMS' + (isAdmin ? ' — ADD ONE' : '') + '</div>';
        return;
    }
    
    grid.innerHTML = list.map(p => {
        const soldOut = !!p.soldOut;
        const isFree = p.type === 'free';
        const isPaid = p.type === 'paid';
        
        let actionBtn = '';
        if (soldOut) {
            actionBtn = `<button class="action-btn sold" onclick="event.stopPropagation()" disabled>🚫 SOLD OUT</button>`;
        } else if (isFree) {
            actionBtn = `<button class="action-btn download" onclick="event.stopPropagation();downloadItem('${p.id}')">⬇ DOWNLOAD</button>`;
        } else if (isPaid) {
            actionBtn = `<button class="action-btn buy" onclick="event.stopPropagation();buyItem('${p.id}')">💬 BUY</button>`;
        }
        
        return `
        <div class="card ${soldOut ? 'sold-out' : ''}" data-id="${p.id}" onclick="openProductDetails('${p.id}')">
            <div class="admin-actions" onclick="event.stopPropagation()">
                <button class="edit-btn" onclick="editProduct('${p.id}')" title="Edit">✏️</button>
                <button onclick="removeProduct('${p.id}')" title="Delete">✕</button>
                <button onclick="toggleSoldOut('${p.id}')" title="Toggle Sold Out">${soldOut ? '✅' : '🚫'}</button>
            </div>
            <div class="type-badge ${isFree ? 'free' : 'paid'}">${isFree ? 'FREE' : 'PAID'}</div>
            ${soldOut ? '<div class="sold-badge">SOLD OUT</div>' : ''}
            <div class="media">
                ${p.images && p.images[0] ? `<img src="${p.images[0]}">` : (p.videos && p.videos[0] ? `<video src="${p.videos[0]}" muted></video>` : `<span class="mono" style="color:var(--muted);font-size:9px;">NO PREVIEW</span>`)}
            </div>
            <div class="card-body">
                <h3>${escapeHtml(p.name)}</h3>
                ${isPaid ? `<div class="price">${escapeHtml(p.price || 'Contact for price')}</div>` : ''}
                <p>${escapeHtml(p.desc || '')}</p>
                ${actionBtn}
            </div>
        </div>
    `}).join('');
}


// ---------- PRODUCT DETAILS ----------
function openProductDetails(id) {
    const p = products.find(x => x.id === id);
    if (!p) return;

    const overlay = document.getElementById('productDetailOverlay');
    const cover = document.getElementById('detailCover');
    const gallery = document.getElementById('detailGallery');
    const type = p.type === 'paid' ? 'PAID' : 'FREE';

    document.getElementById('detailName').textContent = p.name || 'ITEM';
    document.getElementById('detailDesc').textContent = p.desc || 'No description available.';
    document.getElementById('detailType').textContent = type;
    document.getElementById('detailType').classList.toggle('paid', p.type === 'paid');
    document.getElementById('detailType2').textContent = type;
    document.getElementById('detailStatus').textContent = p.soldOut ? 'SOLD OUT' : 'AVAILABLE';
    document.getElementById('detailPrice').textContent = p.type === 'paid' ? (p.price || 'CONTACT') : 'FREE';

    const firstImage = p.images && p.images[0];
    const firstVideo = p.videos && p.videos[0];
    cover.innerHTML = firstImage
        ? `<img src="${firstImage}" alt="">`
        : firstVideo
            ? `<video src="${firstVideo}" muted autoplay loop playsinline></video>`
            : `<span style="font:10px 'JetBrains Mono';color:#68747c">NO PREVIEW</span>`;

    gallery.innerHTML = '';
    (p.images || []).forEach(src => {
        const img = document.createElement('img');
        img.src = src;
        gallery.appendChild(img);
    });
    (p.videos || []).forEach(src => {
        const v = document.createElement('video');
        v.src = src; v.muted = true; v.controls = true; v.playsInline = true;
        gallery.appendChild(v);
    });

    const actions = document.getElementById('detailActions');
    actions.innerHTML = '';
    if (!p.soldOut) {
        if (p.type === 'free') {
            actions.innerHTML = `<button class="detail-download" onclick="closeProductDetails();downloadItem('${p.id}')">⬇ DOWNLOAD NOW</button>`;
        } else {
            actions.innerHTML = `<button class="detail-buy" onclick="closeProductDetails();buyItem('${p.id}')">💬 BUY / ORDER</button>`;
        }
    }

    overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
}
function closeProductDetails() {
    const overlay = document.getElementById('productDetailOverlay');
    if (overlay) overlay.classList.remove('show');
    document.body.style.overflow = '';
}
document.addEventListener('keydown', e => {
    if (e.key === 'Escape') closeProductDetails();
});

// ---------- ADMIN ----------
const adminBtn = document.getElementById('adminBtn');
const ordersBtn = document.getElementById('ordersBtn');
const loginOverlay = document.getElementById('loginOverlay');
const adminBadge = document.getElementById('adminBadge');

adminBtn.addEventListener('click', () => {
    if (isAdmin) {
        openAdminMenu();
    } else {
        loginOverlay.classList.add('show');
        document.getElementById('loginPass').value = '';
        document.getElementById('loginErr').style.display = 'none';
    }
});

function openAdminMenu() {
    if (!isAdmin) return;
    document.getElementById('adminMenuOverlay').classList.add('show');
}
function closeAdminMenu() {
    document.getElementById('adminMenuOverlay').classList.remove('show');
}
function adminAddPost() {
    closeAdminMenu();
    setTimeout(() => openAdd(), 80);
}
function adminOpenOrders() {
    closeAdminMenu();
    setTimeout(() => openOrders(), 80);
}
function adminOpenIPBlock() {
    closeAdminMenu();
    setTimeout(() => openIPBlock(), 80);
}

function closeLogin() { loginOverlay.classList.remove('show'); }

async function tryLogin() {
    const val = document.getElementById('loginPass').value;
    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({password: val})
        });
        if (res.ok) {
            isAdmin = true;
            closeLogin();
            adminBadge.classList.add('show');
            adminBtn.textContent = 'MENU';
            ordersBtn.style.display = 'inline-flex';
            render();
            await loadData();
        } else {
            document.getElementById('loginErr').style.display = 'block';
        }
    } catch(e) {
        document.getElementById('loginErr').style.display = 'block';
    }
}

adminBadge.addEventListener('click', async () => {
    isAdmin = false;
    adminBadge.classList.remove('show');
    adminBtn.textContent = 'ADMIN';
    ordersBtn.style.display = 'none';
    render();
    await fetch('/api/logout', { method: 'POST' });
});

// ---------- ADD/EDIT PRODUCT ----------
const addOverlay = document.getElementById('addOverlay');

function openAdd(productData = null) {
    editingProductId = productData ? productData.id : null;
    pendingImages = [];
    pendingVideos = [];
    
    if (productData) {
        document.getElementById('productModalTitle').textContent = 'EDIT ITEM';
        document.getElementById('saveProductBtn').textContent = 'Update Item';
        document.getElementById('pName').value = productData.name || '';
        document.getElementById('pDesc').value = productData.desc || '';
        document.getElementById('pType').value = productData.type || 'free';
        document.getElementById('pPrice').value = productData.price || '';
        document.getElementById('pDownloadLink').value = productData.downloadLink || '';
        document.getElementById('pSoldOut').checked = !!productData.soldOut;
        
        const imgThumbs = document.getElementById('imgThumbs');
        imgThumbs.innerHTML = '';
        if (productData.images) {
            productData.images.forEach(img => {
                const el = document.createElement('img');
                el.src = img;
                imgThumbs.appendChild(el);
            });
        }
        
        const vidThumbs = document.getElementById('vidThumbs');
        vidThumbs.innerHTML = '';
        if (productData.videos) {
            productData.videos.forEach(vid => {
                const el = document.createElement('video');
                el.src = vid;
                el.muted = true;
                vidThumbs.appendChild(el);
            });
        }
    } else {
        document.getElementById('productModalTitle').textContent = 'ADD ITEM';
        document.getElementById('saveProductBtn').textContent = 'Post Item';
        document.getElementById('pName').value = '';
        document.getElementById('pDesc').value = '';
        document.getElementById('pType').value = 'free';
        document.getElementById('pPrice').value = '';
        document.getElementById('pDownloadLink').value = '';
        document.getElementById('pSoldOut').checked = false;
        document.getElementById('imgThumbs').innerHTML = '';
        document.getElementById('vidThumbs').innerHTML = '';
    }
    
    document.getElementById('addErr').style.display = 'none';
    updateTypeFields();
    addOverlay.classList.add('show');
}

function closeAdd() { addOverlay.classList.remove('show'); }

function updateTypeFields() {
    const type = document.getElementById('pType').value;
    document.getElementById('priceField').style.display = type === 'paid' ? 'block' : 'none';
    document.getElementById('downloadField').style.display = type === 'free' ? 'block' : 'none';
}

document.getElementById('pType').addEventListener('change', updateTypeFields);

document.getElementById('pImages').addEventListener('change', (e) => {
    const files = Array.from(e.target.files).slice(0, 3);
    const thumbs = document.getElementById('imgThumbs');
    files.forEach(f => {
        const reader = new FileReader();
        reader.onload = () => {
            pendingImages.push(reader.result);
            const img = document.createElement('img');
            img.src = reader.result;
            thumbs.appendChild(img);
        };
        reader.readAsDataURL(f);
    });
});

document.getElementById('pVideos').addEventListener('change', (e) => {
    const files = Array.from(e.target.files).slice(0, 2);
    const thumbs = document.getElementById('vidThumbs');
    files.forEach(f => {
        const reader = new FileReader();
        reader.onload = () => {
            pendingVideos.push(reader.result);
            const v = document.createElement('video');
            v.src = reader.result;
            v.muted = true;
            thumbs.appendChild(v);
        };
        reader.readAsDataURL(f);
    });
});

async function saveProduct() {
    const name = document.getElementById('pName').value.trim();
    const desc = document.getElementById('pDesc').value.trim();
    const type = document.getElementById('pType').value;
    const price = document.getElementById('pPrice').value.trim();
    const downloadLink = document.getElementById('pDownloadLink').value.trim();
    const soldOut = document.getElementById('pSoldOut').checked;
    const errBox = document.getElementById('addErr');
    
    if (!name) {
        errBox.textContent = 'Please enter a name.';
        errBox.style.display = 'block';
        return;
    }
    if (type === 'paid' && !price) {
        errBox.textContent = 'Please enter a price for paid items.';
        errBox.style.display = 'block';
        return;
    }
    
    let images = pendingImages;
    let videos = pendingVideos;
    
    if (editingProductId) {
        const existing = products.find(p => p.id === editingProductId);
        if (existing) {
            if (images.length === 0) images = existing.images || [];
            if (videos.length === 0) videos = existing.videos || [];
        }
    }
    
    try {
        const res = await fetch('/api/product' + (editingProductId ? '/' + editingProductId : ''), {
            method: editingProductId ? 'PUT' : 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                name, desc, type, price, soldOut,
                downloadLink: type === 'free' ? downloadLink : '',
                images: images.slice(0, 3),
                videos: videos.slice(0, 2)
            })
        });
        if (res.ok) {
            const data = await res.json();
            products = data.products || [];
            closeAdd();
            render();
        } else {
            errBox.textContent = 'Error saving product.';
            errBox.style.display = 'block';
        }
    } catch(e) {
        errBox.textContent = 'Network error.';
        errBox.style.display = 'block';
    }
}

function editProduct(id) {
    const p = products.find(x => x.id === id);
    if (p) openAdd(p);
}

async function removeProduct(id) {
    if (!confirm('Remove this item?')) return;
    try {
        const res = await fetch(`/api/product/${id}`, { method: 'DELETE' });
        if (res.ok) {
            const data = await res.json();
            products = data.products || [];
            render();
        }
    } catch(e) {}
}

async function toggleSoldOut(id) {
    try {
        const res = await fetch(`/api/product/${id}/soldout`, { method: 'PUT' });
        if (res.ok) {
            const data = await res.json();
            products = data.products || [];
            render();
        }
    } catch(e) {}
}

document.querySelectorAll('.filters button').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.filters button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        currentFilter = btn.dataset.filter;
        render();
    });
});

// ---------- INITIALIZE ----------
(async function init() {
    const isBlocked = await checkBlocked();
    if (!isBlocked) {
        checkUserSetup();
        startChatPolling();
        loadData();
    }
})();
</script>

<script>
(function(){
  const chatSection = document.querySelector('.chat-section');
  if (!chatSection) return;
  const trigger = chatSection.querySelector('.mobile-chat-trigger');
  if (!trigger) return;

  trigger.addEventListener('click', function(){
    const open = chatSection.classList.contains('chat-open');
    document.body.style.overflow = open ? '' : 'hidden';
  });

  window.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && chatSection.classList.contains('chat-open')){
      chatSection.classList.remove('chat-open');
      document.body.style.overflow = '';
    }
  });
})();
</script>

</body>
</html>
'''

@app.route('/')
def index():
    client_ip = get_client_ip()
    data = load_data()
    blocked_ips = data.get('blocked_ips', [])
    
    for blocked in blocked_ips:
        if blocked.get('ip') == client_ip:
            return render_template_string('''
            <!DOCTYPE html>
            <html>
            <head><title>Blocked</title>
            <style>
                body{background:#0a0a0d;color:#ece7dd;display:flex;align-items:center;justify-content:center;height:100vh;font-family:Inter,sans-serif;text-align:center;padding:40px;}
                .blocked{border:2px solid #c0392b;padding:40px;border-radius:12px;max-width:500px;background:#151318;}
                .blocked h1{color:#c0392b;font-family:'Bebas Neue';font-size:48px;letter-spacing:3px;}
                .blocked p{color:#8b8577;line-height:1.8;}
                .blocked .reason{color:#f0c341;font-family:'JetBrains Mono';font-size:13px;margin-top:10px;}
            </style>
            </head>
            <body>
            <div class="blocked">
                <h1>🚫 ACCESS DENIED</h1>
                <p>Your IP address has been blocked from accessing this store.</p>
                <p class="reason">Reason: {{ reason if reason else 'No reason provided' }}</p>
            </div>
            </body>
            </html>
            ''', reason=blocked.get('reason', ''))
    
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
        'downloadLink': data.get('downloadLink', ''),
        'images': data.get('images', [])[:3],
        'videos': data.get('videos', [])[:2],
        'soldOut': data.get('soldOut', False)
    }
    data_obj['products'].insert(0, new_product)
    save_data(data_obj)
    return jsonify({'success': True, 'products': data_obj['products']})

@app.route('/api/product/<product_id>', methods=['PUT'])
def update_product(product_id):
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    data_obj = load_data()
    for p in data_obj['products']:
        if p['id'] == product_id:
            p['name'] = data.get('name', p['name'])
            p['desc'] = data.get('desc', p['desc'])
            p['type'] = data.get('type', p['type'])
            p['price'] = data.get('price', p['price'])
            p['downloadLink'] = data.get('downloadLink', p.get('downloadLink', ''))
            p['images'] = data.get('images', p.get('images', []))[:3]
            p['videos'] = data.get('videos', p.get('videos', []))[:2]
            p['soldOut'] = data.get('soldOut', p.get('soldOut', False))
            save_data(data_obj)
            return jsonify({'success': True, 'products': data_obj['products']})
    return jsonify({'error': 'Product not found'}), 404

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
        'status': 'pending',
        'ip': get_client_ip(),
        'type': data.get('type', 'paid')
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

# Chat API Routes
@app.route('/api/chat')
def get_chat():
    data = load_data()
    return jsonify({
        'messages': data.get('chat_messages', []),
        'users': data.get('users', {})
    })

@app.route('/api/chat/message', methods=['POST'])
def send_chat_message():
    client_ip = get_client_ip()
    data = load_data()
    blocked_ips = data.get('blocked_ips', [])
    for blocked in blocked_ips:
        if blocked.get('ip') == client_ip:
            return jsonify({'error': 'Blocked'}), 403
    
    msg_data = request.json
    if len(data.get('chat_messages', [])) > 100:
        data['chat_messages'] = data['chat_messages'][-100:]
    
    new_msg = {
        'id': 'm_' + str(uuid.uuid4())[:8],
        'userId': msg_data.get('userId'),
        'text': msg_data.get('text', ''),
        'image': msg_data.get('image', ''),
        'time': datetime.now().isoformat()
    }
    data.setdefault('chat_messages', []).append(new_msg)
    save_data(data)
    return jsonify({
        'success': True,
        'messages': data['chat_messages'],
        'users': data.get('users', {})
    })

@app.route('/api/user/setup', methods=['POST'])
def setup_user():
    client_ip = get_client_ip()
    data = load_data()
    blocked_ips = data.get('blocked_ips', [])
    for blocked in blocked_ips:
        if blocked.get('ip') == client_ip:
            return jsonify({'error': 'Blocked'}), 403
    
    user_data = request.json
    if 'users' not in data:
        data['users'] = {}
    
    data['users'][user_data.get('id')] = {
        'name': user_data.get('name'),
        'profilePic': user_data.get('profilePic', ''),
        'joined': user_data.get('joined', datetime.now().isoformat()),
        'ip': client_ip
    }
    save_data(data)
    return jsonify({'success': True})

# IP Block Routes
@app.route('/api/check_block')
def check_block():
    client_ip = get_client_ip()
    data = load_data()
    blocked_ips = data.get('blocked_ips', [])
    for blocked in blocked_ips:
        if blocked.get('ip') == client_ip:
            return jsonify({'blocked': True, 'reason': blocked.get('reason', '')})
    return jsonify({'blocked': False})

@app.route('/api/blocked_ips')
def get_blocked_ips():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    data = load_data()
    return jsonify({'ips': data.get('blocked_ips', [])})

@app.route('/api/block_ip', methods=['POST'])
def block_ip():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    ip = request.json.get('ip')
    reason = request.json.get('reason', '')
    if not ip:
        return jsonify({'error': 'IP required'}), 400
    
    data = load_data()
    if 'blocked_ips' not in data:
        data['blocked_ips'] = []
    for blocked in data['blocked_ips']:
        if blocked.get('ip') == ip:
            return jsonify({'error': 'Already blocked'}), 400
    
    data['blocked_ips'].append({
        'ip': ip,
        'reason': reason,
        'blocked_at': datetime.now().isoformat()
    })
    save_data(data)
    return jsonify({'success': True, 'ips': data['blocked_ips']})

@app.route('/api/unblock_ip', methods=['POST'])
def unblock_ip():
    if not session.get('admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    ip = request.json.get('ip')
    if not ip:
        return jsonify({'error': 'IP required'}), 400
    
    data = load_data()
    data['blocked_ips'] = [b for b in data.get('blocked_ips', []) if b.get('ip') != ip]
    save_data(data)
    return jsonify({'success': True, 'ips': data['blocked_ips']})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
