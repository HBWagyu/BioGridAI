"""Generic US-ish demo farm. No live farm name or county hard-coded."""

from __future__ import annotations

import math

from backend.app.models.domain import (
    Animal,
    EnergySnapshot,
    FarmProfile,
    JDAsset,
    OptimusRobot,
    Paddock,
    WhiplashAsset,
)

ORIGIN_LAT = 39.0417
ORIGIN_LON = -96.5925


def _offset(lat: float, lon: float, north_m: float, east_m: float) -> tuple[float, float]:
    dlat = north_m / 111_111.0
    dlon = east_m / (111_111.0 * math.cos(math.radians(lat)))
    return lat + dlat, lon + dlon


def _rect(lat: float, lon: float, n: float, e: float, s: float, w: float) -> list[tuple[float, float]]:
    return [
        _offset(lat, lon, n, w),
        _offset(lat, lon, n, e),
        _offset(lat, lon, s, e),
        _offset(lat, lon, s, w),
        _offset(lat, lon, n, w),
    ]


def demo_farm() -> FarmProfile:
    parcel = _rect(ORIGIN_LAT, ORIGIN_LON, 420, 380, -420, -380)
    array = _rect(ORIGIN_LAT, ORIGIN_LON, 80, 220, -80, 20)
    paddocks = [
        Paddock(
            paddock_id="P1",
            name="North Open",
            kind="open_pasture",
            polygon=_rect(ORIGIN_LAT, ORIGIN_LON, 400, 0, 80, -360),
            acres=28.0,
            forage_index=0.78,
            occupancy_head=14,
            current_veg_height_in=7.5,
        ),
        Paddock(
            paddock_id="P2",
            name="Array Understory",
            kind="agrivoltaic_understory",
            polygon=array,
            acres=12.0,
            forage_index=0.62,
            occupancy_head=6,
            target_veg_height_in=8.0,
            current_veg_height_in=14.2,
            shade_hours_yesterday=5.4,
        ),
        Paddock(
            paddock_id="P3",
            name="East Recovery",
            kind="open_pasture",
            polygon=_rect(ORIGIN_LAT, ORIGIN_LON, 80, 360, -400, 220),
            acres=22.0,
            forage_index=0.84,
            occupancy_head=0,
            current_veg_height_in=9.0,
        ),
        Paddock(
            paddock_id="P4",
            name="Holding / Processing",
            kind="holding",
            polygon=_rect(ORIGIN_LAT, ORIGIN_LON, -80, 0, -400, -360),
            acres=18.0,
            forage_index=0.55,
            occupancy_head=4,
            current_veg_height_in=5.0,
        ),
    ]
    return FarmProfile(
        name="Prairie Demo Farm (generic)",
        address="Rural route, contiguous United States (demo — replace with your parcel)",
        lat=ORIGIN_LAT,
        lon=ORIGIN_LON,
        acres=80.0,
        solar_kwp=250.0,
        battery_kwh=270.0,
        parcel_polygon=parcel,
        array_polygon=array,
        paddocks=paddocks,
        notes="Simulation profile. Upload GeoJSON / draw your own boundary in Settings.",
    )


def demo_animals(farm: FarmProfile) -> list[Animal]:
    animals: list[Animal] = []
    specs = [
        ("A-101", "CERES-6-101", "Maple", "F", "normal", "P1"),
        ("A-102", "CERES-6-102", "Cedar", "F", "estrus", "P1"),
        ("A-103", "CERES-6-103", "Juniper", "F", "normal", "P1"),
        ("A-104", "CERES-6-104", "Aspen", "F", "calving_watch", "P2"),
        ("A-105", "CERES-6-105", "Willow", "F", "normal", "P2"),
        ("A-106", "CERES-6-106", "Hickory", "M", "normal", "P2"),
        ("A-107", "CERES-6-107", "Birch", "F", "processing_queue", "P4"),
        ("A-108", "CERES-6-108", "Elm", "F", "health_flag", "P4"),
    ]
    for i, (aid, tag, name, sex, status, pid) in enumerate(specs):
        pad = next(p for p in farm.paddocks if p.paddock_id == pid)
        lat, lon = pad.polygon[0]
        lat, lon = _offset(lat, lon, -40 - i * 18, 30 + i * 22)
        animals.append(
            Animal(
                animal_id=aid,
                ceres_tag_id=tag,
                name=name,
                sex=sex,
                status=status,
                lat=lat,
                lon=lon,
                paddock_id=pid,
                activity=55 if status == "health_flag" else 74,
                temp_c=39.4 if status == "health_flag" else 38.5,
            )
        )
    return animals


def demo_optimus(farm: FarmProfile) -> list[OptimusRobot]:
    lat, lon = _offset(farm.lat, farm.lon, -20, -40)
    lat2, lon2 = _offset(farm.lat, farm.lon, 40, 60)
    return [
        OptimusRobot(
            robot_id="OPT-01",
            status="tasking",
            battery_pct=76.0,
            lat=lat,
            lon=lon,
            current_task="animal_patrol_thermal",
            util_pct=41.0,
        ),
        OptimusRobot(
            robot_id="OPT-02",
            status="idle",
            battery_pct=94.0,
            lat=lat2,
            lon=lon2,
            current_task="standby",
            util_pct=8.0,
        ),
    ]


def demo_jd(farm: FarmProfile) -> list[JDAsset]:
    lat, lon = _offset(farm.lat, farm.lon, 200, -200)
    return [
        JDAsset(
            equipment_id="JD-8R-01",
            name="8R Autonomy (demo)",
            kind="tractor",
            status="idle",
            lat=lat,
            lon=lon,
            current_mission="none",
        )
    ]


def demo_whiplash(farm: FarmProfile) -> list[WhiplashAsset]:
    lat, lon = _offset(farm.lat, farm.lon, 70, 30)
    return [
        WhiplashAsset(
            unit_id="WHIP-01",
            status="idle",
            battery_pct=88.0,
            lat=lat,
            lon=lon,
            uncertainty=0.18,
            current_row="array-row-0",
            last_cut_height_in=9.5,
            enabled=True,
        )
    ]


def demo_energy() -> EnergySnapshot:
    return EnergySnapshot(
        solar_kw=168.0,
        load_kw=42.0,
        battery_soc_pct=71.0,
        battery_kwh=191.0,
        export_kw=96.0,
        import_kw=0.0,
        forecast_peak_kw=210.0,
    )


def clone_state():
    farm = demo_farm()
    return {
        "farm": farm,
        "animals": demo_animals(farm),
        "optimus": demo_optimus(farm),
        "jd": demo_jd(farm),
        "whiplash": demo_whiplash(farm),
        "energy": demo_energy(),
    }
