/**
 * JANAVANI CADASTRAL MAP CO-WORK VERTEX CAPTURE SYSTEM
 * Designed to execute locally inside browser developer tools console screens.
 * Captures UTM Zone 44N polygon vertices directly from BhuNaksha layers.
 */
(function() {
    // 1. Initialize persistent volatile data structures within browser window memory scope
    window._janavaniPlotsMatrix = {};
    window._activeGataTrackingId = null;

    console.log("%c🇮🇳 Janavani Cadastral Capture Tool Activated", "color: #7a3b1e; font-weight: bold; font-size: 14px;");
    console.log("Instructions:\n1. Type initialization code: startPlot(GATA_NUMBER)\n2. Hold 'Shift' and click the corners of your plot.\n3. Type getResults() to copy your finalized mapping payload.");

    /** Sets target boundary trackers to monitor a specific Gata identifier */
    window.startPlot = function(gataNumber) {
        window._activeGataTrackingId = String(gataNumber);
        if (!window._janavaniPlotsMatrix[window._activeGataTrackingId]) {
            window._janavaniPlotsMatrix[window._activeGataTrackingId] = [];
        }
        console.log(`%c[Janavani] Active tracking set to Gata: ${gataNumber}. Shift+Click vertices on map canvas.`, "color: #c4732a; font-weight: 500;");
    };

    /** Removes the last registered coordinate pair vertex if a mistake occurs */
    window.undoLastVertex = function() {
        if (!window._activeGataTrackingId) return;
        let pointsArray = window._janavaniPlotsMatrix[window._activeGataTrackingId];
        if (pointsArray.length > 0) {
            let removed = pointsArray.pop();
            console.log(`%cRemoved point ${pointsArray.length + 1}: [${removed.join(', ')}]`, "color: #cc0000;");
        }
    };

    /** Yields structured JSON schema string matching FastAPI LandMappingBatchRequest parameters */
    window.getResults = function(villageNameInput) {
        let village = villageNameInput || "Mohammadpur";
        let operationalPayload = {
            "village_name": village,
            "raw_utm_plots": window._janavaniPlotsMatrix
        };
        console.log("%c=== JANAVANI COMPLIANT SPATIAL PAYLOAD ===", "color: green; font-weight: bold;");
        console.log(JSON.stringify(operationalPayload, null, 2));
        console.log("%c==========================================\nCopy the complete JSON text object printed above.", "color: green;");
    };

    // 2. Attach capture listeners to intercepts user canvas actions cleanly
    document.addEventListener('click', function(event) {
        // Intercept triggers exclusively if the user holds down the Shift key modifier
        if (!event.shiftKey || !window._activeGataTrackingId) return;

        // Extract coordinate strings dynamically from BhuNaksha's native mouse tracer layout class
        let mouseTrackerElement = document.querySelector('.ol-mouse-position');
        if (!mouseTrackerElement || !mouseTrackerElement.textContent.trim()) {
            console.warn("[Janavani] Mouse telemetry position layer unreadable. Ensure your cursor is over the map canvas.");
            return;
        }

        // Clean text string values and map into numeric float arrays
        let rawCoordinates = mouseTrackerElement.textContent.trim().split(',').map(Number);
        if (rawCoordinates.length < 2 || isNaN(rawCoordinates[0]) || isNaN(rawCoordinates[1])) return;

        let activePointsList = window._janavaniPlotsMatrix[window._activeGataTrackingId];
        
        // Block double-triggering events on identical pixel coordinates
        if (activePointsList.length > 0) {
            let lastPoint = activePointsList[activePointsList.length - 1];
            if (lastPoint[0] === rawCoordinates[0] && lastPoint[1] === rawCoordinates[1]) return;
        }

        // Commit coordinate values into memory grid array
        activePointsList.push(rawCoordinates);
        console.log(`Gata ${window._activeGataTrackingId} — Vertex ${activePointsList.length} Captured: [${rawCoordinates.join(', ')}]`);
    });
})();
