from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class ButtonManager:
    @staticmethod
    def start_button():
        return InlineKeyboardMarkup([[
            InlineKeyboardButton("Add Me", url="https://t.me/AutoReqAccepterRobot?startgroup=true")
        ]])

    @staticmethod
    def db_main():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Groups", callback_data="db_groups")],
            [InlineKeyboardButton("Channels", callback_data="db_channels")],
            [InlineKeyboardButton("Refresh", callback_data="db_refresh")]
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
                    f"{chat.title[:30]}",
                    callback_data=f"chat_{chat.chat_id}"
                )
            ])
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("Previous", callback_data=f"list_{chat_type}_{page-1}"))
        if end_idx < len(chats):
            nav_buttons.append(InlineKeyboardButton("Next", callback_data=f"list_{chat_type}_{page+1}"))
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        buttons.append([InlineKeyboardButton("Back", callback_data="db_main")])
        
        return InlineKeyboardMarkup(buttons)

    @staticmethod
    def chat_detail(chat_id, stats):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Pending: {stats['pending_requests']}", callback_data="show_pending")],
            [InlineKeyboardButton("Accept All", callback_data=f"accept_all_{chat_id}")],
            [InlineKeyboardButton("Refresh Stats", callback_data=f"refresh_{chat_id}")],
            [InlineKeyboardButton("Back", callback_data="db_groups_0")]
        ])

    @staticmethod
    def back_button(back_to):
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Back", callback_data=back_to)]
        ])
