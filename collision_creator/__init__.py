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
from mathutils import Vector


def create_bounding_box(offset=0, apply_offset=False, parent_to_target=True):
    # Get the active object
    obj = bpy.context.active_object

    if not apply_offset:
        offset = 0

    # Get the bounding box of the object
    bbox = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    min_x = min([v.x for v in bbox]) - offset
    max_x = max([v.x for v in bbox]) + offset
    min_y = min([v.y for v in bbox]) - offset
    max_y = max([v.y for v in bbox]) + offset
    min_z = min([v.z for v in bbox]) - offset
    max_z = max([v.z for v in bbox]) + offset
    size_x = max_x - min_x
    size_y = max_y - min_y
    size_z = max_z - min_z

    # Create a cube with the size of the bounding box
    bpy.ops.mesh.primitive_cube_add(size=1)
    cube = bpy.context.active_object
    cube.scale = (size_x, size_y, size_z)
    cube.location = (min_x + size_x/2, min_y + size_y/2, min_z + size_z/2)

    # freeze transforms
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    
    # set origin to center of mass
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS', center='MEDIAN')

    # parent to target, without moving
    if parent_to_target:
        cube.parent = obj
        cube.matrix_parent_inverse = obj.matrix_world.inverted()


class CreateBoundingBoxOperator(bpy.types.Operator):
    bl_idname = "collision.create_bounding_box"
    bl_label = "Create Bounding Box"

    def execute(self, context):
        create_bounding_box(offset=context.preferences.addons[__name__].preferences.offset, 
                            apply_offset=context.preferences.addons[__name__].preferences.apply_offset, 
                            parent_to_target=context.preferences.addons[__name__].preferences.parent_to_target
                            )
        return {'FINISHED'}
    

class MyAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __name__  # "collision_creator"

    apply_offset: bpy.props.BoolProperty(
        name="Apply Offset",
        description="Apply an offset to the selected object",
        default=True
    )

    offset: bpy.props.FloatProperty(
        name="Offset",
        description="Offset value",
        default=1.0,
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
        row.operator("collision.create_bounding_box", text="Box", icon="MESH_CUBE")
        row.operator("mesh.primitive_circle_add", text="Convex", icon="MESH_CIRCLE")


def register():
    bpy.utils.register_class(MyAddonPreferences)
    bpy.utils.register_class(CollisionCreatorPanel)
    bpy.utils.register_class(CreateBoundingBoxOperator)


def unregister():
    bpy.utils.unregister_class(MyAddonPreferences)
    bpy.utils.unregister_class(CollisionCreatorPanel)
    bpy.utils.unregister_class(CreateBoundingBoxOperator)


# if __name__ == "__main__":
#     register()