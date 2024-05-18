from roadbook.coordinates import DecimalCoordinates, WalkRoute, SwedenElevationCoordinates

c1 = DecimalCoordinates(lat=68.358554, lon=18.779669)  # Abisko
c2 = DecimalCoordinates(lat=68.286084, lon=18.590195)  # Abisko bivouac
c3 = DecimalCoordinates(lat=65.811885, lon=15.092382)  # Hemavan


class TestWalkRoute:

    def test_route(self):
        c1 = DecimalCoordinates(lat=68.358554, lon=18.779669)  # Abisko
        c2 = DecimalCoordinates(lat=68.286084, lon=18.590195)  # Abisko bivouac
        route_obj = WalkRoute(origin=c1, destination=c2)
        route = route_obj.get_route()
        print(route)
        route_length = route_obj.route_length()
        print(route_length)

    def test_route_profile(self):
        route_obj = WalkRoute(origin=c1, destination=c3)
        route_profile = route_obj.route_profile()
        print(route_profile)

class TestElevation:

    def test_elevation(self):
        point = SwedenElevationCoordinates(north=7587572, east=655498)  # Abisko touriststation
        elevation = point.get_elevation()
        print(elevation)
        assert round(elevation) == 379


class TestCoordinates:

    def test_decimalcoordinates(self):
        point = DecimalCoordinates(lat=68.35820541337962, lon=18.780098785059455)
        sweref_coordinates = point.to_sweref99tm()
        print(sweref_coordinates)

    def test_sweref_coordinates(self):
        point = SwedenElevationCoordinates(north=7587572, east=655498)  # Abisko touriststation
        decimal_coordinates = point.to_decimal_ccordinates()
        print(decimal_coordinates)




