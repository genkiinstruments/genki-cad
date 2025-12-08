from ocp_vscode import show_all
import build123d as bd


# Stamp dimensions (all 3 identical)
STAMP_HEIGHT = 61  # mm
STAMP_WIDTH = 6  # mm
STAMP_DEPTH = 6  # mm
NUM_STAMPS = 3

# Sleeve parameters
SLEEVE_HEIGHT = 15  # mm
TOP_SLEEVE_HEIGHT = 6  # mm (thin sleeve for top alignment)
WALL_THICKNESS = 2  # mm

# Tight fit for TPU (slight interference)
TOLERANCE = -0.2  # negative = interference fit

# Inner cavity dimensions
INNER_WIDTH = (STAMP_WIDTH * NUM_STAMPS) + TOLERANCE  # 18mm - 0.2mm
INNER_DEPTH = STAMP_DEPTH + TOLERANCE  # 6mm - 0.2mm


def run():
    """Preview the stamp holder sleeve."""
    with bd.BuildPart() as part:
        # Outer shell
        with bd.BuildSketch():
            bd.Rectangle(
                INNER_WIDTH + 2 * WALL_THICKNESS, INNER_DEPTH + 2 * WALL_THICKNESS
            )
        bd.extrude(amount=SLEEVE_HEIGHT)

        # Hollow out the center
        with bd.BuildSketch(bd.Plane.XY.offset(0)):
            bd.Rectangle(INNER_WIDTH, INNER_DEPTH)
        bd.extrude(amount=SLEEVE_HEIGHT, mode=bd.Mode.SUBTRACT)

        # Optional: small chamfer on edges for easier stamp insertion
        top_edges = part.edges().filter_by(bd.Plane.XY.offset(SLEEVE_HEIGHT))
        bd.chamfer(top_edges, length=0.5)

    show_all()


def build_holder(stamp_width, stamp_depth):
    """Build a stamp holder with given stamp dimensions."""
    inner_width = (stamp_width * NUM_STAMPS) + TOLERANCE
    inner_depth = stamp_depth + TOLERANCE

    with bd.BuildPart() as part:
        # Outer shell
        with bd.BuildSketch():
            bd.Rectangle(
                inner_width + 2 * WALL_THICKNESS, inner_depth + 2 * WALL_THICKNESS
            )
        bd.extrude(amount=SLEEVE_HEIGHT)

        # Hollow out the center
        with bd.BuildSketch(bd.Plane.XY.offset(0)):
            bd.Rectangle(inner_width, inner_depth)
        bd.extrude(amount=SLEEVE_HEIGHT, mode=bd.Mode.SUBTRACT)

        # Chamfer for easier insertion
        top_edges = part.edges().filter_by(bd.Plane.XY.offset(SLEEVE_HEIGHT))
        bd.chamfer(top_edges, length=0.5)

    return part


def build_top_sleeve(stamp_width, stamp_depth):
    """Build a thin top sleeve for alignment with closed top."""
    inner_width = (stamp_width * NUM_STAMPS) + TOLERANCE
    inner_depth = stamp_depth + TOLERANCE

    with bd.BuildPart() as part:
        # Outer shell
        with bd.BuildSketch():
            bd.Rectangle(
                inner_width + 2 * WALL_THICKNESS, inner_depth + 2 * WALL_THICKNESS
            )
        bd.extrude(amount=TOP_SLEEVE_HEIGHT + WALL_THICKNESS)  # Extra height for closed top

        # Hollow out the center (leave WALL_THICKNESS at top as floor)
        with bd.BuildSketch(bd.Plane.XY.offset(0)):
            bd.Rectangle(inner_width, inner_depth)
        bd.extrude(amount=TOP_SLEEVE_HEIGHT, mode=bd.Mode.SUBTRACT)

    return part


def export():
    """Export stamp holders for all size variations."""
    variations = [
        (6, 6),  # Original
        (7, 7),
        (8, 8),
    ]

    for stamp_width, stamp_depth in variations:
        # Main sleeve
        part = build_holder(stamp_width, stamp_depth)
        assert part.part is not None
        filename = f"stamp_holder_{stamp_width}x{stamp_depth}_h{SLEEVE_HEIGHT}_w{WALL_THICKNESS}"
        bd.export_step(part.part, f"{filename}.step")
        bd.export_stl(part.part, f"{filename}.stl")
        print(f"Exported: {filename}.step, {filename}.stl")

        # Top sleeve
        top_part = build_top_sleeve(stamp_width, stamp_depth)
        assert top_part.part is not None
        top_filename = f"stamp_holder_top_{stamp_width}x{stamp_depth}_h{TOP_SLEEVE_HEIGHT}_w{WALL_THICKNESS}"
        bd.export_step(top_part.part, f"{top_filename}.step")
        bd.export_stl(top_part.part, f"{top_filename}.stl")
        print(f"Exported: {top_filename}.step, {top_filename}.stl")


if __name__ == "__main__":
    export()
