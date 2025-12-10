from ocp_vscode import show_all
import build123d as bd


# USB-C port dimensions
USBC_WIDTH = 9.0  # mm (horizontal, X axis)
USBC_HEIGHT = 3.2  # mm (vertical on enclosure face, Y axis)
USBC_CORNER_RADIUS = 1.0  # mm (rounded corners)
USBC_GAP = 7.6  # mm (gap between ports)
NUM_PORTS = 3
USBC_TAB_DEPTH = 2.0  # mm (how deep tabs insert into ports, Z axis)

# Stamp dimensions (single stamp per jig)
STAMP_HEIGHT = 61  # mm
STAMP_WIDTH = 6  # mm (X axis - horizontal)
STAMP_DEPTH = 6  # mm (Z axis - into enclosure)
STAMP_SPACING = 4  # mm between stamp positions

# 3 stamp positions (each jig holds 1 stamp at different X position)
# Stamps are 6mm wide, so positions are 6mm apart

# Jig parameters
STAMP_OFFSET = 19.0  # mm (stamp center above TOP of USB-C ports, Y axis)
STAMP_X_ADJUST = 3.0  # mm (moved towards center from left port)
WALL_THICKNESS = 2.0  # mm (minimum walls on all sides)
PAD_THICKNESS = 12.0  # mm (thickness of the main plate)
SLEEVE_HEIGHT = 6.0  # mm (height of stamp slot, Y axis)

# Tight fit tolerances
USBC_TOLERANCE = -0.2  # interference fit for USB-C tabs
STAMP_TOLERANCE = -0.2  # interference fit for stamps


def build_jig(stamp_index):
    """
    Build the stamp alignment jig with USB-C registration.

    Args:
        stamp_index: 0, 1, or 2 for the three stamp positions (left to right)

    Coordinate system:
    - X: horizontal along enclosure (USB-C ports in a row)
    - Y: vertical on enclosure face (stamp is 15mm above ports)
    - Z: depth into enclosure (USB-C tabs insert into ports)
    """

    # Stamp cavity dimensions (single stamp, 6mm wide)
    stamp_cavity_width = STAMP_WIDTH + STAMP_TOLERANCE  # X = 6mm (single stamp)
    stamp_cavity_height = SLEEVE_HEIGHT  # Y (vertical height of holder)
    stamp_cavity_depth = STAMP_DEPTH + STAMP_TOLERANCE  # Z = 6mm

    # Port spacing (center to center)
    port_spacing = USBC_WIDTH + USBC_GAP

    # USB-C tab dimensions with tolerance
    usbc_tab_width = USBC_WIDTH + USBC_TOLERANCE
    usbc_tab_height = USBC_HEIGHT + USBC_TOLERANCE

    # Total span of USB-C ports
    total_usbc_span = (NUM_PORTS * USBC_WIDTH) + ((NUM_PORTS - 1) * USBC_GAP)

    # Base position (center of the full 18mm stamp area, same as before)
    base_x_pos = -port_spacing + STAMP_X_ADJUST

    # First stamp starts at left edge of 18mm area (offset by -6mm from center)
    # Each subsequent stamp is offset by 3mm
    stamp_x_pos = base_x_pos - STAMP_WIDTH + (stamp_index * STAMP_SPACING)

    # Body dimensions - FIXED size spanning all USB-C ports (same for all 3 jigs)
    # Use the full 18mm stamp area for body width calculation
    full_stamp_width = STAMP_WIDTH * 3  # 18mm total stamp area
    body_left = base_x_pos - (full_stamp_width / 2) - WALL_THICKNESS
    body_right = port_spacing + (USBC_WIDTH / 2) + WALL_THICKNESS
    body_width = body_right - body_left
    body_center_x = (body_left + body_right) / 2

    # Y: from bottom of USB-C ports to top of stamp cavity + walls
    body_bottom = -(USBC_HEIGHT / 2) - WALL_THICKNESS
    body_top = (USBC_HEIGHT / 2) + STAMP_OFFSET + (SLEEVE_HEIGHT / 2) + WALL_THICKNESS
    body_height = body_top - body_bottom
    body_center_y = (body_bottom + body_top) / 2

    # Z: thickness of the pad (no separate walls, just a thick plate with through-slot)
    body_depth = PAD_THICKNESS

    # Stamp slot center position
    stamp_center_y = (USBC_HEIGHT / 2) + STAMP_OFFSET

    with bd.BuildPart() as part:
        # Main body plate (thick pad)
        with bd.BuildSketch():
            with bd.Locations([(body_center_x, body_center_y)]):
                bd.Rectangle(body_width, body_height)
        bd.extrude(amount=body_depth)

        # Cut stamp slot through the pad
        with bd.BuildSketch():
            with bd.Locations([(stamp_x_pos, stamp_center_y)]):
                bd.Rectangle(stamp_cavity_width, stamp_cavity_height)
        bd.extrude(amount=body_depth, mode=bd.Mode.SUBTRACT)

        # Add USB-C registration tabs (extending backward into ports)
        port_positions = [
            -port_spacing,  # Left port
            0,  # Center port
            port_spacing,  # Right port
        ]

        for x_pos in port_positions:
            with bd.BuildSketch(bd.Plane.XY.offset(body_depth)):
                with bd.Locations([(x_pos, 0)]):
                    bd.RectangleRounded(
                        usbc_tab_width, usbc_tab_height, radius=USBC_CORNER_RADIUS
                    )
            bd.extrude(amount=USBC_TAB_DEPTH)

    return part


def run():
    """Preview the jig."""
    part = build_jig(0)
    show_all()


def export():
    """Export 3 jigs for 3D printing (one for each stamp position)."""
    for stamp_index in range(3):
        part = build_jig(stamp_index)
        assert part.part is not None

        filename = f"stamp_jig_{stamp_index + 1}_{int(STAMP_OFFSET)}mm_offset"
        bd.export_step(part.part, f"{filename}.step")
        bd.export_stl(part.part, f"{filename}.stl")
        print(f"Exported: {filename}.step, {filename}.stl")


if __name__ == "__main__":
    export()
