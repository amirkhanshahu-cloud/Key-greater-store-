import os
import random
import string
import uuid
import urllib.parse
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# In-Memory Database (Orders store karne ke liye)
ORDERS = {}
ADMIN_PASSWORD = "809047"
UPI_ID = "6387982416-oa1b@axl"

def generate_madking_key():
    digits = ''.join(random.choices(string.digits, k=12))
    return f"MADKING-v2-{digits}"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KEY CREATER - Official Store</title>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Poppins', sans-serif;
            -webkit-tap-highlight-color: transparent;
        }

        body {
            background: radial-gradient(circle at 50% 10%, #111827 0%, #030712 100%);
            color: #f9fafb;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: flex-start;
            padding: 24px 14px 60px;
            overflow-x: hidden;
            position: relative;
        }

        /* Glowing background shapes */
        .ambient-glow {
            position: fixed;
            width: 320px;
            height: 320px;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(16, 185, 129, 0.18) 0%, rgba(59, 130, 246, 0.05) 70%, transparent 100%);
            filter: blur(50px);
            z-index: 0;
            animation: pulseGlow 8s infinite alternate ease-in-out;
            pointer-events: none;
        }
        @keyframes pulseGlow {
            0% { transform: scale(1) translate(-20px, -20px); opacity: 0.5; }
            100% { transform: scale(1.3) translate(30px, 30px); opacity: 0.9; }
        }

        /* Liquid Glassmorphism container */
        .liquid-glass {
            position: relative;
            z-index: 1;
            background: rgba(17, 24, 39, 0.65);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.6), inset 0 1px 1px rgba(255, 255, 255, 0.15);
            border-radius: 24px;
        }

        header {
            z-index: 1;
            text-align: center;
            margin-bottom: 28px;
        }

        h1.title {
            font-size: 2.2rem;
            font-weight: 800;
            letter-spacing: 2px;
            background: linear-gradient(135deg, #38ef7d, #11998e, #00d2ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-transform: uppercase;
            text-shadow: 0 5px 20px rgba(16, 185, 129, 0.3);
        }

        p.subtitle {
            font-size: 0.9rem;
            color: #9ca3af;
            margin-top: 4px;
        }

        /* Views */
        .view-section {
            width: 100%;
            max-width: 480px;
            display: none;
            animation: fadeIn 0.4s ease-in-out forwards;
            z-index: 1;
        }
        .view-section.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(14px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* Cards Grid */
        .plans-grid {
            display: flex;
            flex-direction: column;
            gap: 16px;
            width: 100%;
        }

        .plan-card {
            padding: 18px 20px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .plan-card:hover {
            transform: translateY(-2px);
            border-color: rgba(56, 239, 125, 0.4);
            box-shadow: 0 10px 25px -3px rgba(16, 185, 129, 0.25);
        }

        .badge-discount {
            position: absolute;
            top: 0;
            right: 0;
            background: linear-gradient(135deg, #ef4444, #f59e0b);
            color: #fff;
            font-size: 0.65rem;
            font-weight: 800;
            padding: 3px 12px;
            border-bottom-left-radius: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            box-shadow: 0 2px 8px rgba(239, 68, 68, 0.4);
        }

        .plan-info h3 {
            font-size: 1.15rem;
            font-weight: 700;
            color: #f3f4f6;
        }
        .plan-info .price {
            font-size: 1.35rem;
            font-weight: 800;
            color: #10b981;
            margin-top: 4px;
        }
        .old-price {
            font-size: 0.85rem;
            color: #6b7280;
            text-decoration: line-through;
            margin-left: 6px;
            font-weight: 400;
        }

        .btn-buy {
            background: linear-gradient(135deg, #10b981, #059669);
            color: #fff;
            border: none;
            outline: none;
            padding: 10px 22px;
            border-radius: 14px;
            font-weight: 700;
            font-size: 0.95rem;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
            transition: 0.2s transform, 0.2s opacity;
        }
        .btn-buy:active {
            transform: scale(0.96);
        }

        /* Countdown Overlay Modal */
        #timer-modal {
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(10px);
            display: none;
            align-items: center;
            justify-content: center;
            z-index: 1000;
            flex-direction: column;
        }
        .timer-circle {
            width: 100px;
            height: 100px;
            border-radius: 50%;
            border: 4px solid #10b981;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2.8rem;
            font-weight: 800;
            color: #10b981;
            box-shadow: 0 0 30px rgba(16, 185, 129, 0.6);
            animation: pulseCircle 1s infinite alternate;
        }
        @keyframes pulseCircle {
            0% { transform: scale(1); }
            100% { transform: scale(1.08); }
        }

        /* Form elements */
        .form-box {
            padding: 24px 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .input-group label {
            display: block;
            font-size: 0.85rem;
            font-weight: 600;
            color: #9ca3af;
            margin-bottom: 6px;
        }
        .input-group input {
            width: 100%;
            background: rgba(31, 41, 55, 0.7);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 12px 14px;
            border-radius: 12px;
            color: #fff;
            outline: none;
            font-size: 0.95rem;
            transition: border 0.2s;
        }
        .input-group input:focus {
            border-color: #10b981;
            box-shadow: 0 0 10px rgba(16, 185, 129, 0.2);
        }

        .btn-submit {
            background: linear-gradient(135deg, #2563eb, #1d4ed8);
            border: none;
            color: white;
            padding: 14px;
            font-size: 1rem;
            font-weight: 700;
            border-radius: 14px;
            cursor: pointer;
            box-shadow: 0 5px 20px rgba(37, 99, 235, 0.4);
            margin-top: 6px;
        }

        /* Payment Screen */
        .payment-box {
            padding: 26px 20px;
            text-align: center;
        }
        .qr-wrapper {
            background: #ffffff;
            padding: 12px;
            border-radius: 18px;
            display: inline-block;
            margin: 16px 0;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }
        .qr-wrapper img {
            display: block;
            width: 210px;
            height: 210px;
            border-radius: 10px;
        }

        .warning-pill {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #f87171;
            padding: 8px 14px;
            border-radius: 10px;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 14px;
            display: inline-block;
        }

        .countdown-text {
            font-size: 1.15rem;
            font-weight: 700;
            color: #fbbf24;
            margin: 10px 0 16px;
            letter-spacing: 1px;
        }

        .btn-phonepe {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            width: 100%;
            background: rgba(10, 10, 12, 0.85);
            border: 1px solid rgba(103, 58, 183, 0.5);
            color: #ffffff;
            text-decoration: none;
            padding: 14px;
            border-radius: 16px;
            font-weight: 700;
            font-size: 1rem;
            box-shadow: 0 8px 25px rgba(103, 58, 183, 0.35);
            transition: all 0.2s;
        }
        .btn-phonepe:hover {
            border-color: #7c3aed;
            transform: scale(0.99);
        }

        /* Success & Key Screen */
        .success-box {
            padding: 28px 20px;
            text-align: center;
        }
        .success-badge {
            color: #10b981;
            font-size: 1.4rem;
            font-weight: 800;
            margin-bottom: 16px;
            text-transform: uppercase;
        }
        .key-container {
            background: rgba(0, 0, 0, 0.6);
            border: 1px dashed #10b981;
            padding: 16px 12px;
            border-radius: 14px;
            font-family: monospace;
            font-size: 1.1rem;
            color: #34d399;
            font-weight: 700;
            margin: 18px 0;
            word-break: break-all;
            letter-spacing: 1px;
        }
        .btn-copy {
            background: #10b981;
            color: #000;
            font-weight: 800;
            border: none;
            padding: 12px 24px;
            border-radius: 12px;
            cursor: pointer;
            width: 100%;
            font-size: 0.95rem;
            box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
        }

        /* Hidden Admin Trigger (Small Green Dot) */
        #admin-trigger-dot {
            position: fixed;
            bottom: 12px;
            left: 12px;
            width: 9px;
            height: 9px;
            background-color: #10b981;
            border-radius: 50%;
            cursor: pointer;
            opacity: 0.6;
            z-index: 999;
            box-shadow: 0 0 6px #10b981;
        }
        #admin-trigger-dot:hover {
            opacity: 1;
            transform: scale(1.3);
        }

        /* Admin Page UI */
        .admin-table-wrapper {
            overflow-x: auto;
            margin-top: 14px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.85rem;
        }
        th, td {
            padding: 12px 8px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        th {
            color: #9ca3af;
            font-weight: 600;
        }
        .btn-approve {
            background: #eab308;
            color: #000;
            font-weight: 700;
            border: none;
            padding: 6px 14px;
            border-radius: 8px;
            cursor: pointer;
            box-shadow: 0 2px 10px rgba(234, 179, 8, 0.3);
        }
    </style>
</head>
<body>

    <div class="ambient-glow"></div>

    <header>
        <h1 class="title">KEY CREATER</h1>
        <p class="subtitle">Fast, Secure & Instant Key Generation</p>
    </header>

    <!-- 1. USER STORE PAGE -->
    <section id="view-store" class="view-section active">
        <div class="plans-grid">
            
            <!-- 3 Days -->
            <div class="liquid-glass plan-card">
                <div class="plan-info">
                    <h3>3 Days Access</h3>
                    <div class="price">₹50</div>
                </div>
                <button class="btn-buy" onclick="startPurchase('3 Days', 50)">Buy Key</button>
            </div>

            <!-- 7 Days -->
            <div class="liquid-glass plan-card">
                <div class="plan-info">
                    <h3>7 Days Access</h3>
                    <div class="price">₹100</div>
                </div>
                <button class="btn-buy" onclick="startPurchase('7 Days', 100)">Buy Key</button>
            </div>

            <!-- 15 Days -->
            <div class="liquid-glass plan-card">
                <div class="plan-info">
                    <h3>15 Days Access</h3>
                    <div class="price">₹200</div>
                </div>
                <button class="btn-buy" onclick="startPurchase('15 Days', 200)">Buy Key</button>
            </div>

            <!-- 90 Days (Offer) -->
            <div class="liquid-glass plan-card">
                <div class="badge-discount">🔥 50% OFF</div>
                <div class="plan-info">
                    <h3>90 Days Access</h3>
                    <div class="price">₹600 <span class="old-price">₹1200</span></div>
                </div>
                <button class="btn-buy" onclick="startPurchase('90 Days (Offer)', 600)">Buy Key</button>
            </div>

            <!-- Permanent (Offer) -->
            <div class="liquid-glass plan-card">
                <div class="badge-discount">👑 VIP DEAL</div>
                <div class="plan-info">
                    <h3>Permanent Key</h3>
                    <div class="price">₹2000 <span class="old-price">₹4500</span></div>
                </div>
                <button class="btn-buy" onclick="startPurchase('Permanent (Offer)', 2000)">Buy Key</button>
            </div>

        </div>
    </section>

    <!-- 4-SECOND TIMER MODAL -->
    <div id="timer-modal">
        <div class="timer-circle" id="countdown-val">4</div>
        <p style="margin-top: 18px; font-weight: 600; color: #d1d5db;">Redirecting to Order Details...</p>
    </div>

    <!-- 2. USER DETAILS INPUT FORM -->
    <section id="view-details" class="view-section">
        <div class="liquid-glass form-box">
            <h2 style="font-size: 1.25rem; font-weight: 700; color:#10b981;">Order Details</h2>
            <div style="font-size: 0.85rem; color:#9ca3af;" id="selected-plan-text">Selected: </div>
            
            <div class="input-group">
                <label>Free Fire (FF) UID</label>
                <input type="text" id="user-uid" placeholder="Enter your FF UID (e.g. 19283746)" required>
            </div>

            <div class="input-group">
                <label>Name on PhonePe Account</label>
                <input type="text" id="user-phonepe-name" placeholder="Name as shown on PhonePe" required>
            </div>

            <button class="btn-submit" onclick="submitOrderDetails()">Proceed To Pay</button>
        </div>
    </section>

    <!-- 3. QR PAYMENT & TIMER PAGE -->
    <section id="view-payment" class="view-section">
        <div class="liquid-glass payment-box">
            <div class="warning-pill">⚠️ Warning: Only Pay via PhonePe</div>

            <div class="qr-wrapper">
                <img id="qr-code-img" src="" alt="Payment QR Code">
            </div>

            <div style="font-weight: 700; font-size: 1.1rem; color: #f3f4f6;">Amount: <span id="pay-amount" style="color: #10b981;"></span></div>
            <div style="font-size: 0.8rem; color: #9ca3af; margin-top: 4px;">Only use for payment PhonePe</div>

            <div class="countdown-text" id="pay-timer">Time Left: 15:00</div>

            <!-- Liquid Glass Black PhonePe Button -->
            <a href="#" id="phonepe-deep-link" class="btn-phonepe">
                <span>📱 Open PhonePe App</span>
            </a>
        </div>
    </section>

    <!-- 4. KEY GENERATED SUCCESS VIEW -->
    <section id="view-success" class="view-section">
        <div class="liquid-glass success-box">
            <div class="success-badge">✅ Successful Key Generated</div>
            <p style="font-size: 0.85rem; color: #9ca3af;">Aapki key live generate ho chuki hai. Neeche se copy karein:</p>

            <div class="key-container" id="generated-key-box">MADKING-v2-XXXXXXXXXXXX</div>

            <button class="btn-copy" onclick="copyKeyToClipboard()">📋 Copy Key</button>
        </div>
    </section>

    <!-- 5. SECURE ADMIN VIEW -->
    <section id="view-admin" class="view-section" style="max-width: 650px;">
        <div class="liquid-glass form-box">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h2 style="font-size: 1.25rem; font-weight: 700; color: #eab308;">Admin Control Center</h2>
                <button onclick="switchView('view-store')" style="background: none; border: 1px solid rgba(255,255,255,0.2); color:#fff; border-radius:8px; padding: 4px 10px; cursor: pointer; font-size:0.75rem;">Exit</button>
            </div>

            <div class="admin-table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>PhonePe Name</th>
                            <th>UID</th>
                            <th>Plan / Price</th>
                            <th>Status / Action</th>
                        </tr>
                    </thead>
                    <tbody id="admin-orders-list">
                        <!-- Loaded dynamically -->
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <!-- Hidden Green Dot for Admin Portal -->
    <div id="admin-trigger-dot" title="" onclick="promptAdminLogin()"></div>

    <script>
        let currentPlan = null;
        let currentPrice = 0;
        let activeOrderId = null;
        let payTimerInterval = null;
        let pollStatusInterval = null;

        function switchView(viewId) {
            document.querySelectorAll('.view-section').forEach(sec => sec.classList.remove('active'));
            document.getElementById(viewId).classList.add('active');
            window.scrollTo({ top: 0, behavior: 'smooth' });
        }

        // STEP 1: Buy Click -> 4-Second Countdown
        function startPurchase(planName, price) {
            currentPlan = planName;
            currentPrice = price;

            const modal = document.getElementById('timer-modal');
            const countdownEl = document.getElementById('countdown-val');
            modal.style.display = 'flex';

            let count = 4;
            countdownEl.innerText = count;

            const interval = setInterval(() => {
                count--;
                if (count > 0) {
                    countdownEl.innerText = count;
                } else {
                    clearInterval(interval);
                    modal.style.display = 'none';
                    document.getElementById('selected-plan-text').innerText = `Selected Plan: ${currentPlan} - ₹${currentPrice}`;
                    switchView('view-details');
                }
            }, 1000);
        }

        // STEP 2: Submit Details & Generate Order
        async function submitOrderDetails() {
            const uid = document.getElementById('user-uid').value.trim();
            const phonepeName = document.getElementById('user-phonepe-name').value.trim();

            if (!uid || !phonepeName) {
                alert("Kripya saari details (FF UID aur PhonePe Name) fill karein.");
                return;
            }

            const response = await fetch('/api/create-order', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    plan: currentPlan,
                    price: currentPrice,
                    uid: uid,
                    phonepe_name: phonepeName
                })
            });

            const data = await response.json();
            if (data.success) {
                activeOrderId = data.order_id;
                document.getElementById('pay-amount').innerText = `₹${currentPrice}`;
                document.getElementById('qr-code-img').src = data.qr_url;
                document.getElementById('phonepe-deep-link').href = data.phonepe_intent;

                switchView('view-payment');
                start15MinuteTimer();
                startCheckingApproval();
            }
        }

        // STEP 3: 15-Minute Timer
        function start15MinuteTimer() {
            let totalSeconds = 15 * 60;
            const timerEl = document.getElementById('pay-timer');

            if (payTimerInterval) clearInterval(payTimerInterval);

            payTimerInterval = setInterval(() => {
                totalSeconds--;
                if (totalSeconds <= 0) {
                    clearInterval(payTimerInterval);
                    timerEl.innerText = "Time Expired!";
                    alert("Payment window expired. Please try again.");
                    switchView('view-store');
                } else {
                    const minutes = Math.floor(totalSeconds / 60);
                    const seconds = totalSeconds % 60;
                    timerEl.innerText = `Time Left: ${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
                }
            }, 1000);
        }

        // Live check if Admin approved
        function startCheckingApproval() {
            if (pollStatusInterval) clearInterval(pollStatusInterval);

            pollStatusInterval = setInterval(async () => {
                if (!activeOrderId) return;

                const res = await fetch(`/api/order-status/${activeOrderId}`);
                const data = await res.json();

                if (data.status === 'approved') {
                    clearInterval(pollStatusInterval);
                    clearInterval(payTimerInterval);

                    document.getElementById('generated-key-box').innerText = data.key;
                    switchView('view-success');
                }
            }, 2500);
        }

        // Copy Key to Clipboard
        function copyKeyToClipboard() {
            const keyText = document.getElementById('generated-key-box').innerText;
            navigator.clipboard.writeText(keyText).then(() => {
                alert("Key clipboard par copy ho gayi: " + keyText);
            });
        }

        // STEP 4: Admin Access via Small Green Dot
        function promptAdminLogin() {
            const pass = prompt("Enter Admin Secure PIN:");
            if (pass === "809047") {
                loadAdminOrders();
                switchView('view-admin');
            } else if (pass !== null) {
                alert("Access Denied! Incorrect PIN.");
            }
        }

        async function loadAdminOrders() {
            const res = await fetch('/api/admin/orders?pin=809047');
            const orders = await res.json();
            const tbody = document.getElementById('admin-orders-list');
            tbody.innerHTML = '';

            if (orders.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:#6b7280; padding:18px;">No pending orders found.</td></tr>';
                return;
            }

            orders.reverse().forEach(o => {
                const tr = document.createElement('tr');
                const actionBtn = o.status === 'pending' 
                    ? `<button class="btn-approve" onclick="approveOrder('${o.id}')">Approve</button>`
                    : `<span style="color:#10b981; font-weight:700;">Approved</span>`;

                tr.innerHTML = `
                    <td><strong>${o.phonepe_name}</strong></td>
                    <td style="color:#9ca3af;">${o.uid}</td>
                    <td>₹${o.price} <br><small style="color:#6b7280;">${o.plan}</small></td>
                    <td>${actionBtn}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        async function approveOrder(orderId) {
            const res = await fetch('/api/admin/approve', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pin: '809047', order_id: orderId })
            });
            const data = await res.json();
            if (data.success) {
                loadAdminOrders();
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/create-order', methods=['POST'])
def create_order():
    data = request.json or {}
    order_id = str(uuid.uuid4())[:8]

    price = data.get('price', 50)
    phonepe_name = data.get('phonepe_name', 'Unknown')
    uid = data.get('uid', 'Unknown')
    plan = data.get('plan', '3 Days')

    # UPI Intent Deep Link for PhonePe
    # Note: UPI ID is included in deep link so PhonePe automatically opens with the ID and exact amount
    upi_intent = (
        f"upi://pay?pa={UPI_ID}"
        f"&pn=KEY%20CREATER"
        f"&am={price}"
        f"&cu=INR"
        f"&tn=KeyOrder_{order_id}"
    )

    # Standard QR Image URL via clean QR Generator API
    encoded_upi = urllib.parse.quote(upi_intent)
    qr_url = f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={encoded_upi}"

    ORDERS[order_id] = {
        "id": order_id,
        "plan": plan,
        "price": price,
        "uid": uid,
        "phonepe_name": phonepe_name,
        "status": "pending",
        "key": None
    }

    return jsonify({
        "success": True,
        "order_id": order_id,
        "qr_url": qr_url,
        "phonepe_intent": upi_intent
    })

@app.route('/api/order-status/<order_id>', methods=['GET'])
def order_status(order_id):
    order = ORDERS.get(order_id)
    if not order:
        return jsonify({"status": "not_found"}), 404
    return jsonify({
        "status": order["status"],
        "key": order.get("key")
    })

@app.route('/api/admin/orders', methods=['GET'])
def get_admin_orders():
    pin = request.args.get('pin')
    if pin != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 403
    return jsonify(list(ORDERS.values()))

@app.route('/api/admin/approve', methods=['POST'])
def approve_order():
    data = request.json or {}
    pin = data.get('pin')
    order_id = data.get('order_id')

    if pin != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 403

    if order_id in ORDERS:
        ORDERS[order_id]["status"] = "approved"
        ORDERS[order_id]["key"] = generate_madking_key()
        return jsonify({"success": True, "key": ORDERS[order_id]["key"]})

    return jsonify({"error": "Order not found"}), 404

if __name__ == '__main__':
    # Render.com automatic dynamic PORT detection
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
