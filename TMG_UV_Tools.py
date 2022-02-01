import bpy, sys, os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty, IntProperty, FloatProperty, FloatVectorProperty, PointerProperty
from bpy.types import Operator, Header


# Update Blender UI Panels
def tag_redraw(context, space_type="PROPERTIES", region_type="WINDOW"):
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.spaces[0].type == space_type:
                for region in area.regions:
                    if region.type == region_type:
                        region.tag_redraw()


class TMG_UV_Properties(bpy.types.PropertyGroup):
    pass
    

class OBJECT_PT_SelectOB(Operator):
    """Select object from scene and set it to active"""

    bl_idname = "tmg_uv.select_ob"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name="Object Name")

    def execute(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars
        bpy.context.view_layer.objects.active = bpy.data.objects[self.name]
        bpy.data.objects[self.name].select_set(True) 
        tag_redraw(context)
        return {'FINISHED'}


class OBJECT_PT_DeleteOB(Operator):
    """Delete object from scene"""

    bl_idname = "tmg_uv.delete_ob"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name="Object Name")

    def execute(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars

        if bpy.data.objects[self.name]:
            bpy.data.objects.remove(bpy.data.objects[self.name], do_unlink=True)
            tag_redraw(context)

        return {'FINISHED'}


class OBJECT_PT_SetActiveUV(Operator):
    """Set active uv layer from objects"""

    bl_idname = "tmg_uv.set_active_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name="UV Name")

    def execute(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars
        
        for ob in bpy.context.selected_objects:
            if ob.type == "MESH":
                for uv in ob.data.uv_layers:
                    if uv.name == self.name:
                        ob.data.uv_layers[self.name].active_render = True 
        tag_redraw(context)
        return {'FINISHED'}


class OBJECT_PT_SelectUV(Operator):
    """Select uv layer from objects and set it to active"""

    bl_idname = "tmg_uv.select_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name="UV Name")

    def execute(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars
        
        for ob in bpy.context.selected_objects:
            if ob.type == "MESH":
                for uv in ob.data.uv_layers:
                    if uv.name == self.name:
                        ob.data.uv_layers[self.name].active = True 
        tag_redraw(context)
        return {'FINISHED'}


class OBJECT_PT_DeleteUV(Operator):
    """Delete uv from objects"""

    bl_idname = "tmg_uv.delete_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name="UV Name")

    def execute(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars

        for ob in bpy.context.selected_objects:
            if ob.type == "MESH":
                for uv in ob.data.uv_layers:
                    if uv.name == self.name:
                        ob.data.uv_layers.remove(ob.data.uv_layers[self.name])
            tag_redraw(context)
        return {'FINISHED'}


class OBJECT_PT_DeleteAllUV(Operator):
    """Delete all uvs from objects"""

    bl_idname = "tmg_uv.delete_all_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars

        objs = []
        uvs = []

        for ob in bpy.context.selected_objects:
            if ob.type == "MESH":
                objs.append(ob)
                while len(ob.data.uv_layers) > 0:
                    for uv in ob.data.uv_layers:
                        if ob.data.uv_layers.get(uv.name):
                            ob.data.uv_layers.remove(layer=uv)
            tag_redraw(context)
        return {'FINISHED'}


class OBJECT_PT_AddUV(Operator):
    """Add uv to objects"""

    bl_idname = "tmg_uv.add_uv"
    bl_label = ""
    bl_options = {'REGISTER', 'UNDO'}
    name : bpy.props.StringProperty(name="UVMap")

    def execute(self, context):
        scene = context.scene
        tmg_uv_vars = scene.tmg_uv_vars

        for ob in bpy.context.selected_objects:
            if ob.type == "MESH" and len(ob.data.uv_layers) < 8:
                ob.data.uv_layers.new(name=self.name)
            tag_redraw(context)
        return {'FINISHED'}


class OBJECT_PT_TMG_Object_Panel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_tmg_object_panel'
    bl_category = 'TMG UV'
    bl_label = 'Object'
    bl_context = "objectmode"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        scene = context.scene
        props = scene.eevee
        tmg_uv_vars = scene.tmg_uv_vars
        layout = self.layout
             
        objs = []

        # for ob in bpy.context.scene.objects:
        for ob in bpy.context.selected_objects:
            if ob.type == "MESH":
                objs.append(ob)


        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)

        if len(objs) < 1: 
            col.label(text="No objects selected")

        for ob in objs:
            row = col.row(align=True)

            if bpy.context.selected_objects == ob:
                prop = row.operator("tmg_uv.select_ob", text=ob.name, emboss=False)
            else:
                prop = row.operator("tmg_uv.select_ob", text=ob.name, emboss=True)
            prop.name = ob.name

            prop = row.operator("tmg_uv.delete_ob", text='', icon="TRASH")
            prop.name = ob.name       


class OBJECT_PT_TMG_UV_Panel(bpy.types.Panel):
    bl_idname = 'OBJECT_PT_tmg_uv_panel'
    bl_category = 'TMG UV'
    bl_label = 'UV'
    bl_context = "objectmode"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'

    def draw(self, context):
        scene = context.scene
        props = scene.eevee
        tmg_uv_vars = scene.tmg_uv_vars
        layout = self.layout
             
        objs = []
        uvs = []

        for ob in bpy.context.selected_objects:
            if ob.type == "MESH":
                objs.append(ob)
                for uv in ob.data.uv_layers:
                    if uv.name not in uvs:
                        uvs.append(uv.name)

        row = layout.row(align=True)  
        prop = row.operator("tmg_uv.add_uv", text='', icon="PLUS", emboss=True)
        prop = row.operator("tmg_uv.delete_all_uv", text='', icon="X", emboss=True)

        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)  

        ob = bpy.context.active_object

        if len(uvs) < 1 or not ob or ob.type != 'MESH': 
            col.label(text="No UVs on active object")
        
        if bpy.context.active_object and bpy.context.active_object.type == 'MESH':
            for uv in uvs:
                if ob.data.uv_layers.get(uv):
                    row = col.row(align=True)

                    if ob.data.uv_layers[uv].active:
                        prop = row.operator("tmg_uv.select_uv", text=uv, emboss=False)
                    else:
                        prop = row.operator("tmg_uv.select_uv", text=uv, emboss=True)
                    prop.name = uv

                    if ob.data.uv_layers[uv].active_render:
                        prop = row.operator("tmg_uv.set_active_uv", text='', icon="RESTRICT_RENDER_OFF")
                    else:
                        prop = row.operator("tmg_uv.set_active_uv", text='', icon="RESTRICT_RENDER_ON")
                    prop.name = uv     

                    prop = row.operator("tmg_uv.delete_uv", text='', icon="TRASH")
                    prop.name = uv  

