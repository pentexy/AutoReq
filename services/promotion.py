from aiogram import Bot
from aiogram.types import ChatAdministratorRights
from aiogram.enums import ChatMemberStatus
from config import config
import asyncio

class PromotionService:
    def __init__(self, bot_client: Bot):
        self.bot = bot_client
        print("✅ Promotion service initialized with Aiogram")
    
    async def promote_userbot(self, chat_id: int, userbot_user_id: int):
        """Promote userbot to admin using bot's admin privileges"""
        try:
            print(f"Promoting userbot {userbot_user_id} in chat {chat_id}")
            
            # Check if bot has admin rights
            bot_member = await self.bot.get_chat_member(chat_id, self.bot.id)
            if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
                print("Bot is not admin in this chat")
                return False
            
            # Check if bot has promote permission
            if not bot_member.can_promote_members:
                print("Bot does not have promote members permission")
                return False
            
            # Check if userbot is already admin
            try:
                userbot_member = await self.bot.get_chat_member(chat_id, userbot_user_id)
                if userbot_member.status == ChatMemberStatus.ADMINISTRATOR:
                    print("Userbot is already an admin")
                    return True
            except Exception as e:
                print(f"Error checking userbot status: {e}")
            
            # Define admin rights for Aiogram
            rights = ChatAdministratorRights(
                can_change_info=False,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=False,
                can_promote_members=False,
                can_manage_chat=True,
                can_manage_video_chats=True,
                is_anonymous=False,
                can_manage_voice_chats=True,
                can_post_messages=False,
                can_edit_messages=False,
                can_pin_messages=True
            )
            
            # Promote userbot
            await self.bot.promote_chat_member(
                chat_id=chat_id,
                user_id=userbot_user_id,
                rights=rights
            )
            
            # Set custom title
            try:
                await self.bot.set_chat_administrator_custom_title(
                    chat_id=chat_id,
                    user_id=userbot_user_id,
                    custom_title="AutoReq UserBot"
                )
            except Exception as e:
                print(f"Could not set custom title: {e}")
            
            print(f"Successfully promoted userbot in {chat_id}")
            return True
            
        except Exception as e:
            print(f"Error promoting userbot: {e}")
            return False
    
    async def check_bot_permissions(self, chat_id: int):
        """Check if bot has required admin permissions"""
        try:
            bot_member = await self.bot.get_chat_member(chat_id, self.bot.id)
            
            if bot_member.status != ChatMemberStatus.ADMINISTRATOR:
                return False, "Bot is not admin in this chat"
            
            required_permissions = [
                ("can_promote_members", "Promote members"),
                ("can_invite_users", "Invite users"),
            ]
            
            missing_permissions = []
            for perm, name in required_permissions:
                if not getattr(bot_member, perm, False):
                    missing_permissions.append(name)
            
            if missing_permissions:
                return False, f"Missing permissions: {', '.join(missing_permissions)}"
            
            return True, "All permissions available"
            
        except Exception as e:
            return False, f"Error checking permissions: {e}"

# Global instance
promotion_service = None

def init_promotion_service(bot_client: Bot):
    global promotion_service
    promotion_service = PromotionService(bot_client)
    print(f"✅ Promotion service initialized with bot ID: {bot_client.id}")
    return promotion_service
