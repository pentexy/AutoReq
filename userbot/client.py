from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest, GetParticipantsRequest, JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest
from telethon.tl.types import ChatAdminRights, InputPeerChannel, ChannelParticipantsRecent
from telethon.errors import ChannelPrivateError, UserAlreadyParticipantError, FloodWaitError, InviteHashExpiredError, InviteHashInvalidError
from telethon.tl.types import PeerChannel, InputChannel, Channel
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

    async def join_channel_via_invite(self, invite_link: str):
        """Join channel using invite link"""
        if not self.is_connected:
            return False
        
        try:
            # For t.me/+ links (private invite links)
            if "t.me/+" in invite_link:
                hash = invite_link.split("+")[1]
                # Check if it's a valid invite
                invite = await self.client(CheckChatInviteRequest(hash))
                if isinstance(invite, ChatInviteAlready):
                    print("✅ Userbot already in channel")
                    return True
                elif isinstance(invite, ChatInvite):
                    # Join using the hash
                    await self.client(ImportChatInviteRequest(hash))
                    print(f"✅ Userbot joined via private invite")
                    return True
            else:
                # For public links like t.me/username
                # Extract username or channel id from link
                if "t.me/" in invite_link:
                    username = invite_link.split("t.me/")[1]
                    if username.startswith("+"):
                        # It's a private invite
                        hash = username[1:]
                        await self.client(ImportChatInviteRequest(hash))
                        print(f"✅ Userbot joined via private invite")
                        return True
                    else:
                        # It's a public channel/group
                        entity = await self.client.get_entity(username)
                        await self.client(JoinChannelRequest(entity))
                        print(f"✅ Userbot joined public channel")
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

    async def join_channel_by_id(self, chat_id: int):
        """Try to join channel by ID (works if userbot has access)"""
        if not self.is_connected:
            return False
        
        try:
            # Convert -100 format to regular ID
            if str(chat_id).startswith('-100'):
                raw_id = int(str(chat_id)[4:])  # Remove -100 prefix
            else:
                raw_id = chat_id
            
            # Try to get entity
            try:
                entity = await self.client.get_entity(PeerChannel(raw_id))
            except:
                # Try with the original ID
                entity = await self.client.get_entity(chat_id)
            
            # Join the channel
            await self.client(JoinChannelRequest(entity))
            print(f"✅ Userbot joined channel by ID: {chat_id}")
            return True
            
        except UserAlreadyParticipantError:
            print(f"✅ Userbot already in channel: {chat_id}")
            return True
        except Exception as e:
            print(f"❌ Failed to join channel by ID {chat_id}: {e}")
            return False

    async def join_channel(self, chat_id: int, invite_link: str = None):
        """Join channel via multiple methods"""
        if not self.is_connected:
            return False
        
        print(f"🔄 Attempting to join channel {chat_id}")
        
        # Method 1: Try using invite link
        if invite_link:
            print(f"🔗 Trying invite link: {invite_link}")
            success = await self.join_channel_via_invite(invite_link)
            if success:
                return True
            else:
                print("❌ Failed with invite link")
        
        # Method 2: Try direct join by ID
        print("🆔 Trying direct join by ID...")
        success = await self.join_channel_by_id(chat_id)
        if success:
            return True
        else:
            print("❌ Failed with direct join")
        
        # Method 3: Last resort - ask user to manually add userbot
        print("💡 All automatic methods failed. Userbot needs to be manually added to the channel.")
        return False

    async def promote_to_admin(self, chat_id: int):
        """Promote userbot to admin in the channel"""
        if not self.is_connected:
            return False
        
        try:
            # Get entity
            entity = await self.client.get_entity(chat_id)
            
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
            print(f"💡 Please manually add the userbot to the channel and grant admin rights.")
            return False
        
        # Wait a bit before promoting
        await asyncio.sleep(3)
        
        # Step 2: Promote to admin
        promoted = await self.promote_to_admin(chat_id)
        if not promoted:
            print(f"❌ Failed to promote in channel {chat_id}")
            print(f"💡 Please manually grant admin rights to the userbot in the channel.")
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
