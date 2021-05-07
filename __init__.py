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
    "blender" : (2, 80, 0),
    "version" : (0, 0, 1),
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
from bpy.props import StringProperty, FloatProperty, PointerProperty, BoolProperty

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

class DMSceneProps(PropertyGroup):
    symmetry_mode: BoolProperty(
        name="Symmetry Mode",
        description="Use symmetry when making molds",
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

_classes = (DRMoldUnitOperator, DMSceneProps, DRMoldCleanupOperator, DRMoldOperator, DRAddVClampOperator, DRAddHClampOperator, DRAddPinOperator, DRAddFunnelOperator,
            DRMoldPanel, DRDonatePanel, DMPreferences)

def register():
    for _class in _classes:
        register_class(_class)
    
    bpy.types.Scene.dr_molds = PointerProperty(type=DMSceneProps)

def unregister():
    del bpy.types.Scene.dr_molds
    
    for _class in _classes:
        unregister_class(_class)

if __name__ == "__main__":
    register()