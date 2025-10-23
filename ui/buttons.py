from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class ButtonManager:
    @staticmethod
    def start_button():
        return InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text="Add to Group", url="http://t.me/AutoReqAccepterRobot?startgroup=true")
        ]])

    @staticmethod
    def db_main():
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Groups", callback_data="db_groups")],
            [InlineKeyboardButton(text="Channels", callback_data="db_channels")],
            [InlineKeyboardButton(text="Refresh", callback_data="db_refresh")]
        ])

    @staticmethod
    def chat_list(chats, page=0, chat_type="group"):
        buttons = []
        chats_per_page = 8
        start_idx = page * chats_per_page
        end_idx = start_idx + chats_per_page
        
        for chat in chats[start_idx:end_idx]:
            buttons.append([
                InlineKeyboardButton(
                    text=f"{chat['title'][:30]}",
                    callback_data=f"chat_{chat['chat_id']}"
                )
            ])
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton(text="Previous", callback_data=f"list_{chat_type}_{page-1}"))
        if end_idx < len(chats):
            nav_buttons.append(InlineKeyboardButton(text="Next", callback_data=f"list_{chat_type}_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        buttons.append([InlineKeyboardButton(text="Back", callback_data="db_main")])
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    @staticmethod
    def chat_detail(chat_id, stats):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"Pending: {stats['pending_requests']}", callback_data="show_pending")],
            [InlineKeyboardButton(text="Accept All", callback_data=f"accept_all_{chat_id}")],
            [InlineKeyboardButton(text="Refresh Stats", callback_data=f"refresh_{chat_id}")],
            [InlineKeyboardButton(text="Back", callback_data="db_groups_0")]
        ])

    @staticmethod
    def back_button(back_to):
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Back", callback_data=back_to)]
        ])
