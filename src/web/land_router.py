from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, List
import io
import json
from src.utils.geodesy import GeodeticConverter
from src.services.kml_composer import KmlComposerEngine

router = APIRouter(prefix="/api/v1/land", tags=["Property Rights & Mapping Engine"])

class LandPlotCoordinateMap(BaseModel):
    easting: float = Field(..., description="UTM Easting Grid Metric Parameter Point")
    northing: float = Field(..., description="UTM Northing Grid Metric Parameter Point")

class LandMappingBatchRequest(BaseModel):
    village_name: str = Field(..., description="Name of target mapping village administrative center")
    raw_utm_plots: Dict[str, List[List[float]]] = Field(..., description="JSON structure string mapping Gata IDs to vertex coordinates array matrices")

@router.post("/compile-kml")
async def process_utm_land_map_compilation(payload: LandMappingBatchRequest):
    """Processes incoming data matrices, transforms projection indices, and outputs standard KML streams."""
    transformed_plots_matrix: Dict[str, List[Tuple[float, float]]] = {}
    
    try:
        for gata_id, vertices_list in payload.raw_utm_plots.items():
            transformed_vertices: List[Tuple[float, float]] = []
            for vertex in vertices_list:
                if len(vertex) < 2:
                    continue
                # Execute conversion from UTM Zone 44N metrics back to standard Lat/Long
                lat, lon = GeodeticConverter.utm_zone_44n_to_wgs84(vertex[0], vertex[1])
                transformed_vertices.append((lat, lon))
            transformed_plots_matrix[gata_id] = transformed_vertices
            
        # Build the final KML text output document structure
        kml_document_output = KmlComposerEngine.construct_kml_polygon_document(
            village_name=payload.village_name,
            plots_matrix=transformed_plots_matrix
        )
        
        kml_byte_stream = io.BytesIO(kml_document_output.encode("utf-8"))
        return StreamingResponse(
            kml_byte_stream,
            media_type="application/vnd.google-earth.kml+xml",
            headers={"Content-Disposition": f"attachment; filename=janavani_land_map_{payload.village_name}.kml"}
        )
        
    except Exception as run_error:
        raise HTTPException(status_code=422, detail=f"Spatial processing pipeline error trace: {str(run_error)}")
