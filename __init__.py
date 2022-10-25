bl_info = {
    "name": "Low Poly Tree Generator",
    "author": "Lukas Florea",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Properties > Low Poly Tree",
    "description": "Generates a low poly tree with leafs",
    "warning": "",
    "wiki_url": "https://github.com/LuFlo/low-poly-tree-generator/wiki",
    "tracker_url": "https://github.com/LuFlo/low-poly-tree-generator/issues/new",
    "category": "Add Mesh"
}

import bpy
import random
import string
from bpy.props import (
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
    EnumProperty,
    BoolProperty,
    PointerProperty,
    CollectionProperty,
)
from bpy.types import PropertyGroup, Panel
from . import util


def generate_seed_for_scene(scene):
    letter = string.ascii_letters
    scene.lptg_seed = ''.join(random.choice(letter) for i in range(10))

class PerformGeneration(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.generate_tree"
    bl_label = "Generate Tree"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        try:
            util.generate_tree(context,
                               stem_mat=scene.lptg_stem_material,
                               leaf_mat_prefix=scene.lptg_leaf_material,
                               initial_radius=scene.lptg_init_radius,
                               depth=scene.lptg_branch_depth,
                               leaf_size=scene.lptg_leaf_size,
                               leaf_size_deviation=scene.lptg_leaf_size_deviation,
                               max_branch_probability=scene.lptg_max_branch_probability,
                               start_branch_propability=scene.lptg_start_branch_probability,
                               branch_probability_coeff=scene.lptg_branch_probability_coeff,
                               angle_profiles=[scene.lptg_angles_1, scene.lptg_angles_2, scene.lptg_angles_3])
            if scene.lptg_generate_seed_on_generate:
                generate_seed_for_scene(scene)
        except ValueError as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class NewSeed(bpy.types.Operator):
    bl_idname = "object.new_seed"
    bl_label = "New seed"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        try:
            generate_seed_for_scene(scene)
        except ValueError as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class VIEW3D_PT_low_poly_tree(Panel):

    bl_category = "Low Poly Tree"
    bl_idname = "VIEW3D_PT_low_poly_tree"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "Low Poly Tree"

    @classmethod
    def poll(cls, context):
        return True

    def draw(self, context):
        layout = self.layout

        seedBox = layout.box()
        seedBox.label(text="Seed")
        row = seedBox.row()
        row.operator("object.new_seed")

        row = seedBox.row()
        row.column().label(text="Seed")
        row.column().prop(context.scene, "lptg_seed")

        seedBox.prop(context.scene, "lptg_generate_seed_on_generate")

        branchBox = layout.box()
        branchBox.label(text="Branch")
        branchBox.row().prop(context.scene, "lptg_branch_depth")
        branchBox.row().prop(context.scene, "lptg_start_branch_probability")
        branchBox.row().prop(context.scene, "lptg_max_branch_probability")
        branchBox.row().prop(context.scene, "lptg_branch_probability_coeff")
        branchBox.row().prop(context.scene, "lptg_init_radius")
        branchBox.row().prop(context.scene, "lptg_radius_factor")
        branchBox.row().prop(context.scene, "lptg_stem_section_length")
        branchBox.row().prop(context.scene, "lptg_stem_length_factor")

        angleBox = layout.box()
        angleBox.label(text="Profile")
        angleBox.row().prop(context.scene, "lptg_angles_1", text="Angle Range 1/3")
        angleBox.row().prop(context.scene, "lptg_angles_2", text="Angle Range 2/3")
        angleBox.row().prop(context.scene, "lptg_angles_3", text="Angle Range 3/3")

        row = branchBox.row()
        row.column().label(text="Stem material")
        row.column().prop(context.scene, "lptg_stem_material")

        leafBox = layout.box()
        leafBox.label(text="Leaf")
        row = leafBox.row()
        row.column().label(text="Leaf material prefix")
        row.column().prop(context.scene, "lptg_leaf_material")

        leafBox.row().prop(context.scene, "lptg_generate_leaf")
        row = leafBox.row()
        row.column().label(text="Leaf geometry")
        row.column().prop(context.scene, "lptg_leaf_geometry")
        leafBox.row().prop_search(context.scene, "lptg_leaf_object", context.scene, "objects")

        leafBox.row().prop(context.scene, "lptg_leaf_size")
        leafBox.row().prop(context.scene, "lptg_leaf_size_deviation")

        row = layout.row()
        row.operator("object.generate_tree")


def register():
    bpy.utils.register_class(VIEW3D_PT_low_poly_tree)
    bpy.utils.register_class(PerformGeneration)
    bpy.utils.register_class(NewSeed)

    bpy.types.Scene.lptg_seed = StringProperty(
        default="hYukTFphuI",
        name="", description="Seed for the random number generator")
    bpy.types.Scene.lptg_branch_depth = IntProperty(
        name="Branch depth",
        default=10, min=1, max=20)
    bpy.types.Scene.lptg_stem_material = PointerProperty(
        type=bpy.types.Material,
        name="", description="Stem Material")
    bpy.types.Scene.lptg_leaf_material = StringProperty(
        default="leaf_",
        name="", description="Every material which begins with this prefix will be "
                             "considered as leaf material. The individual material is "
                             "chosen randomly for each leaf.")
    bpy.types.Scene.lptg_generate_seed_on_generate = BoolProperty(
        name="Generate New Seed Everytime", 
        description="True to generate a new seed everytime generate tree is pressed.", default=False)
    bpy.types.Scene.lptg_generate_leaf = BoolProperty(
        name="Generate Leaf", 
        description="True to generate leaf, false otherwise.", default=True)
    bpy.types.Scene.lptg_leaf_object = StringProperty(
        name="Leaf Object",
        description="Leaf object to be used if 'Leaf Object' is choosed in the geometry field."
    )
    bpy.types.Scene.lptg_angles_1 = FloatVectorProperty(
        default=(7, 35), min=0, max=90, size=2,
        name="Angle Range 1",
        description="Angle range of the first 1/3 of branches")
    bpy.types.Scene.lptg_angles_2 = FloatVectorProperty(
        default=(7, 35), min=0, max=90, size=2,
        name="Angle Range 2",
        description="Angle range of the 1/3 - 2/3 of branches")
    bpy.types.Scene.lptg_angles_3 = FloatVectorProperty(
        default=(7, 35), min=0, max=90, size=2,
        name="Angle Range 3",
        description="Angle range of the rest of branches")
    bpy.types.Scene.lptg_init_radius = FloatProperty(
        default=1.0, min=0.0, max=10.0,
        name="Root radius",
        description="Stem radius at the root of the tree")
    bpy.types.Scene.lptg_radius_factor = FloatProperty(
        default=0.8, min=0.05, max=1.0,
        name="Radius factor",
        description="Factor by which the stem radius gets smaller after each section")
    bpy.types.Scene.lptg_start_branch_probability = FloatProperty(
        default=0.2, min=0.01, max=1.0,
        name="Start branch probability",
        description="Start of branch probability")
    bpy.types.Scene.lptg_max_branch_probability = FloatProperty(
        default=0.9, min=0.01, max=1.0,
        name="Max branch probability",
        description="Cap of branch probability")
    bpy.types.Scene.lptg_branch_probability_coeff = FloatProperty(
        default=0.8, min=0.01, max=1.0,
        name="Branch probability coefficient",
        description="Coefficient of branch probability")
    bpy.types.Scene.lptg_stem_section_length = FloatProperty(
        default=2.0, min=0.05, max=10.0,
        name="Initial stem length",
        description="Initial length of the first section of the stem")
    bpy.types.Scene.lptg_stem_length_factor = FloatProperty(
        default=0.9, min=0.05, max=1.0,
        name="Stem length factor",
        description="Factor by which the stem length gets smaller after each section")
    bpy.types.Scene.lptg_leaf_geometry = EnumProperty(
        items=[('mesh.primitive_cube_add', "Cube", "Cube mesh", 'CUBE', 0),
               ('mesh.primitive_ico_sphere_add', "Sphere", "Sphere mesh", 'MESH_ICOSPHERE', 1),
               ('mesh.custom', "Leaf Object", "Leaf object mesh", 'LEAF_OBJECT', 2)],
        default='mesh.primitive_ico_sphere_add',
        name="",
        description="The geometry mesh from which the leaves are created",)
    bpy.types.Scene.lptg_leaf_size = FloatProperty(
        default=0.5, min=0.0, max=10.0,
        name="Leaf size",
        description="Base size for the leaves")
    bpy.types.Scene.lptg_leaf_size_deviation = FloatProperty(
        default=10.0, min=0.0, max=99.0,
        name="Max leaf size deviation",
        subtype='PERCENTAGE',
        description="Allowed percentage for the random deviation of the leaf size")


def unregister():
    bpy.utils.unregister_class(VIEW3D_PT_low_poly_tree)
    bpy.utils.unregister_class(PerformGeneration)
    bpy.utils.unregister_class(NewSeed)
