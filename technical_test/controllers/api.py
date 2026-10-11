import zoneinfo
import json
from datetime import datetime, time, timedelta
from odoo import fields, http
from odoo.http import request


class TechnicalTestAPI(http.Controller):
    # Api - task1
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

    # Api - task2
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

    #Api -task3
    def _authenticate_api_key(self):
        """Authenticates request using an API Key passed in headers or params."""
        api_key = request.httprequest.headers.get("x-api-key") or request.params.get("api_key")
        if not api_key:
            return None
        try:
            user_id = request.env["res.users.apikeys"]._check_credentials(
                scope="rpc", key=api_key
            )
            if user_id:
                # Return authenticated user environment (Sudo or user env)
                return request.env["res.users"].browse(user_id)
        except Exception:
            pass

        return None

    @http.route(
        "/api/products/rop",
        type="http",
        auth="public",
        methods=["POST"],
        csrf=False,
    )
    def update_product_rop(self, **kwargs):
        user = self._authenticate_api_key()
        if not user:
            return request.make_json_response(
                {
                    "success": False,
                    "message": "Unauthorized: Invalid or missing API key.",
                },
                status=401,
            )

        try:
            data = json.loads(request.httprequest.data or "{}")
        except json.JSONDecodeError:
            return request.make_json_response(
                {
                    "success": False,
                    "message": "Invalid JSON payload.",
                },
                status=400,
            )

        product_id = data.get("product_id")
        rop_count = data.get("rop_count")
        if product_id is None or rop_count is None:
            return request.make_json_response(
                {
                    "success": False,
                    "message": "'product_id' and 'rop_count' are required fields.",
                },
                status=400,
            )

        try:
            product_id = int(product_id)
            rop_count = int(rop_count)
            if rop_count < 0:
                raise ValueError("ROP count cannot be negative.")
        except ValueError as e:
            return request.make_json_response(
                {
                    "success": False,
                    "message": f"Invalid data format: {str(e)}",
                },
                status=400,
            )

        ProductTemplate = request.env["product.template"].with_user(user)
        product = ProductTemplate.browse(product_id)
        if not product.exists():
            return request.make_json_response(
                {
                    "success": False,
                    "message": f"Product with ID {product_id} not found.",
                },
                status=404,
            )
        try:
            product.write({
                "rop_count": rop_count,
                "has_rop": rop_count > 0,
            })
        except Exception as e:
            return request.make_json_response(
                {
                    "success": False,
                    "message": f"Failed to update product ROP: {str(e)}",
                },
                status=500,
            )

        return request.make_json_response(
            {
                "success": True,
                "message": f"ROP count updated successfully for product {product.name}.",
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "default_code": product.default_code or "",
                    "has_rop": product.has_rop,
                    "rop_count": product.rop_count,
                    "qty_available": product.qty_available,
                },
            },
            status=200,
        )

    # API - Task 4
    @http.route(
        "/api/pos/sessions/<int:session_id>/orders",
        type="http",
        auth="user",
        methods=["GET"],
    )
    def get_session_orders(self, session_id, limit=80, page=1, **kwargs):
        limit = int(limit)
        page = int(page)
        PosSession = request.env["pos.session"]
        session = PosSession.browse(session_id).exists()
        if not session:
            return request.make_json_response(
                {
                    "success": False,
                    "count": 0,
                    "orders": [],
                    "message": "POS Session not found.",
                },
                status=404,
            )

        offset = (page - 1) * limit
        domain = [("session_id", "=", session.id)]
        PosOrder = request.env["pos.order"]
        total_count = PosOrder.search_count(domain)

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
                "session_id",
            ],
            offset=offset,
            limit=limit,
            order="date_order asc, id asc",
        )

        payload = {
            "success": True,
            "count": len(orders),
            "total_count": total_count,
            "page": page,
            "limit": limit,
            "session": {
                "id": session.id,
                "name": session.name,
                "state": session.state,
            },
            "orders": orders,
        }

        return request.make_json_response(payload)
