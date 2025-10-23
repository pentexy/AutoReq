from pyrogram import Client
from pyrogram.types import ChatPrivileges
from pyrogram.enums import ChatMemberStatus
from config import config
import asyncio

class PromotionService:
    def __init__(self, bot_client: Client):
        self.bot = bot_client
    
    async def promote_userbot(self, chat_id: int, userbot_user_id: int):
        """Promote userbot to admin using bot's admin privileges"""
        try:
            print(f"Promoting userbot {userbot_user_id} in chat {chat_id}")
            
            # Check if bot has admin rights
            bot_member = await self.bot.get_chat_member(chat_id, "me")
            if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
                print("Bot is not admin in this chat")
                return False
            
            # Check if bot has promote permission
            if not bot_member.privileges.can_promote_members:
                print("Bot does not have promote members permission")
                return False
            
            # Check if userbot is already admin
            try:
                userbot_member = await self.bot.get_chat_member(chat_id, userbot_user_id)
                if userbot_member.status == ChatMemberStatus.ADMINISTRATOR:
                    print("Userbot is already an admin")
                    return True
            except:
                pass
            
            # Promote userbot with specific privileges
            privileges = ChatPrivileges(
                can_change_info=False,
                can_delete_messages=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_restrict_members=False,
                can_promote_members=False,
                can_manage_chat=True,
                can_manage_video_chats=True,
                is_anonymous=False,
            )
            
            await self.bot.promote_chat_member(
                chat_id=chat_id,
                user_id=userbot_user_id,
                privileges=privileges
            )
            
            # Set admin title
            try:
                await self.bot.set_administrator_title(
                    chat_id=chat_id,
                    user_id=userbot_user_id,
                    title="AutoReq UserBot"
                )
            except:
                pass  # Title setting is optional
            
            print(f"Successfully promoted userbot in {chat_id}")
            return True
            
        except Exception as e:
            print(f"Error promoting userbot: {e}")
            return False
    
    async def check_bot_permissions(self, chat_id: int):
        """Check if bot has required admin permissions"""
        try:
            bot_member = await self.bot.get_chat_member(chat_id, "me")
            
            if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
                return False, "Bot is not admin in this chat"
            
            required_permissions = [
                ("can_promote_members", "Promote members"),
                ("can_invite_users", "Invite users"),
            ]
            
            missing_permissions = []
            for perm, name in required_permissions:
                if not getattr(bot_member.privileges, perm, False):
                    missing_permissions.append(name)
            
            if missing_permissions:
                return False, f"Missing permissions: {', '.join(missing_permissions)}"
            
            return True, "All permissions available"
            
        except Exception as e:
            return False, f"Error checking permissions: {e}"

# Global instance
promotion_service = None

def init_promotion_service(bot_client: Client):
    global promotion_service
    promotion_service = PromotionService(bot_client)
