from __future__ import annotations

from django.contrib import admin
from django.urls import path
from ninja import NinjaAPI
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.routers.blacklist import blacklist_router
from ninja_jwt.routers.obtain import obtain_pair_router
from ninja_jwt.routers.verify import verify_router

from apps.ai_profiler.api import profiler_router
from apps.authentication.api import auth_router
from apps.common.api import health_router
from apps.common.api_uploads import uploads_router
from apps.common.exceptions import AppError
from apps.common.schemas import ErrorOut
from config.api_description import API_DESCRIPTION
from config.redoc_view import redoc_view
from apps.compliance.api import compliance_router
from apps.feed.api import feed_router
from apps.funds.api import funds_router
from apps.funds.api_playlists import playlists_router
from apps.investments.api_goals import goals_router
from apps.investments.api_investments import investments_router
from apps.investments.api_plans import plans_router
from apps.investments.api_portfolio import portfolio_router
from apps.kyc.api import kyc_router
from apps.market_data.api import market_router
from apps.notifications.api import notifications_router
from apps.payments.api_callbacks import callbacks_router
from apps.payments.api_payments import payments_router
from apps.payments.api_wallet import wallet_router
from apps.payments.api_withdrawals import withdrawals_router
from apps.pools.api import pools_router
from apps.referrals.api import referrals_router
from apps.simulation.api import simulation_router
from apps.users.api import users_router
from apps.wishlist.api import wishlist_router

api = NinjaAPI(
    title="Belong API",
    version="1.0.0",
    auth=JWTAuth(),
    description=API_DESCRIPTION,
)

api.add_router("/health", health_router, tags=["health"])
api.add_router("/users", users_router, tags=["users"])
api.add_router("/auth", auth_router, tags=["auth"])
api.add_router("/funds", funds_router, tags=["funds"])
api.add_router("/market", market_router, tags=["market"])
api.add_router("/investments", investments_router, tags=["investments"])
api.add_router("/portfolio", portfolio_router, tags=["portfolio"])
api.add_router("/payments", payments_router, tags=["payments"])
api.add_router("/callbacks", callbacks_router, tags=["callbacks"])
api.add_router("/withdrawals", withdrawals_router, tags=["withdrawals"])
api.add_router("/simulation", simulation_router, tags=["simulation"])
api.add_router("/wishlist", wishlist_router, tags=["wishlist"])
api.add_router("/notifications", notifications_router, tags=["notifications"])
api.add_router("/feed", feed_router, tags=["feed"])
api.add_router("/kyc", kyc_router, tags=["kyc"])
api.add_router("/pools", pools_router, tags=["pools"])
api.add_router("/recurring-plans", plans_router, tags=["recurring-plans"])
api.add_router("/investment-goals", goals_router, tags=["investment-goals"])
api.add_router("/wallet", wallet_router, tags=["wallet"])
api.add_router("/ai-profiler", profiler_router, tags=["ai-profiler"])
api.add_router("/playlists", playlists_router, tags=["playlists"])
api.add_router("/referrals", referrals_router, tags=["referrals"])
api.add_router("/compliance", compliance_router, tags=["compliance"])
api.add_router("/uploads", uploads_router, tags=["uploads"])


@api.exception_handler(AppError)
def handle_app_error(request, exc: AppError):
    return api.create_response(
        request,
        ErrorOut(
            error={"code": exc.code, "message": str(exc), "details": exc.details}
        ).dict(),
        status=exc.status_code,
    )


api.add_router("/token", obtain_pair_router, tags=["token"])
api.add_router("/token", verify_router, tags=["token"])
api.add_router("/token", blacklist_router, tags=["token"])

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("api/redoc/", redoc_view),
]
