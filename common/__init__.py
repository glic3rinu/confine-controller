try:
    # psycopg2 needs us to register the uuid type
    import psycopg2.extras
    psycopg2.extras.register_uuid()
except (ImportError, AttributeError):
    pass
