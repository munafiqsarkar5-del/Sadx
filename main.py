import os
import secrets
import sqlite3
from urllib.parse import quote

from flask import (
    Flask, request, redirect, session, flash,
    render_template_string, abort, send_from_directory
)
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "SADX")
WHATSAPP_NUMBER = "923274540554"
DB = "store.db"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

HTML = r"""
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>MEOW STORE</title>
<style>
:root{--bg:#09090f;--panel:#12121c;--panel2:#191927;--text:#f7f4ff;--muted:#a5a1b8;--purple:#a855f7;--pink:#ec4899;--line:#2b2940;--green:#4ade80}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at 10% 0%,#291342 0,transparent 38%),radial-gradient(ellipse at 95% 25%,#171d45 0,transparent 32%),var(--bg);color:var(--text);font-family:Inter,system-ui,-apple-system,Segoe UI,sans-serif;min-height:100vh}
a{color:inherit;text-decoration:none}button,.btn{border:0;cursor:pointer;font-weight:800;border-radius:12px;padding:12px 16px;display:inline-flex;align-items:center;justify-content:center;gap:8px}
.nav{max-width:1160px;margin:auto;padding:20px 22px;display:flex;align-items:center;justify-content:space-between;gap:16px;border-bottom:1px solid #ffffff12}
.logo{font-weight:1000;letter-spacing:1.4px;font-size:20px}.logo span{color:#d8a4ff}.navright{display:flex;gap:9px;align-items:center}
.btn-primary{background:linear-gradient(100deg,var(--purple),var(--pink));color:white;box-shadow:0 8px 28px #a855f733}.btn-secondary{background:#ffffff0b;color:var(--text);border:1px solid var(--line)}.btn-danger{background:#5c2033;color:#ffd7e3}.btn-small{font-size:12px;padding:9px 11px}
.wrap{max-width:1160px;margin:auto;padding:30px 22px 70px}.hero{padding:42px 0 30px;max-width:750px}.eyebrow{color:#d8a4ff;font-size:12px;font-weight:900;letter-spacing:2.2px;text-transform:uppercase}
h1{font-size:clamp(38px,7vw,68px);line-height:1.02;letter-spacing:-2px;margin:14px 0}.gradient{background:linear-gradient(90deg,#fff,#d8a4ff 45%,#f9a8d4);-webkit-background-clip:text;background-clip:text;color:transparent}
.sub{color:var(--muted);font-size:16px;line-height:1.75;max-width:610px}.chips{display:flex;gap:8px;flex-wrap:wrap;margin-top:22px}.chip{border:1px solid var(--line);background:#ffffff08;border-radius:99px;padding:8px 12px;color:#d9d5e7;font-size:12px}
.section-head{display:flex;align-items:end;justify-content:space-between;gap:15px;margin:28px 0 18px}.section-head h2{margin:0;font-size:24px}.muted{color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:18px}.product{overflow:hidden;background:linear-gradient(150deg,#191927,#101019);border:1px solid var(--line);border-radius:19px;transition:transform .2s,border-color .2s}.product:hover{transform:translateY(-4px);border-color:#8953bd}.photo{height:190px;background:linear-gradient(140deg,#27143c,#14172b);display:flex;align-items:center;justify-content:center;overflow:hidden;color:#d8a4ff;font-size:44px}.photo img{width:100%;height:100%;object-fit:cover}.product-body{padding:17px}.tag{display:inline-flex;font-size:10px;letter-spacing:1px;font-weight:900;padding:6px 9px;border-radius:99px;background:#a855f71f;color:#d8a4ff}.tag.sold{background:#ef44441b;color:#fca5a5}.product h3{font-size:19px;margin:12px 0 7px;overflow-wrap:anywhere}.details{color:var(--muted);font-size:13px;line-height:1.6;white-space:pre-wrap;min-height:40px}.price-row{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-top:18px}.price{font-weight:950;font-size:21px}.empty{padding:38px;border:1px dashed #46405d;border-radius:18px;color:var(--muted);text-align:center}
.panel{max-width:760px;margin:30px auto;background:#11111bf0;border:1px solid var(--line);border-radius:22px;padding:clamp(20px,4vw,34px);box-shadow:0 25px 80px #0005}.panel h1{font-size:36px;letter-spacing:-1px}.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.field{display:flex;flex-direction:column;gap:7px;margin-bottom:14px}.field.full{grid-column:1/-1}label{font-size:12px;font-weight:800;color:#d9d3e9}input,textarea,select{width:100%;border:1px solid #39354f;background:#0a0a12;color:white;border-radius:11px;padding:13px;font:inherit;outline:none}input:focus,textarea:focus,select:focus{border-color:var(--purple)}textarea{min-height:95px;resize:vertical}.flash{padding:12px 15px;border-radius:11px;margin:15px 0;background:#302044;border:1px solid #7446a0}.flash.error{background:#3c1c2a;border-color:#85364e}.flash.success{background:#153525;border-color:#276644}
.keybox{font-family:ui-monospace,SFMono-Regular,monospace;font-size:clamp(27px,7vw,43px);font-weight:900;letter-spacing:2px;text-align:center;background:#09090f;border:1px dashed #a855f7;border-radius:15px;padding:23px 10px;color:#e9c7ff;overflow-wrap:anywhere;margin:18px 0}
.tablelist{display:grid;gap:10px;margin-top:14px}.itemrow{display:flex;align-items:center;gap:12px;background:#ffffff06;border:1px solid var(--line);padding:12px;border-radius:13px}.thumb{width:54px;height:54px;object-fit:cover;border-radius:10px;background:#241b34}.iteminfo{flex:1;min-width:0}.iteminfo strong{display:block;overflow-wrap:anywhere}.iteminfo small{color:var(--muted)}.actions{display:flex;gap:7px;flex-wrap:wrap;justify-content:flex-end}.footer{text-align:center;color:#716d83;font-size:12px;padding:25px 15px;border-top:1px solid #ffffff0d}
@media(max-width:600px){.nav{padding:16px}.wrap{padding:20px 15px 50px}.hero{padding-top:30px}.form-grid{grid-template-columns:1fr}.field.full{grid-column:auto}.itemrow{align-items:flex-start;flex-wrap:wrap}.actions{width:100%;justify-content:flex-start}.section-head{align-items:start;flex-direction:column}}
</style>
</head>
<body>
<header class="nav">
  <a class="logo" href="{{ url_for('home') }}">🐾 MEOW <span>STORE</span></a>
  <div class="navright">
    {% if admin %}<a class="btn btn-secondary btn-small" href="{{ url_for('admin') }}">Dashboard</a><a class="btn btn-primary btn-small" href="{{ url_for('logout') }}">Exit</a>
    {% else %}<a class="btn btn-secondary btn-small" href="{{ url_for('login') }}">Admin</a>{% endif %}
  </div>
</header>
<main class="wrap">
{% with messages = get_flashed_messages(with_categories=true) %}
{% for category, message in messages %}<div class="flash {{ category }}">{{ message }}</div>{% endfor %}
{% endwith %}

{% if page == "store" %}
<section class="hero">
  <div class="eyebrow">✦ Your next digital find starts here</div>
  <h1>Small store.<br><span class="gradient">Big discoveries.</span></h1>
  <p class="sub">Welcome to MEOW STORE — browse the collection, pick what you like, and tap Buy Now to generate your unique order key instantly.</p>
  <div class="chips"><span class="chip">✦ Digital products</span><span class="chip">⚡ Instant order key</span><span class="chip">💬 WhatsApp checkout</span></div>
</section>
<div class="section-head"><div><div class="eyebrow">The collection</div><h2>Featured products</h2></div><span class="muted">{{ products|length }} product(s)</span></div>
<div class="grid">
{% for p in products %}
<article class="product">
  <div class="photo">{% if p.image %}<img src="{{ url_for('uploads', name=p.image) }}" alt="{{ p.name }}">{% else %}<span>🐾</span>{% endif %}</div>
  <div class="product-body">
    {% if p.sold %}<span class="tag sold">SOLD OUT</span>{% elif p.free %}<span class="tag">FREE</span>{% else %}<span class="tag">PREMIUM</span>{% endif %}
    <h3>{{ p.name }}</h3><div class="details">{{ p.details }}</div>
    <div class="price-row"><span class="price">{{ "FREE" if p.free else p.price }}</span>
    {% if not p.sold %}<form method="post" action="{{ url_for('buy', pid=p.id) }}"><button class="btn btn-primary" type="submit">BUY NOW ↗</button></form>{% else %}<button class="btn btn-secondary" disabled>Unavailable</button>{% endif %}</div>
  </div>
</article>
{% else %}<div class="empty" style="grid-column:1/-1">No products yet. Admin can add the first product.</div>{% endfor %}
</div>

{% elif page == "key" %}
<div class="panel" style="text-align:center">
  <div class="eyebrow">✓ Order created</div><h1>Your key is ready.</h1>
  <p class="sub" style="margin:0 auto">Keep this unique order key. Use the WhatsApp button to send your product and order details.</p>
  <div class="keybox" id="orderKey">{{ order_key }}</div>
  <h2>{{ product.name }}</h2><p class="muted">Price: {{ "FREE" if product.free else product.price }}</p>
  <button class="btn btn-secondary" onclick="copyKey()">⧉ Copy order key</button>
  <a class="btn btn-primary" target="_blank" rel="noopener" href="{{ wa_url }}">Open WhatsApp ↗</a>
  <p class="muted" id="copyStatus" style="font-size:12px"></p>
  <a class="btn btn-secondary" href="{{ url_for('home') }}">← Back to store</a>
</div>
<script>
function copyKey(){const key=document.getElementById('orderKey').innerText;
if(navigator.clipboard&&window.isSecureContext){navigator.clipboard.writeText(key).then(()=>document.getElementById('copyStatus').innerText='Key copied!');}
else{const t=document.createElement('textarea');t.value=key;document.body.appendChild(t);t.select();try{document.execCommand('copy');document.getElementById('copyStatus').innerText='Key copied!';}catch(e){document.getElementById('copyStatus').innerText='Please select and copy the key manually.';}t.remove();}}
</script>

{% elif page == "login" %}
<div class="panel">
  <div class="eyebrow">Restricted access</div><h1>Admin <span class="gradient">login</span></h1><p class="sub">Sign in to manage your MEOW STORE products and order keys.</p>
  <form method="post"><div class="field"><label for="password">ADMIN PASSWORD</label><input id="password" name="password" type="password" placeholder="Enter admin password" required autocomplete="current-password"></div><button class="btn btn-primary" type="submit">Unlock dashboard →</button> <a class="btn btn-secondary" href="{{ url_for('home') }}">Back to store</a></form>
</div>

{% else %}
<div class="section-head"><div><div class="eyebrow">Store management</div><h2>Admin dashboard</h2></div><a class="btn btn-secondary" href="{{ url_for('home') }}">View store ↗</a></div>
<div class="panel" style="max-width:none;margin:0 0 25px">
  <h2>＋ Add product</h2>
  <form method="post" action="{{ url_for('add') }}" enctype="multipart/form-data">
    <div class="form-grid">
      <div class="field"><label>PRODUCT NAME</label><input name="name" maxlength="100" required placeholder="Product name"></div>
      <div class="field"><label>PRICE</label><input name="price" maxlength="40" placeholder="e.g. Rs. 500"></div>
      <div class="field full"><label>DESCRIPTION</label><textarea name="details" maxlength="1000" placeholder="Tell customers about the product"></textarea></div>
      <div class="field"><label>PRODUCT TYPE</label><select name="free"><option value="0">Paid product</option><option value="1">Free product</option></select></div>
      <div class="field"><label>PRODUCT IMAGE</label><input type="file" name="image" accept=".jpg,.jpeg,.png,.webp,.gif,image/*"></div>
    </div>
    <button class="btn btn-primary" type="submit">＋ Add product</button>
  </form>
</div>
<div class="section-head"><div><div class="eyebrow">Inventory</div><h2>Products</h2></div><span class="muted">{{ products|length }} item(s)</span></div>
<div class="tablelist">
{% for p in products %}
<div class="itemrow">
  {% if p.image %}<img class="thumb" src="{{ url_for('uploads', name=p.image) }}" alt="">{% else %}<div class="thumb" style="display:grid;place-items:center">🐾</div>{% endif %}
  <div class="iteminfo"><strong>{{ p.name }}</strong><small>{{ "FREE" if p.free else p.price }} · {{ "SOLD OUT" if p.sold else "AVAILABLE" }}</small></div>
  <div class="actions">
    <form method="post" action="{{ url_for('toggle', pid=p.id) }}"><button class="btn btn-secondary btn-small" type="submit">{{ "Mark available" if p.sold else "Mark sold out" }}</button></form>
    <form method="post" action="{{ url_for('delete', pid=p.id) }}" onsubmit="return confirm('Delete this product?')"><button class="btn btn-danger btn-small" type="submit">Delete</button></form>
  </div>
</div>
{% else %}<div class="empty">No products yet. Add one above.</div>{% endfor %}
</div>
<div class="section-head"><div><div class="eyebrow">Recent activity</div><h2>Recent order keys</h2></div></div>
<div class="tablelist">
{% for o in orders %}<div class="itemrow"><div class="iteminfo"><strong>{{ o.key }} · {{ o.name }}</strong><small>{{ o.created[:19].replace('T',' ') }}</small></div></div>
{% else %}<div class="empty">No orders yet.</div>{% endfor %}
</div>
{% endif %}
</main>
<footer class="footer">© {{ year }} MEOW STORE · Made for digital discoveries</footer>
</body></html>
"""

def conn():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    c.execute("""CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL, details TEXT, price TEXT,
        image TEXT, sold INTEGER DEFAULT 0, free INTEGER DEFAULT 0
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER, name TEXT, key TEXT UNIQUE, created TEXT
    )""")
    # Upgrade older databases safely.
    columns = {row["name"] for row in c.execute("PRAGMA table_info(products)").fetchall()}
    if "free" not in columns:
        c.execute("ALTER TABLE products ADD COLUMN free INTEGER DEFAULT 0")
    c.commit()
    return c

def page(template_page, **context):
    return render_template_string(
        HTML, page=template_page, admin=bool(session.get("admin")),
        year=__import__("datetime").datetime.now().year, **context
    )

@app.route("/uploads/<path:name>")
def uploads(name):
    return send_from_directory(UPLOAD_FOLDER, name)

@app.route("/")
def home():
    c = conn()
    products = c.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    c.close()
    return page("store", products=products)

@app.route("/buy/<int:pid>", methods=["POST"])
def buy(pid):
    c = conn()
    p = c.execute("SELECT * FROM products WHERE id=?", (pid,)).fetchone()
    if not p:
        c.close()
        abort(404)
    if p["sold"]:
        c.close()
        flash("This product is sold out.", "error")
        return redirect("/")
    order_key = "MEOW-" + secrets.token_hex(4).upper()
    c.execute(
        "INSERT INTO orders(product_id,name,key,created) VALUES(?,?,?,datetime('now'))",
        (pid, p["name"], order_key)
    )
    c.commit()
    c.close()
    price = "FREE" if p["free"] else (p["price"] or "Contact for price")
    message = f"Hello MEOW STORE! I want to order: {p['name']}\\nOrder Key: {order_key}\\nPrice: {price}"
    wa_url = "https://wa.me/" + WHATSAPP_NUMBER + "?text=" + quote(message)
    return page("key", product=p, order_key=order_key, wa_url=wa_url)

@app.route("/admin", methods=["GET"])
def admin():
    if not session.get("admin"):
        return redirect("/admin/login")
    c = conn()
    products = c.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    orders = c.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 100").fetchall()
    c.close()
    return page("admin", products=products, orders=orders)

@app.route("/admin/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        supplied = request.form.get("password", "")
        if secrets.compare_digest(supplied, ADMIN_PASSWORD):
            session["admin"] = True
            session.permanent = False
            return redirect("/admin")
        flash("Wrong password.", "error")
    return page("login")

@app.route("/admin/logout")
def logout():
    session.clear()
    return redirect("/")

def need_admin():
    if not session.get("admin"):
        abort(403)

@app.route("/admin/add", methods=["POST"])
def add():
    need_admin()
    name = request.form.get("name", "").strip()
    details = request.form.get("details", "").strip()
    price = request.form.get("price", "").strip() or "Contact for price"
    free = 1 if request.form.get("free") == "1" else 0
    if not name:
        flash("Product name is required.", "error")
        return redirect("/admin")
    f = request.files.get("image")
    filename = None
    if f and f.filename:
        original = secure_filename(f.filename)
        ext = original.rsplit(".", 1)[-1].lower() if "." in original else ""
        if ext not in ALLOWED_EXTENSIONS:
            flash("Invalid image type. Use JPG, PNG, WEBP or GIF.", "error")
            return redirect("/admin")
        filename = secrets.token_hex(12) + "." + ext
        f.save(os.path.join(UPLOAD_FOLDER, filename))
    c = conn()
    c.execute(
        "INSERT INTO products(name,details,price,image,free) VALUES(?,?,?,?,?)",
        (name, details, price, filename, free)
    )
    c.commit()
    c.close()
    flash("Product added successfully.", "success")
    return redirect("/admin")

@app.route("/admin/toggle/<int:pid>", methods=["POST"])
def toggle(pid):
    need_admin()
    c = conn()
    c.execute("UPDATE products SET sold=CASE sold WHEN 1 THEN 0 ELSE 1 END WHERE id=?", (pid,))
    c.commit()
    c.close()
    return redirect("/admin")

@app.route("/admin/delete/<int:pid>", methods=["POST"])
def delete(pid):
    need_admin()
    c = conn()
    p = c.execute("SELECT image FROM products WHERE id=?", (pid,)).fetchone()
    if p and p["image"]:
        path = os.path.join(UPLOAD_FOLDER, os.path.basename(p["image"]))
        if os.path.isfile(path):
            os.remove(path)
    c.execute("DELETE FROM products WHERE id=?", (pid,))
    c.commit()
    c.close()
    flash("Product deleted.", "success")
    return redirect("/admin")

if __name__ == "__main__":
    c = conn()
    c.close()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
