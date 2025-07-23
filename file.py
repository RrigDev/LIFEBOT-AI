from supabase import create_client, Client

# Your Supabase credentials
url = "https://zphpikwyhjeybysfpcfn.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpwaHBpa3d5aGpleWJ5c2ZwY2ZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0NjgwMTgsImV4cCI6MjA2ODA0NDAxOH0.2S0VxzExFvYj56BrrcS1dH9xfV9I2Tng_S8VJFrBrS4"

# Create Supabase client
supabase: Client = create_client(url, key)

# Replace 'test_table' with your actual table name
response = supabase.table("test_table").select("*").execute()
print(response)

