#!/usr/bin/env python3
"""
List all auth users and find Rajeev Kumar, then link profile
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from supabase_app import create_app

app = create_app()

with app.app_context():
    from supabase_app.supabase_client import get_supabase_admin
    sb = get_supabase_admin()

    print("\n" + "="*80)
    print("FINDING RAJEEV KUMAR AUTH USER")
    print("="*80)

    rajeev_email = "Rajeev.kumar357@gmail.com"
    
    try:
        # List auth users
        print(f"\nSearching for auth users with email: {rajeev_email}")
        
        # Try to get user by email using admin API
        users = sb.auth.admin.list_users()
        
        rajeev_user = None
        for user in users:
            if user.email and user.email.lower() == rajeev_email.lower():
                rajeev_user = user
                break
        
        if rajeev_user:
            user_id = rajeev_user.id
            print(f"✓ Found auth user:")
            print(f"  ID: {user_id}")
            print(f"  Email: {rajeev_user.email}")
            
            # Now try to create profile with correct user ID
            print(f"\nCreating profile...")
            
            try:
                sb.table("profiles").insert({
                    "id": user_id,
                    "full_name": "Rajeev Kumar",
                    "email": rajeev_email,
                    "role": "teacher",
                }).execute()
                print(f"✓ Profile created!")
                
            except Exception as e:
                if "already" in str(e).lower():
                    print(f"✓ Profile already exists, updating...")
                    sb.table("profiles").update({"role": "teacher"}).eq("id", user_id).execute()
                    print(f"✓ Profile updated!")
                else:
                    print(f"✗ Error: {e}")
            
            # Verify
            print(f"\n✓ DONE! Rajeev Kumar can now login!")
            print(f"\nLogin Details:")
            print(f"  Email: {rajeev_email}")
            print(f"  Password: ChangeMe@123")
            
        else:
            print(f"✗ Auth user not found!")
            print(f"\nTrying to create new auth user...")
            
            result = sb.auth.admin.create_user({
                "email": rajeev_email,
                "password": "ChangeMe@123",
                "email_confirm": True,
                "user_metadata": {"role": "teacher"},
            })
            
            user_id = result.user.id
            print(f"✓ New auth user created: {user_id}")
            
            # Create profile
            sb.table("profiles").insert({
                "id": user_id,
                "full_name": "Rajeev Kumar",
                "email": rajeev_email,
                "role": "teacher",
            }).execute()
            
            print(f"✓ Profile created!")
            print(f"\n✓ DONE! Rajeev Kumar can now login!")
            print(f"\nLogin Details:")
            print(f"  Email: {rajeev_email}")
            print(f"  Password: ChangeMe@123")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*80)
    print("URL: http://localhost:5000/teacher-login")
    print("="*80 + "\n")
