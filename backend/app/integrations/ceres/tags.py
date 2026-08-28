"""Ceres Gen 6 ear-tag client. Exclusive livestock telemetry path."""

from __future__ import annotations

from backend.app.models.domain import Animal


class CeresGen6Client:
    def __init__(self, animals: list[Animal], simulation: bool = True) -> None:
        self.animals = animals
        self.simulation = simulation

    def list_animals(self) -> list[Animal]:
        return self.animals

    def in_polygon(self, polygon: list[tuple[float, float]]) -> list[Animal]:
        if not polygon:
            return []
        lats = [p[0] for p in polygon]
        lons = [p[1] for p in polygon]
        min_lat, max_lat = min(lats), max(lats)
        min_lon, max_lon = min(lons), max(lons)
        return [
            a
            for a in self.animals
            if min_lat <= a.lat <= max_lat and min_lon <= a.lon <= max_lon
        ]
