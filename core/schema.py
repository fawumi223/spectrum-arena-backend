from drf_spectacular.openapi import AutoSchema


class SpectacularAutoSchema(AutoSchema):
    """
    Enforces drf-spectacular schema compatibility
    across all API views (including GIS + generics).
    """
    pass

