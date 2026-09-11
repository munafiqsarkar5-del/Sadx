import os, secrets, sqlite3
from urllib.parse import quote
from flask import Flask, request, redirect, session, flash, render_template_string, url_for, abort
from werkzeug.utils import secure_filename

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","change-me")
ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD","SADX")
WA="923303257478"
DB="store.db"
UPLOAD="uploads"
os.makedirs(UPLOAD,exist_ok=True)

HTML=r"""<!doctype html><html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DARK STORE</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#07090a;color:#eee;font-family:Arial,sans-serif}
body:before{content:"";position:fixed;inset:0;pointer-events:none;background:radial-gradient(circle at 15% 10%,#00e98718,transparent 35%),radial-gradient(circle at 90% 80%,#ff315418,transparent 35%)}
header{position:sticky;top:0;z-index:4;background:#07090aee;backdrop-filter:blur(12px);border-bottom:1px solid #20292b;padding:14px 5%;display:flex;justify-content:space-between;align-items:center}
.logo{font-size:24px;font-weight:1000;letter-spacing:2px}.logo b{color:#00e987}.btn,.buy{border:0;border-radius:10px;padding:11px 14px;font-weight:900;cursor:pointer}.btn{background:#151c1d;color:#ddd}.buy{background:#00e987;color:#03130b}
.wrap{width:min(1050px,90%);margin:auto}.hero{padding:55px 0 30px}.tag{color:#00e987;font-size:11px;font-weight:900;letter-spacing:4px}.hero h1{font-size:clamp(38px,8vw,70px);line-height:.95;margin:10px 0}.hero h1 span{color:#00e987}.muted{color:#839091;line-height:1.6}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(245px,1fr));gap:18px}.card,.panel,.login{background:#0e1314;border:1px solid #222c2e;border-radius:18px;overflow:hidden;box-shadow:0 15px 40px #0008}.pic{height:235px;background:#0a0e0f;position:relative}.pic img{width:100%;height:100%;object-fit:cover}.noimg{height:100%;display:grid;place-items:center;color:#354143;font-size:28px;font-weight:1000}.sold{position:absolute;right:10px;top:10px;background:#ff3f59;padding:7px 9px;border-radius:7px;font-size:10px;font-weight:900}.body{padding:17px}.body h2{margin:0 0 8px}.body p{color:#899596;line-height:1.5;min-height:55px}.row{display:flex;justify-content:space-between;align-items:center;gap:8px}.flash{padding:12px;border-radius:10px;margin:15px 0;background:#15241e}.error{background:#2b1519;color:#ff9aa5}
.center{min-height:100vh;display:grid;place-items:center;padding:20px}.login{padding:25px;width:min(390px,100%)}input,textarea{width:100%;background:#080b0c;color:#fff;border:1px solid #2a3537;border-radius:10px;padding:13px;margin:6px 0;font:inherit}textarea{min-height:110px;resize:vertical}.full{width:100%;margin-top:8px}.back{display:block;text-align:center;color:#829091;margin-top:16px;font-size:13px}
.panel{padding:20px;margin:25px 0}.panel h2{font-size:15px;letter-spacing:2px}.upload{display:block;border:1px dashed #344143;padding:13px;border-radius:10px;color:#8b9899;margin:7px 0}.adminrow{display:flex;gap:12px;align-items:center;padding:12px 0;border-top:1px solid #20282a}.thumb{width:55px;height:55px;background:#080b0c;border-radius:8px;overflow:hidden;display:grid;place-items:center;font-size:8px;color:#687475}.thumb img{width:100%;height:100%;object-fit:cover}.info{flex:1}.info small{display:block;color:#718082;margin-top:4px}.actions{display:flex;gap:6px;flex-wrap:wrap}.mini{background:#151c1d;color:#ddd;border:1px solid #303a3c;border-radius:7px;padding:8px;font-size:9px;font-weight:900}.danger{color:#ff8794}
.order{display:grid;grid-template-columns:150px 1fr auto;gap:10px;padding:10px 0;border-top:1px solid #20282a;font-size:12px}.order b{color:#00e987}.order small{color:#697576}
footer{text-align:center;color:#526062;padding:45px 0;font-size:10px}@media(max-width:600px){.pic{height:220px}.order{grid-template-columns:1fr}.adminrow{align-items:flex-start}.actions{justify-content:flex-start}}
</style></head><body>
<header><div><div class="logo">DARK<b>STORE</b></div><small style="color:#657172">PREMIUM DIGITAL STORE</small></div>
<div style="display:flex;gap:7px"><a class="btn" href="/admin">{{"STORE" if admin else "ADMIN"}}</a>{% if admin %}<a class="btn" href="/admin/logout">EXIT</a>{% endif %}</div></header>
<main class="wrap">
{% with msgs=get_flashed_messages(with_categories=true) %}{% for c,m in msgs %}<div class="flash {{c}}">{{m}}</div>{% endfor %}{% endwith %}
{% if page=="store" %}
<section class="hero"><div class="tag">WELCOME</div><h1>Find your <span>next deal.</span></h1><p class="muted">Choose a product and press BUY NOW. A unique order key is generated automatically.</p></section>
<div class="grid">{% for p in products %}<article class="card"><div class="pic">{% if p.image %}<img src="/uploads/{{p.image}}" alt="product">{% else %}<div class="noimg">DARK<br>STORE</div>{% endif %}{% if p.sold %}<div class="sold">SOLD OUT</div>{% endif %}</div><div class="body"><h2>{{p.name}}</h2><p>{{p.details}}</p><div class="row"><b>{% if p.free %}<span style="color:#00e987">FREE</span>{% else %}{{p.price}}{% endif %}</b>{% if not p.sold %}<form method="post" action="/buy/{{p.id}}"><button class="buy">BUY NOW ↗</button></form>{% else %}<button class="buy" disabled style="background:#343b3c;color:#aaa">SOLD OUT</button>{% endif %}</div></div></article>{% else %}<p class="muted">No products yet. Add one from Admin.</p>{% endfor %}</div>
{% elif page=="key" %}
<div class="center"><div class="login" style="text-align:center">
  <div class="tag">ORDER CREATED</div>
  <h1 style="margin:10px 0">YOUR KEY</h1>
  <p class="muted">{{product.name}}</p>
  <div style="font-size:30px;font-weight:1000;letter-spacing:4px;color:#00e987;background:#080b0c;border:1px dashed #00e98755;border-radius:12px;padding:18px 10px;margin:18px 0">{{order_key}}</div>
  <p class="muted">Save this key. It has also been added to your WhatsApp message.</p>
  <a class="buy" style="display:block" href="{{wa_url}}">OPEN WHATSAPP ↗</a>
  <a class="back" href="/">← Back to Store</a>
</div></div>
{% elif page=="login" %}
<div class="center"><div class="login"><div class="logo">DARK<b>STORE</b></div><h2>ADMIN LOGIN</h2><form method="post"><input type="password" name="password" placeholder="Admin password" required><button class="buy full">ENTER PANEL</button></form><a class="back" href="/">← Store</a></div></div>
{% else %}
<section class="panel"><h2>＋ ADD PRODUCT</h2><form method="post" action="/admin/add" enctype="multipart/form-data"><input name="name" placeholder="Product full name" required><input name="price" placeholder="Price e.g. Rs. 1500 (Free product can leave blank)"><label class="upload">PRODUCT TYPE <select name="free" style="width:100%;margin-top:8px;background:#080b0c;color:#fff;border:1px solid #2a3537;border-radius:10px;padding:13px"><option value="0">PAID</option><option value="1">FREE</option></select></label><textarea name="details" placeholder="Full details..." required></textarea><label class="upload">PRODUCT IMAGE <input type="file" name="image" accept="image/*"></label><button class="buy">ADD PRODUCT</button></form></section>
<section class="panel"><h2>PRODUCTS</h2>{% for p in products %}<div class="adminrow"><div class="thumb">{% if p.image %}<img src="/uploads/{{p.image}}">{% else %}NO IMG{% endif %}</div><div class="info"><b>{{p.name}}</b><small>{% if p.free %}FREE{% else %}{{p.price}}{% endif %} · {{'SOLD OUT' if p.sold else 'AVAILABLE'}}</small></div><div class="actions"><form method="post" action="/admin/toggle/{{p.id}}"><button class="mini">{{'UNSOLD' if p.sold else 'SOLD OUT'}}</button></form><form method="post" action="/admin/delete/{{p.id}}" onsubmit="return confirm('Delete product?')"><button class="mini danger">DELETE</button></form></div></div>{% endfor %}</section>
<section class="panel"><h2>RECENT ORDER KEYS</h2>{% for o in orders %}<div class="order"><b>{{o.key}}</b><span>{{o.name}}</span><small>{{o.created[:19].replace('T',' ')}}</small></div>{% else %}<p class="muted">No orders yet.</p>{% endfor %}</section>
{% endif %}</main><footer>© DARK STORE</footer></body></html>"""

def conn():
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row
    c.execute("CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY AUTOINCREMENT,name TEXT,details TEXT,price TEXT,image TEXT,sold INTEGER DEFAULT 0,free INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS orders(id INTEGER PRIMARY KEY AUTOINCREMENT,product_id INTEGER,name TEXT,key TEXT UNIQUE,created TEXT)")
    try:
        c.execute("ALTER TABLE products ADD COLUMN free INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass
    c.commit(); return c

@app.route("/uploads/<path:name>")
def uploads(name):
    from flask import send_from_directory
    return send_from_directory(UPLOAD,name)

@app.route("/")
def home():
    c=conn(); products=c.execute("SELECT * FROM products ORDER BY id DESC").fetchall(); c.close()
    return render_template_string(HTML,page="store",products=products,admin=False)

@app.route("/buy/<int:pid>",methods=["POST"])
def buy(pid):
    c=conn(); p=c.execute("SELECT * FROM products WHERE id=?",(pid,)).fetchone()
    if not p: c.close(); abort(404)
    if p["sold"]: c.close(); flash("Product is sold out.","error"); return redirect("/")
    key="DS-"+secrets.token_hex(4).upper()
    c.execute("INSERT INTO orders(product_id,name,key,created) VALUES(?,?,?,datetime('now'))",(pid,p["name"],key)); c.commit(); c.close()
    msg=f"Hello, I want to order: {p['name']}\nOrder Key: {key}\nPrice: {("FREE" if p["free"] else p["price"])}"
    wa_url="https://wa.me/"+WA+"?text="+quote(msg)
    return render_template_string(HTML,page="key",product=p,order_key=key,wa_url=wa_url,admin=False)

@app.route("/admin",methods=["GET"])
def admin():
    if not session.get("admin"): return redirect("/admin/login")
    c=conn(); products=c.execute("SELECT * FROM products ORDER BY id DESC").fetchall(); orders=c.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 100").fetchall(); c.close()
    return render_template_string(HTML,page="admin",products=products,orders=orders,admin=True)

@app.route("/admin/login",methods=["GET","POST"])
def login():
    if request.method=="POST":
        if secrets.compare_digest(request.form.get("password",""),ADMIN_PASSWORD):
            session["admin"]=True; return redirect("/admin")
        flash("Wrong password.","error")
    return render_template_string(HTML,page="login",admin=False)

@app.route("/admin/logout")
def logout(): session.clear(); return redirect("/")

def need_admin():
    if not session.get("admin"): abort(403)

@app.route("/admin/add",methods=["POST"])
def add():
    need_admin(); name=request.form["name"].strip(); details=request.form["details"].strip(); price=request.form.get("price","").strip() or "FREE"; free=1 if request.form.get("free")=="1" else 0
    f=request.files.get("image"); filename=None
    if f and f.filename:
        ext=f.filename.rsplit(".",1)[-1].lower() if "." in f.filename else ""
        if ext not in {"jpg","jpeg","png","webp","gif"}: flash("Invalid image type.","error"); return redirect("/admin")
        filename=secrets.token_hex(8)+"."+secure_filename(ext); f.save(os.path.join(UPLOAD,filename))
    c=conn(); c.execute("INSERT INTO products(name,details,price,image,free) VALUES(?,?,?,?,?)",(name,details,price,filename,free)); c.commit(); c.close()
    flash("Product added.","success"); return redirect("/admin")

@app.route("/admin/toggle/<int:pid>",methods=["POST"])
def toggle(pid):
    need_admin(); c=conn(); c.execute("UPDATE products SET sold=CASE sold WHEN 1 THEN 0 ELSE 1 END WHERE id=?",(pid,)); c.commit(); c.close(); return redirect("/admin")

@app.route("/admin/delete/<int:pid>",methods=["POST"])
def delete(pid):
    need_admin(); c=conn(); p=c.execute("SELECT image FROM products WHERE id=?",(pid,)).fetchone()
    if p and p["image"]:
        path=os.path.join(UPLOAD,p["image"])
        if os.path.isfile(path): os.remove(path)
    c.execute("DELETE FROM products WHERE id=?",(pid,)); c.commit(); c.close(); return redirect("/admin")

if __name__=="__main__":
    conn().close()
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)))
