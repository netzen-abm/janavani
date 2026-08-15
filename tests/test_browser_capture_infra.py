import os
import pytest

def test_browser_capture_tool_script_existance_and_integrity():
    """Confirms the frontend javascript vertex extraction utility exists and contains required functions."""
    target_script_path = "src/web_mvp/public/bhunaksha_capture_tool.js"
    
    # Assert path parameters inside project directories
    assert os.path.exists(target_script_path) is True
    
    with open(target_script_path, "r", encoding="utf-8") as f:
        script_code = f.read()
        
    # Verify core functional triggers are intact to ensure browser context stability
    assert "window._janavaniPlotsMatrix" in script_code
    assert "window.startPlot" in script_code
    assert "window.undoLastVertex" in script_code
    assert "window.getResults" in script_code
    assert ".ol-mouse-position" in script_code
