from typing import Any, Dict, List, Tuple
import io

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from src.services.kml_composer import KmlComposerEngine
from src.utils.geodesy import GeodeticConverter

router = APIRouter(prefix="/api/v1/land", tags=["Property Rights & Mapping Engine"])


class LandPlotCoordinateMap(BaseModel):
    easting: float = Field(..., description="UTM Easting Grid Metric Parameter Point")
    northing: float = Field(..., description="UTM Northing Grid Metric Parameter Point")


class LandMappingBatchRequest(BaseModel):
    village_name: str = Field(..., description="Name of target mapping village administrative center")
    raw_utm_plots: Dict[str, List[List[float]]] = Field(
        ...,
        description="JSON structure mapping Gata IDs to vertex-coordinate arrays",
    )


@router.post("/compile-kml")
async def process_utm_land_map_compilation(payload: LandMappingBatchRequest):
    """Transform UTM coordinates and stream a standard KML document."""
    transformed_plots_matrix: Dict[str, List[Tuple[float, float]]] = {}

    try:
        for gata_id, vertices_list in payload.raw_utm_plots.items():
            transformed_vertices: List[Tuple[float, float]] = []
            for vertex in vertices_list:
                if len(vertex) < 2:
                    continue
                # Convert UTM Zone 44N coordinates to WGS84 latitude/longitude.
                lat, lon = GeodeticConverter.utm_zone_44n_to_wgs84(vertex[0], vertex[1])
                transformed_vertices.append((lat, lon))
            transformed_plots_matrix[gata_id] = transformed_vertices

        kml_document_output = KmlComposerEngine.construct_kml_polygon_document(
            village_name=payload.village_name,
            plots_matrix=transformed_plots_matrix,
        )
        kml_byte_stream = io.BytesIO(kml_document_output.encode("utf-8"))
        safe_village = "".join(
            character for character in payload.village_name
            if character.isalnum() or character in ("-", "_")
        )[:80] or "land_map"
        return StreamingResponse(
            kml_byte_stream,
            media_type="application/vnd.google-earth.kml+xml",
            headers={
                "Content-Disposition": f'attachment; filename="janavani_land_map_{safe_village}.kml"'
            },
        )
    except (ValueError, TypeError, KeyError) as run_error:
        raise HTTPException(
            status_code=422,
            detail="Spatial processing pipeline rejected the supplied coordinates.",
        ) from run_error
