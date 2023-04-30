# %%
from build123d import *
from ocp_vscode import show, set_port, set_defaults

from touchscreen_mount import TouchscreenMount

set_port(3939)
set_defaults(grid=(True, True, True), axes=True, axes0=True, reset_camera=False)

# %%


def rpi_cutouts(base_sk: BuildSketch):
    return


def rpi_spacer():
    # Stock standoff height minus the extra height added to the display by the adhesive
    pcb_mounting_height = 6.8 - 0.6
    side_length = 8.5
    wall_thickness = 1.2
    bottom_thickness = 1.2
    pcb_thickness = 1.6
    lcd_thickness = 3.8
    screw_hole_diam = 3.5
    total_height = pcb_mounting_height + pcb_thickness + lcd_thickness

    with BuildPart() as spacer:
        with BuildSketch() as spacer_sk:
            Rectangle(side_length, side_length)
        extrude(amount=total_height)

        with BuildSketch(spacer.faces().sort_by(Axis.Z).last) as ledge_sk:
            with Locations((wall_thickness / 2, -wall_thickness / 2)):
                Rectangle(side_length - wall_thickness, side_length - wall_thickness)
        ledge = extrude(amount=-(total_height - pcb_mounting_height), mode=Mode.SUBTRACT)

        with BuildSketch(ledge.faces().sort_by(Axis.Z).first) as ledge_sk2:
            with Locations((wall_thickness / 2, wall_thickness / 2)):
                Rectangle(side_length - wall_thickness * 2, side_length - wall_thickness * 2)
        ledge2 = extrude(amount=pcb_mounting_height - bottom_thickness, mode=Mode.SUBTRACT)
        
        with BuildSketch(ledge2.faces().sort_by(Axis.Z).first) as screw_hole_sk:
            Circle(screw_hole_diam / 2)
        screw_hole = extrude(until=Until.LAST, mode=Mode.SUBTRACT)

        RigidJoint(
            "plate",
            spacer.part,
            Pos(screw_hole.faces().sort_by(Axis.Z).first.center()),
        )
        pcb_joint_face: Face = spacer.faces().filter_by(Axis.Z).sort_by(Axis.Z)[2]
        pcb_joint_vertex: Vertex = pcb_joint_face.vertices().group_by(Axis.X)[0][1]
        RigidJoint("pcb", spacer.part, Pos(pcb_joint_vertex.center()))

    show(
        spacer.part,
        pcb_joint_vertex,
        # plate_joint,
        render_joints=True,
        # screw_hole_face,
        # spacer_sk2,
    )
    
    spacer.part.export_step("rpi_spacer.step")
    
    return spacer.part


def rpi_touchscreen_pcb() -> Compound:
    pcb_width = 85.2
    pcb_height = 54.85
    pcb_thickness = 1.6
    with BuildPart() as pcb:
        with BuildSketch() as pcb_sk:
            Rectangle(pcb_width, pcb_height)
        extrude(amount=pcb_thickness)
        # Create joint for connecting to LCD
        pcb_lcd_joint = RigidJoint("lcd", pcb.part)

    pcb_bottom_face = pcb.part.faces().sort_by(Axis.Z).first
    pcb_top_face = pcb.part.faces().sort_by(Axis.Z).last

    with BuildPart() as lcd:
        lcd_width = 82.5
        lcd_height = 54.35
        # The adhesive foam used on this PCB adds about 1.2mm extra height
        lcd_thickness = 3.8 + 1.2
        with BuildSketch(pcb_bottom_face) as lcd_sk:
            Rectangle(lcd_width, lcd_height)
        extrude(amount=lcd_thickness)
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
    corners = pcb.faces().sort_by(Axis.Z).first.vertices()
    for idx, loc in enumerate(Locations(*corners)):
        RigidJoint(f"spacer{idx}", pcb_assembly, loc * Pos(0, 0, -pcb_thickness))

    return pcb_assembly


rpi_spacer()
# show(
#     rpi_mount,
#     render_joints=True,
#     # transparent=True,
# )

# rpi_mount.export_step("4Max_Pro_Touchscreen_Mount.step")
# rpi_mount.plate.export_stl("4Max_Pro_Touchscreen_Mount_Plate.stl")
# rpi_mount.spacer.export_stl("4Max_Pro_Touchscreen_Mount_Spacer.stl")