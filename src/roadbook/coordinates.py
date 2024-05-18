from __future__ import annotations

from pydantic import BaseModel
from pathlib import Path
import osmnx
import networkx
import rasterio
import pyproj
import time


class DecimalCoordinates(BaseModel):
    lat: float
    lon: float

    def middle(self, coords: DecimalCoordinates) -> DecimalCoordinates:
        lat = (self.lat + coords.lat) / 2
        lon = (self.lon + coords.lon) / 2
        return DecimalCoordinates(lat=lat, lon=lon)

    def to_sweref99tm(self) -> SWEREF99TMCoordinates:
        # Initialize transformer
        transformer = pyproj.Transformer.from_crs("EPSG:4326", "EPSG:3006", always_xy=True)
        # Transform the coordinates
        easting, northing = transformer.transform(self.lon, self.lat)
        return SWEREF99TMCoordinates(east=easting, north=northing)


class SWEREF99TMCoordinates(BaseModel):
    north: float
    east: float

    def to_decimal_ccordinates(self) -> DecimalCoordinates:
        transformer = pyproj.Transformer.from_crs("EPSG:3006", "EPSG:4326", always_xy=True)
        # Transform the coordinates
        lon, lat = transformer.transform(self.east, self.north)
        return DecimalCoordinates(lon=lon, lat=lat)


class SwedenElevationCoordinates(SWEREF99TMCoordinates):

    tif_base_directory: Path = Path("/home/forza-pc/Downloads/Sverige/nh_all")

    def get_north_digits(self):
        # the int() function truncate the inner result
        return int(self.north / 10**5)

    def get_east_digits(self):
        # the int() function truncate the inner result
        return int(self.east / 10**5)

    def get_tif_file(self) -> Path:
        north_digits = self.get_north_digits()
        east_digits = self.get_east_digits()
        file_name = f"nh_{north_digits}_{east_digits}.tif"
        file_path = self.tif_base_directory / file_name
        return file_path

    def get_elevation(self) -> float:
        tif_path = self.get_tif_file()
        with rasterio.open(tif_path) as src:
            # Since the coordinates are in the same CRS as the raster, we can use them directly
            for val in src.sample([(self.east, self.north)]):
                return val[0]  # Return the first band value


class RouteProfile(BaseModel):
    km: float
    ascend: float
    descend: float
    route_higher: float
    route_lower: float

    @property
    def km_effort(self) -> float:
        return self.km * (self.ascend / 100)

    @property
    def estimate_time(self) -> float:
        return self.km_effort / 3.5


class WalkRoute:

    walk_graph_file_path: Path = Path(__file__).parent / "walk_route.graphml"

    def __init__(self, origin: DecimalCoordinates, destination: DecimalCoordinates):
        self.origin: DecimalCoordinates = origin
        self.destination: DecimalCoordinates = destination
        self._walk_graph: networkx.MultiDiGraph = osmnx.load_graphml(filepath=self.walk_graph_file_path)

    def download_walk_graph(self):
        # Étape 1 : Définir la zone englobante et créer le graphe
        north, south = 68.386792, 65.701051  # Latitude de Abisko et Hemavan
        east, west = 19.051666, 14.842529  # Longitude de Abisko et Hemavan
        # Créer le graphe pour la zone englobante
        G = osmnx.graph_from_bbox(north, south, east, west, network_type='walk')
        # Étape 2 : Sauvegarder le graphe dans un fichier
        osmnx.save_graphml(G, filepath=self.walk_graph_file_path)

    @property
    def walk_graph(self) -> networkx.MultiDiGraph:
        if self._walk_graph is not None:
            return self._walk_graph
        # Creating a "walk" graph from coordinates
        middle_point = self.origin.middle(self.destination)
        middle_as_tuple = (middle_point.lat, middle_point.lon)
        walk_graph = osmnx.graph_from_point(middle_as_tuple, dist=500000, network_type='walk')
        self._walk_graph = walk_graph
        return walk_graph

    @property
    def origin_node(self):
        origin_node = osmnx.distance.nearest_nodes(self.walk_graph, self.origin.lon, self.origin.lat)
        return origin_node

    @property
    def destination_node(self):
        destination_node = osmnx.distance.nearest_nodes(self.walk_graph, self.destination.lon, self.destination.lat)
        return destination_node

    def get_coordinates(self, node_id: int) -> DecimalCoordinates:
        lon = self.walk_graph.nodes[node_id]["x"]
        lat = self.walk_graph.nodes[node_id]["y"]
        return DecimalCoordinates(lat=lat, lon=lon)

    def get_route(self) -> list[int]:
        route = networkx.shortest_path(self.walk_graph, self.origin_node, self.destination_node, weight='length')
        return route

    def get_route_elevations(self, route: list[int]) -> list[float]:
        elevation_list: list[float] = []
        for node in route:
            coordinates = self.get_coordinates(node).to_sweref99tm()
            elevation_coordinates = SwedenElevationCoordinates(**coordinates.dict())
            elevation = elevation_coordinates.get_elevation()
            if elevation < -100:  # if we cannot have true elevation
                continue
            elevation_list.append(elevation)
        return elevation_list

    @staticmethod
    def get_elevation_profile(elevation_list: list[float]) -> tuple[float, float]:  # D+, D-
        ascend = 0
        descend = 0
        for i in range(1, len(elevation_list)):
            delta = elevation_list[i] - elevation_list[i -1]
            if delta < 0:
                descend += delta
            else:
                ascend += delta
        return ascend, descend

    def route_length(self) -> float:
        distance = networkx.shortest_path_length(self.walk_graph, self.origin_node, self.destination_node, weight='length')
        return distance

    def route_profile(self) -> RouteProfile:
        route = self.get_route()
        length = self.route_length()
        route_elevation_list = self.get_route_elevations(route)
        ascend, descend = self.get_elevation_profile(route_elevation_list)
        route_min = min(route_elevation_list)
        route_max = max(route_elevation_list)

        route_profile = RouteProfile(
            km=length / 1000,
            ascend=ascend,
            descend=descend,
            route_higher=route_max,
            route_lower=route_min
        )
        return route_profile
