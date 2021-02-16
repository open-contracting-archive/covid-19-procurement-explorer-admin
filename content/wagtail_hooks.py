from wagtail.core import hooks
# from wagtail.admin.menu import ActionMenuItem

@hooks.register('construct_main_menu')
def hide_snippets_menu_item(request, menu_items):
  menu_items[:] = [item for item in menu_items if item.name != 'reports']

@hooks.register('construct_main_menu')
def hide_snippets_menu_item(request, menu_items):
  menu_items[:] = [item for item in menu_items if item.name != 'settings']

@hooks.register('construct_main_menu')
def hide_snippets_menu_item(request, menu_items):
  menu_items[:] = [item for item in menu_items if item.name != 'explorer']

# remove submit to moderation button
@hooks.register('construct_page_action_menu')
def remove_submit_to_moderator_option(menu_items, request, context):
    menu_items[:] = [item for item in menu_items if item.name != 'action-submit']

@hooks.register('construct_page_action_menu')
def remove_delete_option(menu_items, request, context):
    menu_items[:] = [item for item in menu_items if item.name != 'action-delete']

@hooks.register('construct_page_action_menu')
def remove_lock_option(menu_items, request, context):
    menu_items[:] = [item for item in menu_items if item.name != 'action-lock']

@hooks.register('construct_page_action_menu')
def remove_unpublish_option(menu_items, request, context):
    menu_items[:] = [item for item in menu_items if item.name != 'action-unpublish']

@hooks.register('construct_page_action_menu')
def remove_save_draft_option(menu_items, request, context):
    menu_items[:] = [item for item in menu_items if item.name != 'action-save-draft']

# @hooks.register('construct_page_action_menu')
# def rename_publish_option(menu_items, request, context):
#   menu_items[:] = [
#             PublishMenuItem(default=True, label='Save'),
#     ]
