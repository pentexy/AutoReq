from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class ButtonManager:
    @staticmethod
    def start_button():
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Add to Group", url="http://t.me/AutoReqAccepterRobot?startgroup=true")
        ]])

    @staticmethod
    def user_manage_main():
        """Buttons for regular users to manage their chats"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="My Groups", callback_data="my_groups")],
            [InlineKeyboardButton(text="My Channels", callback_data="my_channels")],
            [InlineKeyboardButton(text="Refresh", callback_data="my_refresh")]
        ])

    @staticmethod
    def db_main():
        """Buttons for owner database management"""
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="All Groups", callback_data="db_groups")],
            [InlineKeyboardButton(text="All Channels", callback_data="db_channels")],
            [InlineKeyboardButton(text="User Stats", callback_data="db_users")],
            [InlineKeyboardButton(text="Refresh", callback_data="db_refresh")]
        ])

    @staticmethod
    def chat_list(chats, page=0, list_type="db_groups"):
        buttons = []
        chats_per_page = 8
        start_idx = page * chats_per_page
        end_idx = start_idx + chats_per_page
        
        for chat in chats[start_idx:end_idx]:
            status = "✅" if chat.get('is_active', True) else "❌"
            buttons.append([
                InlineKeyboardButton(
                    text=f"{status} {chat['title'][:25]}",
                    callback_data=f"chat_{chat['chat_id']}"
                )
            ])
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"list_{list_type}_{page-1}"))
        if end_idx < len(chats):
            nav_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"list_{list_type}_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        if list_type.startswith("my_"):
            buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="my_main")])
        else:
            buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="db_main")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def chat_detail(chat_id, stats, is_owner=False):
        buttons = [
            [InlineKeyboardButton(text=f"📊 Stats: {stats['pending_requests']} pending", callback_data="show_stats")],
            [InlineKeyboardButton(text="✅ Accept All", callback_data=f"accept_all_{chat_id}")],
            [InlineKeyboardButton(text="🔄 Refresh", callback_data=f"refresh_{chat_id}")]
        ]
        
        if is_owner:
            buttons.append([InlineKeyboardButton(text="🗑️ Remove", callback_data=f"remove_{chat_id}")])
        
        if chat_id.startswith("-100"):  # Channel
            buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="db_channels_0")])
        else:  # Group
            buttons.append([InlineKeyboardButton(text="🔙 Back", callback_data="db_groups_0")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def back_button(back_to):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Back", callback_data=back_to)]
        ])
