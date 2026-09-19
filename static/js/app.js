/**
 * BloodChain AI - Frontend Application Controller
 * Handles interactive navigation, Chart.js instances,
 * and seamless integration with the Flask REST APIs.
 */

let predictionChartInstance = null;
let reportsBarChartInstance = null;
let reportsDonutChartInstance = null;
let currentViewId = "viewDashboard";

const VIEW_METADATA = {
    viewDashboard: {
        title: "Dashboard",
        subtitle: "Monitor blood inventory, demand and distribution at a glance."
    },
    viewInventory: {
        title: "Blood Inventory",
        subtitle: "Manage all blood groups, record expiry dates, and monitor stock warnings."
    },
    viewAIPrediction: {
        title: "AI Demand Prediction",
        subtitle: "Predict future blood demand using hospital data and usage patterns."
    },
    viewDistribution: {
        title: "Smart Distribution",
        subtitle: "Match supply with hospital demand using AI optimization."
    },
    viewAlerts: {
        title: "Alerts",
        subtitle: "Stay updated with critical stock levels, expiry dates and system alerts."
    },
    viewReports: {
        title: "Reports",
        subtitle: "Visual insights for better decision making."
    }
};

document.addEventListener("DOMContentLoaded", () => {
    initEventListeners();
    loadDashboardData();
    loadAlertsData();
});

function initEventListeners() {
    // Login Form
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", (e) => {
            e.preventDefault();
            const userType = document.getElementById("loginUserType").value;
            document.getElementById("currentUserLabel").textContent = userType;
            document.getElementById("viewLogin").classList.add("hidden");
            document.getElementById("appContainer").classList.remove("hidden");
            switchView("viewDashboard");
            showToast(`Logged in as ${userType}`);
        });
    }

    // Logout
    const btnLogout = document.getElementById("btnLogout");
    if (btnLogout) {
        btnLogout.addEventListener("click", () => {
            document.getElementById("appContainer").classList.add("hidden");
            document.getElementById("viewLogin").classList.remove("hidden");
            showToast("Logged out successfully");
        });
    }

    // Sidebar navigation
    document.querySelectorAll(".nav-item").forEach(btn => {
        btn.addEventListener("click", () => {
            const targetView = btn.getAttribute("data-view");
            if (targetView) switchView(targetView);
        });
    });

    // Top Bell icon -> Alerts
    const btnBell = document.getElementById("btnBellAlerts");
    if (btnBell) {
        btnBell.addEventListener("click", () => switchView("viewAlerts"));
    }

    // Prediction controls
    const btnPredict = document.getElementById("btnRunPrediction");
    if (btnPredict) {
        btnPredict.addEventListener("click", runPrediction);
    }
    const predictBgSelect = document.getElementById("predictBloodGroupSelect");
    if (predictBgSelect) {
        predictBgSelect.addEventListener("change", runPrediction);
    }

    // Approve distribution
    const btnApproveDist = document.getElementById("btnApproveDistribution");
    if (btnApproveDist) {
        btnApproveDist.addEventListener("click", approveDistributionAction);
    }

    // Modal controls for Inventory
    const btnOpenAdd = document.getElementById("btnOpenAddModal");
    if (btnOpenAdd) {
        btnOpenAdd.addEventListener("click", () => {
            document.getElementById("addStockModal").classList.remove("hidden");
        });
    }

    const btnOpenIssue = document.getElementById("btnOpenIssueModal");
    if (btnOpenIssue) {
        btnOpenIssue.addEventListener("click", () => {
            document.getElementById("issueStockModal").classList.remove("hidden");
        });
    }

    // Form: Add Stock
    const formAdd = document.getElementById("formAddStock");
    if (formAdd) {
        formAdd.addEventListener("submit", async (e) => {
            e.preventDefault();
            const bg = document.getElementById("addBloodGroup").value;
            const units = document.getElementById("addUnits").value;
            const facility = document.getElementById("addFacilityName").value;
            const exp = document.getElementById("addExpiryDate").value;

            try {
                const res = await fetch("/api/inventory", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ blood_group: bg, units: units, facility_name: facility, expiry_date: exp })
                });
                const result = await res.json();
                if (result.success) {
                    showToast(result.message);
                    closeModals();
                    loadFullInventory();
                    loadDashboardData();
                }
            } catch (err) {
                console.error("Add inventory error:", err);
            }
        });
    }

    // Form: Issue Stock
    const formIssue = document.getElementById("formIssueStock");
    if (formIssue) {
        formIssue.addEventListener("submit", async (e) => {
            e.preventDefault();
            const bg = document.getElementById("issueBloodGroup").value;
            const units = document.getElementById("issueUnits").value;

            try {
                const res = await fetch("/api/inventory/issue", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ blood_group: bg, units: units })
                });
                const result = await res.json();
                if (result.success) {
                    showToast(result.message);
                    closeModals();
                    loadFullInventory();
                    loadDashboardData();
                } else {
                    alert(result.error || "Issue failed");
                }
            } catch (err) {
                console.error("Issue inventory error:", err);
            }
        });
    }

    // Reset Demo
    const btnReset = document.getElementById("btnResetDemoData");
    if (btnReset) {
        btnReset.addEventListener("click", async () => {
            if (!confirm("Reset demo data to initial baseline?")) return;
            await fetch("/api/reset-demo", { method: "POST" });
            location.reload();
        });
    }
}

function closeModals() {
    const addM = document.getElementById("addStockModal");
    const issueM = document.getElementById("issueStockModal");
    if (addM) addM.classList.add("hidden");
    if (issueM) issueM.classList.add("hidden");
}

function switchView(viewId) {
    currentViewId = viewId;

    const meta = VIEW_METADATA[viewId] || { title: "BloodChain AI", subtitle: "" };
    document.getElementById("topPageTitle").textContent = meta.title;
    document.getElementById("topPageSubtitle").textContent = meta.subtitle;

    document.querySelectorAll(".view-panel").forEach(p => p.classList.add("hidden"));
    const target = document.getElementById(viewId);
    if (target) target.classList.remove("hidden");

    document.querySelectorAll(".nav-item").forEach(btn => {
        if (btn.getAttribute("data-view") === viewId) {
            btn.classList.add("active", "bg-blue-600", "text-white");
            btn.classList.remove("text-slate-300", "hover:bg-slate-800");
        } else {
            btn.classList.remove("active", "bg-blue-600", "text-white");
            btn.classList.add("text-slate-300", "hover:bg-slate-800");
        }
    });

    if (viewId === "viewAIPrediction") {
        runPrediction();
    } else if (viewId === "viewReports") {
        loadReportsCharts();
    } else if (viewId === "viewInventory") {
        loadFullInventory();
    } else if (viewId === "viewAlerts") {
        loadAlertsData();
    }

    lucide.createIcons();
}

// ----------------------------------------------------
// 1. DASHBOARD DATA
// ----------------------------------------------------
async function loadDashboardData() {
    try {
        const res = await fetch("/api/dashboard");
        const data = await res.json();

        document.getElementById("dashTotalUnits").textContent = data.total_units;
        document.getElementById("dashHospitalsCount").textContent = data.hospitals_connected;
        document.getElementById("dashBloodBanksCount").textContent = data.blood_banks_connected;
        document.getElementById("dashAlertsCount").textContent = data.active_alerts_count;
        document.getElementById("navAlertBadge").textContent = data.active_alerts_count;

        const tbody = document.getElementById("dashInventoryTableBody");
        tbody.innerHTML = "";

        data.inventory_table.forEach(row => {
            let statusBadge = "";
            if (row.status === "Normal") {
                statusBadge = `<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700">Normal</span>`;
            } else if (row.status === "Low") {
                statusBadge = `<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700">Low</span>`;
            } else {
                statusBadge = `<span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-700">Critical</span>`;
            }

            const tr = document.createElement("tr");
            tr.className = "hover:bg-slate-50 transition";
            tr.innerHTML = `
                <td class="py-3.5 font-bold text-slate-900">${row.blood_group}</td>
                <td class="py-3.5">${row.available_units}</td>
                <td class="py-3.5">${statusBadge}</td>
                <td class="py-3.5 ${row.expiring_soon > 0 ? 'text-amber-600 font-semibold' : 'text-slate-400'}">${row.expiring_soon}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Failed to load dashboard data:", err);
    }
}

// ----------------------------------------------------
// 2. AI PREDICTION
// ----------------------------------------------------
async function runPrediction() {
    const hospitalId = document.getElementById("predictHospitalSelect").value;
    const bloodGroup = document.getElementById("predictBloodGroupSelect").value;
    const period = document.getElementById("predictPeriodSelect").value;

    try {
        const res = await fetch("/api/predict", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ blood_group: bloodGroup, hospital_id: hospitalId, prediction_period: period })
        });
        const data = await res.json();

        document.getElementById("predCurrentStock").innerHTML = `${data.current_stock} <span class="text-xs font-normal text-slate-400">units</span>`;
        document.getElementById("predPredictedDemand").innerHTML = `${data.predicted_demand} <span class="text-xs font-normal text-slate-400">units</span>`;
        document.getElementById("predExpectedShortage").innerHTML = `${data.shortage} <span class="text-xs font-normal text-red-400">units</span>`;

        document.getElementById("predChartTitle").textContent = `Demand Forecast (${data.blood_group})`;
        document.getElementById("predRecommendationText").textContent = data.recommendation;

        renderPredictionLineChart(data);
    } catch (err) {
        console.error("Prediction error:", err);
    }
}

function renderPredictionLineChart(data) {
    const ctx = document.getElementById("predictionLineChart").getContext("2d");
    if (predictionChartInstance) predictionChartInstance.destroy();

    const past = [35, 48, 46, 62, null, null, null];
    const pred = [null, null, null, 62, 82, 98, data.predicted_demand];

    predictionChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels || ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
            datasets: [
                {
                    label: 'Past Demand',
                    data: past,
                    borderColor: '#2563eb',
                    backgroundColor: '#2563eb',
                    borderWidth: 2.5,
                    pointRadius: 4,
                    tension: 0.3
                },
                {
                    label: 'Predicted Demand',
                    data: pred,
                    borderColor: '#f97316',
                    backgroundColor: '#f97316',
                    borderWidth: 2.5,
                    pointRadius: 4,
                    tension: 0.3
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    beginAtZero: true,
                    max: Math.max(120, data.predicted_demand + 15),
                    ticks: { stepSize: 30, color: '#94a3b8', font: { size: 10 } },
                    grid: { color: '#f1f5f9' }
                },
                x: {
                    ticks: { color: '#94a3b8', font: { size: 10 } },
                    grid: { display: false }
                }
            }
        }
    });
}

// ----------------------------------------------------
// 3. SMART DISTRIBUTION
// ----------------------------------------------------
async function approveDistributionAction() {
    const btn = document.getElementById("btnApproveDistribution");
    btn.disabled = true;
    btn.innerHTML = `<span class="animate-spin inline-block mr-1">↻</span> Dispatching...`;

    try {
        const res = await fetch("/api/distribution", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ units: 35, blood_group: "B+" })
        });
        const result = await res.json();

        if (result.success) {
            btn.classList.remove("bg-blue-700", "hover:bg-blue-600");
            btn.classList.add("bg-emerald-600", "text-white");
            btn.innerHTML = `<i data-lucide="check" class="w-4 h-4 inline mr-1"></i> Dispatched Successfully`;
            lucide.createIcons();

            showToast("Success: 35 units of B+ dispatched from Blood Bank B → Hospital A!");
            
            setTimeout(() => {
                loadDashboardData();
                loadAlertsData();
            }, 800);
        }
    } catch (err) {
        console.error("Distribution error:", err);
        btn.disabled = false;
        btn.textContent = "Approve Distribution";
    }
}

// ----------------------------------------------------
// 4. ALERTS
// ----------------------------------------------------
async function loadAlertsData() {
    try {
        const res = await fetch("/api/alerts");
        const alerts = await res.json();

        const container = document.getElementById("alertsListContainer");
        container.innerHTML = "";

        alerts.forEach(a => {
            let bgClass = "bg-[#fef2f2] border-red-200";
            let iconClass = "bg-red-500 text-white";
            let iconName = "droplet";
            let titleClass = "text-red-700 font-bold";

            if (a.alert_type === "LOW_STOCK") {
                bgClass = "bg-[#fffbeb] border-amber-200";
                iconClass = "bg-amber-400 text-white";
                iconName = "alert-triangle";
                titleClass = "text-amber-700 font-bold";
            } else if (a.alert_type === "EXPIRY_WARNING") {
                bgClass = "bg-[#fff7ed] border-orange-200";
                iconClass = "bg-orange-400 text-white";
                iconName = "hourglass";
                titleClass = "text-orange-700 font-bold";
            } else if (a.alert_type === "ACTION") {
                bgClass = "bg-[#f0fdf4] border-emerald-200";
                iconClass = "bg-emerald-500 text-white";
                iconName = "check";
                titleClass = "text-emerald-700 font-bold";
            }

            const card = document.createElement("div");
            card.className = `p-4 rounded-2xl border ${bgClass} flex items-start justify-between shadow-xs`;
            card.innerHTML = `
                <div class="flex items-start space-x-3.5">
                    <div class="w-8 h-8 rounded-full ${iconClass} flex items-center justify-center flex-shrink-0 shadow-sm mt-0.5">
                        <i data-lucide="${iconName}" class="w-4 h-4"></i>
                    </div>
                    <div>
                        <span class="text-[11px] tracking-wider uppercase ${titleClass}">${a.title}</span>
                        <p class="text-xs text-slate-800 font-medium mt-0.5">${a.message}</p>
                    </div>
                </div>
                <span class="text-[11px] text-slate-400 font-medium whitespace-nowrap ml-4">${a.time_ago}</span>
            `;
            container.appendChild(card);
        });

        lucide.createIcons();
    } catch (err) {
        console.error("Failed to load alerts:", err);
    }
}

// ----------------------------------------------------
// 5. REPORTS CHARTS
// ----------------------------------------------------
async function loadReportsCharts() {
    try {
        const res = await fetch("/api/reports");
        const data = await res.json();

        // 1. Bar Chart: Blood Demand vs Predicted Demand
        const barCtx = document.getElementById("reportsBarChart").getContext("2d");
        if (reportsBarChartInstance) reportsBarChartInstance.destroy();

        reportsBarChartInstance = new Chart(barCtx, {
            type: 'bar',
            data: {
                labels: data.demand_forecast.labels,
                datasets: [
                    {
                        label: 'Actual Demand',
                        data: data.demand_forecast.actual,
                        backgroundColor: '#2563eb',
                        borderRadius: 4,
                        barPercentage: 0.6,
                        categoryPercentage: 0.6
                    },
                    {
                        label: 'Predicted Demand',
                        data: data.demand_forecast.predicted,
                        backgroundColor: '#f97316',
                        borderRadius: 4,
                        barPercentage: 0.6,
                        categoryPercentage: 0.6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true, max: 120, ticks: { stepSize: 30, color: '#94a3b8', font: { size: 10 } }, grid: { color: '#f1f5f9' } },
                    x: { ticks: { color: '#94a3b8', font: { size: 10 } }, grid: { display: false } }
                }
            }
        });

        // 2. Donut Chart: Inventory Distribution
        const donutCtx = document.getElementById("reportsDonutChart").getContext("2d");
        if (reportsDonutChartInstance) reportsDonutChartInstance.destroy();

        const inv = data.inventory_distribution;
        reportsDonutChartInstance = new Chart(donutCtx, {
            type: 'doughnut',
            data: {
                labels: inv.labels,
                datasets: [{
                    data: inv.percentages,
                    backgroundColor: inv.colors,
                    borderWidth: 2,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: '72%',
                plugins: { legend: { display: false } }
            }
        });

        const legendContainer = document.getElementById("reportsDonutLegend");
        legendContainer.innerHTML = "";
        inv.labels.forEach((bg, idx) => {
            const item = document.createElement("div");
            item.className = "flex items-center justify-between";
            item.innerHTML = `
                <div class="flex items-center space-x-2">
                    <span class="w-2.5 h-2.5 rounded-full" style="background-color: ${inv.colors[idx]}"></span>
                    <span class="font-bold text-slate-700">${bg}</span>
                </div>
                <span class="text-slate-500 font-medium">${inv.percentages[idx]}%</span>
            `;
            legendContainer.appendChild(item);
        });

    } catch (err) {
        console.error("Reports load error:", err);
    }
}

// ----------------------------------------------------
// 6. INVENTORY MANAGEMENT TABLE
// ----------------------------------------------------
async function loadFullInventory() {
    try {
        const res = await fetch("/api/inventory");
        const items = await res.json();

        const tbody = document.getElementById("fullInventoryTableBody");
        tbody.innerHTML = "";

        items.forEach(item => {
            let badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-emerald-100 text-emerald-700">Safe (${item.days_to_expiry}d)</span>`;
            if (item.urgency === "CRITICAL_EXPIRY") {
                badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-red-100 text-red-700 animate-pulse">Expiring in ${item.days_to_expiry}d</span>`;
            } else if (item.urgency === "MODERATE") {
                badge = `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold bg-amber-100 text-amber-700">${item.days_to_expiry}d left</span>`;
            }

            const tr = document.createElement("tr");
            tr.className = "hover:bg-slate-50 transition";
            tr.innerHTML = `
                <td class="py-3 font-semibold text-slate-900">${item.facility_name}</td>
                <td class="py-3 font-bold text-red-600">${item.blood_group}</td>
                <td class="py-3 text-slate-500">${item.component_type}</td>
                <td class="py-3 font-semibold">${item.units} units</td>
                <td class="py-3 text-slate-400">${item.collection_date}</td>
                <td class="py-3 text-slate-400">${item.expiry_date}</td>
                <td class="py-3">${badge}</td>
            `;
            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Inventory error:", err);
    }
}

function showToast(message) {
    const toast = document.getElementById("toast");
    const toastMessage = document.getElementById("toastMessage");
    if (!toast || !toastMessage) return;

    toastMessage.textContent = message;
    toast.classList.remove("translate-y-20", "opacity-0");
    toast.classList.add("translate-y-0", "opacity-100");

    setTimeout(() => {
        toast.classList.add("translate-y-20", "opacity-0");
        toast.classList.remove("translate-y-0", "opacity-100");
    }, 3500);
}
