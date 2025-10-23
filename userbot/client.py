from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import ChatAdminRights, InputPeerChannel
from telethon.errors import ChannelPrivateError, UserAlreadyParticipantError
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

    async def join_channel(self, chat_id: int, invite_link: str = None):
        """Join channel via invite link or chat ID"""
        if not self.is_connected:
            return False
        
        try:
            # Try to get the channel entity
            try:
                channel = await self.client.get_entity(chat_id)
            except ChannelPrivateError:
                # If channel is private and we have invite link, use it
                if invite_link:
                    if "t.me/+" in invite_link:
                        hash = invite_link.split("+")[1]
                        await self.client(ImportChatInviteRequest(hash))
                    else:
                        await self.client.join_chat(invite_link)
                    print(f"✅ Userbot joined channel via invite link")
                    return True
                else:
                    print(f"❌ No invite link provided for private channel")
                    return False
            
            # Try to join the channel
            try:
                await self.client(InviteToChannelRequest(channel, [await self.client.get_me()]))
                print(f"✅ Userbot joined channel {chat_id}")
                return True
            except UserAlreadyParticipantError:
                print(f"✅ Userbot already in channel {chat_id}")
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
            channel = await self.client.get_entity(chat_id)
            me = await self.client.get_me()
            
            # Define admin rights
            admin_rights = ChatAdminRights(
                post_messages=True,
                add_admins=False,
                invite_users=True,
                change_info=True,
                ban_users=True,
                delete_messages=True,
                pin_messages=True,
                edit_messages=True,
                manage_call=True
            )
            
            # Promote to admin
            await self.client(EditAdminRequest(
                channel=channel,
                user_id=me,
                admin_rights=admin_rights,
                rank="AutoReq UserBot"
            ))
            
            print(f"✅ Userbot promoted to admin in {chat_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error promoting userbot in {chat_id}: {e}")
            return False

    async def accept_join_request(self, chat_id: int, user_id: int):
        """Accept join request in channel"""
        if not self.is_connected:
            return False
        
        try:
            # First ensure userbot is in the channel and is admin
            channel = await self.client.get_entity(chat_id)
            
            # Get the participant (join request)
            participants = await self.client.get_participants(channel, limit=100)
            
            # Check if user is in participants (pending)
            for participant in participants:
                if participant.id == user_id:
                    # This means user is already a participant or pending
                    # For channels, we need to use the specific method
                    try:
                        # Try to get the specific join request
                        result = await self.client.get_participants(
                            channel, 
                            filter=ChannelParticipantsRequest(channel),
                            limit=100
                        )
                        
                        # Look for the specific user in pending requests
                        for user in result:
                            if user.id == user_id:
                                # Accept the join request
                                await self.client.edit_permissions(
                                    channel, 
                                    user_id, 
                                    view_messages=True,
                                    send_messages=True
                                )
                                print(f"✅ Join request accepted for {user_id} in {chat_id}")
                                return True
                    except Exception as e:
                        print(f"❌ Error in accept_join_request: {e}")
                        return False
            
            print(f"❌ No pending join request found for {user_id} in {chat_id}")
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
        
        # Step 2: Promote to admin
        promoted = await self.promote_to_admin(chat_id)
        if not promoted:
            print(f"❌ Failed to promote in channel {chat_id}")
            return False
        
        print(f"✅ Userbot setup completed for channel {chat_id}")
        return True

# Global instance
userbot_client = UserBotClient()
