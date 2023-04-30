# %%
from build123d import *
from ocp_vscode import show, set_port, set_defaults

from touchscreen_mount import TouchscreenMount

set_port(3939)
set_defaults(grid=(True, True, True), axes=True, axes0=True)

# %%
pcb_screw_x_spacing = 94.8
pcb_screw_y_spacing = 53
pcb_screw_hole_diam = 2.8

# Measurements for cutouts in the plate
centre_cutout_width = 77.75
centre_cutout_height = 34.8
centre_cutout_corner_radius = 2

edge_cutout_width = 16.5
edge_cutout_height = 22

def stock_spacer() -> Part:
    outer_diam = 6
    inner_diam = 3.5
    height = 6.8
    # PCB spacers/standoffs
    with BuildPart() as spacer:
        with BuildSketch() as spacer_sk:
            Circle(radius=outer_diam / 2)
            Circle(radius=inner_diam / 2, mode=Mode.SUBTRACT)
        extrude(amount=height)
    # Create joints for connecting to plate and PCB
    RigidJoint("plate", spacer.part)
    RigidJoint("pcb", spacer.part, Location((0, 0, height)))

    spacer.part.label = "PCB Spacer"
    spacer.part.color = "grey"

    return spacer.part

def stock_touchscreen_pcb() -> Compound:
    pcb_width = 107.6
    pcb_height = 60
    pcb_thickness = 1.6
    with BuildPart() as pcb:
        with BuildSketch() as pcb_sk:
            RectangleRounded(pcb_width, pcb_height, radius=2)
        extrude(amount=pcb_thickness)
        bottom_face = pcb.part.faces().sort_by(Axis.Z).first
        # PCB screw holes
        with BuildSketch(bottom_face) as pcb_screw_holes_sk:
            with Locations((-0.4, 0)):
                with GridLocations(pcb_screw_x_spacing, pcb_screw_y_spacing, 2, 2) as screw_holes:
                    Circle(pcb_screw_hole_diam / 2)
                    spacer_joint_locations = screw_holes.locations
        extrude(dir=(0, 0, 1), until=Until.LAST, mode=Mode.SUBTRACT)
        # Create joint for connecting to LCD
        pcb_lcd_joint = RigidJoint("lcd", pcb.part)
    with BuildPart() as lcd:
        with BuildSketch(bottom_face) as lcd_sk:
            lcd_width = 84.6
            lcd_height = 55.5
            lcd_thickness = 3.8
            with Locations((-0.4, 0)):
                Rectangle(lcd_width, lcd_height)
        extrude(amount=lcd_thickness)
        # Create joint for connecting to PCB
        lcd_pcb_joint = RigidJoint("pcb", lcd.part)
    pcb_lcd_joint.connect_to(lcd_pcb_joint)

    pcb.part.label = "PCB"
    pcb.part.color = "green"
    lcd.part.label = "LCD"
    lcd.part.color = "black"

    pcb_assembly = Compound(
        label="PCB Assembly",
        children=[pcb.part, lcd.part],
    )
    # Create joints for connecting to spacers
    for idx, loc in enumerate(spacer_joint_locations):
        RigidJoint(f"spacer{idx}", pcb_assembly, loc * Pos(0, 0, -pcb_thickness))

    return pcb_assembly


stock_mount = TouchscreenMount(
    stock_touchscreen_pcb(),
    stock_spacer(),
    pcb_screw_x_spacing,
    pcb_screw_y_spacing,
    pcb_screw_hole_diam,
)

show(
    stock_mount,
    render_joints=True,
    # transparent=True,
    reset_camera=False,
)

stock_mount.export_step("4Max_Pro_Touchscreen_Mount.step")
stock_mount.plate_part.export_stl("4Max_Pro_Touchscreen_Mount_Plate.stl")
stock_mount.spacer_part.export_stl("4Max_Pro_Touchscreen_Mount_Spacer.stl")