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

    async def is_userbot_in_channel(self, chat_id: int):
        """Simple check if userbot can access the channel"""
        if not self.is_connected:
            return False
        
        try:
            # Try to get the channel entity - this will fail if not a member
            entity = await self.client.get_entity(chat_id)
            
            # If we can get the entity, we're probably in the channel
            # Try a simple operation that doesn't require admin rights
            try:
                # Try to get basic chat info
                chat = await self.client.get_entity(chat_id)
                return True
            except:
                return False
                
        except Exception as e:
            # If we can't get the entity, we're not in the channel
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
            print(f"🔗 Using invite link: {invite_link}")
            
            # For t.me/+ links (private invite links)
            if "t.me/+" in invite_link:
                hash = invite_link.split("+")[1]
                # Remove any query parameters
                hash = hash.split('?')[0]
                
                # Import the invite
                await self.client(ImportChatInviteRequest(hash))
                print(f"✅ Userbot joined via private invite")
                return True
            else:
                # For other links, use join_chat method
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
        """Join channel - assume success if no error"""
        if not self.is_connected:
            return False
        
        print(f"🔄 Joining channel {chat_id}")
        
        # Method 1: Try using invite link
        if invite_link:
            print(f"🔗 Using invite link...")
            success = await self.join_channel_via_invite(invite_link)
            if success:
                print(f"✅ Join successful via invite link")
                return True
        
        # If no invite link or join failed
        print(f"❌ No invite link or join failed")
        return False

    async def promote_to_admin(self, chat_id: int):
        """Promote userbot to admin in the channel"""
        if not self.is_connected:
            return False
        
        try:
            # Get entity - this will fail if not in channel
            entity = await self.client.get_entity(chat_id)
            me = await self.client.get_me()
            
            # Define admin rights (minimal set for accepting requests)
            admin_rights = ChatAdminRights(
                invite_users=True,  # Most important for accepting requests
                ban_users=True,
                delete_messages=True,
                pin_messages=True,
                manage_call=True,
                post_messages=False,
                add_admins=False,
                change_info=False,
                edit_messages=False
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

    async def test_channel_access(self, chat_id: int):
        """Test if userbot has proper access to the channel"""
        if not self.is_connected:
            return False
        
        try:
            # Try to get entity
            entity = await self.client.get_entity(chat_id)
            
            # Try a simple operation
            await self.client.get_permissions(entity, await self.client.get_me())
            
            print(f"✅ Userbot has access to channel {chat_id}")
            return True
            
        except Exception as e:
            print(f"❌ Userbot cannot access channel {chat_id}: {e}")
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
            
            print(f"✅ Join request accepted for {user_id} in {chat_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error accepting join request: {e}")
            return False

    async def setup_channel(self, chat_id: int, invite_link: str = None):
        """Full setup: join channel and get admin rights"""
        print(f"🔧 Setting up userbot in channel {chat_id}")
        
        # Get userbot info for reference
        userbot_info = await self.get_userbot_info()
        userbot_ref = f"@{userbot_info['username']}" if userbot_info and userbot_info.get('username') else f"Userbot (ID: {userbot_info['id']})" if userbot_info else "Userbot"
        
        # Step 1: Join channel
        print("📥 Step 1: Joining channel...")
        joined = await self.join_channel(chat_id, invite_link)
        if not joined:
            print(f"❌ Failed to join channel {chat_id}")
            print(f"💡 Please manually add {userbot_ref} to the channel")
            return False
        
        # Wait a bit
        await asyncio.sleep(3)
        
        # Step 2: Test access
        print("🔍 Step 2: Testing access...")
        has_access = await self.test_channel_access(chat_id)
        if not has_access:
            print(f"❌ Userbot cannot access channel {chat_id}")
            print(f"💡 Please ensure {userbot_ref} is properly added to the channel")
            return False
        
        # Step 3: Promote to admin
        print("👑 Step 3: Promoting to admin...")
        promoted = await self.promote_to_admin(chat_id)
        if not promoted:
            print(f"❌ Failed to promote in channel {chat_id}")
            print(f"💡 Please manually grant admin rights to {userbot_ref}")
            print(f"💡 Required permissions: Invite Users, Ban Users, Delete Messages")
            return False
        
        print(f"✅ Userbot setup completed for channel {chat_id}")
        return True

    async def get_channel_info(self, chat_id: int):
        """Get information about a channel"""
        try:
            entity = await self.client.get_entity(chat_id)
            if entity:
                # Simple check - if we can get entity, we have some access
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
            print(f"❌ Error getting channel info: {e}")
            return None

# Global instance
userbot_client = UserBotClient()
