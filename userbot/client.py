from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest, GetParticipantsRequest
from telethon.tl.functions.messages import ImportChatInviteRequest, GetBotCallbackAnswerRequest
from telethon.tl.types import ChatAdminRights, InputPeerChannel, ChannelParticipantsRecent
from telethon.errors import ChannelPrivateError, UserAlreadyParticipantError, FloodWaitError
from telethon.tl.types import PeerChannel
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

    async def get_entity_safe(self, chat_id: int):
        """Safely get entity with proper error handling"""
        try:
            entity = await self.client.get_entity(chat_id)
            return entity
        except ValueError:
            # Entity not found in cache, try to get it by ID
            try:
                entity = await self.client.get_entity(PeerChannel(chat_id))
                return entity
            except Exception as e:
                print(f"❌ Could not get entity for {chat_id}: {e}")
                return None
        except Exception as e:
            print(f"❌ Error getting entity for {chat_id}: {e}")
            return None

    async def join_channel(self, chat_id: int, invite_link: str = None):
        """Join channel via invite link or chat ID"""
        if not self.is_connected:
            return False
        
        try:
            # First, get the entity safely
            entity = await self.get_entity_safe(chat_id)
            if not entity:
                if invite_link:
                    # Try to join via invite link
                    try:
                        if "t.me/+" in invite_link:
                            hash = invite_link.split("+")[1]
                            await self.client(ImportChatInviteRequest(hash))
                        else:
                            await self.client.join_chat(invite_link)
                        print(f"✅ Userbot joined channel via invite link: {chat_id}")
                        return True
                    except UserAlreadyParticipantError:
                        print(f"✅ Userbot already in channel: {chat_id}")
                        return True
                    except Exception as e:
                        print(f"❌ Failed to join via invite link {chat_id}: {e}")
                        return False
                else:
                    print(f"❌ No entity found and no invite link for {chat_id}")
                    return False
            
            # Try to join the channel using the entity
            try:
                await self.client(InviteToChannelRequest(entity, [await self.client.get_me()]))
                print(f"✅ Userbot joined channel: {chat_id}")
                return True
            except UserAlreadyParticipantError:
                print(f"✅ Userbot already in channel: {chat_id}")
                return True
            except Exception as e:
                print(f"❌ Failed to join channel {chat_id}: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Error joining channel {chat_id}: {e}")
            return False

    async def promote_to_admin(self, chat_id: int):
        """Promote userbot to admin in the channel"""
        if not self.is_connected:
            return False
        
        try:
            entity = await self.get_entity_safe(chat_id)
            if not entity:
                print(f"❌ Could not get entity for promotion: {chat_id}")
                return False
            
            me = await self.client.get_me()
            
            # Define admin rights (minimal required for accepting requests)
            admin_rights = ChatAdminRights(
                invite_users=True,  # Most important for accepting requests
                ban_users=True,
                delete_messages=True,
                pin_messages=True,
                manage_call=True,
                post_messages=True if hasattr(entity, 'broadcast') and entity.broadcast else False,
                add_admins=False,  # Don't allow to add other admins
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
            # Get the entity safely
            entity = await self.get_entity_safe(chat_id)
            if not entity:
                print(f"❌ Could not get entity for accepting request: {chat_id}")
                return False
            
            # Use the correct method for accepting join requests
            # For channels, we need to use the specific method
            try:
                # Get pending join requests
                participants = await self.client(GetParticipantsRequest(
                    channel=entity,
                    filter=ChannelParticipantsRecent(),
                    offset=0,
                    limit=100,
                    hash=0
                ))
                
                # Look for the specific user in participants
                user_found = False
                for participant in participants.users:
                    if participant.id == user_id:
                        user_found = True
                        break
                
                if user_found:
                    # For recent participants (pending), we approve them by editing permissions
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
                else:
                    print(f"❌ User {user_id} not found in recent participants of {chat_id}")
                    return False
                    
            except Exception as e:
                print(f"❌ Error in accept_join_request for {chat_id}: {e}")
                return False
            
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
        await asyncio.sleep(2)
        
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
            entity = await self.get_entity_safe(chat_id)
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
