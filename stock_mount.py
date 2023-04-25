# %%
import math

import copy
from build123d import *
from ocp_vscode import show, set_port, set_defaults

set_port(3939)
set_defaults(grid=(True, True, True), axes=True, axes0=True)

# %%

pcb_width = 107.6
pcb_height = 60
pcb_thickness = 1.6
pcb_screw_x_spacing = 94.8
pcb_screw_y_spacing = 53
pcb_standoff_height = 6.8
pcb_screw_hole_diameter = 2.8
pcb_standoff_od = 6
pcb_standoff_id = 3.5

lcd_height = 55.5
lcd_width = 84.6
lcd_thickness = 3.8

lcd_screw_x_spacing = 96
lcd_screw_y_spacing = 53

plate_height = 59
plate_thickness = 3
plate_corner_radius = 3
printer_mount_angle = 45
printer_screw_x_spacing = 116
printer_screw_y_spacing_3d = 28.5
printer_screw_z_spacing = 28
printer_screw_y_spacing = printer_screw_z_spacing / math.sin(math.radians(printer_mount_angle))
printer_screw_hole_od = 10
printer_screw_hole_id = 3.6
printer_screw_hole_length_including_counterbore = 10.5
printer_screw_hole_counterbore_depth = 6.1
printer_screw_hole_counterbore_diameter = 6.8
printer_screw_hole_protrusion_offset = math.tan(math.radians(printer_mount_angle)) * 7.2 / 2

centre_cutout_width = 77.75
centre_cutout_height = 34.8
centre_cutout_corner_radius = 2

edge_cutout_width = 16.5
edge_cutout_height = 22

padding = 25
overall_width = printer_screw_x_spacing + padding / 2
overall_height = printer_screw_y_spacing + padding

with BuildPart() as plate:
    # Base shape of mounting plate
    with BuildSketch() as base_sk:
        Rectangle(overall_width, overall_height)

        # Edge cutouts
        with Locations(base_sk.edges().group_by(Axis.X)[-1][0] @ 0.5):
            edge_cutout = Rectangle(
                edge_cutout_width,
                edge_cutout_height,
                align=(Align.MAX, Align.CENTER),
                mode=Mode.SUBTRACT,
            )
            mirror(edge_cutout.faces(), about=Plane.YZ, mode=Mode.SUBTRACT)

        fillet(base_sk.vertices(), radius=plate_corner_radius)

        # Centre cutout
        RectangleRounded(
            centre_cutout_width,
            centre_cutout_height,
            centre_cutout_corner_radius,
            mode=Mode.SUBTRACT,
        )
    extrude(amount=plate_thickness)

    top_face = plate.part.faces().sort_by(Axis.Z).last
    bottom_face = plate.part.faces().sort_by(Axis.Z).first

    # Screw posts for mounting to printer
    with Locations(top_face):
        locs = GridLocations(printer_screw_x_spacing, printer_screw_y_spacing, 2, 2)
    for l in locs:
        pln1 = Plane(l).rotated(
            (printer_mount_angle + 180, 0, 0)
        ).offset(-printer_screw_hole_protrusion_offset)
        # Protruding part of screw post
        with BuildSketch(pln1) as screw_post_sk:
            Circle(printer_screw_hole_od / 2)
        screw_post = extrude(until=Until.NEXT)

        # Screw hole
        with BuildSketch(pln1) as screw_hole_sk:
            Circle(printer_screw_hole_id / 2)
        screw_hole = extrude(until=Until.LAST, mode=Mode.SUBTRACT)

        # Counterbore for printer screw hole
        pln2 = pln1.offset(
            printer_screw_hole_length_including_counterbore - printer_screw_hole_counterbore_depth
        )
        with BuildSketch(pln2) as counterbore_sk:
            Circle(printer_screw_hole_counterbore_diameter / 2)
        extrude(amount=100, mode=Mode.SUBTRACT)
    
    # PCB screw holes
    with BuildSketch(top_face) as pcb_screw_holes_sk:
        with GridLocations(pcb_screw_x_spacing, pcb_screw_y_spacing, 2, 2) as screw_holes:
            Circle(pcb_screw_hole_diameter / 2)
    extrude(dir=(0, 0, -1), until=Until.LAST, mode=Mode.SUBTRACT)

with BuildPart() as spacer:
    with BuildSketch() as spacer_sk:
        Circle(radius=pcb_standoff_od / 2)
        Circle(radius=pcb_standoff_id / 2, mode=Mode.SUBTRACT)
    extrude(amount=pcb_standoff_height)

show(
    plate,
    # colors=["gold", "cyan", "magenta", "lime"],
    transparent=True,
    reset_camera=False,
)

plate.part.export_step("4Max_Pro_Touchscreen_Mount.step")
spacer.part.export_step("4Max_Pro_Touchscreen_Spacer.step")