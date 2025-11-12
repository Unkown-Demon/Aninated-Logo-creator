import numpy as np
from math import sin, cos, tan, pi

# --- Matrix Utility Functions (based on GLM/OpenGL conventions) ---

def perspective(fovy, aspect, near, far):
    """Creates a perspective projection matrix."""
    f = 1.0 / tan(np.radians(fovy) / 2.0)
    return np.array([
        [f / aspect, 0.0, 0.0, 0.0],
        [0.0, f, 0.0, 0.0],
        [0.0, 0.0, (far + near) / (near - far), -1.0],
        [0.0, 0.0, (2.0 * far * near) / (near - far), 0.0]
    ], dtype=np.float32).T

def lookat(eye, center, up):
    """Creates a view matrix (camera)."""
    f = (center - eye)
    f = f / np.linalg.norm(f)
    up = up / np.linalg.norm(up)
    s = np.cross(f, up)
    s = s / np.linalg.norm(s)
    u = np.cross(s, f)
    
    return np.array([
        [s[0], u[0], -f[0], -np.dot(s, eye)],
        [s[1], u[1], -f[1], -np.dot(u, eye)],
        [s[2], u[2], -f[2], np.dot(f, eye)],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float32)

def translate(v):
    """Creates a translation matrix."""
    return np.array([
        [1.0, 0.0, 0.0, v[0]],
        [0.0, 1.0, 0.0, v[1]],
        [0.0, 0.0, 1.0, v[2]],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float32).T

def rotate(angle, axis):
    """Creates a rotation matrix around an axis (angle in degrees)."""
    angle = np.radians(angle)
    c = cos(angle)
    s = sin(angle)
    t = 1.0 - c
    x, y, z = axis / np.linalg.norm(axis)
    
    return np.array([
        [t*x*x + c,   t*x*y - s*z, t*x*z + s*y, 0.0],
        [t*x*y + s*z, t*y*y + c,   t*y*z + s*x, 0.0],
        [t*x*z - s*y, t*y*z + s*x, t*z*z + c,   0.0],
        [0.0,         0.0,         0.0,         1.0]
    ], dtype=np.float32).T

def scale(v):
    """Creates a scale matrix."""
    return np.array([
        [v[0], 0.0, 0.0, 0.0],
        [0.0, v[1], 0.0, 0.0],
        [0.0, 0.0, v[2], 0.0],
        [0.0, 0.0, 0.0, 1.0]
    ], dtype=np.float32).T

# --- Geometry Generation Functions ---

def create_cube(size=1.0):
    """Generates vertices and indices for a cube with texture coordinates."""
    s = size / 2.0
    
    # Vertices (position, texture coordinate)
    # Texture coordinates are repeated for each face to allow unique texturing
    vertices = np.array([
        # Front face
        [-s, -s, s, 0.0, 0.0], [s, -s, s, 1.0, 0.0], [s, s, s, 1.0, 1.0], [-s, s, s, 0.0, 1.0],
        # Back face
        [-s, -s, -s, 1.0, 0.0], [-s, s, -s, 1.0, 1.0], [s, s, -s, 0.0, 1.0], [s, -s, -s, 0.0, 0.0],
        # Top face
        [-s, s, s, 0.0, 1.0], [s, s, s, 1.0, 1.0], [s, s, -s, 1.0, 0.0], [-s, s, -s, 0.0, 0.0],
        # Bottom face
        [-s, -s, s, 0.0, 0.0], [-s, -s, -s, 0.0, 1.0], [s, -s, -s, 1.0, 1.0], [s, -s, s, 1.0, 0.0],
        # Right face
        [s, -s, s, 0.0, 0.0], [s, -s, -s, 1.0, 0.0], [s, s, -s, 1.0, 1.0], [s, s, s, 0.0, 1.0],
        # Left face
        [-s, -s, s, 1.0, 0.0], [-s, s, s, 1.0, 1.0], [-s, s, -s, 0.0, 1.0], [-s, -s, -s, 0.0, 0.0],
    ], dtype=np.float32)
    
    # Indices for two triangles per face
    indices = np.array([
        0, 1, 2, 2, 3, 0,    # Front
        4, 5, 6, 6, 7, 4,    # Back
        8, 9, 10, 10, 11, 8, # Top
        12, 13, 14, 14, 15, 12, # Bottom
        16, 17, 18, 18, 19, 16, # Right
        20, 21, 22, 22, 23, 20, # Left
    ], dtype=np.uint32)
    
    return vertices, indices

def create_cylinder(sides=32, height=0.1, radius=1.0):
    """Generates vertices and indices for a cylinder (coin)."""
    vertices = []
    indices = []
    
    # Top and Bottom center points
    top_center_index = 0
    bottom_center_index = 1
    vertices.append([0.0, height / 2.0, 0.0, 0.5, 0.5]) # Top center (0)
    vertices.append([0.0, -height / 2.0, 0.0, 0.5, 0.5]) # Bottom center (1)
    
    # Side vertices
    for i in range(sides):
        angle = 2.0 * pi * i / sides
        x = radius * cos(angle)
        z = radius * sin(angle)
        
        # Top edge vertex (for side and top face)
        vertices.append([x, height / 2.0, z, cos(angle) * 0.5 + 0.5, sin(angle) * 0.5 + 0.5]) # Top face UV
        # Bottom edge vertex (for side and bottom face)
        vertices.append([x, -height / 2.0, z, cos(angle) * 0.5 + 0.5, sin(angle) * 0.5 + 0.5]) # Bottom face UV
        
        # Side face vertices (repeated for proper side UV mapping)
        vertices.append([x, height / 2.0, z, i / sides, 1.0]) # Side Top UV
        vertices.append([x, -height / 2.0, z, i / sides, 0.0]) # Side Bottom UV
        
    # Indices for Top and Bottom faces
    for i in range(sides):
        # The indices for the vertices are offset by 2 (for the center points)
        # and then by 4 for each side segment (4 vertices per segment)
        
        # Indices for Top and Bottom faces
        # Vertices for top/bottom face are at index 2 + i*4 and 3 + i*4
        i_top_curr = 2 + i * 4
        i_top_next = 2 + (i + 1) % sides * 4
        i_bottom_curr = 3 + i * 4
        i_bottom_next = 3 + (i + 1) % sides * 4
        
        # Top face (Triangle fan from center)
        indices.extend([top_center_index, i_top_curr, i_top_next])
        
        # Bottom face (Triangle fan from center) - Winding order reversed for correct culling
        indices.extend([bottom_center_index, i_bottom_next, i_bottom_curr])
        
        # Side faces (Two triangles per side)
        # Vertices for side face are at index 4 + i*4 and 5 + i*4
        i_side_top_curr = 4 + i * 4
        i_side_bottom_curr = 5 + i * 4
        i_side_top_next = 4 + (i + 1) % sides * 4
        i_side_bottom_next = 5 + (i + 1) % sides * 4
        
        # First triangle: Top-Current, Bottom-Current, Top-Next
        indices.extend([i_side_top_curr, i_side_bottom_curr, i_side_top_next])
        # Second triangle: Top-Next, Bottom-Current, Bottom-Next
        indices.extend([i_side_top_next, i_side_bottom_curr, i_side_bottom_next])
        
    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def create_pyramid(size=1.0, height=1.0):
    """Generates vertices and indices for a square-based pyramid."""
    s = size / 2.0
    h = height
    
    # Vertices (position, texture coordinate)
    # Base vertices
    v0 = [-s, 0.0, s, 0.0, 0.0] # Base BL
    v1 = [s, 0.0, s, 1.0, 0.0]  # Base BR
    v2 = [s, 0.0, -s, 1.0, 1.0] # Base TR
    v3 = [-s, 0.0, -s, 0.0, 1.0] # Base TL
    
    # Apex vertex
    v_apex = [0.0, h, 0.0, 0.5, 1.0]
    
    # Side face vertices (repeated for unique UV mapping)
    # Front face
    v4 = [-s, 0.0, s, 0.0, 0.0]
    v5 = [s, 0.0, s, 1.0, 0.0]
    v6 = v_apex
    # Right face
    v7 = [s, 0.0, s, 0.0, 0.0]
    v8 = [s, 0.0, -s, 1.0, 0.0]
    v9 = v_apex
    # Back face
    v10 = [s, 0.0, -s, 0.0, 0.0]
    v11 = [-s, 0.0, -s, 1.0, 0.0]
    v12 = v_apex
    # Left face
    v13 = [-s, 0.0, -s, 0.0, 0.0]
    v14 = [-s, 0.0, s, 1.0, 0.0]
    v15 = v_apex
    
    vertices = np.array([
        # Base (v0, v1, v2, v3)
        v0, v1, v2, v3,
        # Sides (v4-v15)
        v4, v5, v6, v7, v8, v9, v10, v11, v12, v13, v14, v15
    ], dtype=np.float32)
    
    # Indices
    indices = np.array([
        # Base
        0, 1, 2, 2, 3, 0,
        # Sides
        4, 5, 6, # Front
        7, 8, 9, # Right
        10, 11, 12, # Back
        13, 14, 15, # Left
    ], dtype=np.uint32)
    
    return vertices, indices

# Dictionary to easily access models
MODELS = {
    'cube': create_cube,
    'coin': create_cylinder,
    'pyramid': create_pyramid,
}

# Example usage (for testing)
if __name__ == '__main__':
    cube_v, cube_i = create_cube()
    print("Cube Vertices Shape:", cube_v.shape)
    print("Cube Indices Shape:", cube_i.shape)
    
    coin_v, coin_i = create_cylinder(sides=16, height=0.2)
    print("Coin Vertices Shape:", coin_v.shape)
    print("Coin Indices Shape:", coin_i.shape)
    
    pyramid_v, pyramid_i = create_pyramid()
    print("Pyramid Vertices Shape:", pyramid_v.shape)
    print("Pyramid Indices Shape:", pyramid_i.shape)
    
    # Test matrix
    R = rotate(45, np.array([0, 1, 0]))
    T = translate(np.array([1, 0, 0]))
    M = T @ R
    print("\nModel Matrix (T * R):\n", M)
