from odoo import models, fields, api, _
from odoo.exceptions import AccessError


class ResUsers(models.Model):
    _inherit = 'res.users'

    restrict_locations = fields.Boolean('Restrict Location')

    stock_cancel_location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_cancel_location_users',
        'user_id',
        'location_id',
        'Stock Cancel Locations')

    stock_location_ids = fields.Many2many(
        'stock.location',
        'location_security_stock_location_users',
        'user_id',
        'location_id',
        'Stock Locations')

    default_picking_type_ids = fields.Many2many(
        'stock.picking.type', 'stock_picking_type_users_rel',
        'user_id', 'picking_type_id', string='Default Warehouse Operations')


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    allowed_user_ids = fields.Many2many(
        'res.users', 'stock_picking_type_users_rel',
        'picking_type_id', 'user_id',  string='Allowed Users')


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.one
    @api.constrains('state', 'location_id', 'location_dest_id')
    def check_user_location_rights(self):
        if self.state in ['draft', 'waiting', 'assigned', 'confirmed']:
            return True
        user_locations = self.env.user.stock_location_ids
        if self.env.user.restrict_locations:
            message = _(
                'Invalid Location. You cannot process this move since you do '
                'not control the location "%s". '
                'Please contact your Adminstrator.')
            if self.state in ['done']:
                if self.location_id not in user_locations:
                    raise AccessError(message % self.location_id.name)
                elif self.location_dest_id not in user_locations:
                    raise AccessError(message % self.location_dest_id.name)
            if self.state in ['cancel']:
                if self.location_id not in user_locations | self.env.user.stock_cancel_location_ids:
                    raise AccessError(message % self.location_id.name)
                elif self.location_dest_id not in user_locations | self.env.user.stock_cancel_location_ids:
                    raise AccessError(message % self.location_id.name)


