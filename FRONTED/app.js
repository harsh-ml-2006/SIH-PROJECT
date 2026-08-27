// =====================================================
// DISASTER DIGITAL TWIN  --  KIIT Bhubaneswar
// =====================================================

// =====================================================
// 1. MAP  (KIIT University)
// =====================================================

const map = L.map("map", {
    center: [20.3541, 85.8207],
    zoom: 13,
    zoomControl: true
});

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


// =====================================================
// 2. MARKERS
// =====================================================

function makeIcon(emoji, size) {
    return L.divIcon({
        html: "<div style='font-size:" + size + "px;line-height:1'>" + emoji + "</div>",
        className: "custom-marker",
        iconSize: [30, 30],
        iconAnchor: [15, 15]
    });
}

// KIIT University
L.marker([20.3541, 85.8207], { icon: makeIcon("\uD83C\uDF93", 22) })
    .addTo(map)
    .bindPopup("<strong>KIIT University</strong><br>Kalinga Institute of Industrial Technology<br>Patia, Bhubaneswar, Odisha");

// KIMS Hospital
L.marker([20.3568, 85.8150], { icon: makeIcon("\uD83C\uDFE5", 20) })
    .addTo(map)
    .bindPopup("<strong>KIMS Hospital</strong><br>2600-bed multi-specialty hospital<br>KIIT Campus-5");

// OSDMA HQ
L.marker([20.2726, 85.8390], { icon: makeIcon("\uD83C\uDFE0", 20) })
    .addTo(map)
    .bindPopup("<strong>OSDMA HQ</strong><br>Odisha State Disaster Management Authority<br>Rajiv Bhawan, Unit 5");

// Kuakhai River
L.marker([20.2870, 85.8750], { icon: makeIcon("\uD83C\uDF0A", 20) })
    .addTo(map)
    .bindPopup("<strong>Kuakhai River Belt</strong><br>Mahanadi distributary<br>High flood risk during monsoon");


// =====================================================
// 3. RISK ZONES
// =====================================================

var lowZone = L.circle([20.3541, 85.8207], {
    radius: 800,
    color: "#2ecc71", fillColor: "#2ecc71",
    fillOpacity: 0.15, weight: 1.5
}).addTo(map).bindPopup("<strong>Low Risk</strong><br>KIIT Campus -- Good drainage");

var moderateZone = L.circle([20.3400, 85.8100], {
    radius: 1500,
    color: "#f1c40f", fillColor: "#f1c40f",
    fillOpacity: 0.18, weight: 1.5
}).addTo(map).bindPopup("<strong>Moderate Risk</strong><br>Patia-Chandrasekharpur area");

var highZone = L.circle([20.3200, 85.8350], {
    radius: 1800,
    color: "#e67e22", fillColor: "#e67e22",
    fillOpacity: 0.22, weight: 1.5
}).addTo(map).bindPopup("<strong>High Risk</strong><br>Low-lying residential areas<br>Poor drainage, waterlogging common");

var criticalZone = L.circle([20.2870, 85.8750], {
    radius: 1200,
    color: "#e74c3c", fillColor: "#e74c3c",
    fillOpacity: 0.30, weight: 1.5
}).addTo(map).bindPopup("<strong>CRITICAL</strong><br>Kuakhai River flood plain<br>Immediate evacuation during heavy rain");


// =====================================================
// 4. SLIDER
// =====================================================

var rainSlider   = document.getElementById("rainSlider");
var rainIncrease = document.getElementById("rainIncrease");

rainSlider.addEventListener("input", function () {
    rainIncrease.innerText = rainSlider.value;
});


// =====================================================
// 5. SIMULATE
// =====================================================

function simulate() {

    var increase        = Number(rainSlider.value);
    var currentRainfall = 80;
    var newRainfall     = currentRainfall * (1 + increase / 100);

    // demo prediction
    var probability = 35 + (increase * 1.2);
    if (probability > 99) probability = 99;

    // risk level
    var risk;
    if (probability >= 75)      risk = "CRITICAL";
    else if (probability >= 50) risk = "HIGH";
    else if (probability >= 25) risk = "MODERATE";
    else                        risk = "LOW";

    // affected pop
    var affectedPop  = 3000;
    var affectedArea = 1.5;
    if (risk === "CRITICAL")       { affectedPop = 25000; affectedArea = 5.0; }
    else if (risk === "HIGH")      { affectedPop = 12500; affectedArea = 3.0; }
    else if (risk === "MODERATE")  { affectedPop = 3000;  affectedArea = 1.5; }
    else                           { affectedPop = 500;   affectedArea = 0.5; }

    // ---- UPDATE UI ----

    document.getElementById("rainfall").innerText    = newRainfall.toFixed(0);
    document.getElementById("probability").innerText = probability.toFixed(0);
    document.getElementById("affectedPop").innerText  = affectedPop.toLocaleString();
    document.getElementById("affectedArea").innerText = affectedArea.toFixed(1);

    // prob bar
    var probBar = document.querySelector(".prob-bar");
    if (probBar) probBar.style.width = probability.toFixed(0) + "%";

    // rain bar
    var rainBar = document.querySelector(".rain-bar");
    if (rainBar) rainBar.style.width = Math.min((newRainfall / 250) * 100, 100).toFixed(0) + "%";

    // risk badge
    var riskEl = document.getElementById("risk");
    riskEl.innerText = risk;
    riskEl.className = "risk-badge " + risk.toLowerCase();

    // emergency action
    var actionText = "Action: Continue routine monitoring";
    if (risk === "CRITICAL")       actionText = "ACTION: EVACUATE -- Activate OSDMA protocol";
    else if (risk === "HIGH")      actionText = "Action: Prepare emergency resources";
    else if (risk === "MODERATE")  actionText = "Action: Monitor area drainage";
    document.getElementById("emergencyAction").innerHTML =
        "<span class='em-icon'>&#128680;</span><span>" + actionText + "</span>";

    // sim result
    document.getElementById("simulationResult").innerHTML =
        "<strong>Simulation Result</strong><br><br>" +
        "New Rainfall: <strong>" + newRainfall.toFixed(1) + " mm</strong><br>" +
        "Flood Probability: <strong>" + probability.toFixed(0) + "%</strong><br>" +
        "Risk Level: <strong>" + risk + "</strong><br>" +
        "Affected Population: <strong>" + affectedPop.toLocaleString() + "</strong><br>" +
        "Affected Area: <strong>" + affectedArea.toFixed(1) + " km2</strong><br><br>" +
        "Recommended: <strong>" +
        (risk === "CRITICAL"
            ? "EVACUATE -- Deploy NDRF, activate all emergency shelters."
            : risk === "HIGH"
            ? "ALERT -- Prepare rescue teams, standby shelters."
            : risk === "MODERATE"
            ? "MONITOR -- Track water levels and drainage."
            : "NORMAL -- Continue routine operations.") +
        "</strong>";

    // ---- MAP UPDATE ----
    if (risk === "CRITICAL") {
        criticalZone.setStyle({ fillOpacity: 0.55 });
        criticalZone.setRadius(1800);
        highZone.setStyle({ fillOpacity: 0.40 });
        highZone.setRadius(2200);
    } else if (risk === "HIGH") {
        criticalZone.setStyle({ fillOpacity: 0.35 });
        criticalZone.setRadius(1400);
        highZone.setStyle({ fillOpacity: 0.30 });
        highZone.setRadius(2000);
    } else {
        criticalZone.setStyle({ fillOpacity: 0.30 });
        criticalZone.setRadius(1200);
        highZone.setStyle({ fillOpacity: 0.22 });
        highZone.setRadius(1800);
    }
}


// =====================================================
// 6. FIX MAP SIZE
// =====================================================

window.addEventListener("load", function () {
    setTimeout(function () { map.invalidateSize(); }, 500);
});
window.addEventListener("resize", function () {
    map.invalidateSize();
});