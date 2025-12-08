from ocp_vscode import show_all
import build123d as bd


# Light blocker dimensions
OUTER_DIAMETER = 3.75  # mm (for 1mm wall thickness)
HEIGHT = 10.0  # mm

# Flange at bottom to cover LED and block side emission
FLANGE_DIAMETER = 3.9  # mm (wider than body to block side light, 0.1mm gap at 4mm spacing)
FLANGE_HEIGHT = 0.5  # mm

# Inner hole tapers from bottom (PCB) to top (enclosure)
HOLE_DIAMETER_BOTTOM = 2.25  # mm (over LED)
HOLE_DIAMETER_TOP = 1.75  # mm (tight fit for 1.8mm light guide, TPU gives)


def build_light_blocker():
    """Build a tapered light blocker sleeve with flange."""
    with bd.BuildPart() as part:
        # Bottom flange (covers LED)
        bd.Cylinder(
            radius=FLANGE_DIAMETER / 2,
            height=FLANGE_HEIGHT,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
        )

        # Main cylinder (starts after flange)
        with bd.Locations([(0, 0, FLANGE_HEIGHT)]):
            bd.Cylinder(
                radius=OUTER_DIAMETER / 2,
                height=HEIGHT - FLANGE_HEIGHT,
                align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN)
            )

        # Inner tapered hole (cone) - goes through entire height
        bd.Cone(
            bottom_radius=HOLE_DIAMETER_BOTTOM / 2,
            top_radius=HOLE_DIAMETER_TOP / 2,
            height=HEIGHT,
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

    filename = f"light_blocker_d{OUTER_DIAMETER}_h{HEIGHT}"
    bd.export_step(part.part, f"{filename}.step")
    bd.export_stl(part.part, f"{filename}.stl")
    print(f"Exported: {filename}.step, {filename}.stl")


if __name__ == "__main__":
    export()
