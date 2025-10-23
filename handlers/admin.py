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

@router.message(Command("manage"))
async def manage_handler(message: Message):
    """Available to all users to manage their own chats"""
    user_id = message.from_user.id
    
    # Get chats added by this user
    user_chats = list(db.chats.find({"added_by": user_id}))
    
    if not user_chats:
        manage_text = """
<b>📊 Chat Management</b>

You haven't added me to any groups/channels yet.

Add me to your group/channel and make me admin with:
• Manage Chat permission  
• Invite Users via link permission

Then use /manage to control your chats.
"""
        await message.answer(
            manage_text,
            reply_markup=ButtonManager.start_button(),
            parse_mode=ParseMode.HTML
        )
        return
    
    # Show user's chats
    total_chats = len(user_chats)
    groups = [c for c in user_chats if c['chat_type'] == 'group']
    channels = [c for c in user_chats if c['chat_type'] == 'channel']
    
    manage_text = f"""
<b>📊 Your Chat Management</b>

<b>Your Groups:</b> {len(groups)}
<b>Your Channels:</b> {len(channels)}
<b>Total Chats:</b> {total_chats}

Select an option below to manage:
"""
    
    await message.answer(
        manage_text,
        reply_markup=ButtonManager.user_manage_main(),
        parse_mode=ParseMode.HTML
    )

@router.message(Command("setup"))
async def setup_handler(message: Message):
    """Setup userbot in channels with auto-promotion"""
    user_id = message.from_user.id
    
    if not userbot_client.is_connected:
        await message.answer("Userbot is not connected.")
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
    
    await setup_msg.edit_text(f"Setup complete: {success_count}/{len(user_channels)} channels")
    
@router.message(Command("refresh_invite"))
async def refresh_invite_handler(message: Message):
    """Refresh invite link for a channel"""
    user_id = message.from_user.id
    
    # Get the command argument (channel ID)
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /refresh_invite <channel_id>")
        return
    
    channel_id = args[1]
    
    # Check if user owns this channel
    channel = db.get_chat(channel_id)
    if not channel or channel['added_by'] != user_id:
        await message.answer("❌ Channel not found or you don't have permission.")
        return
    
    refresh_msg = await message.answer(f"🔄 Refreshing invite link for {channel['title']}...")
    
    try:
        # Create new invite link
        invite = await message.bot.create_chat_invite_link(
            int(channel_id),
            name="AutoReq UserBot Join",
            creates_join_request=False,
            expire_date=None,
            member_limit=1
        )
        
        # Update database
        db.chats.update_one(
            {"chat_id": channel_id},
            {"$set": {"invite_link": invite.invite_link, "userbot_setup": False}}
        )
        
        await refresh_msg.edit_text(
            f"✅ New invite link created for {channel['title']}\n\n"
            f"🔗 Link: <code>{invite.invite_link}</code>\n\n"
            f"Now use /setup to setup userbot with the new link.",
            parse_mode=ParseMode.HTML
        )
        
    except Exception as e:
        await refresh_msg.edit_text(f"❌ Error creating invite link: {e}")

@router.message(Command("db"))
async def db_handler(message: Message):
    """Owner-only full database management"""
    if message.from_user.id != config.OWNER_ID:
        return await message.answer("❌ Owner only command")
    
    all_chats = db.get_all_chats()
    total_chats = len(all_chats)
    groups = [c for c in all_chats if c['chat_type'] == 'group']
    channels = [c for c in all_chats if c['chat_type'] == 'channel']
    
    stats_text = f"""
<b>📊 Database Management (Owner)</b>

<b>Total Groups:</b> {len(groups)}
<b>Total Channels:</b> {len(channels)}
<b>Total Chats:</b> {total_chats}
"""
    
    await message.answer(
        stats_text,
        reply_markup=ButtonManager.db_main(),
        parse_mode=ParseMode.HTML
    )

@router.message(Command("stats"))
async def stats_handler(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    
    all_chats = db.get_all_chats()
    groups = [chat for chat in all_chats if chat['chat_type'] == 'group']
    channels = [chat for chat in all_chats if chat['chat_type'] == 'channel']
    
    stats_text = f"""
<b>📈 Overall Statistics (Owner)</b>

<b>Groups:</b> {len(groups)}
<b>Channels:</b> {len(channels)}
<b>Total Chats:</b> {len(all_chats)}

<b>Active Chats:</b> {len([c for c in all_chats if c.get('is_active', True)])}
"""
    
    await message.answer(stats_text, parse_mode=ParseMode.HTML)

@router.message(Command("debug"))
async def debug_handler(message: Message):
    if message.from_user.id != config.OWNER_ID:
        return
    
    all_chats = db.get_all_chats()
    total_chats = len(all_chats)
    active_chats = len([c for c in all_chats if c.get('is_active', True)])
    
    debug_text = f"""
<b>🔧 Debug Information</b>

<b>Total Chats in DB:</b> {total_chats}
<b>Active Chats:</b> {active_chats}
<b>Bot Status:</b> ✅ Running
<b>Userbot Status:</b> {'✅ Connected' if userbot_client.is_connected else '❌ Disconnected'}

<b>Recent Chats:</b>
"""
    
    for chat in all_chats[-5:]:  # Show last 5 chats
        status = "✅" if chat.get('is_active', True) else "❌"
        debug_text += f"• {status} {chat['title']} ({chat['chat_type']}) - by {chat['added_by']}\n"
    
    await message.answer(debug_text, parse_mode=ParseMode.HTML)

@router.message(Command("setup"))
async def setup_handler(message: Message):
    """Manually setup userbot in a channel"""
    user_id = message.from_user.id
    
    # Get user's channels that need setup
    user_channels = list(db.chats.find({
        "added_by": user_id,
        "chat_type": "channel",
        "userbot_setup": False
    }))
    
    if not user_channels:
        await message.answer("✅ All your channels are already setup or no channels found.")
        return
    
    if not userbot_client.is_connected:
        await message.answer("❌ Userbot is not connected. Check your session string.")
        return
    
    text = "<b>🔄 Channels Needing Setup</b>\n\n"
    for channel in user_channels:
        text += f"• {channel['title']}\n"
    
    text += "\nStarting setup process..."
    setup_msg = await message.answer(text, parse_mode=ParseMode.HTML)
    
    success_count = 0
    for channel in user_channels:
        try:
            success = await userbot_client.setup_channel(
                int(channel['chat_id']), 
                channel.get('invite_link')
            )
            
            if success:
                db.chats.update_one(
                    {"chat_id": channel['chat_id']},
                    {"$set": {"userbot_setup": True}}
                )
                success_count += 1
                await asyncio.sleep(2)  # Rate limit
        except Exception as e:
            print(f"❌ Setup failed for {channel['title']}: {e}")
    
    await setup_msg.edit_text(
        f"<b>✅ Setup Complete</b>\n\nSuccessfully setup {success_count}/{len(user_channels)} channels.",
        parse_mode=ParseMode.HTML
    )

@router.message(Command("channel_info"))
async def channel_info_handler(message: Message):
    """Check channel information and userbot status"""
    user_id = message.from_user.id
    
    # Get user's channels
    user_channels = list(db.chats.find({
        "added_by": user_id,
        "chat_type": "channel"
    }))
    
    if not user_channels:
        await message.answer("❌ No channels found in your account.")
        return
    
    text = "<b>📊 Your Channels Status</b>\n\n"
    
    for channel in user_channels:
        chat_id = int(channel['chat_id'])
        
        # Get channel info from userbot
        channel_info = await userbot_client.get_channel_info(chat_id) if userbot_client.is_connected else None
        
        text += f"<b>📺 {channel['title']}</b>\n"
        text += f"ID: <code>{channel['chat_id']}</code>\n"
        text += f"Setup: {'✅' if channel.get('userbot_setup') else '❌'}\n"
        text += f"Active: {'✅' if channel.get('is_active', True) else '❌'}\n"
        
        if channel_info:
            text += f"Participants: {channel_info.get('participants_count', 'Unknown')}\n"
            text += f"Type: {'Broadcast' if channel_info.get('broadcast') else 'Group'}\n"
        else:
            text += f"Status: ❌ Cannot access\n"
        
        text += "\n"
    
    await message.answer(text, parse_mode=ParseMode.HTML)

@router.message(Command("force_setup"))
async def force_setup_handler(message: Message):
    """Force setup userbot in a specific channel"""
    user_id = message.from_user.id
    
    if not userbot_client.is_connected:
        await message.answer("❌ Userbot is not connected. Check your session string.")
        return
    
    # Get the command argument (channel ID)
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Usage: /force_setup <channel_id>")
        return
    
    channel_id = args[1]
    
    # Check if user owns this channel
    channel = db.get_chat(channel_id)
    if not channel or channel['added_by'] != user_id:
        await message.answer("❌ Channel not found or you don't have permission.")
        return
    
    setup_msg = await message.answer(f"🔄 Force setting up channel {channel['title']}...")
    
    try:
        success = await userbot_client.setup_channel(
            int(channel_id), 
            channel.get('invite_link')
        )
        
        if success:
            db.chats.update_one(
                {"chat_id": channel_id},
                {"$set": {"userbot_setup": True}}
            )
            await setup_msg.edit_text(f"✅ Successfully force-setup channel {channel['title']}")
        else:
            await setup_msg.edit_text(f"❌ Failed to force-setup channel {channel['title']}")
            
    except Exception as e:
        await setup_msg.edit_text(f"❌ Error during force-setup: {e}")
