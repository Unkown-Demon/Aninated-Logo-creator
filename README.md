# Animated Logo Creator Telegram Bot

**Animated Logo Creator** is a Telegram bot built with Python that allows users to upload 3 to 4 images and transform them into animated 3D objects (like a spinning coin, cube, or pyramid). The 3D rendering is performed using **OpenGL** via the `moderngl` library for high-quality, off-screen animation generation.

## 🚀 Features

*   **3D Object Generation:** Create animated 3D models (Coin, Cube, Pyramid) from user-uploaded images.
*   **Texture Mapping:** Maps the uploaded images onto the faces of the 3D objects.
*   **OpenGL Rendering:** Utilizes `moderngl` for fast, headless 3D rendering.
*   **Telegram Interface:** Built with `Aiogram` for an asynchronous and responsive user experience.
*   **GIF Output:** Generates the final animation as a high-quality GIF file.

## 🛠️ Technologies Used

*   **Python 3.11+**
*   **Telegram Bot Framework:** `Aiogram`
*   **3D Graphics:** `moderngl`, `PyOpenGL`
*   **Image Processing:** `Pillow`
*   **Video/GIF Creation:** `imageio`
*   **Linear Algebra:** `NumPy`

## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Unkown-Demon/Aninated-Logo-creator.git
cd Aninated-Logo-creator
```

### 2. Install Dependencies

It is highly recommended to use a virtual environment.

```bash
# Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### 3. Configuration

Create a Telegram Bot via BotFather and get your **BOT_TOKEN**.

Open the `config.py` file and replace the placeholder with your actual token:

```python
# config.py
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE" 
OUTPUT_DIR = "assets/output"
```

### 4. Run the Bot

```bash
python bot/main.py
```

## 🤖 Bot Usage

1.  **Start:** Send the `/start` command to the bot.
2.  **Upload Images:** Send **3 or 4** images (logos) that you want to use as textures.
3.  **Select Shape:** Choose the desired 3D shape (Coin, Cube, Pyramid) from the inline keyboard.
4.  **Render:** Send the `/render` command to start the animation generation process.
5.  **Receive GIF:** The bot will process the request and send back the animated GIF.

## 📂 Project Structure

```
Aninated-Logo-creator/
├── bot/
│   └── main.py             # Main Aiogram bot logic and handlers
├── core/
│   ├── models.py           # 3D model generation (Cube, Coin, Pyramid) and matrix utilities
│   ├── renderer.py         # Offscreen OpenGL renderer using moderngl
│   ├── render_logic.py     # Animation logic and frame generation
│   ├── video_logic.py      # GIF/Video creation using imageio
│   ├── vertex_shader.glsl  # Basic Vertex Shader
│   └── fragment_shader.glsl# Basic Fragment Shader
├── assets/
│   └── output/             # Directory for temporary and final rendered files
├── config.py               # Bot token and configuration
├── requirements.txt        # Python dependencies
└── README.md               # This file
```

## 📝 Future Enhancements

*   Add more 3D shapes (e.g., Sphere, Torus).
*   Implement user-selectable design effects and shaders (e.g., color shift, glow).
*   Allow users to choose between GIF and MP4 output formats.
*   Implement a proper texture mapping strategy for multi-face objects like the Cube.

## 🤝 Contribution

Feel free to fork the repository and submit pull requests. Any contributions are welcome!

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.
