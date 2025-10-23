from aiogram import Router, F
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER
from aiogram.enums import ParseMode
from database.operations import db
from userbot.client import userbot_client
from utils.logger import Logger
from config import config
import asyncio

router = Router()

@router.my_chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def bot_added_to_chat(event: ChatMemberUpdated):
    try:
        chat = event.chat
        user = event.from_user
        
        print(f"Bot added to {chat.title} (ID: {chat.id}) by {user.id}")
        
        # Determine chat type
        if chat.type in ["group", "supergroup"]:
            chat_type = "group"
        elif chat.type == "channel":
            chat_type = "channel"
        else:
            return
        
        # Create invite link for the chat
        invite_link = None
        try:
            invite = await event.bot.create_chat_invite_link(
                chat.id, 
                name="AutoReq UserBot Join",
                creates_join_request=False,
                expire_date=None,
                member_limit=1
            )
            invite_link = invite.invite_link
            print(f"Created invite link: {invite_link}")
        except Exception as e:
            print(f"Could not create invite link: {e}")
        
        # Save to database
        chat_data = {
            "chat_id": str(chat.id),
            "title": chat.title,
            "chat_type": chat_type,
            "added_by": user.id,
            "invite_link": invite_link,
            "is_active": True,
            "userbot_setup": False
        }
        
        result = db.add_chat(chat_data)
        
        if result:
            print(f"Chat {chat.title} saved to database")
            
            # If it's a channel and userbot is connected, setup userbot
            if chat_type == "channel" and userbot_client.is_connected and invite_link:
                print(f"Setting up userbot for channel {chat.id}")
                
                # Step 1: Userbot joins channel
                join_success = await userbot_client.setup_channel(chat.id, invite_link)
                
                if join_success:
                    # Step 2: Bot promotes userbot to admin
                    userbot_info = await userbot_client.get_userbot_info()
                    if userbot_info:
                        promote_success = await promotion_service.promote_userbot(
                            chat.id, 
                            userbot_info['id']
                        )
                        
                        if promote_success:
                            # Update database with setup status
                            db.chats.update_one(
                                {"chat_id": str(chat.id)},
                                {"$set": {"userbot_setup": True}}
                            )
                            print(f"Userbot setup completed for {chat.title}")
                        else:
                            print(f"Failed to promote userbot in {chat.title}")
                    else:
                        print(f"Could not get userbot info for promotion")
                else:
                    print(f"Userbot failed to join {chat.title}")
            
            # Send DM to user who added bot
            try:
                dm_text = f"""
Bot Added Successfully

Chat: {chat.title}
Type: {chat_type}
ID: {chat.id}
"""
                if chat_type == "channel":
                    if userbot_client.is_connected:
                        setup_status = "Complete" if join_success else "Incomplete"
                        dm_text += f"\nUserbot Status: {setup_status}"
                    else:
                        dm_text += f"\nUserbot Status: Not Connected"
                
                dm_text += f"\n\nUse /manage to control your chats."
                
                await event.bot.send_message(
                    user.id,
                    dm_text
                )
                print(f"DM sent to {user.id}")
            except Exception as e:
                print(f"Could not send DM to {user.id}: {e}")
            
            # Log to owner
            await Logger.log_to_owner(
                f"Bot added to {chat.title} ({chat_type}) by {user.id}"
            )
        else:
            print(f"Failed to save chat {chat.title} to database")
            
    except Exception as e:
        print(f"Error in bot_added_to_chat: {e}")
        await Logger.log_error(f"Bot added to chat error: {e}")
# Handler for join requests (for channels)
@router.chat_join_request()
async def chat_join_request_handler(update: ChatMemberUpdated):
    try:
        chat = update.chat
        user = update.from_user
        
        print(f"📨 Join request from {user.id} in {chat.title} (ID: {chat.id})")
        
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
        db.update_chat_stats(str(chat.id), {
            "total_requests": stats["total_requests"] + 1,
            "pending_requests": stats["pending_requests"] + 1
        })
        
        # Auto-accept if chat is active and userbot is setup
        chat_data = db.get_chat(str(chat.id))
        if (chat_data and chat_data.get('is_active', True) and 
            chat_data.get('userbot_setup', False) and
            userbot_client.is_connected):
            
            print(f"🔄 Auto-accepting join request for {user.id} in {chat.id}")
            
            # Add small delay to ensure everything is ready
            await asyncio.sleep(1)
            
            success = await userbot_client.accept_join_request(chat.id, user.id)
            
            if success:
                db.update_request_status(str(chat.id), user.id, "accepted")
                # Update stats
                stats = db.get_chat_stats(str(chat.id))
                db.update_chat_stats(str(chat.id), {
                    "pending_requests": stats["pending_requests"] - 1,
                    "accepted_requests": stats["accepted_requests"] + 1
                })
                await Logger.log_request_accepted(chat.title, user.username or user.first_name)
                print(f"✅ Request accepted for {user.id} in {chat.id}")
            else:
                print(f"❌ Failed to accept request for {user.id} in {chat.id}")
        else:
            reason = "inactive chat" if not chat_data or not chat_data.get('is_active', True) else "userbot not setup" if not chat_data.get('userbot_setup', False) else "userbot not connected"
            print(f"⏸️  Auto-accept disabled for {chat.title} - {reason}")
        
    except Exception as e:
        print(f"❌ Join request error in {chat.id}: {e}")
        await Logger.log_error(f"Join request error: {e}")

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
        db.update_chat_stats(str(chat.id), {
            "total_requests": stats["total_requests"] + 1,
            "pending_requests": stats["pending_requests"] + 1
        })
        
        # Auto-accept if chat is active and userbot is setup
        chat_data = db.get_chat(str(chat.id))
        if (chat_data and chat_data.get('is_active', True) and 
            chat_data.get('userbot_setup', False) and
            userbot_client.is_connected):
            
            print(f"🔄 Auto-accepting join request for {user.id}")
            success = await userbot_client.accept_join_request(chat.id, user.id)
            
            if success:
                db.update_request_status(str(chat.id), user.id, "accepted")
                # Update stats
                stats = db.get_chat_stats(str(chat.id))
                db.update_chat_stats(str(chat.id), {
                    "pending_requests": stats["pending_requests"] - 1,
                    "accepted_requests": stats["accepted_requests"] + 1
                })
                await Logger.log_request_accepted(chat.title, user.username or user.first_name)
                print(f"✅ Request accepted for {user.id}")
            else:
                print(f"❌ Failed to accept request for {user.id}")
        else:
            print(f"⏸️  Auto-accept disabled for {chat.title} - userbot not setup")
        
    except Exception as e:
        print(f"❌ Join request error: {e}")
        await Logger.log_error(f"Join request error: {e}")

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
