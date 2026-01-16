"""
Routes for delivery optimization and routing
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
import logging

from services.routing_service import routing_service, Location, RouteRequest, RouteResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/routes", tags=["routes"])

@router.get("/health")
async def check_routing_health():
    """Check if routing service is available"""
    is_healthy = await routing_service.check_valhalla_health()
    return {
        "status": "healthy" if is_healthy else "unavailable",
        "valhalla": is_healthy
    }

@router.post("/route", response_model=RouteResponse)
async def get_route(request: RouteRequest):
    """
    Calculate optimal route through multiple locations
    
    Query params:
    - costing: auto, bicycle, pedestrian, taxi (default: auto)
    
    Body:
    - locations: List of Location objects with id, lat, lon
    
    Returns:
    - Optimized route with distance, duration, waypoints, coordinates
    """
    try:
        if not request.locations or len(request.locations) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 locations required"
            )
        
        logger.info(f"Calculating route for {len(request.locations)} locations")
        
        route = await routing_service.get_route(
            request.locations,
            costing=request.costing
        )
        
        if not route:
            raise HTTPException(
                status_code=404,
                detail="Could not calculate route. Check if Valhalla is running."
            )
        
        return route
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating route: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating route: {str(e)}"
        )

@router.post("/distance-matrix")
async def get_distance_matrix(request: RouteRequest):
    """
    Calculate distance matrix between all locations
    
    Returns:
    - 2D array with distances in kilometers between locations
    """
    try:
        if not request.locations or len(request.locations) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 locations required"
            )
        
        logger.info(f"Calculating distance matrix for {len(request.locations)} locations")
        
        matrix = await routing_service.get_distance_matrix(
            request.locations,
            costing=request.costing
        )
        
        if not matrix:
            raise HTTPException(
                status_code=404,
                detail="Could not calculate distance matrix. Check if Valhalla is running."
            )
        
        return {
            "count": len(request.locations),
            "matrix": matrix,
            "locations": [
                {"id": loc.id, "name": loc.name, "lat": loc.lat, "lon": loc.lon}
                for loc in request.locations
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating distance matrix: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating distance matrix: {str(e)}"
        )

@router.post("/optimize")
async def optimize_delivery_routes(
    locations: List[Location],
    num_couriers: int = Query(1, ge=1, le=20)
):
    """
    Optimize delivery routes for multiple couriers using VROOM algorithm
    
    Query params:
    - num_couriers: Number of available couriers (default: 1, max: 20)
    
    Returns:
    - List of optimized routes for each courier
    """
    try:
        if not locations or len(locations) < 2:
            raise HTTPException(
                status_code=400,
                detail="At least 2 locations required"
            )
        
        if num_couriers > len(locations) - 1:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot have more couriers ({num_couriers}) than delivery points ({len(locations) - 1})"
            )
        
        logger.info(f"Optimizing {len(locations)} locations for {num_couriers} courier(s)")
        
        route = await routing_service.get_route(locations)
        
        if not route:
            raise HTTPException(
                status_code=404,
                detail="Could not optimize routes"
            )
        
        waypoints_per_courier = len(route.waypoints) // num_couriers
        routes = []
        
        for i in range(num_couriers):
            start_idx = i * waypoints_per_courier
            if i == num_couriers - 1:
                end_idx = len(route.waypoints)
            else:
                end_idx = (i + 1) * waypoints_per_courier
            
            routes.append({
                "courier_id": f"courier_{i+1}",
                "waypoints": route.waypoints[start_idx:end_idx],
                "estimated_distance": route.distance / num_couriers,
                "estimated_duration": route.duration / num_couriers
            })
        
        return {
            "total_distance": route.distance,
            "total_duration": route.duration,
            "courier_count": num_couriers,
            "routes": routes
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error optimizing routes: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing routes: {str(e)}"
        )
