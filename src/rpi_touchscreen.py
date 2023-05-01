# %%
from build123d import *
from ocp_vscode import show, set_port, set_defaults

from touchscreen_mount import TouchscreenMount

set_port(3939)
set_defaults(
    grid=(True, True, True),
    axes=True,
    axes0=True,
    reset_camera=False,
    collapse="C",
)

# %%

adhesive_foam_thickness = 0.6
# Stock standoff height minus the extra height added to the display by the adhesive
pcb_mounting_height = 6.8 - adhesive_foam_thickness
spacer_side_length = 7
spacer_wall_thickness = 1.2
spacer_bottom_thickness = 1.2
pcb_thickness = 1.6
lcd_thickness = 3.8
screw_hole_diam = 2.4
spacer_height = pcb_mounting_height + pcb_thickness + lcd_thickness

pcb_width = 85.2
pcb_height = 54.85
pcb_screw_hole_diam = 1.8

lcd_width = 82.5
lcd_height = 54.35


'''
Plate cutouts
'''
def rpi_cutouts(base_sk: BuildSketch):
    connector_cutout_width = 42
    connector_cutout_height = 10
    centre_cutout_width = 80
    centre_cutout_height = 28
    centre_cutout_corner_radius = 2
    with Locations(base_sk.edges().sort_by(Axis.Y).last @ 0.763):
        connector_cutout = Rectangle(
            connector_cutout_width,
            connector_cutout_height,
            mode=Mode.SUBTRACT,
            align=(Align.MAX, Align.MAX),
        )
    fillet(connector_cutout.vertices().group_by(Axis.Y)[1], 3)
    fillet(connector_cutout.vertices().group_by(Axis.Y)[0], 1)
    
    with Locations((0, -2)):
        centre_cutout = RectangleRounded(
            centre_cutout_width,
            centre_cutout_height,
            centre_cutout_corner_radius,
            mode=Mode.SUBTRACT,
        )


'''
Spacer/standoff
'''
with BuildPart() as spacer:
    with BuildSketch() as spacer_sk:
        Rectangle(spacer_side_length, spacer_side_length)
    extrude(amount=spacer_height)

    with BuildSketch(spacer.faces().sort_by(Axis.Z).last) as ledge_sk:
        with Locations((spacer_wall_thickness / 2, -spacer_wall_thickness / 2)):
            Rectangle(
                spacer_side_length - spacer_wall_thickness,
                spacer_side_length - spacer_wall_thickness,
            )
    ledge = extrude(amount=-(spacer_height - pcb_mounting_height), mode=Mode.SUBTRACT)

    with BuildSketch(ledge.faces().sort_by(Axis.Z).first) as ledge_sk2:
        with Locations((spacer_wall_thickness / 2, spacer_wall_thickness / 2)):
            Rectangle(
                spacer_side_length - spacer_wall_thickness * 2,
                spacer_side_length - spacer_wall_thickness * 2,
            )
    ledge2 = extrude(amount=pcb_mounting_height - spacer_bottom_thickness, mode=Mode.SUBTRACT)
    
    with BuildSketch(ledge2.faces().sort_by(Axis.Z).first) as screw_hole_sk:
        Circle(screw_hole_diam / 2)
    screw_hole = extrude(until=Until.LAST, mode=Mode.SUBTRACT)

    plate_joint = RigidJoint(
        "plate",
        spacer.part,
        Pos(screw_hole.faces().sort_by(Axis.Z).first.center()),
    )
    pcb_joint_face: Face = spacer.faces().filter_by(Axis.Z).sort_by(Axis.Z)[2]
    pcb_joint_vertex: Vertex = pcb_joint_face.vertices().group_by(Axis.X)[0][1]
    pcb_joint = RigidJoint("pcb", spacer.part, Pos(pcb_joint_vertex.center()))

    # Find offset from plate joint to PCB joint
    corner_to_screw_offset = (
        pcb_joint.relative_location.position - plate_joint.relative_location.position
    )
    pcb_screw_x_spacing = pcb_width + corner_to_screw_offset.X * 2
    pcb_screw_y_spacing = pcb_height - corner_to_screw_offset.Y * 2

spacer.part.label = "Spacer"
spacer.part.color = "grey"

'''
PCB
'''
with BuildPart() as pcb:
    with BuildSketch() as pcb_sk:
        Rectangle(pcb_width, pcb_height)
    extrude(amount=pcb_thickness)
    # Create joint for connecting to LCD
    pcb_lcd_joint = RigidJoint("lcd", pcb.part)
    pcb_bottom_face = pcb.part.faces().sort_by(Axis.Z).first
    pcb_top_face = pcb.part.faces().sort_by(Axis.Z).last
with BuildPart() as lcd:
    with BuildSketch(pcb_bottom_face) as lcd_sk:
        Rectangle(lcd_width, lcd_height)
        # Get global corner locations for joints with spacers
        corner_locs = GridLocations(pcb_width, pcb_height, 2, 2).locations
    extrude(amount=lcd_thickness + adhesive_foam_thickness * 2)
    # Create joint for connecting to PCB
    lcd_pcb_joint = RigidJoint("pcb", lcd.part)
with BuildPart() as connector:
    connector_length = 33.5
    connector_width = 4.95
    connector_height = 13.6
    connector_distance_to_right = 7
    connector_distance_to_top = 0.6
    with BuildSketch(pcb_top_face) as connector_sk:
        loc = pcb_top_face.edges().sort_by(Axis.X).last @ 1 - (
            connector_distance_to_right, connector_distance_to_top
        )
        with Locations(loc):
            Rectangle(connector_length, connector_width, align=(Align.MAX, Align.MAX))
    extrude(amount=connector_height)

pcb_lcd_joint.connect_to(lcd_pcb_joint)

pcb.part.label = "PCB"
pcb.part.color = "green"
lcd.part.label = "LCD"
lcd.part.color = "black"
connector.part.label = "Connector"
connector.part.color = "black"

pcb_assembly = Compound(
    label="PCB Assembly",
    children=[pcb.part, lcd.part, connector.part],
)
# Create joints for connecting to spacers
for idx, loc in enumerate(corner_locs):
    if idx >= 2:
        rotation = (idx - 1) * -90
    else:
        rotation = idx * 90
    RigidJoint(
        f"spacer{idx}",
        pcb_assembly,
        loc * Pos(0, 0, -pcb_thickness) * Rot(0, 0, 90 + rotation),
    )

'''
Assemble
'''
spacer_joint_positions = GridLocations(
    pcb_screw_x_spacing,
    pcb_screw_y_spacing,
    2,
    2,
).locations

rpi_mount = TouchscreenMount(
    pcb=pcb_assembly,
    spacer=spacer.part,
    make_cutouts=rpi_cutouts,
    spacer_joint_positions=Pos(-4.6, 0) * spacer_joint_positions,
    spacer_screw_hole_diam=pcb_screw_hole_diam,
    spacer_joint_initial_rot=90,
    spacer_joint_rot_increment=-90,
)

show(
    rpi_mount,
    render_joints=True,
    # transparent=True,
)

rpi_mount.export_step("4Max_Pro_RPi_Touchscreen_Mount.step")
rpi_mount.plate.export_stl("4Max_Pro_RPi_Touchscreen_Mount_Plate.stl")
rpi_mount.spacer.export_stl("4Max_Pro_RPi_Touchscreen_Mount_Spacer.stl")
# rpi_mount.plate.export_3mf(
#     "4Max_Pro_RPi_Touchscreen_Mount_Plate.3mf",
#     tolerance=1e-3,
#     angular_tolerance=0.1,
#     unit=Unit.MILLIMETER,
# )
# rpi_mount.spacer.export_3mf(
#     "4Max_Pro_RPi_Touchscreen_Mount_Spacer.3mf",
#     tolerance=1e-3,
#     angular_tolerance=0.1,
#     unit=Unit.MILLIMETER,
# )