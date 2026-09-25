import os
import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from QUAKE2_MAP_2_T3D import (
    Vector3, Color, Face, Brush, Entity, MAPParser,
    PolygonTriangulator, T3DWriter, convert_map_to_t3d
)


class TestVector3(unittest.TestCase):
    def test_add(self):
        a = Vector3(1, 2, 3)
        b = Vector3(4, 5, 6)
        c = a + b
        self.assertEqual(c.x, 5)
        self.assertEqual(c.y, 7)
        self.assertEqual(c.z, 9)

    def test_to_unreal(self):
        v = Vector3(100, 100, 100)
        u = v.to_unreal(grid_snap=0)
        self.assertAlmostEqual(u.x, 254.0)
        self.assertAlmostEqual(u.y, -254.0)
        self.assertAlmostEqual(u.z, 254.0)


class TestColor(unittest.TestCase):
    def test_from_quake_value_intensity(self):
        color, intensity = Color.from_quake_value("400")
        self.assertAlmostEqual(intensity, 400.0 / 3.0, places=5)

    def test_from_quake_value_color(self):
        color, intensity = Color.from_quake_value("400 255 128 64")
        self.assertAlmostEqual(color.r, 1.0)
        self.assertAlmostEqual(color.g, 128.0 / 255.0, places=5)
        self.assertAlmostEqual(color.b, 64.0 / 255.0, places=5)


class TestFace(unittest.TestCase):
    def test_distance_to_point(self):
        face = Face(
            Vector3(0, 0, 0), Vector3(64, 0, 0), Vector3(0, 64, 0),
            "base_floor"
        )
        self.assertAlmostEqual(abs(face.distance_to_point(Vector3(0, 0, 10))), 10.0, places=5)
        self.assertAlmostEqual(face.distance_to_point(Vector3(0, 0, 0)), 0.0, places=5)


class TestBrush(unittest.TestCase):
    def _make_cube_brush(self):
        brush = Brush()
        # Winding chosen so each face's cross product points inward (Quake convention)
        brush.add_face(Face(Vector3(-64, -64, -16), Vector3(64, -64, -16), Vector3(-64, 64, -16), "floor"))
        brush.add_face(Face(Vector3(-64, -64, 16), Vector3(-64, 64, 16), Vector3(64, 64, 16), "ceil"))
        brush.add_face(Face(Vector3(-64, 64, -16), Vector3(64, 64, -16), Vector3(64, 64, 16), "wall"))
        brush.add_face(Face(Vector3(64, -64, -16), Vector3(-64, -64, -16), Vector3(-64, -64, 16), "wall"))
        brush.add_face(Face(Vector3(-64, -64, -16), Vector3(-64, 64, -16), Vector3(-64, 64, 16), "wall"))
        brush.add_face(Face(Vector3(64, 64, -16), Vector3(64, -64, -16), Vector3(64, -64, 16), "wall"))
        return brush

    def test_cube_vertices(self):
        brush = self._make_cube_brush()
        verts = brush.calculate_vertices()
        self.assertGreaterEqual(len(verts), 2)

    def test_face_polygons(self):
        brush = self._make_cube_brush()
        polygons = brush.calculate_face_polygons()
        self.assertGreaterEqual(len(polygons), 1)

    def test_face_polygons_parsed(self):
        sample_path = Path(__file__).resolve().parent / "sample.map"
        parser = MAPParser(str(sample_path))
        parser.parse()
        worldspawn = next(e for e in parser.entities if e.get_classname() == "worldspawn")
        brush = worldspawn.brushes[0]
        polygons = brush.calculate_face_polygons()
        self.assertEqual(len(polygons), 6)


class TestTriangulator(unittest.TestCase):
    def test_triangle(self):
        tri = PolygonTriangulator()
        verts = [Vector3(0, 0, 0), Vector3(1, 0, 0), Vector3(0, 1, 0)]
        result = tri.triangulate(verts)
        self.assertEqual(len(result), 1)

    def test_quad(self):
        tri = PolygonTriangulator()
        verts = [Vector3(0, 0, 0), Vector3(1, 0, 0), Vector3(1, 1, 0), Vector3(0, 1, 0)]
        result = tri.triangulate(verts)
        self.assertGreaterEqual(len(result), 2)


class TestMAPParser(unittest.TestCase):
    def test_parse_sample(self):
        sample_path = Path(__file__).resolve().parent / "sample.map"
        parser = MAPParser(str(sample_path))
        parser.parse()
        self.assertGreaterEqual(len(parser.entities), 3)

        worldspawn = next((e for e in parser.entities if e.get_classname() == "worldspawn"), None)
        self.assertIsNotNone(worldspawn)
        self.assertEqual(len(worldspawn.brushes), 1)

        player_start = next((e for e in parser.entities if e.get_classname() == "info_player_start"), None)
        self.assertIsNotNone(player_start)
        origin = player_start.get_origin()
        self.assertAlmostEqual(origin.x, 0.0)
        self.assertAlmostEqual(origin.y, 0.0)
        self.assertAlmostEqual(origin.z, 32.0)

        light = next((e for e in parser.entities if e.is_light()), None)
        self.assertIsNotNone(light)


class TestConversion(unittest.TestCase):
    def test_convert_sample(self):
        sample_path = Path(__file__).resolve().parent / "sample.map"
        output_path = Path(__file__).resolve().parent / "output.t3d"
        log_path = Path(__file__).resolve().parent / "output.log"

        try:
            convert_map_to_t3d(str(sample_path), str(output_path), grid_size=2.54)
            self.assertTrue(output_path.exists())
            content = output_path.read_text(encoding="utf-8")
            self.assertIn("Begin Map", content)
            self.assertIn("End Map", content)
            self.assertIn("Begin Actor Class=/Script/Engine.Brush", content)
            self.assertIn("Begin Actor Class=/Script/Engine.PointLight", content)
            self.assertIn("Begin Actor Class=/Script/Engine.PlayerStart", content)
        finally:
            for p in (output_path, log_path):
                if p.exists():
                    p.unlink()


if __name__ == "__main__":
    unittest.main()
