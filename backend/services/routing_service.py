"""
Optimized Routing Service with caching and fast fallback
Strategy: Cache > OSRM (with 3s timeout) > Instant straight-line calculation
"""
import json
import asyncio
import math
from typing import List, Dict, Optional, Tuple, Union
from pydantic import BaseModel
import httpx
import logging

logger = logging.getLogger(__name__)

# Simple in-memory cache for routes
_route_cache = {}

class Location(BaseModel):
    """Location with coordinates"""
    id: Union[str, int]
    lat: float
    lon: float
    name: Optional[str] = None
    type: str = "waypoint"
    
    class Config:
        json_encoders = {
            int: str,
        }

class RouteRequest(BaseModel):
    """Request for route calculation"""
    locations: List[Location]
    costing: str = "auto"
    
class RouteResponse(BaseModel):
    """Response with route details"""
    distance: float  # meters
    duration: float  # seconds
    waypoints: List[int]
    coordinates: List[Tuple[float, float]]

class RoutingService:
    """Fast routing service with intelligent fallback"""
    
    def __init__(self, valhalla_url: str = "http://localhost:8002"):
        self.valhalla_url = valhalla_url
        self.session = None
        self.osrm_url = "https://router.project-osrm.org/route/v1/driving"
        
    async def init_session(self):
        """Initialize async HTTP session"""
        if not self.session:
            self.session = httpx.AsyncClient(timeout=10.0)
    
    async def close_session(self):
        """Close async session"""
        if self.session:
            await self.session.aclose()
            self.session = None
    
    def _get_cache_key(self, locations: List[Location]) -> str:
        """Generate cache key from location coordinates"""
        coords = ",".join([f"{loc.lat:.4f}:{loc.lon:.4f}" for loc in locations])
        return f"route_{coords}"
    
    def _get_haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance in km using Haversine formula (instant)"""
        R = 6371  # Earth's radius in km
        
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat / 2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        return R * c
    
    def _straight_line_route(self, locations: List[Location]) -> RouteResponse:
        """Generate instant straight-line route with time estimate"""
        if len(locations) < 2:
            return None
        
        # Create straight line between locations
        coordinates = [(loc.lat, loc.lon) for loc in locations]
        
        # Calculate total distance
        total_distance = 0
        for i in range(len(locations) - 1):
            dist = self._get_haversine_distance(
                locations[i].lat, locations[i].lon,
                locations[i+1].lat, locations[i+1].lon
            )
            total_distance += dist
        
        # Estimate duration: average speed 40 km/h on roads
        total_duration = (total_distance / 40) * 3600  # seconds
        
        logger.info(f"Instant route: {total_distance:.2f} km, {total_duration:.0f} sec")
        
        return RouteResponse(
            distance=total_distance * 1000,  # Convert to meters
            duration=total_duration,
            waypoints=list(range(len(locations))),
            coordinates=coordinates
        )
    
    async def check_valhalla_health(self) -> bool:
        """Check if Valhalla is available"""
        try:
            await self.init_session()
            response = await self.session.get(f"{self.valhalla_url}/status", timeout=2.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Valhalla check failed: {e}")
            return False
    
    async def get_route(
        self, 
        locations: List[Location],
        costing: str = "auto"
    ) -> Optional[RouteResponse]:
        """
        Get route with 3-tier strategy:
        1. Return from cache (instant - <1ms)
        2. Try OSRM API (real roads - 1-3 sec with timeout)
        3. Fallback to straight-line (instant - <1ms)
        
        Total time: <3 seconds guaranteed
        """
        if len(locations) < 2:
            return None
        
        # 1. Check cache first (instant)
        cache_key = self._get_cache_key(locations)
        if cache_key in _route_cache:
            logger.info(f"✓ Route cache hit")
            return _route_cache[cache_key]
        
        # 2. Try OSRM with strict timeout (1-3 seconds max)
        osrm_route = await self._try_osrm_route(locations)
        if osrm_route:
            _route_cache[cache_key] = osrm_route
            return osrm_route
        
        # 3. Fallback to instant straight-line (guaranteed <1ms)
        logger.info("Using instant straight-line fallback")
        fallback_route = self._straight_line_route(locations)
        _route_cache[cache_key] = fallback_route
        return fallback_route
    
    async def _try_osrm_route(self, locations: List[Location]) -> Optional[RouteResponse]:
        """Try OSRM with 3-second timeout"""
        try:
            coords_str = ";".join([f"{loc.lon},{loc.lat}" for loc in locations])
            url = f"{self.osrm_url}/{coords_str}?overview=full&geometries=geojson&steps=false"
            
            await self.init_session()
            
            # Strict 3-second timeout
            response = await asyncio.wait_for(
                self.session.get(url),
                timeout=3.0
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get("code") == "Ok" and "routes" in data and len(data["routes"]) > 0:
                    route = data["routes"][0]
                    geometry = route.get("geometry", {})
                    
                    route_coords = []
                    if "coordinates" in geometry:
                        # Convert from GeoJSON [lon, lat] to [lat, lon]
                        route_coords = [(lat, lon) for lon, lat in geometry["coordinates"]]
                    
                    distance = route.get("distance", 0)  # meters
                    duration = route.get("duration", 0)  # seconds
                    
                    logger.info(f"✓ OSRM route: {distance/1000:.2f} km, {duration:.0f} sec")
                    
                    return RouteResponse(
                        distance=distance,
                        duration=duration,
                        waypoints=list(range(len(locations))),
                        coordinates=route_coords if route_coords else [(loc.lat, loc.lon) for loc in locations]
                    )
        
        except asyncio.TimeoutError:
            logger.warning("⏱ OSRM timeout (3s), using fallback")
        except Exception as e:
            logger.warning(f"⚠ OSRM error: {e}")
        
        return None
    
    def get_distance_matrix(self, locations: List[Location]) -> List[List[float]]:
        """Fast distance matrix using Haversine (instant)"""
        n = len(locations)
        matrix = [[0.0 for _ in range(n)] for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = self._get_haversine_distance(
                        locations[i].lat, locations[i].lon,
                        locations[j].lat, locations[j].lon
                    )
                    matrix[i][j] = dist * 1000  # meters
        
        return matrix
    
    def optimize_route(self, locations: List[Location]) -> List[int]:
        """Quick greedy optimization: nearest unvisited neighbor"""
        if len(locations) <= 2:
            return list(range(len(locations)))
        
        unvisited = set(range(1, len(locations)))
        route = [0]
        
        while unvisited:
            last = route[-1]
            nearest = min(unvisited, key=lambda i: self._get_haversine_distance(
                locations[last].lat, locations[last].lon,
                locations[i].lat, locations[i].lon
            ))
            route.append(nearest)
            unvisited.remove(nearest)
        
        return route

# Global singleton instance
routing_service = RoutingService()
