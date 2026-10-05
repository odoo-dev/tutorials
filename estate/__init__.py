from . import models

# def uninstall_hook(env):
#     if env['estate.property'].search_count([('state', 'not in', ['new', 'cancelled'])]):
#         raise UserError("error......................")
#
#
# # @api.ondelete(at_uninstall=True)
# def _unlink_if_new_or_cancelled(env):
#     if env['estate.property'].search_count([('state', 'not in', ['new', 'cancelled'])]):
#         raise UserError("error......................")
