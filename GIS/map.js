// GIS Map and Location Data
// =====================================================
// MEMBER 2 - MAP + GIS MODULE
// DISASTER DIGITAL TWIN 
// =====================================================


// =====================================================
// GLOBAL VARIABLES
// =====================================================

let floodMap;

let locationLayer;
let riskLayer;
let riverLayer;

let riskGeoJsonLayer;


// =====================================================
// 1. INITIALIZE MAP
// =====================================================

function initializeFloodMap() {

    // Prevent duplicate initialization

    if (floodMap) {
        return;
    }


    // Create map

    floodMap = L.map("map", {

        zoomControl: true

    }).setView(

        [20.3541, 85.8207],

        13

    );


    // =================================================
    // OPENSTREETMAP
    // =================================================

    L.tileLayer(

        "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",

        {

            maxZoom: 19,

            attribution:
                "&copy; OpenStreetMap contributors"

        }

    ).addTo(floodMap);


    // =================================================
    // CREATE LAYERS
    // =================================================

    locationLayer =
        L.layerGroup().addTo(floodMap);


    riskLayer =
        L.layerGroup().addTo(floodMap);


    riverLayer =
        L.layerGroup().addTo(floodMap);


    // =================================================
    // ADD GIS DATA
    // =================================================

    addImportantLocations();

    addRiver();

    loadRiskZones();

    createLayerControl();


    // Fix map display

    setTimeout(function () {

        floodMap.invalidateSize();

    }, 500);

}


// =====================================================
// 2. CREATE CUSTOM MARKER
// =====================================================

function createGISIcon(emoji) {

    return L.divIcon({

        className: "gis-marker",

        html: `
            <div class="gis-marker-icon">
                ${emoji}
            </div>
        `,

        iconSize: [34, 34],

        iconAnchor: [17, 17],

        popupAnchor: [0, -15]

    });

}


// =====================================================
// 3. ADD IMPORTANT LOCATIONS
// =====================================================

function addImportantLocations() {

    if (
        typeof GIS_LOCATIONS === "undefined"
    ) {

        console.error(
            "GIS_LOCATIONS not found"
        );

        return;

    }


    addLocationMarker(
        GIS_LOCATIONS.hospital,
        "🏥"
    );


    addLocationMarker(
        GIS_LOCATIONS.shelter,
        "🏠"
    );


    addLocationMarker(
        GIS_LOCATIONS.osdma,
        "🚨"
    );

}


// =====================================================
// 4. ADD LOCATION MARKER
// =====================================================

function addLocationMarker(
    location,
    emoji
) {

    const marker = L.marker(

        [
            location.lat,
            location.lng
        ],

        {

            icon:
                createGISIcon(emoji)

        }

    );


    marker.bindPopup(`

        <div class="gis-popup">

            <h3>
                ${location.name}
            </h3>

            <p>
                <strong>Type:</strong>
                ${location.type}
            </p>

            <p>
                ${location.description}
            </p>

            <p>
                <strong>Coordinates:</strong><br>

                ${location.lat.toFixed(4)},
                ${location.lng.toFixed(4)}
            </p>

        </div>

    `);


    marker.addTo(
        locationLayer
    );

}


// =====================================================
// 5. ADD RIVER
// =====================================================

function addRiver() {

    if (
        typeof GIS_LOCATIONS === "undefined"
    ) {
        return;
    }


    const river =
        GIS_LOCATIONS.river;


    const marker = L.marker(

        [
            river.lat,
            river.lng
        ],

        {

            icon:
                createGISIcon("🌊")

        }

    );


    marker.bindPopup(`

        <div class="gis-popup">

            <h3>
                🌊 ${river.name}
            </h3>

            <p>
                <strong>Type:</strong>
                ${river.type}
            </p>

            <p>
                ${river.description}
            </p>

        </div>

    `);


    marker.addTo(
        riverLayer
    );

}


// =====================================================
// 6. RISK COLOR
// =====================================================

function getRiskColor(risk) {

    switch (
        String(risk).toUpperCase()
    ) {

        case "LOW":
            return "#2ecc71";

        case "MODERATE":
            return "#f1c40f";

        case "HIGH":
            return "#e67e22";

        case "CRITICAL":
            return "#e74c3c";

        default:
            return "#64748b";

    }

}


// =====================================================
// 7. RISK ZONE STYLE
// =====================================================

function riskZoneStyle(feature) {

    const risk =
        feature.properties.risk;


    const color =
        getRiskColor(risk);


    return {

        color: color,

        fillColor: color,

        fillOpacity: 0.35,

        weight: 2

    };

}


// =====================================================
// 8. RISK POPUP
// =====================================================

function createRiskPopup(feature) {

    const data =
        feature.properties;


    return `

        <div class="gis-popup">

            <h3>
                ${data.name}
            </h3>

            <p>
                <strong>Zone ID:</strong>
                ${data.id}
            </p>

            <p>
                <strong>Risk Level:</strong>
                ${data.risk}
            </p>

            <p>
                <strong>Flood Probability:</strong>
                ${data.probability}%
            </p>

        </div>

    `;

}


// =====================================================
// 9. LOAD RISK ZONES
// =====================================================

async function loadRiskZones() {

    try {

        const response = await fetch(
            "map/data/risk_zones.geojson"
        );


        if (!response.ok) {

            throw new Error(
                "GeoJSON file not found"
            );

        }


        const geojson =
            await response.json();


        displayRiskZones(
            geojson
        );

    }

    catch (error) {

        console.error(
            "Risk zone error:",
            error
        );

    }

}


// =====================================================
// 10. DISPLAY RISK ZONES
// =====================================================

function displayRiskZones(geojson) {

    riskGeoJsonLayer =

        L.geoJSON(

            geojson,

            {

                style:
                    riskZoneStyle,


                onEachFeature:

                    function(
                        feature,
                        layer
                    ) {

                        // Popup

                        layer.bindPopup(

                            createRiskPopup(
                                feature
                            )

                        );


                        // Hover

                        layer.on(

                            "mouseover",

                            function () {

                                layer.setStyle({

                                    weight: 4,

                                    fillOpacity:
                                        0.60

                                });

                            }

                        );


                        // Mouse out

                        layer.on(

                            "mouseout",

                            function () {

                                layer.setStyle(

                                    riskZoneStyle(
                                        feature
                                    )

                                );

                            }

                        );


                        // Click

                        layer.on(

                            "click",

                            function () {

                                console.log(

                                    "Selected Zone:",

                                    feature.properties

                                );

                            }

                        );

                    }

            }

        );


    riskGeoJsonLayer.addTo(
        riskLayer
    );

}


// =====================================================
// 11. LAYER CONTROL
// =====================================================

function createLayerControl() {

    const overlays = {

        "🏥 Emergency Locations":
            locationLayer,

        "🔴 Flood Risk Zones":
            riskLayer,

        "🌊 River":
            riverLayer

    };


    L.control.layers(

        null,

        overlays,

        {

            collapsed: false

        }

    ).addTo(
        floodMap
    );

}


// =====================================================
// 12. UPDATE FLOOD RISK
// FUTURE ML / BACKEND CONNECTION
// =====================================================

function updateFloodRisk(prediction) {

    if (
        !prediction ||
        !riskGeoJsonLayer
    ) {
        return;
    }


    const selectedRisk =

        String(
            prediction.risk || ""
        ).toUpperCase();


    const zoneId =
        prediction.zone_id;


    riskGeoJsonLayer.eachLayer(

        function (layer) {

            if (
                !layer.feature
            ) {
                return;
            }


            const zone =
                layer.feature.properties;


            const zoneRisk =

                String(
                    zone.risk || ""
                ).toUpperCase();


            // Exact zone

            if (

                zoneId &&

                zone.id === zoneId

            ) {

                layer.setStyle({

                    weight: 5,

                    fillOpacity: 0.75,

                    color:
                        getRiskColor(
                            selectedRisk ||
                            zoneRisk
                        )

                });

            }


            // Risk matching

            else if (

                !zoneId &&

                zoneRisk === selectedRisk

            ) {

                layer.setStyle({

                    weight: 5,

                    fillOpacity: 0.70

                });

            }


            // Other zones

            else {

                layer.setStyle({

                    weight: 1,

                    fillOpacity: 0.15

                });

            }

        }

    );


    console.log(
        "Map Risk Updated:",
        prediction
    );

}


// =====================================================
// 13. FOCUS ON ZONE
// =====================================================

function focusOnZone(zoneId) {

    if (
        !riskGeoJsonLayer
    ) {
        return;
    }


    riskGeoJsonLayer.eachLayer(

        function (layer) {

            if (
                !layer.feature
            ) {
                return;
            }


            const id =
                layer.feature
                    .properties
                    .id;


            if (
                id === zoneId
            ) {

                floodMap.fitBounds(

                    layer.getBounds(),

                    {

                        padding:
                            [40, 40]

                    }

                );


                layer.openPopup();

            }

        }

    );

}


// =====================================================
// 14. REFRESH MAP
// =====================================================

function refreshFloodMap() {

    if (
        floodMap
    ) {

        floodMap.invalidateSize();

    }

}


// =====================================================
// 15. START MAP
// =====================================================

document.addEventListener(

    "DOMContentLoaded",

    function () {

        initializeFloodMap();

    }

);


window.addEventListener(

    "resize",

    function () {

        refreshFloodMap();

    }

);
