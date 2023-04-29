# %%
import math

import copy
from build123d import *
from ocp_vscode import show, set_port, set_defaults

set_port(3939)
set_defaults(grid=(True, True, True), axes=True, axes0=True)

# %%

pcb_screw_x_spacing = 94.8
pcb_screw_y_spacing = 53
pcb_screw_hole_diam = 2.8

lcd_height = 55.5
lcd_width = 84.6
lcd_thickness = 3.8

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
    def __init__(self, pcb_screw_x_spacing, pcb_screw_y_spacing, pcb_screw_hole_diam):
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
        self.printer_screw_hole_counterbore_diam = 6.8
        self.printer_screw_hole_protrusion_offset = math.tan(
            math.radians(self.printer_mount_angle)
        ) * 7.2 / 2

        padding = 25
        self.overall_width = self.printer_screw_x_spacing + padding / 2
        self.overall_height = self.printer_screw_y_spacing + padding

        self.plate_part = self.plate(
            pcb_screw_x_spacing,
            pcb_screw_y_spacing,
        )
        self.spacer_part: Part = self.spacer()
        self.pcb_part: Part = self.pcb()

        spacers: list[Part] = []
        for idx, plate_spacer_joint in enumerate(self.plate_part.joints.values()):
            spacer_copy = copy.copy(self.spacer_part)
            spacer_copy.label += f" {idx}"
            # Connect screw hole joint to spacer joint, which automatically positions the spacer
            # over the screw hole
            plate_spacer_joint.connect_to(spacer_copy.joints["plate"])
            spacers.append(spacer_copy)

        for idx, pcb_spacer_joint in enumerate(self.pcb_part.joints.values()):
            # Connect PCB joint to spacer joint, which automatically positions the PCB connected
            # to the spacers
            spacers[idx].joints["pcb"].connect_to(pcb_spacer_joint)
        
        super().__init__(
            label="4Max Pro Touchscreen Mount",
            children=[
                self.plate_part,
                self.pcb_part,
                *spacers,
            ],
        )

    def plate(self, pcb_screw_x_spacing, pcb_screw_y_spacing) -> Part:
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
                    Circle(self.printer_screw_hole_counterbore_diam / 2)
                extrude(amount=100, mode=Mode.SUBTRACT)
            
            # PCB screw holes
            with BuildSketch(bottom_face) as pcb_screw_holes_sk:
                with GridLocations(pcb_screw_x_spacing, pcb_screw_y_spacing, 2, 2) as screw_holes:
                    Circle(pcb_screw_hole_diam / 2)
                    pcb_screw_locations = screw_holes.locations
            extrude(dir=(0, 0, 1), until=Until.LAST, mode=Mode.SUBTRACT)

            for idx, loc in enumerate(pcb_screw_locations):
                RigidJoint(f"spacer{idx}", plate.part, loc)

        plate.part.label = "Plate"
        plate.part.color = "black"

        return plate.part

    def spacer(self) -> Part:
        outer_diam = 6
        inner_diam = 3.5
        height = 6.8

        # PCB spacers/standoffs
        with BuildPart() as spacer:
            with BuildSketch() as spacer_sk:
                Circle(radius=outer_diam / 2)
                Circle(radius=inner_diam / 2, mode=Mode.SUBTRACT)
            extrude(amount=height)

        RigidJoint("plate", spacer.part)
        RigidJoint("pcb", spacer.part, Location((0, 0, height)))

        spacer.part.label = "PCB Spacer"
        spacer.part.color = "grey"

        return spacer.part
    
    def pcb(self) -> Part:
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
                with GridLocations(pcb_screw_x_spacing, pcb_screw_y_spacing, 2, 2) as screw_holes:
                    Circle(pcb_screw_hole_diam / 2)
            extrude(dir=(0, 0, 1), until=Until.LAST, mode=Mode.SUBTRACT)

            for idx, loc in enumerate(screw_holes.locations):
                RigidJoint(f"spacer{idx}", pcb.part, loc)

        pcb.part.label = "PCB"
        pcb.part.color = "green"

        return pcb.part


assembly = TouchscreenMount(
    pcb_screw_x_spacing,
    pcb_screw_y_spacing,
    pcb_screw_hole_diam,
)

show(
    assembly,
    render_joints=True,
    # transparent=True,
    reset_camera=False,
)

assembly.export_step("4Max_Pro_Touchscreen_Mount.step")
assembly.plate_part.export_stl("4Max_Pro_Touchscreen_Mount_Plate.stl")
assembly.spacer_part.export_stl("4Max_Pro_Touchscreen_Mount_Spacer.stl")