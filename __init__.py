# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Dauntless Molds",
    "author" : "Martijn Dekker",
    "description" : "",
    "blender" : (2, 92, 0),
    "version" : (0, 1, 2),
    "location" : "",
    "warning" : "",
    "category" : "Mesh"
}

from . operator import DRMoldUnitOperator
from . operator import DRMoldCleanupOperator
from . operator import DRMoldOperator
from . operator import DRAddVClampOperator
from . operator import DRAddHClampOperator
from . operator import DRAddPinOperator
from . operator import DRAddFunnelOperator
from . moldPanel import DRMoldPanel
from . moldPanel import DRDonatePanel
import bpy
from bpy.utils import register_class, unregister_class
from bpy.types import AddonPreferences, PropertyGroup
from bpy.props import StringProperty, FloatProperty, PointerProperty, BoolProperty, CollectionProperty

class DMPreferences(AddonPreferences):
    bl_idname = __name__
    filepath: StringProperty(
        name="OpenSCAD Path",
        subtype="FILE_PATH",
    )

    def draw(self, context):
        layout = self.layout
        layout.label(text="Dauntless Molds preferences")
        layout.prop(self, "filepath")

class DMStepListItem(PropertyGroup):
    name: StringProperty(
        name="Name",
        description="A name for this item",
        default="Untitled"
    )
    ref: PointerProperty(
        name="Object",
        description="Object to store",
        type=bpy.types.Object
    )

class DMSceneProps(PropertyGroup):
    symmetry_mode: BoolProperty(
        name="Symmetry Mode",
        description="Use symmetry when making molds",
        default=True
    )
    
    sides_upside_down: BoolProperty(
        name="Print Sides Upside-Down",
        description="Assume that side parts of the mold will be printed upside-down. This mainly affects overhang compensation.",
        default=True
    )
    
    remesh_resolution: FloatProperty(
        name="Remesh Resolution",
        description="The resolution of the remesh operations",
        subtype='DISTANCE',
        min=0,
        default=2 # 2mm
    )

    glove_thickness: FloatProperty(
        name="Glove Mold Thickness",
        description="The thickness of the glove mold",
        subtype='DISTANCE',
        min=0,
        default=3 # 3mm
    )
    glove_rim_height: FloatProperty(
        name="Glove Rim Height",
        description="The height of the glove mold's rim",
        subtype='DISTANCE',
        min=0,
        default=6 # 6mm
    )
    glove_rim_width: FloatProperty(
        name="Glove Rim Width",
        description="The width of the glove mold's rim",
        subtype='DISTANCE',
        min=0,
        default=6 # 6mm
    )
    shell_thickness: FloatProperty(
        name="Shell Thickness",
        description="The thickness of the mold shell, over the glove mold's rim",
        subtype='DISTANCE',
        min=0,
        default=4 # 4mm
    )
    shell_rim_height: FloatProperty(
        name="Shell Rim Height",
        description="The height of the mold shell's rim",
        subtype='DISTANCE',
        min=0,
        default=10 # 10mm
    )
    shell_rim_width: FloatProperty(
        name="Shell Rim Width",
        description="The width of the mold shell's rim",
        subtype='DISTANCE',
        min=0,
        default=10 # 10mm
    )

    mold_parent: PointerProperty(
        name="Parent Mesh",
        description="Mesh that this mesh was based on",
        type=bpy.types.Object
    )
    mold_draft_angle: PointerProperty(
        name="Draft Angle Mesh",
        description="Mesh with any gaps filled in",
        type=bpy.types.Object
    )
    mold_glove_surface: PointerProperty(
        name="Glove Mold Surface Mesh",
        description="Mesh for glove mold surface",
        type=bpy.types.Object
    )
    mold_glove_inflated: PointerProperty(
        name="Glove Mold Inflated Mesh",
        description="Inflated mesh for glove mold rim",
        type=bpy.types.Object
    )
    mold_glove_complete: PointerProperty(
        name="Glove Mold Completed Mesh",
        description="Finished glove mold cutout mesh",
        type=bpy.types.Object
    )

    mold_shell_base: PointerProperty(
        name="Mold Shell Base Shape",
        description="Mold shell base shape",
        type=bpy.types.Object
    )
    mold_shell_organic: PointerProperty(
        name="Mold Shell Inflated Shape",
        description="Mold shell, inflated",
        type=bpy.types.Object
    )
    mold_shell_finished: PointerProperty(
        name="Mold Shell Finished Shape",
        description="Mold shell, mostly finished",
        type=bpy.types.Object
    )
    mold_shell_cut: PointerProperty(
        name="Mold Shell Cut Shape",
        description="Mold shell shape, cut to size",
        type=bpy.types.Object
    )
    mold_shell_half: CollectionProperty(
        name="Mold Shell Half",
        description="Mold shell half",
        type=DMStepListItem
    )
    mold_base_shape: PointerProperty(
        name="Mold Base Shape",
        description="Middle part of the mold",
        type=bpy.types.Object
    )

_classes = (DRMoldUnitOperator, DMStepListItem, DMSceneProps,
            DRMoldCleanupOperator, DRMoldOperator, DRAddVClampOperator, DRAddHClampOperator, DRAddPinOperator, DRAddFunnelOperator,
            DRMoldPanel, DRDonatePanel, DMPreferences)

def register():
    for _class in _classes:
        register_class(_class)
    
    bpy.types.Object.dr_molds = PointerProperty(type=DMSceneProps)

def unregister():
    del bpy.types.Object.dr_molds
    
    for _class in _classes:
        unregister_class(_class)

if __name__ == "__main__":
    register()