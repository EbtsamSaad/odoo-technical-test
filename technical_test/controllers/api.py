import zoneinfo
from datetime import datetime, time, timedelta
from odoo import fields, http
from odoo.http import request


class TechnicalTestAPI(http.Controller):
    # Api (task2)
    def _get_user_tz(self):
        """Retrieve the user timezone or fall back to UTC."""
        tz_name = (
            request.env.context.get("tz") or request.env.user.tz or "UTC"
        )
        try:
            return zoneinfo.ZoneInfo(tz_name)
        except Exception:
            return zoneinfo.ZoneInfo("UTC")

    @http.route(
        "/api/orders",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_pos_orders(self, start_date=None, end_date=None, **kwargs):
        if not start_date or not end_date:
            return request.make_json_response(
                {
                    "success": False,
                    "message": "start_date and end_date are required.",
                },
                status=400,
            )
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d").date()
            end = datetime.strptime(end_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return request.make_json_response(
                {
                    "success": False,
                    "message": "Invalid date format. Use YYYY-MM-DD.",
                },
                status=400,
            )

        # 1. Get the user's timezone
        user_tz = self._get_user_tz()
        utc_tz = zoneinfo.ZoneInfo("UTC")

        # 2. Combine date with time start (00:00:00) and end (23:59:59.999999 or start of next day)
        start_local = datetime.combine(start, time.min).replace(tzinfo=user_tz)
        # End of day boundary (start of next day in local time)
        end_local = datetime.combine(end + timedelta(days=1), time.min).replace(tzinfo=user_tz)

        # 3. Convert local datetimes to UTC datetimes
        start_utc = start_local.astimezone(utc_tz)
        end_utc = end_local.astimezone(utc_tz)

        # 4. Format into naive UTC strings for Odoo ORM domain filtering
        start_utc_str = fields.Datetime.to_string(start_utc.replace(tzinfo=None))
        end_utc_str = fields.Datetime.to_string(end_utc.replace(tzinfo=None))
        domain = [
            ("date_order", ">=", start_utc_str),
            ("date_order", "<", end_utc_str),
        ]
        PosOrder = request.env["pos.order"]
        orders = PosOrder.search_read(
            domain=domain,
            fields=[
                "id",
                "name",
                "pos_reference",
                "partner_id",
                "date_order",
                "state",
                "amount_total",
            ],
            order="date_order asc",
        )

        return request.make_json_response(
            {
                "success": True,
                "count": len(orders),
                "user_timezone": str(user_tz),
                "orders": orders,
            }
        )

    # Api (task2)
    @http.route(
        "/api/products/rop",
        type="http",
        auth="user",
        methods=["GET"],
        csrf=False,
    )
    def get_products_rop(self, limit=80, page=1, **kwargs):
        domain = [("rop_count", ">", 0)]
        # Calculate pagination parameters
        try:
            limit = int(limit)
            page = max(1, int(page))
            offset = (page - 1) * limit
        except ValueError:
            limit, offset, page = 80, 0, 1

        ProductTemplate = request.env["product.template"]
        total_count = ProductTemplate.search_count(domain)

        products = ProductTemplate.search_read(
            domain=domain,
            fields=[
                "id",
                "name",
                "default_code",
                "has_rop",
                "rop_count",
                "qty_available",
            ],
            offset=offset,
            limit=limit,
            order="name asc",
        )
        payload = {
            "success": True,
            "count": len(products),
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "products": products,
        }
        return request.make_json_response(payload)
