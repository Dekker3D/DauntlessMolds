import bpy


class DRPanel(bpy.types.Panel):
    bl_category = "Dauntless Molds"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        obj = context.active_object
        return obj is not None and obj.type == 'MESH' and obj.mode in {'OBJECT'}

class DRMoldPanel(DRPanel):
    bl_idname = "DR_Molds_PT_MoldPanel"
    bl_label = "Dauntless Molds"

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        box.label(text="Building the mold")
        box.operator("drmold.cleanup", text="Clean up")
        box.operator("drmold.addfunnel", text="Add funnel")
        box.operator("drmold.doall", text="Do all steps")
        
        box = layout.box()
        box.label(text="Adding clamps and pins")
        box.operator("drmold.addvclamp", text="Add vertical clamp")
        box.operator("drmold.addhclamp", text="Add horizontal clamp")
        box.operator("drmold.addpin", text="Add pin")

class DRDonatePanel(DRPanel):
    bl_idname = "DR_Molds_PT_DonatePanel"
    bl_label = "Donate"

    def draw(self, context):
        layout = self.layout

        layout.label(text="If you haven't already,")
        layout.label(text="Consider donating to the")
        layout.label(text="developer of this add-on!")

