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

        bpy.context.view_layer.objects.active = bpy.data.objects[self.name]
        bpy.data.objects[self.name].select_set(True) 

        if bpy.context.view_layer.objects.active == bpy.data.objects[self.name]:
            bpy.context.view_layer.objects.active = None
            tag_redraw(context)

        if bpy.data.objects[self.name]:
            bpy.data.objects.remove(bpy.data.objects[self.name], do_unlink=True)

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
            if ob.type == "MESH":
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
        layout = self.layout
        

class OBJECT_PT_TMG_Object_Panel_List(bpy.types.Panel):
    bl_idname = "OBJECT_PT_tmg_object_panel_list"
    bl_label = ""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "OBJECT_PT_tmg_object_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout

        objs = []
        for ob in bpy.context.scene.objects:
            if ob.type == "MESH":
                objs.append(ob)

        layout.label(text="Objects : %s" %len(objs))
        

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
            col.label(text="No Objects in Scene")

        for ob in objs:
            row = col.row(align=True)

            # if bpy.context.space_data.objects == ob:
            if bpy.context.selected_objects == ob:
                prop = row.operator("tmg_uv.select_ob", text=ob.name, emboss=False) #  icon="RESTRICT_SELECT_OFF",
            else:
                prop = row.operator("tmg_uv.select_ob", text=ob.name, emboss=True) #  icon="RESTRICT_SELECT_ON",
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
        layout = self.layout

            
class OBJECT_PT_TMG_UV_Panel_List(bpy.types.Panel):
    bl_idname = "OBJECT_PT_tmg_uv_panel_list"
    bl_label = ""
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = "OBJECT_PT_tmg_uv_panel"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout

        objs = []
        uvs = []

        for ob in bpy.context.scene.objects:
            if ob.type == "MESH":
                objs.append(ob)
                for uv in ob.data.uv_layers:
                    if uv.name not in uvs:
                        uvs.append(uv.name)

        layout.label(text="UVs : %s" %len(uvs))
        prop = layout.operator("tmg_uv.add_uv", text='', icon="PLUS", emboss=True)
        prop = layout.operator("tmg_uv.delete_all_uv", text='', icon="X", emboss=True)
        

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


        box = layout.box()
        col = box.column(align=False)
        row = col.row(align=True)  

        if len(uvs) < 1: 
            col.label(text="No UVs on Objects")
        
        for uv in uvs:
            row = col.row(align=True)

            if bpy.context.selected_objects == uv:
                prop = row.operator("tmg_uv.select_uv", text=uv, emboss=False) #  icon="RESTRICT_SELECT_OFF",
            else:
                prop = row.operator("tmg_uv.select_uv", text=uv, emboss=True) #  icon="RESTRICT_SELECT_ON",
            prop.name = uv

            prop = row.operator("tmg_uv.delete_uv", text='', icon="TRASH")
            prop.name = uv        

