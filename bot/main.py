import asyncio
import logging
import os
import aiohttp
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import BOT_TOKEN, OUTPUT_DIR
from core.render_logic import render_animation
from core.video_logic import create_gif

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- State Machine ---
class LogoCreation(StatesGroup):
    waiting_for_images = State()
    waiting_for_shape = State()
    waiting_for_config = State()
    
# --- Utility Functions ---
def get_shape_keyboard():
    buttons = [
        [InlineKeyboardButton(text="Tanga (Coin)", callback_data="shape_coin")],
        [InlineKeyboardButton(text="Kub (Cube)", callback_data="shape_cube")],
        [InlineKeyboardButton(text="Piramida (Pyramid)", callback_data="shape_pyramid")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

async def download_image(file_id: str, destination_path: str):
    """Downloads a file from Telegram."""
    file = await bot.get_file(file_id)
    file_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(file_url) as response:
            if response.status == 200:
                with open(destination_path, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
                return True
            return False

# --- Handlers ---

@dp.message(CommandStart())
async def command_start_handler(message: types.Message, state: FSMContext) -> None:
    """Handle /start command."""
    await state.clear()
    await message.answer(
        "Assalomu alaykum! Animated Logo Creator botiga xush kelibsiz.\n\n"
        "Iltimos, 3D animatsiya uchun ishlatiladigan 3-4 ta rasm (logo) yuboring."
    )
    await state.set_state(LogoCreation.waiting_for_images)

@dp.message(LogoCreation.waiting_for_images, F.photo)
async def handle_image_upload(message: types.Message, state: FSMContext) -> None:
    """Handle image uploads and store file IDs."""
    data = await state.get_data()
    images = data.get("images", [])
    
    # Store only the file_id and file_unique_id
    new_image = {
        "file_id": message.photo[-1].file_id,
        "file_unique_id": message.photo[-1].file_unique_id
    }
    
    # Simple check to avoid adding the same image twice based on unique ID
    if not any(img['file_unique_id'] == new_image['file_unique_id'] for img in images):
        images.append(new_image)
        await state.update_data(images=images)
    
    count = len(images)
    
    if count < 3:
        await message.answer(f"Rasm qabul qilindi. Yana {3 - count} ta rasm yuboring (jami 3-4 ta bo'lishi kerak).")
    elif count == 4:
        await message.answer(
            f"4 ta rasm qabul qilindi. Rasm yuklash tugadi.\n\n"
            "Endi 3D shaklni tanlang:",
            reply_markup=get_shape_keyboard()
        )
        await state.set_state(LogoCreation.waiting_for_shape)
    elif count == 3:
        await message.answer(
            f"3 ta rasm qabul qilindi. Yana bir rasm yuborishingiz yoki shaklni tanlashingiz mumkin.",
            reply_markup=get_shape_keyboard()
        )
        # Stay in the same state to allow one more image or shape selection

@dp.callback_query(LogoCreation.waiting_for_images, F.data.startswith("shape_"))
@dp.callback_query(LogoCreation.waiting_for_shape, F.data.startswith("shape_"))
async def handle_shape_selection(callback: types.CallbackQuery, state: FSMContext) -> None:
    """Handle shape selection."""
    shape = callback.data.split("_")[1]
    data = await state.get_data()
    images = data.get("images", [])
    
    if len(images) < 3:
        await callback.message.edit_text(
            "Iltimos, avval kamida 3 ta rasm yuboring."
        )
        await callback.answer()
        return
        
    await state.update_data(shape=shape)
    
    # Proceed to configuration (Phase 6)
    await callback.message.edit_text(
        f"Shakl tanlandi: **{shape.capitalize()}**.\n\n"
        "Endi animatsiya sozlamalarini tanlang (Hozircha faqat /render buyrug'i mavjud)."
    )
    await callback.answer()
    await state.set_state(LogoCreation.waiting_for_config)
    
@dp.message(LogoCreation.waiting_for_images)
async def handle_invalid_message_in_images_state(message: types.Message) -> None:
    """Handle non-photo messages in the image upload state."""
    await message.answer("Iltimos, faqat rasm (photo) yuboring.")

@dp.message(LogoCreation.waiting_for_config, F.text == "/render")
async def handle_render_command(message: types.Message, state: FSMContext) -> None:
    """Handle the render command and start the animation process."""
    data = await state.get_data()
    shape = data.get("shape")
    images_data = data.get("images")
    
    if not shape or not images_data:
        await message.answer("Iltimos, avval rasmlarni yuklang va shaklni tanlang.")
        return
        
    await message.answer("Renderlash jarayoni boshlandi. Bu biroz vaqt olishi mumkin...")
    
    # 1. Download images
    user_id = message.from_user.id
    temp_dir = os.path.join(OUTPUT_DIR, str(user_id))
    os.makedirs(temp_dir, exist_ok=True)
    
    image_paths = []
    for i, img_data in enumerate(images_data):
        file_id = img_data['file_id']
        file_path = os.path.join(temp_dir, f"input_{i}.png")
        if await download_image(file_id, file_path):
            image_paths.append(file_path)
        else:
            await message.answer(f"Rasm yuklashda xatolik yuz berdi: {file_id}")
            return
            
    # 2. Render animation frames
    try:
        frames = await asyncio.to_thread(render_animation, image_paths, shape, temp_dir)
    except Exception as e:
        logging.error(f"Rendering error: {e}")
        await message.answer(f"Renderlashda kutilmagan xatolik yuz berdi: {e}")
        return
        
    # 3. Create GIF (or video, currently only GIF is planned for Phase 7)
    output_filename = f"{shape}_{user_id}_{int(asyncio.get_event_loop().time())}.gif"
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    try:
        await asyncio.to_thread(create_gif, frames, output_path)
    except Exception as e:
        logging.error(f"GIF creation error: {e}")
        await message.answer(f"GIF yaratishda xatolik yuz berdi: {e}")
        return
        
    # 4. Send result
    await message.answer_document(
        types.FSInputFile(output_path),
        caption=f"Sizning **{shape.capitalize()}** shaklidagi animatsiyangiz tayyor!"
    )
    
    # 5. Cleanup (optional, but good practice)
    # Clean up temporary files and directory
    for path in image_paths:
        os.remove(path)
    os.rmdir(temp_dir)
    os.remove(output_path)
    
    # Reset state for a new creation
    await state.clear()
    await message.answer("Yangi animatsiya yaratish uchun /start buyrug'ini yuboring.")

@dp.message(LogoCreation.waiting_for_config)
async def handle_config_message(message: types.Message) -> None:
    """Handle non-/render messages in the config state."""
    await message.answer("Iltimos, animatsiyani boshlash uchun /render buyrug'ini yuboring.")

# --- Main function to run the bot ---
async def main() -> None:
    # Create output directory if it doesn't exist
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Delete webhook to ensure clean polling start
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Start the bot
    await dp.start_polling(bot)

if __name__ == "__main__":
    # Initialize bot and dispatcher here for the main execution block
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Check if the token is set
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logging.error("!!! BOT_TOKEN is not set in config.py. Please replace 'YOUR_BOT_TOKEN_HERE' with your actual Telegram bot token. !!!")
    else:
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            logging.info("Bot stopped by user.")
