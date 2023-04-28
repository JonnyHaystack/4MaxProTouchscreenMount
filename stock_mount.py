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

# Measurements for the plate itself
plate_height = 59
plate_thickness = 3
plate_corner_radius = 3

# Measurements for cutouts in the plate
centre_cutout_width = 77.75
centre_cutout_height = 34.8
centre_cutout_corner_radius = 2

edge_cutout_width = 16.5
edge_cutout_height = 22


class TouchscreenMount(Compound):
    def __init__(self, pcb_screw_x_spacing, pcb_screw_y_spacing):
        # Measurements for the points of attachment to the printer
        self.printer_mount_angle = 45
        self.printer_screw_x_spacing = 116
        printer_screw_z_spacing = 28
        self.printer_screw_y_spacing = printer_screw_z_spacing / math.sin(
            math.radians(self.printer_mount_angle)
        )
        self.printer_screw_hole_od = 10
        self.printer_screw_hole_id = 3.6
        self.printer_screw_hole_length = 10.5
        self.printer_screw_hole_counterbore_depth = 6.1
        self.printer_screw_hole_counterbore_diameter = 6.8
        self.printer_screw_hole_protrusion_offset = math.tan(
            math.radians(self.printer_mount_angle)
        ) * 7.2 / 2

        padding = 25
        self.overall_width = self.printer_screw_x_spacing + padding / 2
        self.overall_height = self.printer_screw_y_spacing + padding

        self.plate_part, pcb_screw_locations = self.plate(
            pcb_screw_x_spacing,
            pcb_screw_y_spacing,
        )
        self.spacer_part: Part = self.spacer()
        self.pcb_part: Part = self.pcb()

        spacers = []
        for idx, loc in enumerate(pcb_screw_locations):
            spacer_copy = copy.copy(self.spacer_part)
            spacer_copy.label = f"PCB Spacer {idx}"
            # Place rigid joint on plate
            screw_hole_joint = RigidJoint(f"screw_hole{idx}", self.plate_part, loc)
            # Place rigid joint on spacer
            spacer_joint = RigidJoint("spacer", spacer_copy)
            # Connect screw hole joint to spacer joint, which automatically positions the spacer
            # over the screw hole
            screw_hole_joint.connect_to(spacer_joint)
            spacers.append(spacer_copy)
    
        super().__init__(
            label="4Max Pro Touchscreen Mount",
            children=[self.plate_part, self.pcb_part, *spacers],
        )

    def plate(self, pcb_screw_x_spacing, pcb_screw_y_spacing) -> tuple[Part, list[Location]]:
        with BuildPart() as plate:
            # Base shape of mounting plate
            with BuildSketch() as base_sk:
                Rectangle(self.overall_width, self.overall_height)

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
                locs = GridLocations(
                    self.printer_screw_x_spacing,
                    self.printer_screw_y_spacing,
                    2,
                    2,
                )
            for l in locs:
                pln1 = Plane(l).rotated(
                    (self.printer_mount_angle + 180, 0, 0)
                ).offset(-self.printer_screw_hole_protrusion_offset)
                # Protruding part of screw post
                with BuildSketch(pln1) as screw_post_sk:
                    Circle(self.printer_screw_hole_od / 2)
                screw_post = extrude(until=Until.NEXT)

                # Screw hole
                with BuildSketch(pln1) as screw_hole_sk:
                    Circle(self.printer_screw_hole_id / 2)
                screw_hole = extrude(until=Until.LAST, mode=Mode.SUBTRACT)

                # Counterbore for printer screw hole
                pln2 = pln1.offset(
                    self.printer_screw_hole_length - self.printer_screw_hole_counterbore_depth
                )
                with BuildSketch(pln2) as counterbore_sk:
                    Circle(self.printer_screw_hole_counterbore_diameter / 2)
                extrude(amount=100, mode=Mode.SUBTRACT)
            
            # PCB screw holes
            with BuildSketch(bottom_face) as pcb_screw_holes_sk:
                with GridLocations(pcb_screw_x_spacing, pcb_screw_y_spacing, 2, 2) as screw_holes:
                    Circle(pcb_screw_hole_diameter / 2)
                    pcb_screw_locations = screw_holes.locations
            extrude(dir=(0, 0, 1), until=Until.LAST, mode=Mode.SUBTRACT)

        plate.part.label = "Plate"
        return plate.part, pcb_screw_locations

    def spacer(self) -> Part:
        # PCB spacers/standoffs
        with BuildPart() as spacer:
            with BuildSketch() as spacer_sk:
                Circle(radius=pcb_standoff_od / 2)
                Circle(radius=pcb_standoff_id / 2, mode=Mode.SUBTRACT)
            extrude(amount=pcb_standoff_height)

        return spacer.part
    
    def pcb(self) -> Part:
        with BuildPart() as pcb:
            with BuildSketch() as pcb_sk:
                RectangleRounded(pcb_width, pcb_height, radius=2)
            extrude(amount=pcb_thickness)

        pcb.part.label = "PCB"
        return pcb.part


assembly = TouchscreenMount(
    pcb_screw_x_spacing,
    pcb_screw_y_spacing,
)

show(
    assembly,
    render_joints=True,
    transparent=True,
    reset_camera=False,
)

assembly.export_step("4Max_Pro_Touchscreen_Mount.step")
assembly.plate_part.export_stl("4Max_Pro_Touchscreen_Mount_Plate.stl")
assembly.spacer_part.export_stl("4Max_Pro_Touchscreen_Mount_Spacer.stl")