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

from . operator import DRMoldCleanupOperator
from . operator import DRMoldOperator
from . operator import DRAddVClampOperator
from . operator import DRAddHClampOperator
from . operator import DRAddPinOperator
from . operator import DRAddFunnelOperator
from . moldPanel import DRMoldPanel
from . moldPanel import DRDonatePanel
from bpy.utils import register_class, unregister_class
from bpy.types import AddonPreferences
from bpy.props import StringProperty

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

_classes = (DRMoldCleanupOperator, DRMoldOperator, DRAddVClampOperator, DRAddHClampOperator, DRAddPinOperator, DRAddFunnelOperator, DRMoldPanel, DRDonatePanel, DMPreferences)

def register():
    for _class in _classes:
        register_class(_class)

def unregister():
    for _class in _classes:
        unregister_class(_class)

if __name__ == "__main__":
    register()