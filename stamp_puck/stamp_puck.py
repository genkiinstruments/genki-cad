from ocp_vscode import show_all
import build123d as bd


# Puck dimensions
DIAMETER = 76.0  # mm
HEIGHT = 14.5  # mm


def build_puck():
    """Build a solid puck for gripping while hammering."""
    with bd.BuildPart() as part:
        bd.Cylinder(
            radius=DIAMETER / 2,
            height=HEIGHT,
            align=(bd.Align.CENTER, bd.Align.CENTER, bd.Align.MIN),
        )
    return part


def run():
    """Preview the puck."""
    part = build_puck()
    show_all()


def export():
    """Export the puck for 3D printing."""
    part = build_puck()
    assert part.part is not None

    filename = f"stamp_puck_d{int(DIAMETER)}_h{HEIGHT}"
    bd.export_step(part.part, f"{filename}.step")
    bd.export_stl(part.part, f"{filename}.stl")
    print(f"Exported: {filename}.step, {filename}.stl")


if __name__ == "__main__":
    export()
