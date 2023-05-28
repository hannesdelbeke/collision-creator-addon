bl_info = {
    "name": "Collision creator",
    "author": "Hannes",
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "3D View N-Panel 'Collisions'",
    "description": "Create quick & simple collision meshes",
    "warning": "",
    "doc_url": "",
    "category": "Modeling",
}


import bpy
import bmesh
from mathutils import Vector


def create_bounding_box(offset=0, apply_offset=False, parent_to_target=True):
    """Create a bounding box from the active object."""
    # Get the active object
    obj = bpy.context.active_object

    if not obj:
        print("No object selected, cannot create bounding box")
        return
    
    if not apply_offset:
        offset = 0
    
    # Push an undo step
    bpy.ops.ed.undo_push(message="Create bounding box collision mesh")

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


def create_convex_hull(obj=None):
    """Create a convex hull from the active object and return it."""
    obj = obj or bpy.context.active_object

    if not obj:
        print("No object selected, cannot create convex hull")
        return
    
    orig_mesh = obj.data
    
    new_bmesh = bmesh.new()
    new_bmesh.from_mesh(orig_mesh)
    obj_copy = obj.copy()

    new_mesh = bpy.data.meshes.new(f"UCX_{orig_mesh.name}")
    conv_hull = bmesh.ops.convex_hull(new_bmesh, input=new_bmesh.verts)
    bmesh.ops.delete(
            new_bmesh,
            geom=conv_hull.get("geom_unused", []) + conv_hull.get("geom_interior", []),
            context='VERTS',
            )
    new_bmesh.to_mesh(new_mesh)
    obj_copy.name = f"UCX_{obj.name}"
    obj_copy.data = new_mesh

    bpy.context.scene.collection.objects.link(obj_copy)
    new_bmesh.free()  # not sure if this is needed

    # set obj_copy as active object
    bpy.context.view_layer.objects.active = obj_copy

    return obj_copy


def add_thickness(obj=None, offset=0, apply_offset=True, apply_modifier=True) -> bpy.types.Object:
    """Add thickness to the object using the solidify modifier."""

    obj = obj or bpy.context.active_object

    if not apply_offset:
        return obj
    
    if not obj:
        print(f"Object '{obj}' is not valid, cannot add thickness")
        return obj

    # Add the solidify modifier
    mod = obj.modifiers.new(name="Solidify", type="SOLIDIFY")
    mod.thickness = offset
    mod.use_even_offset = False
    mod.offset = 0
    # mod.use_quality_normals = True
    mod.use_rim = False
    
    mod_name = mod.name
    mod = None  # free the reference to the modifier so it can be applied without access violation crash
    if apply_modifier:
        bpy.ops.object.modifier_apply(modifier=mod_name)

    # set active
    bpy.context.view_layer.objects.active = obj
    return obj


def _create_convex_hull(offset=0, apply_offset=False, parent_to_target=True):#
    """
    Create a convex hull from the active object.
    apply_offset: Apply an offset to the selected object
    """
    
    # Push an undo step
    bpy.ops.ed.undo_push(message="Create convex hull collision mesh")

    obj_original = bpy.context.active_object
    create_convex_hull()
    add_thickness( offset=offset, apply_offset=apply_offset)

    # # parent to target, without moving
    # if parent_to_target:
    #     obj.parent = obj_original
    #     obj.matrix_parent_inverse = obj_original.matrix_world.inverted()


class CreateBoundingBoxOperator(bpy.types.Operator):
    """Create a bounding box around the selected object"""
    bl_idname = "collision.create_bounding_box"
    bl_label = "Create Bounding Box"

    def execute(self, context):
        create_bounding_box(offset=context.preferences.addons[__name__].preferences.offset, 
                            apply_offset=context.preferences.addons[__name__].preferences.apply_offset, 
                            parent_to_target=context.preferences.addons[__name__].preferences.parent_to_target
                            )
        return {'FINISHED'}
    
class CreateConvexHullOperator(bpy.types.Operator):
    """Create a convex hull around the selected object"""
    bl_idname = "collision.create_convex_hull"
    bl_label = "Create Convex Hull"

    def execute(self, context):
        _create_convex_hull(offset=context.preferences.addons[__name__].preferences.offset, 
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
    """draw a N-Panel in the 3D View to control the collision creator addon"""
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
        row.operator(CreateBoundingBoxOperator.bl_idname, text="Box", icon="MESH_CUBE")
        row.operator(CreateConvexHullOperator.bl_idname, text="Convex", icon="MESH_CIRCLE")


def register():
    bpy.utils.register_class(MyAddonPreferences)
    bpy.utils.register_class(CollisionCreatorPanel)
    bpy.utils.register_class(CreateBoundingBoxOperator)
    bpy.utils.register_class(CreateConvexHullOperator)


def unregister():
    bpy.utils.unregister_class(MyAddonPreferences)
    bpy.utils.unregister_class(CollisionCreatorPanel)
    bpy.utils.unregister_class(CreateBoundingBoxOperator)
    bpy.utils.unregister_class(CreateConvexHullOperator)


if __name__ == "__main__":
    register()
