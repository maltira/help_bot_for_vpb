from config import dp
from functions.start_command import router as start_router
from functions.ticket.create_ticket import router as create_ticket_router
from functions.ticket.close_ticket import router as close_ticket_router
from functions.faq import router as faq_router
from functions.ticket.admin_commands.menu import router as menu_router
from functions.ticket.admin_commands.list_of_tickets.page import router as page_router
from functions.ticket.admin_commands.list_of_tickets.list_all_tickets import router as list_all_router

dp.include_router(start_router)
dp.include_router(create_ticket_router)
dp.include_router(close_ticket_router)
dp.include_router(faq_router)
dp.include_router(menu_router)
dp.include_router(page_router)
dp.include_router(list_all_router)