#!/usr/bin/env python3
"""
Add missing department column to profiles table
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

def add_department_column():
    """Add department column to profiles table"""
    from supabase_app import create_app
    from supabase_app.supabase_client import get_supabase_admin
    
    app = create_app()
    
    with app.app_context():
        sb = get_supabase_admin()
        
        print("Adding 'department' column to profiles table...")
        
        try:
            # Try to add the column
            # Since the Supabase Python client doesn't support ALTER TABLE directly,
            # we'll need to use the raw SQL execution via the service role key
            
            from supabase import create_client
            import postgrest
            
            # Get service role key for admin access
            url = sb.config.url
            service_role_key = sb.config.headers.get('Authorization', '').replace('Bearer ', '')
            
            # Use raw PostgreSQL connection approach - actually we'll try using
            # the Supabase API with a workaround
            
            # First, let's check if we can read a profile and see column structure
            profiles = sb.table("profiles").select("*").limit(1).execute()
            if profiles.data and 'department' not in profiles.data[0]:
                print("✓ Confirmed: 'department' column is missing")
                print("\nTo fix this, run this SQL in Supabase SQL Editor:")
                print("""
ALTER TABLE public.profiles 
ADD COLUMN IF NOT EXISTS department TEXT;
                """)
                return False
            elif profiles.data and 'department' in profiles.data[0]:
                print("✓ 'department' column already exists in profiles table!")
                return True
            
        except Exception as e:
            print(f"Error: {e}")
            return False

if __name__ == "__main__":
    success = add_department_column()
    sys.exit(0 if success else 1)
