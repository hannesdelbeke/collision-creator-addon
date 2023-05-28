bl_info = {
    "name": "Collision creator",
    "author": "Hannes",
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "N-Panel",
    "description": "create quick simple collision meshes",
    "warning": "",
    "doc_url": "",
    "category": "Modeling",
}


import bpy


class MyAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__  # "collision_creator"

    apply_offset: bpy.props.BoolProperty(
        name="Apply Offset",
        description="Apply an offset to the selected object",
        default=False
    )

    offset: bpy.props.FloatProperty(
        name="Offset",
        description="Offset value",
        default=0
    )

    parent_to_target: bpy.props.BoolProperty(
        name="Parent to Target",
        description="Parent the selected object to the target object",
        default=True
    )

    tri_count_limit: bpy.props.IntProperty(
        name="Triangle Count Limit",
        description="Triangle count limit",
        default=32,
        min=1,
    )


class CollisionCreatorPanel(bpy.types.Panel):
    bl_idname = "MYADDON_PT_panel"
    bl_label = bl_info["name"]
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Collisions"


    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(context.preferences.addons[__name__].preferences, "apply_offset")
        row.prop(context.preferences.addons[__name__].preferences, "offset")

        row = layout.row()
        row.prop(context.preferences.addons[__name__].preferences, "parent_to_target")
        
        row = layout.row()
        row.prop(context.preferences.addons[__name__].preferences, "tri_count_limit")

        row = layout.row()
        row.operator("mesh.primitive_cube_add", text="Box", icon="MESH_CUBE")
        row.operator("mesh.primitive_circle_add", text="Convex", icon="MESH_CIRCLE")


def register():
    bpy.utils.register_class(MyAddonPreferences)
    bpy.utils.register_class(CollisionCreatorPanel)


def unregister():
    bpy.utils.unregister_class(MyAddonPreferences)
    bpy.utils.unregister_class(CollisionCreatorPanel)


# if __name__ == "__main__":
#     register()