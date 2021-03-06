import bpy, sys, os

from . TMG_UV_Tools import *

from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, FloatVectorProperty, PointerProperty
from bpy.types import Operator, Header


# GNU GENERAL PUBLIC LICENSE
# Version 3, 29 June 2007

# Extra online resources used in this script
# https://blender.stackexchange.com/questions/155515/how-do-a-create-a-foldout-ui-panel

# Thank you all that download, suggest, and request features
# As well as the whole Blender community. You're all epic :)


bl_info = {
    "name": "TMG_UV_Tools",
    "author": "Johnathan Mueller",
    "descrtion": "A panel to manage uv layers",
    "blender": (2, 80, 0),
    "version": (0, 1, 1),
    "location": "View3D (ObjectMode) > Sidebar > TMG > UV Tab",
    "warning": "",
    "category": "Object"
}

classes = (
    ## Properties
    TMG_UV_Properties,

    ## UV Operators
    OBJECT_PT_TMG_UV_ActiveRenderUV,
    OBJECT_PT_TMG_UV_AddUV,
    OBJECT_PT_TMG_UV_DeleteAllUV,
    OBJECT_PT_TMG_UV_DeleteOB,
    OBJECT_PT_TMG_UV_DeleteUV,
    OBJECT_PT_TMG_UV_RenameUV,
    OBJECT_PT_TMG_UV_SelectOB,
    OBJECT_PT_TMG_UV_SelectUV,
    EDIT_PT_TMG_UV_Unwrap,
    
    ## UV Object Panel
    OBJECT_PT_TMG_UV_Object_Panel,
    OBJECT_PT_TMG_UV_Object_Panel_List,
    # OBJECT_PT_TMG_UV_Panel, 
    OBJECT_PT_TMG_UV_Panel_List,

    ## UV Edit Panel
    EDIT_PT_TMG_UV_Panel,
    EDIT_PT_TMG_UV_Unwrap_Settings_Panel,
    EDIT_PT_TMG_UV_Panel_List,
)

def register():
    for rsclass in classes:
        bpy.utils.register_class(rsclass)
        bpy.types.Scene.tmg_uv_vars = bpy.props.PointerProperty(type=TMG_UV_Properties)

def unregister():
    for rsclass in classes:
        bpy.utils.unregister_class(rsclass)

if __name__ == "__main__":
    register()

