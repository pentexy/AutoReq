from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest, GetParticipantsRequest, JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, GetBotCallbackAnswerRequest
from telethon.tl.types import ChatAdminRights, InputPeerChannel, ChannelParticipantsRecent
from telethon.errors import ChannelPrivateError, UserAlreadyParticipantError, FloodWaitError, InviteHashExpiredError, InviteHashInvalidError
from telethon.tl.types import PeerChannel, InputChannel
import asyncio
from config import config

class UserBotClient:
    def __init__(self):
        self.client = None
        self.is_connected = False
    
    async def start(self):
        if not config.SESSION_STRING:
            print("❌ No userbot session configured")
            return False
        
        try:
            self.client = TelegramClient(
                session=StringSession(config.SESSION_STRING),
                api_id=config.API_ID,
                api_hash=config.API_HASH
            )
            
            await self.client.start()
            self.is_connected = True
            print("✅ Userbot started successfully")
            return True
        except Exception as e:
            print(f"❌ Userbot failed to start: {e}")
            return False

    async def create_invite_link_via_bot(self, bot_token: str, chat_id: int):
        """Create an invite link using the bot"""
        try:
            from telethon import TelegramClient as BotClient
            from telethon.sessions import MemorySession
            
            # Create a temporary bot client to generate invite link
            bot_client = BotClient(
                MemorySession(),
                api_id=config.API_ID,
                api_hash=config.API_HASH
            )
            
            await bot_client.start(bot_token=bot_token)
            
            # Create invite link
            invite = await bot_client.create_chat_invite_link(
                chat_id,
                name="AutoReq UserBot Join",
                creates_join_request=False  # Direct join
            )
            
            await bot_client.disconnect()
            return invite.invite_link
            
        except Exception as e:
            print(f"❌ Failed to create invite link via bot: {e}")
            return None

    async def join_channel_via_invite(self, invite_link: str):
        """Join channel using invite link"""
        if not self.is_connected:
            return False
        
        try:
            # Join using the invite link
            await self.client.join_chat(invite_link)
            print(f"✅ Userbot joined via invite link")
            return True
            
        except UserAlreadyParticipantError:
            print(f"✅ Userbot already in channel")
            return True
        except (InviteHashExpiredError, InviteHashInvalidError):
            print(f"❌ Invite link expired or invalid")
            return False
        except Exception as e:
            print(f"❌ Failed to join via invite: {e}")
            return False

    async def join_channel(self, chat_id: int, invite_link: str = None):
        """Join channel via multiple methods"""
        if not self.is_connected:
            return False
        
        # Method 1: Try using existing invite link
        if invite_link:
            success = await self.join_channel_via_invite(invite_link)
            if success:
                return True
            else:
                print("❌ Failed with existing invite link, trying to create new one...")
        
        # Method 2: Create new invite link via bot and join
        try:
            new_invite_link = await self.create_invite_link_via_bot(config.BOT_TOKEN, chat_id)
            if new_invite_link:
                print(f"🔗 Created new invite link: {new_invite_link}")
                success = await self.join_channel_via_invite(new_invite_link)
                if success:
                    return True
        except Exception as e:
            print(f"❌ Failed to create/use new invite link: {e}")
        
        # Method 3: Try direct join (might work for public channels)
        try:
            # Remove the -100 prefix for direct access
            if str(chat_id).startswith('-100'):
                raw_id = int(str(chat_id).replace('-100', ''))
                entity = await self.client.get_entity(PeerChannel(raw_id))
            else:
                entity = await self.client.get_entity(chat_id)
            
            await self.client(JoinChannelRequest(entity))
            print(f"✅ Userbot joined channel directly: {chat_id}")
            return True
            
        except UserAlreadyParticipantError:
            print(f"✅ Userbot already in channel: {chat_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to join channel directly {chat_id}: {e}")
        
        return False

    async def promote_to_admin(self, chat_id: int):
        """Promote userbot to admin in the channel"""
        if not self.is_connected:
            return False
        
        try:
            # Get entity using different methods
            entity = None
            try:
                entity = await self.client.get_entity(chat_id)
            except:
                try:
                    if str(chat_id).startswith('-100'):
                        raw_id = int(str(chat_id).replace('-100', ''))
                        entity = await self.client.get_entity(PeerChannel(raw_id))
                except:
                    pass
            
            if not entity:
                print(f"❌ Could not get entity for promotion: {chat_id}")
                return False
            
            me = await self.client.get_me()
            
            # Define admin rights
            admin_rights = ChatAdminRights(
                invite_users=True,
                ban_users=True,
                delete_messages=True,
                pin_messages=True,
                manage_call=True,
                post_messages=True,
                add_admins=False,
                change_info=True,
                edit_messages=True
            )
            
            # Promote to admin
            await self.client(EditAdminRequest(
                channel=entity,
                user_id=me,
                admin_rights=admin_rights,
                rank="AutoReq UserBot"
            ))
            
            print(f"✅ Userbot promoted to admin in: {chat_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error promoting userbot in {chat_id}: {e}")
            return False

    async def accept_join_request(self, chat_id: int, user_id: int):
        """Accept join request in channel"""
        if not self.is_connected:
            return False
        
        try:
            # Get entity
            entity = await self.client.get_entity(chat_id)
            
            # For channels, approve the join request by editing permissions
            await self.client.edit_permissions(
                entity,
                user_id,
                view_messages=True,
                send_messages=True,
                send_media=True,
                send_stickers=True,
                send_gifs=True,
                send_games=True,
                send_inline=True,
                embed_links=True
            )
            
            print(f"✅ Join request accepted for {user_id} in {chat_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error accepting join request: {e}")
            return False

    async def setup_channel(self, chat_id: int, invite_link: str = None):
        """Full setup: join channel and get admin rights"""
        print(f"🔧 Setting up userbot in channel {chat_id}")
        
        # Step 1: Join channel
        joined = await self.join_channel(chat_id, invite_link)
        if not joined:
            print(f"❌ Failed to join channel {chat_id}")
            return False
        
        # Wait a bit before promoting
        await asyncio.sleep(3)
        
        # Step 2: Promote to admin
        promoted = await self.promote_to_admin(chat_id)
        if not promoted:
            print(f"❌ Failed to promote in channel {chat_id}")
            return False
        
        print(f"✅ Userbot setup completed for channel {chat_id}")
        return True

    async def get_channel_info(self, chat_id: int):
        """Get information about a channel"""
        try:
            entity = await self.client.get_entity(chat_id)
            if entity:
                return {
                    'title': getattr(entity, 'title', 'Unknown'),
                    'username': getattr(entity, 'username', None),
                    'participants_count': getattr(entity, 'participants_count', 0),
                    'broadcast': getattr(entity, 'broadcast', False)
                }
            return None
        except Exception as e:
            print(f"❌ Error getting channel info: {e}")
            return None

# Global instance
userbot_client = UserBotClient()
