import moderngl
import numpy as np
from PIL import Image
# Import matrix utilities from models.py
from core.models import perspective, lookat

class OffscreenRenderer:
    def __init__(self, width=512, height=512):
        self.width = width
        self.height = height
        
        # Create a headless context
        self.ctx = moderngl.create_context(standalone=True, require=330)
        
        # Create a framebuffer object (FBO) for off-screen rendering
        self.fbo = self.ctx.framebuffer(
            color_attachments=[self.ctx.texture((width, height), 4)]
        )
        
        self.ctx.enable(moderngl.DEPTH_TEST)
        self.ctx.enable(moderngl.CULL_FACE)
        
        # Load shaders
        with open('core/vertex_shader.glsl', 'r') as f:
            vertex_shader = f.read()
        with open('core/fragment_shader.glsl', 'r') as f:
            fragment_shader = f.read()
            
        self.program = self.ctx.program(
            vertex_shader=vertex_shader,
            fragment_shader=fragment_shader,
        )
        
        # Uniforms
        self.program['model'].write(np.identity(4, dtype='f4'))
        self.program['view'].write(np.identity(4, dtype='f4'))
        self.program['projection'].write(np.identity(4, dtype='f4'))
        
        # Placeholder for VBO and VAO
        self.vbo = None
        self.vao = None
        
    def load_texture(self, image_path):
        img = Image.open(image_path).convert('RGBA')
        texture = self.ctx.texture(img.size, 4, img.tobytes())
        return texture

    def load_geometry(self, vertices, indices):
        # Vertices: (x, y, z, u, v)
        self.vbo = self.ctx.buffer(vertices.astype('f4').tobytes())
        
        # VAO (Vertex Array Object)
        self.vao = self.ctx.vertex_array(
            self.program,
            [
                # in_position: 3 floats, offset 0
                # in_texcoord: 2 floats, offset 3 * 4 bytes
                (self.vbo, '3f 2f', 'in_position', 'in_texcoord')
            ],
            index_buffer=self.ctx.buffer(indices.astype('i4').tobytes())
        )

    def render_frame(self, model_matrix, texture):
        self.fbo.use()
        self.ctx.clear(0.0, 0.0, 0.0, 0.0) # Clear with transparent background
        
        # Update uniforms
        self.program['model'].write(model_matrix.astype('f4'))
        
        # Bind texture
        texture.use(0)
        self.program['u_texture'].value = 0
        
        # Render
        self.vao.render(moderngl.TRIANGLES)
        
        # Read pixels
        self.ctx.finish() # Ensure all rendering commands are executed
        image_data = self.fbo.read(components=4, dtype='f1')
        
        # Convert to numpy array and then to PIL Image
        image_array = np.frombuffer(image_data, dtype=np.float32).reshape(self.height, self.width, 4)
        image_array = (image_array * 255).astype(np.uint8)
        
        return Image.fromarray(image_array, 'RGBA')

    def set_camera(self, view_matrix, projection_matrix):
        self.program['view'].write(view_matrix.astype('f4'))
        self.program['projection'].write(projection_matrix.astype('f4'))

    def release(self):
        if self.vbo:
            self.vbo.release()
        if self.vao:
            self.vao.release()
        self.fbo.release()
        self.ctx.release()

if __name__ == '__main__':
    # This part is for testing the renderer setup
    print("Renderer setup complete. Need to implement geometry and matrix utilities.")
