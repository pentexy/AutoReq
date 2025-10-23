from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.enums import ParseMode
from database.operations import db
from ui.buttons import ButtonManager
from userbot.client import userbot_client
from config import config
import asyncio

router = Router()

# This will be set by main.py
promotion_service = None

@router.message(Command("setup"))
async def setup_handler(message: Message):
    """Setup userbot in channels with auto-promotion"""
    user_id = message.from_user.id
    
    if not userbot_client.is_connected:
        await message.answer("Userbot is not connected.")
        return
    
    # Check if promotion service is available
    if promotion_service is None:
        await message.answer("Promotion service not available. Please restart the bot.")
        return
    
    # Get user's channels that need setup
    user_channels = list(db.chats.find({
        "added_by": user_id,
        "chat_type": "channel", 
        "userbot_setup": False
    }))
    
    if not user_channels:
        await message.answer("All your channels are already setup.")
        return
    
    setup_msg = await message.answer(f"Starting setup for {len(user_channels)} channels...")
    
    success_count = 0
    
    for channel in user_channels:
        try:
            channel_text = f"Setting up: {channel['title']}"
            await setup_msg.edit_text(f"{channel_text}")
            
            # Step 1: Userbot joins channel
            join_success = await userbot_client.setup_channel(
                int(channel['chat_id']), 
                channel.get('invite_link')
            )
            
            if join_success:
                # Step 2: Bot promotes userbot
                userbot_info = await userbot_client.get_userbot_info()
                if userbot_info:
                    promote_success = await promotion_service.promote_userbot(
                        int(channel['chat_id']), 
                        userbot_info['id']
                    )
                    
                    if promote_success:
                        db.chats.update_one(
                            {"chat_id": channel['chat_id']},
                            {"$set": {"userbot_setup": True}}
                        )
                        success_count += 1
                        channel_text = f"Success: {channel['title']}"
                    else:
                        channel_text = f"Promote failed: {channel['title']}"
                else:
                    channel_text = f"No userbot info: {channel['title']}"
            else:
                channel_text = f"Join failed: {channel['title']}"
            
            await setup_msg.edit_text(f"{channel_text}")
            await asyncio.sleep(2)
            
        except Exception as e:
            print(f"Setup failed for {channel['title']}: {e}")
            channel_text = f"Error: {channel['title']} - {str(e)}"
            await setup_msg.edit_text(f"{channel_text}")
    
    result_text = f"Setup complete: {success_count}/{len(user_channels)} channels"
    if success_count < len(user_channels):
        result_text += "\n\nFor failed channels, ensure:\n- Bot is admin with promote rights\n- Userbot is channel member"
    
    await setup_msg.edit_text(result_text)
