// =====================================================
// DISASTER MANAGEMENT DIGITAL TWIN
// =====================================================


// =====================================================
// 1. CREATE MAP
// =====================================================

const map = L.map("map", {
    center: [22.5726, 88.3639],
    zoom: 11,
    zoomControl: true
});


// =====================================================
// 2. OPENSTREETMAP MAP LAYER
// =====================================================

L.tileLayer(
    "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    {
        maxZoom: 19,
        attribution: "&copy; OpenStreetMap contributors"
    }
).addTo(map);


// =====================================================
// 3. HOSPITAL
// =====================================================

const hospitalIcon = L.divIcon({
    html: "🏥",
    className: "custom-marker",
    iconSize: [30, 30],
    iconAnchor: [15, 15]
});


L.marker(
    [22.5726, 88.3639],
    {
        icon: hospitalIcon
    }
)
.addTo(map)
.bindPopup(`
    <strong>🏥 Emergency Hospital</strong>
    <br>
    Emergency medical facility
`);


// =====================================================
// 4. SHELTER
// =====================================================

const shelterIcon = L.divIcon({
    html: "🏠",
    className: "custom-marker",
    iconSize: [30, 30],
    iconAnchor: [15, 15]
});


L.marker(
    [22.5958, 88.2636],
    {
        icon: shelterIcon
    }
)
.addTo(map)
.bindPopup(`
    <strong>🏠 Emergency Shelter</strong>
    <br>
    Safe evacuation location
`);


// =====================================================
// 5. MODERATE RISK ZONE
// =====================================================

const moderateZone = L.circle(
    [22.58, 88.38],
    {
        radius: 2500,

        color: "#f1c40f",

        fillColor: "#f1c40f",

        fillOpacity: 0.30,

        weight: 2
    }
)
.addTo(map)
.bindPopup(`
    <strong>🟡 Moderate Risk Zone</strong>
    <br>
    Monitor water level and rainfall.
`);


// =====================================================
// 6. HIGH RISK ZONE
// =====================================================

const highZone = L.circle(
    [22.55, 88.35],
    {
        radius: 1800,

        color: "#e67e22",

        fillColor: "#e67e22",

        fillOpacity: 0.35,

        weight: 2
    }
)
.addTo(map)
.bindPopup(`
    <strong>🟠 High Risk Zone</strong>
    <br>
    Prepare emergency resources.
`);


// =====================================================
// 7. CRITICAL RISK ZONE
// =====================================================

const criticalZone = L.circle(
    [22.62, 88.40],
    {
        radius: 1200,

        color: "#e74c3c",

        fillColor: "#e74c3c",

        fillOpacity: 0.45,

        weight: 2
    }
)
.addTo(map)
.bindPopup(`
    <strong>🔴 Critical Risk Zone</strong>
    <br>
    Immediate emergency preparation required.
`);


// =====================================================
// 8. RAINFALL SLIDER
// =====================================================

const rainSlider =
    document.getElementById("rainSlider");


const rainIncrease =
    document.getElementById("rainIncrease");


rainSlider.addEventListener(
    "input",
    function () {

        rainIncrease.innerText =
            rainSlider.value;

    }
);


// =====================================================
// 9. WHAT-IF SIMULATION
// =====================================================

function simulate() {

    // Get slider value

    const increase =
        Number(rainSlider.value);


    // Current rainfall

    const currentRainfall = 150;


    // Calculate new rainfall

    const newRainfall =
        currentRainfall *
        (1 + increase / 100);


    // =================================================
    // TEMPORARY DEMO PREDICTION
    // =================================================

    let probability =
        85 + (increase * 0.28);


    // Maximum 99%

    if (probability > 99) {

        probability = 99;

    }


    // Determine risk

    let risk = "HIGH";


    if (probability >= 90) {

        risk = "CRITICAL";

    }


    // =================================================
    // UPDATE DASHBOARD
    // =================================================

    document.getElementById(
        "probability"
    ).innerText =
        probability.toFixed(0);


    const riskElement =
        document.getElementById("risk");


    riskElement.innerText =
        risk;


    // Remove old risk classes

    riskElement.classList.remove(
        "high",
        "critical",
        "moderate"
    );


    // Add new class

    if (risk === "CRITICAL") {

        riskElement.classList.add(
            "critical"
        );

    } else {

        riskElement.classList.add(
            "high"
        );

    }


    // =================================================
    // SIMULATION RESULT
    // =================================================

    let affectedPopulation = 12500;


    if (risk === "CRITICAL") {

        affectedPopulation = 18500;

    }


    document.getElementById(
        "simulationResult"
    ).innerHTML = `

        <strong>🔮 Simulation Result</strong>

        <br><br>

        🌧️ New Rainfall:
        <strong>
            ${newRainfall.toFixed(1)} mm
        </strong>

        <br>

        ⚠️ Flood Probability:
        <strong>
            ${probability.toFixed(0)}%
        </strong>

        <br>

        🚨 Risk Level:
        <strong>
            ${risk}
        </strong>

        <br>

        👥 Estimated Affected Population:
        <strong>
            ${affectedPopulation.toLocaleString()}
        </strong>

        <br><br>

        🏠 Recommended Action:
        <strong>
            ${risk === "CRITICAL"
                ? "Prepare evacuation and emergency resources."
                : "Monitor the area and prepare resources."
            }
        </strong>

    `;


    // =================================================
    // VISUAL MAP UPDATE
    // =================================================

    if (risk === "CRITICAL") {

        criticalZone.setStyle({

            fillOpacity: 0.60,

            radius: 1800

        });

    } else {

        criticalZone.setStyle({

            fillOpacity: 0.45,

            radius: 1200

        });

    }

}


// =====================================================
// 10. FIX LEAFLET SIZE
// =====================================================

window.addEventListener(
    "load",
    function () {

        setTimeout(
            function () {

                map.invalidateSize();

            },
            500
        );

    }
);


// Also fix when browser window changes

window.addEventListener(
    "resize",
    function () {

        map.invalidateSize();

    }
);