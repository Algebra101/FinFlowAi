const API_BASE = "http://localhost:8000/api";

// DOM Elements
const loginScreen = document.getElementById("login-screen");
const appScreen = document.getElementById("app-screen");
const emailStep = document.getElementById("email-step");
const otpStep = document.getElementById("otp-step");

const loginEmail = document.getElementById("login-email");
const loginOtp = document.getElementById("login-otp");
const btnSendOtp = document.getElementById("btn-send-otp");
const btnVerifyOtp = document.getElementById("btn-verify-otp");
const btnBackEmail = document.getElementById("btn-back-email");
const loginMessage = document.getElementById("login-message");

const displayBizName = document.getElementById("display-biz-name");
const displayEmail = document.getElementById("display-email");
const btnLogout = document.getElementById("btn-logout");

const navBtns = document.querySelectorAll(".nav-btn");
const viewSections = document.querySelectorAll(".view-section");

// State
let currentEmail = "";
let currentSmeId = null;
let currentBizName = "";

// Toast Helper
function showToast(message, isError = false) {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.style.borderLeftColor = isError ? "var(--danger)" : "var(--success)";
    toast.classList.add("show");
    setTimeout(() => toast.classList.remove("show"), 3000);
}

// ==========================================
// AUTHENTICATION (IDENTITY SERVICE)
// ==========================================
btnSendOtp.addEventListener("click", async () => {
    const email = loginEmail.value.trim();
    if (!email) return showToast("Please enter your email", true);

    btnSendOtp.textContent = "Sending...";
    btnSendOtp.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/send-otp`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email, purpose: "login" })
        });
        const data = await res.json();
        
        if (!res.ok) throw new Error(data.detail || "Failed to send OTP");

        currentEmail = email;
        emailStep.classList.remove("active");
        otpStep.classList.add("active");
        loginMessage.textContent = "";
        
        // Demo helper: Auto-fill OTP if backend returned hint
        if (data.hint_for_testing) {
            loginOtp.value = data.hint_for_testing;
            showToast(`[Demo] OTP is ${data.hint_for_testing}`);
        } else {
            showToast("OTP sent to your email");
        }
    } catch (err) {
        loginMessage.textContent = err.message;
    } finally {
        btnSendOtp.textContent = "Send Verification Code";
        btnSendOtp.disabled = false;
    }
});

btnVerifyOtp.addEventListener("click", async () => {
    const otp = loginOtp.value.trim();
    if (otp.length !== 6) return showToast("Enter a 6-digit code", true);

    btnVerifyOtp.textContent = "Verifying...";
    btnVerifyOtp.disabled = true;

    try {
        const res = await fetch(`${API_BASE}/verify-otp`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: currentEmail, otp })
        });
        const data = await res.json();

        if (!res.ok) throw new Error(data.detail || "Invalid OTP");

        // Login Success
        currentSmeId = data.sme_id;
        currentBizName = data.business_name;
        
        loginScreen.classList.remove("active");
        appScreen.classList.add("active");
        
        displayBizName.textContent = currentBizName;
        displayEmail.textContent = currentEmail;
        
        showToast("Welcome to FinCore AI!");
        loadDashboardData();
        
    } catch (err) {
        loginMessage.textContent = err.message;
    } finally {
        btnVerifyOtp.textContent = "Verify Identity";
        btnVerifyOtp.disabled = false;
    }
});

btnBackEmail.addEventListener("click", () => {
    otpStep.classList.remove("active");
    emailStep.classList.add("active");
    loginOtp.value = "";
    loginMessage.textContent = "";
});

btnLogout.addEventListener("click", () => {
    currentSmeId = null;
    currentEmail = "";
    appScreen.classList.remove("active");
    loginScreen.classList.add("active");
    otpStep.classList.remove("active");
    emailStep.classList.add("active");
    loginOtp.value = "";
});

// ==========================================
// NAVIGATION
// ==========================================
navBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        navBtns.forEach(b => b.classList.remove("active"));
        viewSections.forEach(s => s.classList.remove("active"));
        
        btn.classList.add("active");
        document.getElementById(btn.dataset.target).classList.add("active");
    });
});

// ==========================================
// DATA LOADING
// ==========================================
async function loadDashboardData() {
    try {
        // 1. Fetch Connected Banks
        const banksRes = await fetch(`${API_BASE}/mono/linked-accounts/${currentSmeId}`);
        const banksData = await banksRes.json();
        
        const accounts = banksData.accounts || [];
        let totalBalance = 0;
        
        // Populate Bank Grid
        const bankGrid = document.getElementById("bank-accounts-grid");
        bankGrid.innerHTML = "";
        
        accounts.forEach(acct => {
            totalBalance += acct.balance;
            bankGrid.innerHTML += `
                <div class="bank-card glass-panel">
                    <i class="ri-bank-line bank-icon"></i>
                    <h4>${acct.bank_name}</h4>
                    <p>${acct.label} (${acct.account_number})</p>
                    <div class="bal">₦${acct.balance.toLocaleString('en-US', {minimumFractionDigits: 2})}</div>
                </div>
            `;
        });
        
        document.getElementById("dash-total-balance").textContent = `₦${totalBalance.toLocaleString('en-US', {minimumFractionDigits: 2})}`;
        
        // Mock Virtual Account for Demo since Gateway doesn't expose it
        const mockVAs = {"ideaa8841@gmail.com": "1691693318", "ibraheemsalam06@gmail.com": "6591999562"};
        document.getElementById("dash-virtual-account").textContent = mockVAs[currentEmail] || "0123456789";

        // 2. Fetch Transactions (for first linked account)
        if (accounts.length > 0) {
            const txnsRes = await fetch(`${API_BASE}/mono/transactions/${accounts[0].account_number}`);
            const txnsData = await txnsRes.json();
            
            const tbody = document.getElementById("dash-txns-body");
            tbody.innerHTML = "";
            
            const txns = (txnsData.data || []).slice(0, 10);
            txns.forEach(t => {
                const isCredit = t.type === 'credit';
                tbody.innerHTML += `
                    <tr>
                        <td>${new Date(t.date).toLocaleDateString()}</td>
                        <td>${t.narration}</td>
                        <td class="amt ${isCredit ? 'credit' : 'debit'}">
                            ${isCredit ? '+' : '-'}₦${(t.amount/100).toLocaleString('en-US', {minimumFractionDigits: 2})}
                        </td>
                    </tr>
                `;
            });
            
            // 3. Fetch Forecast for that account
            fetchForecast(accounts[0].account_number);
        }

        // 4. Fetch Risk & Credit
        const creditRes = await fetch(`${API_BASE}/credit/score/${currentSmeId}`);
        const creditData = await creditRes.json();
        document.getElementById("risk-score").textContent = creditData.score || "--";
        document.getElementById("risk-band").textContent = creditData.risk_band || "--";
        document.getElementById("risk-limit").textContent = creditData.eligible_limit ? `₦${creditData.eligible_limit.toLocaleString()}` : "₦0.00";

        // 5. Fetch Fraud Summary
        const fraudRes = await fetch(`${API_BASE}/fraud/risk-summary/${currentSmeId}`);
        const fraudData = await fraudRes.json();
        
        const cscoreTier = (fraudData.overall_risk && fraudData.overall_risk.includes("HIGH")) ? "RED" : 
                           (fraudData.overall_risk && fraudData.overall_risk.includes("MODERATE")) ? "ORANGE" : "GREEN";
        
        const circle = document.getElementById("dash-cscore-circle");
        circle.className = `score-circle ${cscoreTier.toLowerCase()}`;
        document.getElementById("dash-cscore-tier").textContent = cscoreTier;
        
        const flagCount = fraudData.breakdown ? fraudData.breakdown.total_flags : 0;
        document.getElementById("dash-fraud-status").textContent = flagCount > 0 ? `${flagCount} flagged anomalies detected.` : "No anomalies detected.";

    } catch (err) {
        console.error("Error loading dashboard:", err);
        showToast("Error loading dashboard data", true);
    }
}

// ==========================================
// CHART.JS FORECASTING
// ==========================================
let forecastChartInstance = null;

async function fetchForecast(accountId) {
    try {
        const res = await fetch(`${API_BASE}/forecast/${accountId}?days=30`);
        const data = await res.json();
        
        const forecast = data.forecast || [];
        if (forecast.length === 0) return;

        const labels = forecast.map(f => new Date(f.date).toLocaleDateString(undefined, {month: 'short', day: 'numeric'}));
        const balances = forecast.map(f => f.projected_balance);

        const ctx = document.getElementById('forecastChart').getContext('2d');
        
        if (forecastChartInstance) {
            forecastChartInstance.destroy();
        }

        forecastChartInstance = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Projected Balance (Delta PINNs)',
                    data: balances,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false }
                },
                scales: {
                    y: {
                        grid: { color: 'rgba(255,255,255,0.05)' },
                        ticks: { color: '#94a3b8' }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { color: '#94a3b8', maxTicksLimit: 10 }
                    }
                }
            }
        });
    } catch (err) {
        console.error("Error loading forecast chart:", err);
    }
}
