from ocp_vscode import show_all
import build123d as bd


# Light blocker dimensions (rectangular outer)
OUTER_SIZE = 3.75  # mm (square outer dimension)
HEIGHT = 11.0  # mm (1mm longer to compress between enclosure and PCB)

# Inner hole dimensions
HOLE_DIAMETER_LIGHTGUIDE = 1.8  # mm (exact fit for 1.8mm light guide)
HOLE_DIAMETER_LED = 3.0  # mm (clears 2mm x 2mm LED diagonal of 2.83mm)
FLARE_HEIGHT = 2.5  # mm (height of flared section at bottom for LED)


def build_light_blocker():
    """Build a light blocker with tight hole that flares at bottom for LED."""
    with bd.BuildPart() as part:
        # Main body - rectangular
        with bd.BuildSketch():
            bd.Rectangle(OUTER_SIZE, OUTER_SIZE)
        bd.extrude(amount=HEIGHT)

        # Tight hole for light guide (from flare height to top)
        with bd.Locations([(0, 0, FLARE_HEIGHT)]):
            bd.Cylinder(
                radius=HOLE_DIAMETER_LIGHTGUIDE / 2,
                height=HEIGHT - FLARE_HEIGHT,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
                mode=bd.Mode.SUBTRACT
            )

        # Flared cone at bottom for LED clearance
        bd.Cone(
            bottom_radius=HOLE_DIAMETER_LED / 2,
            top_radius=HOLE_DIAMETER_LIGHTGUIDE / 2,
            height=FLARE_HEIGHT,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
            mode=bd.Mode.SUBTRACT
        )

    return part


def run():
    """Preview the light blocker."""
    part = build_light_blocker()
    show_all()


def export():
    """Export the light blocker for 3D printing."""
    part = build_light_blocker()
    assert part.part is not None

    filename = f"light_blocker_{OUTER_SIZE}x{OUTER_SIZE}_h{HEIGHT}"
    bd.export_step(part.part, f"{filename}.step")
    bd.export_stl(part.part, f"{filename}.stl")
    print(f"Exported: {filename}.step, {filename}.stl")


if __name__ == "__main__":
    export()
