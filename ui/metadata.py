from PyQt6.QtWidgets import QTextEdit

class MetadataPanel(QTextEdit):
    def set_context(self, ctx):
        self.setReadOnly(True)
        text = ""
        text += f"Camera: {ctx.raw.camera_make} {ctx.raw.camera_model}\n"
        text += f"ISO: {ctx.raw.iso_speed}\n"
        text += f"Black levels: {ctx.black}\n"
        text += f"WB multipliers: {ctx.wb}\n"
        text += f"Color matrix:\n{ctx.rgb_xyz}\n"
        self.setText(text)
