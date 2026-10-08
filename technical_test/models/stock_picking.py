from odoo import _, fields, models
from odoo.exceptions import ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def button_validate(self):
        today = fields.Date.context_today(self)

        for picking in self:
            scheduled_date = False
            if picking.scheduled_date:
                scheduled_date = fields.Datetime.context_timestamp(
                    picking,
                    picking.scheduled_date,
                ).date()

            if (
                picking.picking_type_code == "outgoing"
                and scheduled_date
                and scheduled_date >= today
            ):
                raise ValidationError(
                    _(
                        "You cannot validate this outgoing transfer because "
                        "its scheduled date is today or a future date."
                    )
                )

        return super().button_validate()