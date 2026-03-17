bl_info = {
    "name": "Copy UV Layout to Clipboard",
    "author": "schouffy",
    "version": (0, 1, 0),
    "blender": (5, 0, 0),
    "location": "UV Editor > UV menu",
    "description": "Copy UV layout directly to clipboard. Linux requires xclip (sudo apt install xclip).",
    "category": "UV",
}

import bpy
import tempfile
import os

class UV_OT_copy_to_clipboard(bpy.types.Operator):
    bl_idname = "uv.copy_uv_to_clipboard"
    bl_label = "Copy UV Layout to Clipboard"
    bl_description = "Export UV layout and copy it to clipboard"
    bl_options = {'REGISTER', 'UNDO'}

    size: bpy.props.IntProperty(
        name="Size",
        default=1024,
        min=64,
        max=8192
    )

    def execute(self, context):
        obj = context.object

        if not obj or obj.type != 'MESH':
            self.report({'ERROR'}, "No active mesh object")
            return {'CANCELLED'}

        # Create temp file
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, "uv_layout_clipboard.png")

        # Export UV layout
        bpy.ops.uv.export_layout(
            filepath=filepath,
            size=(self.size, self.size),
            opacity=0.3,
            check_existing=False
        )

        # Copy to clipboard (platform dependent)
        try:
            import platform
            system = platform.system()

            if system == "Windows":
                import subprocess
                subprocess.run(
                    ['powershell', '-command',
                     f'Add-Type -AssemblyName System.Windows.Forms; '
                     f'$img = [System.Drawing.Image]::FromFile("{filepath}"); '
                     f'[System.Windows.Forms.Clipboard]::SetImage($img)']
                )

            elif system == "Darwin":  # macOS
                subprocess.run(["osascript", "-e",
                    f'set the clipboard to (read (POSIX file "{filepath}") as PNG picture)'])

            elif system == "Linux":
                subprocess.run(["xclip", "-selection", "clipboard", "-t", "image/png", "-i", filepath])

            else:
                self.report({'WARNING'}, "Unsupported OS for clipboard copy")
                return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"Clipboard copy failed: {e}")
            return {'CANCELLED'}

        self.report({'INFO'}, "UV layout copied to clipboard")
        return {'FINISHED'}


def menu_func(self, context):
    self.layout.separator()
    self.layout.operator(UV_OT_copy_to_clipboard.bl_idname)


def register():
    bpy.utils.register_class(UV_OT_copy_to_clipboard)
    bpy.types.IMAGE_MT_uvs.append(menu_func)


def unregister():
    bpy.types.IMAGE_MT_uvs.remove(menu_func)
    bpy.utils.unregister_class(UV_OT_copy_to_clipboard)


if __name__ == "__main__":
    register()