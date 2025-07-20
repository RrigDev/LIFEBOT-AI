from supabase import create_client

url = "https://zphpikwyhjeybysfpcfn.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpwaHBpa3d5aGpleWJ5c2ZwY2ZuIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI0NjgwMTgsImV4cCI6MjA2ODA0NDAxOH0.2S0VxzExFvYj56BrrcS1dH9xfV9I2Tng_S8VJFrBrS4"

supabase = create_client(url, key)

response = supabase.table("meals").select("*").execute()
print(response)
