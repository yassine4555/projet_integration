try:
    import supabase
    print(f"Supabase version: {supabase.__version__}")
    print(f"Supabase file: {supabase.__file__}")
    from supabase import create_client, Client, ClientOptions
    print("Successfully imported create_client, Client, ClientOptions")
except Exception as e:
    print(f"Error: {e}")
    import dir
    print(dir(supabase))
