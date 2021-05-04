import bpy

class MoldPanel(bpy.types.Panel):
    bl_idname = "DR_Molds_Panel"
    bl_label = "Dauntless Molds"
    bl_category = "Dauntless Molds"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        column1 = row.column()
        column1.operator("drmold.cleanup", text="Clean up")
        column1.operator("drmold.doall", text="Do all steps")
        column2 = row.column()
        column2.operator("drmold.addvclamp", text="Add vertical clamp")
        column2.operator("drmold.addhclamp", text="Add horizontal clamp")
        column2.operator("drmold.addpin", text="Add pin")