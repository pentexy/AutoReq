from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest, GetParticipantsRequest, JoinChannelRequest, GetFullChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest, GetFullChatRequest
from telethon.tl.types import ChatAdminRights, InputPeerChannel, ChannelParticipantsRecent
from telethon.errors import ChannelPrivateError, UserAlreadyParticipantError, FloodWaitError, InviteHashExpiredError, InviteHashInvalidError
from telethon.tl.types import PeerChannel, InputChannel, Channel, ChatInvite, ChatInviteAlready
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

    async def get_userbot_info(self):
        """Get userbot information"""
        if not self.is_connected:
            return None
        
        try:
            me = await self.client.get_me()
            return {
                'id': me.id,
                'username': me.username,
                'first_name': me.first_name,
                'phone': me.phone
            }
        except Exception as e:
            print(f"❌ Error getting userbot info: {e}")
            return None

    async def join_channel_via_invite(self, invite_link: str):
        """Join channel using invite link"""
        if not self.is_connected:
            return False
        
        try:
            print(f"Using invite link: {invite_link}")
            
            # For t.me/+ links (private invite links)
            if "t.me/+" in invite_link:
                hash = invite_link.split("+")[1]
                # Remove any query parameters
                hash = hash.split('?')[0]
                
                # Import the invite
                await self.client(ImportChatInviteRequest(hash))
                print("Userbot joined via private invite")
                return True
            else:
                # For other links, use join_chat method
                await self.client.join_chat(invite_link)
                print("Userbot joined via invite link")
                return True
                
        except UserAlreadyParticipantError:
            print("Userbot already in channel")
            return True
        except (InviteHashExpiredError, InviteHashInvalidError):
            print("Invite link expired or invalid")
            return False
        except Exception as e:
            print(f"Failed to join via invite: {e}")
            return False

    async def join_channel(self, chat_id: int, invite_link: str = None):
        """Join channel"""
        if not self.is_connected:
            return False
        
        print(f"Joining channel {chat_id}")
        
        # Method 1: Try using invite link
        if invite_link:
            print("Using invite link...")
            success = await self.join_channel_via_invite(invite_link)
            if success:
                print("Join successful via invite link")
                return True
        
        print("No invite link or join failed")
        return False

    async def test_channel_access(self, chat_id: int):
        """Test if userbot has access to the channel"""
        if not self.is_connected:
            return False
        
        try:
            # Try to get entity
            entity = await self.client.get_entity(chat_id)
            print(f"Userbot has access to channel {chat_id}")
            return True
            
        except Exception as e:
            print(f"Userbot cannot access channel {chat_id}: {e}")
            return False

    async def accept_join_request(self, chat_id: int, user_id: int):
        """Accept join request in channel"""
        if not self.is_connected:
            return False
        
        try:
            # Get entity
            entity = await self.client.get_entity(chat_id)
            
            # For channels, approve the join request
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
            
            print(f"Join request accepted for {user_id} in {chat_id}")
            return True
            
        except Exception as e:
            print(f"Error accepting join request: {e}")
            return False

    async def setup_channel(self, chat_id: int, invite_link: str = None):
        """Join channel only - promotion will be done by bot"""
        print(f"Setting up userbot in channel {chat_id}")
        
        # Step 1: Join channel
        print("Step 1: Joining channel...")
        joined = await self.join_channel(chat_id, invite_link)
        if not joined:
            print(f"Failed to join channel {chat_id}")
            return False
        
        # Wait a bit
        await asyncio.sleep(3)
        
        # Step 2: Test access
        print("Step 2: Testing access...")
        has_access = await self.test_channel_access(chat_id)
        if not has_access:
            print(f"Userbot cannot access channel {chat_id}")
            return False
        
        print(f"Userbot setup completed for channel {chat_id}")
        return True

    async def get_channel_info(self, chat_id: int):
        """Get information about a channel"""
        try:
            entity = await self.client.get_entity(chat_id)
            if entity:
                has_access = await self.test_channel_access(chat_id)
                
                return {
                    'title': getattr(entity, 'title', 'Unknown'),
                    'username': getattr(entity, 'username', None),
                    'participants_count': getattr(entity, 'participants_count', 0),
                    'broadcast': getattr(entity, 'broadcast', False),
                    'userbot_has_access': has_access
                }
            return None
        except Exception as e:
            print(f"Error getting channel info: {e}")
            return None

# Global instance
userbot_client = UserBotClient()
