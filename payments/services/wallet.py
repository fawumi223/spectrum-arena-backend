from payments.models import Wallet

def ensure_wallet_exists(user):
    """
    Idempotent wallet creator.
    Safe to call multiple times.
    """
    wallet, created = Wallet.objects.get_or_create(user=user)
    return wallet

