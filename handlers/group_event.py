from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.enums import ParseMode
from database.operations import db
from utils.logger import Logger
from config import config

router = Router()

# Handler for when bot is added to group/channel
@router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def bot_added_to_chat(event: ChatMemberUpdated):
    try:
        chat = event.chat
        user = event.from_user
        
        print(f"🤖 Bot added to {chat.title} by {user.id}")
        
        # Determine chat type
        if chat.type in ["group", "supergroup"]:
            chat_type = "group"
        elif chat.type == "channel":
            chat_type = "channel"
        else:
            return
        
        # Save to database
        chat_data = {
            "chat_id": str(chat.id),
            "title": chat.title,
            "chat_type": chat_type,
            "added_by": user.id,
            "is_active": True
        }
        
        result = db.add_chat(chat_data)
        
        if result:
            print(f"✅ Chat {chat.title} saved to database")
            
            # Send DM to user who added bot
            try:
                dm_text = f"""
<b>✅ Bot Added Successfully!</b>

<b>Chat:</b> {chat.title}
<b>Type:</b> {chat_type}
<b>ID:</b> {chat.id}

I've been successfully added to your {chat_type} and saved in my database.

Use /db command to manage this {chat_type}.
"""
                await event.bot.send_message(
                    user.id,
                    dm_text,
                    parse_mode=ParseMode.HTML
                )
                print(f"✅ DM sent to {user.id}")
            except Exception as e:
                print(f"❌ Could not send DM to {user.id}: {e}")
            
            # Log to owner
            await Logger.log_to_owner(
                f"Bot added to {chat.title} ({chat_type}) by {user.id}"
            )
        else:
            print(f"❌ Failed to save chat {chat.title} to database")
            
    except Exception as e:
        print(f"❌ Error in bot_added_to_chat: {e}")
        await Logger.log_error(f"Bot added to chat error: {e}")

# Handler for when bot is removed from group/channel
@router.my_chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def bot_removed_from_chat(event: ChatMemberUpdated):
    try:
        chat = event.chat
        print(f"❌ Bot removed from {chat.title}")
        
        # Update database to mark as inactive
        db.chats.update_one(
            {"chat_id": str(chat.id)},
            {"$set": {"is_active": False}}
        )
        
        await Logger.log_to_owner(f"Bot removed from {chat.title}")
        
    except Exception as e:
        print(f"❌ Error in bot_removed_from_chat: {e}")

# Handler for join requests (for channels)
@router.chat_join_request()
async def chat_join_request_handler(update: ChatMemberUpdated):
    try:
        chat = update.chat
        user = update.from_user
        
        print(f"📨 Join request from {user.id} in {chat.title}")
        
        # Save request to database
        request_data = {
            "chat_id": str(chat.id),
            "user_id": user.id,
            "username": user.username or "",
            "first_name": user.first_name or "",
            "status": "pending"
        }
        
        db.add_request(request_data)
        
        # Update chat stats
        stats = db.get_chat_stats(str(chat.id))
        db.update_chat_stats(str(chat.id), stats)
        
        # Auto-accept if chat is active
        chat_data = db.get_chat(str(chat.id))
        if chat_data and chat_data.get('is_active', True):
            from userbot.client import userbot_client
            success = await userbot_client.accept_join_request(chat.id, user.id)
            if success:
                db.update_request_status(str(chat.id), user.id, "accepted")
                await Logger.log_request_accepted(chat.title, user.username or user.first_name)
                print(f"✅ Request accepted for {user.id}")
        
    except Exception as e:
        print(f"❌ Join request error: {e}")
        await Logger.log_error(f"Join request error: {e}")
