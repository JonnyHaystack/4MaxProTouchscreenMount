import copy
import math
from collections.abc import Callable

from build123d import *


class TouchscreenMount(Compound):
    def __init__(
            self,
            pcb: Compound,
            spacer: Part,
            make_cutouts: Callable[[BuildSketch]],
            pcb_screw_x_spacing: float,
            pcb_screw_y_spacing: float,
            pcb_screw_hole_diam: float,
    ):
        # Customised components
        self.spacer = spacer
        self.pcb = pcb

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

        # Measurements for the plate itself
        padding = 25
        self.plate_width = self.printer_screw_x_spacing + padding / 2
        self.plate_height = self.printer_screw_y_spacing + padding
        self.plate_thickness = 3
        self.plate_corner_radius = 3

        self.plate = self.make_plate(
            make_cutouts,
            pcb_screw_x_spacing,
            pcb_screw_y_spacing,
            pcb_screw_hole_diam,
        )

        spacers: list[Part] = []
        for idx, plate_spacer_joint in enumerate(self.plate.joints.values()):
            spacer_copy = copy.copy(self.spacer)
            spacer_copy.label += f" {idx}"
            # Connect screw hole joint to spacer joint, which automatically positions the spacer
            # over the screw hole
            plate_spacer_joint.connect_to(spacer_copy.joints["plate"])
            spacers.append(spacer_copy)

        for idx, pcb_spacer_joint in enumerate(self.pcb.joints.values()):
            # Connect PCB joint to spacer joint, which automatically positions the PCB connected
            # to the spacers
            spacers[idx].joints["pcb"].connect_to(pcb_spacer_joint)
        
        super().__init__(
            label="4Max Pro Touchscreen Mount",
            children=[
                self.plate,
                self.pcb,
                *spacers,
            ],
        )

    def make_plate(
            self,
            make_cutouts: Callable[[BuildSketch]],
            pcb_screw_x_spacing: float,
            pcb_screw_y_spacing: float,
            pcb_screw_hole_diam: float,
    ) -> Part:
        with BuildPart() as plate:
            # Base shape of mounting plate
            with BuildSketch() as base_sk:
                RectangleRounded(self.plate_width, self.plate_height, self.plate_corner_radius)
                make_cutouts(base_sk)

            extrude(amount=self.plate_thickness)

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
            # Create joints for connecting to spacers
            for idx, loc in enumerate(pcb_screw_locations):
                RigidJoint(f"spacer{idx}", plate.part, loc)

        plate.part.label = "Plate"
        plate.part.color = "indigo"

        return plate.part