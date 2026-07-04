import requests

CINETPAY_APIKEY = 'TA_CLE_API_ICI' # Tu l’auras sur cinetpay.com
CINETPAY_SITE_ID = 'TON_SITE_ID_ICI'

@app.route('/depot', methods=['GET','POST'])
def depot():
    if 'pseudo' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        montant = int(request.form['montant'])
        transaction_id = f"BET229_{session['pseudo']}_{int(datetime.now().timestamp())}"

        # 1. Créer paiement CinetPay
        data = {
            "apikey": CINETPAY_APIKEY,
            "site_id": CINETPAY_SITE_ID,
            "transaction_id": transaction_id,
            "amount": montant,
            "currency": "XOF",
            "description": f"Recharge BetPro229 {session['pseudo']}",
            "return_url": f"https://on-39350.up.railway.app/retour",
            "notify_url": f"https://on-39350.up.railway.app/notify"
        }

        r = requests.post("https://api.cinetpay.com/v1/?method=payment", data=data).json()

        if r['code'] == '201':
            return redirect(r['data']['payment_url']) # Redirige vers page CinetPay
        else:
            return "Erreur paiement: " + r['message']

    return render_template_string('...ton formulaire dépôt...')    return render_template_string('''
    <!doctype html>
    <html>
    <head><title>BetPro 229</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body{font-family:Arial;background:#0a0a0a;color:#fff;padding:20px;text-align:center}
       .card{background:#1a1a1a;padding:20px;border-radius:15px;margin:20px auto;max-width:400px}
       .solde{font-size:40px;color:#00ff88;font-weight:bold}
       .btn{background:#00ff88;color:#000;padding:15px;border:none;border-radius:10px;
             width:100%;margin:10px 0;font-size:18px;font-weight:bold}
        input{width:100%;padding:12px;margin:10px 0;border-radius:8px;border:none}
        a{color:#00ff88;text-decoration:none}
    </style>
    </head>
    <body>
        <div class="card">
            <h2>🔥 BetPro 229</h2>
            <p>Bienvenue {{pseudo}}</p>
            <p>Solde:</p>
            <div class="solde">{{solde}} FCFA</div>
            <a href="/depot"><button class="btn">💰 Déposer</button></a>
            <a href="/chat"><button class="btn" style="background:#ff6b00">💬 Chat</button></a>
            <a href="/logout"><button class="btn" style="background:#ff4444">Déconnexion</button></a>
        </div>
    </body></html>
    ''', pseudo=session['pseudo'], solde=solde)

# Connexion/Inscription
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        pseudo = request.form['pseudo']
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE pseudo=?", (pseudo,))
        user = c.fetchone()
        if not user:
            c.execute("INSERT INTO users(pseudo,solde) VALUES(?,0)", (pseudo,))
            conn.commit()
        session['pseudo'] = pseudo
        conn.close()
        return redirect(url_for('home'))

    return render_template_string('''
    <!doctype html><html><head><title>Connexion</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body{font-family:Arial;background:#0a0a0a;color:#fff;display:flex;
    justify-content:center;align-items:center;height:100vh}
   .card{background:#1a1a1a;padding:30px;border-radius:15px;width:90%;max-width:350px}
    input,button{width:100%;padding:15px;margin:10px 0;border-radius:10px;border:none;font-size:16px}
    button{background:#00ff88;color:#000;font-weight:bold}</style></head>
    <body><div class="card"><h2>🔥 BetPro 229</h2>
    <form method="POST">
    <input name="pseudo" placeholder="Ton pseudo" required>
    <button type="submit">Commencer</button>
    </form></div></body></html>
    ''')

# Dépôt simulation CinetPay
@app.route('/depot', methods=['GET','POST'])
def depot():
    if 'pseudo' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        montant = float(request.form['montant'])
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        c.execute("UPDATE users SET solde=solde+? WHERE pseudo=?", (montant, session['pseudo']))
        c.execute("INSERT INTO depots(pseudo,montant,statut,date) VALUES(?,?,?,?)",
                  (session['pseudo'], montant, 'SIMULE', datetime.now()))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))

    return render_template_string('''
    <html><head><title>Dépôt</title><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body{font-family:Arial;background:#0a0a0a;color:#fff;padding:20px}
   .card{background:#1a1a1a;padding:20px;border-radius:15px;max-width:400px;margin:auto}
    input,button{width:100%;padding:15px;margin:10px 0;border-radius:10px;border:none;font-size:16px}
    button{background:#00ff88;color:#000;font-weight:bold}</style></head>
    <body><div class="card"><h2>💰 Dépôt Test</h2>
    <p>⚠️ Version test - argent fictif</p>
    <form method="POST">
    <input type="number" name="montant" placeholder="Montant FCFA" required min="100">
    <button type="submit">Simuler Dépôt</button>
    </form><br><a href="/">← Retour</a></div></body></html>
    ''')

# Chat
@app.route('/chat', methods=['GET','POST'])
def chat():
    if 'pseudo' not in session:
        return redirect(url_for('login'))

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    if request.method == 'POST':
        msg = request.form['msg']
        c.execute("INSERT INTO messages(pseudo,msg,date) VALUES(?,?,?)",
                  (session['pseudo'], msg, datetime.now()))
        conn.commit()

    c.execute("SELECT pseudo,msg,date FROM messages ORDER BY id DESC LIMIT 20")
    messages = c.fetchall()
    conn.close()

    return render_template_string('''
    <html><head><title>Chat</title><meta name="viewport" content="width=device-width, initial-scale=1">
    <style>body{font-family:Arial;background:#0a0a0a;color:#fff;padding:20px}
   .card{background:#1a1a1a;padding:20px;border-radius:15px;max-width:500px;margin:auto}
   .msg{margin:10px 0;padding:10px;background:#2a2a2a;border-radius:8px}
    input,button{padding:12px;border-radius:8px;border:none;margin:5px 0}
    input{width:70%} button{background:#00ff88;color:#000;font-weight:bold}</style></head>
    <body><div class="card"><h2>💬 Chat BetPro</h2>
    {% for p,m,d in messages %}
    <div class="msg"><b>{{p}}:</b> {{m}}<br><small>{{d}}</small></div>
    {% endfor %}
    <form method="POST">
    <input name="msg" placeholder="Tape ton message..." required>
    <button type="submit">Envoyer</button>
    </form><br><a href="/" style="color:#00ff88">← Retour</a></div></body></html>
    ''', messages=messages)

@app.route('/logout')
def logout():
    session.pop('pseudo', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
