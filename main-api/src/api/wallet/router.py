import asyncio

from fastapi import APIRouter, status

from domain.rewards.schemas import RewardFiltersSchema
from domain.wallet.exceptions import (
    WalletNotFound,
    CouldNotCreateInvoice,
    CouldNotPayInvoice,
    InsufficientFunds
)
from domain.wallet.schemas import LightningTransactionSchema
from infrastructure.lnbits.exceptions import (
    WalletCreationFailure,
    InvoiceIsAlreadyPaid
)

from .schemas import (
    DepositResponseSchema,
    DepositRequestSchema,
    WithdrawResponseSchema,
    WithdrawRequestSchema,
    WalletDetailResponse
)
from ..dependencies.types import (
    GetAuthenticatedUserDep,
    WalletServiceDep,
    PaginationDep, RewardServiceDep
)
from ..exceptions.http import (
    ServerErrorException,
    NotFoundException,
    BadRequestException
)
from ..exceptions.schemas import HTTPExceptionDetailSchema


router = APIRouter(tags=["Wallets"])


@router.get(
    "/",
    response_model=WalletDetailResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionDetailSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionDetailSchema}
    }
)
async def get_my_wallet(
    user: GetAuthenticatedUserDep,
    wallet_service: WalletServiceDep,
    reward_service: RewardServiceDep
):
    """
    Fetches the wallet details of the user authorized.
    Creates a new wallet if no wallet found.

    Throws
    - **401** if the user is not authorized.
    - **500** if there was an error fetching / creating the wallet.
    """
    try:
        wallet_details, reserved_sats = await asyncio.gather(
            wallet_service.get_or_create_wallet(user_id=user.id),
            reward_service.get_total_reward(
                RewardFiltersSchema(
                    rewarder_id=user.id,
                    is_closed=False
                )
            )
        )

        return WalletDetailResponse(
            user_id=user.id,
            free_sats=int(wallet_details.total_sats),  # temp workaround
            in_rewards=reserved_sats
        )
    except WalletCreationFailure as wallet_creation_failure:
        raise ServerErrorException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(
                wallet_creation_failure
            )
        )
    except WalletNotFound as wallet_not_found:
        raise ServerErrorException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(
                wallet_not_found
            )
        )


@router.post(
    "/deposit",
    response_model=DepositResponseSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionDetailSchema},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionDetailSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionDetailSchema}
    }
)
async def deposit_sats(
    body: DepositRequestSchema,
    user: GetAuthenticatedUserDep,
    wallet_service: WalletServiceDep
):
    """
    Creates an incoming invoice to the wallet of the user authorized.

    Throws
    - **401** if the user is not authorized.
    - **404** if the user's wallet not found.
    - **500** if there was en error making the invoice.
    """
    try:
        data = await wallet_service.create_incoming_invoice(
                wallet_owner_id=user.id,
                amount_sats=body.amount_sats
        )
        return DepositResponseSchema(
            invoice=data.invoice,
            checking_id=data.checking_id
        )
    except WalletNotFound as wallet_not_found:
        raise NotFoundException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(wallet_not_found)
        )
    except CouldNotCreateInvoice as could_not_create_invoice:
        raise ServerErrorException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(could_not_create_invoice)
        )


@router.post(
    "/withdraw",
    response_model=WithdrawResponseSchema,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionDetailSchema},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionDetailSchema},
        status.HTTP_400_BAD_REQUEST: {"model": HTTPExceptionDetailSchema},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": HTTPExceptionDetailSchema}
    }
)
async def withdraw_sats(
    body: WithdrawRequestSchema,
    user: GetAuthenticatedUserDep,
    wallet_service: WalletServiceDep
):
    """
    Pays the invoice passed from the authorized user's wallet.

    Throws
    - **400** if there's not enough funds to pay the invoice or the invoice has been already paid.
    - **401** if the user is not authorized.
    - **404** if the user's wallet not found.
    - **500** if there was en error paying the invoice.
    """
    try:
        await wallet_service.pay_invoice(
            payer_id=user.id,
            invoice=body.invoice
        )
    except WalletNotFound as wallet_not_found:
        raise NotFoundException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(wallet_not_found)
        )
    except InsufficientFunds as insufficient_funds:
        raise BadRequestException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(insufficient_funds)
        )
    except InvoiceIsAlreadyPaid as invoice_is_already_paid:
        raise BadRequestException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(invoice_is_already_paid)
        )
    except CouldNotPayInvoice as could_not_pay_invoice:
        raise ServerErrorException(
            detail=HTTPExceptionDetailSchema.from_standard_exception(could_not_pay_invoice)
        )

    return WithdrawResponseSchema(
        success=True
    )


@router.get(
    "/history",
    response_model=list[LightningTransactionSchema],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": HTTPExceptionDetailSchema},
        status.HTTP_404_NOT_FOUND: {"model": HTTPExceptionDetailSchema}
    }
)
async def get_wallet_history(
    user: GetAuthenticatedUserDep,
    wallet_service: WalletServiceDep,
    pagination: PaginationDep
):
    try:
        return await wallet_service.get_wallet_history(
            user_id=user.id,
            pagination=pagination
        )
    except WalletNotFound as wallet_not_found:
        raise NotFoundException(detail=HTTPExceptionDetailSchema.from_standard_exception(wallet_not_found))
