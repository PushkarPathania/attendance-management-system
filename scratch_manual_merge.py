"""
Manual merge for remaining orphan teachers whose names didn't auto-match.
Maps real-email orphans to their @example.com counterparts by inspecting the data.
"""
from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin
import uuid

# Manual mapping: orphan email -> active teacher email (the @example.com one that has assignments)
# Built by cross-referencing the original data with the orphan list
MANUAL_MAP = {
    # Orphan (real email) -> Active teacher (example email) that has their assignments
    "pawanchandel13@gmail.com": "pawan@example.com",           # Pawan Chandel -> Pawan
    "sachin.sehota@gmail.com": None,                           # No match in assignments
    "nareshkumarspch@gmail.com": None,                         # No match
    "mohanpathania6747@gmail.com": None,                       # No match
    "jagdeep9906@gmail.com": "jagdeep@example.com",            # Jagdeep Singh -> Jagdeep
    "talvinder.m@gmail.com": "talvinder@example.com",          # Talvinder Singh -> Talvinder
    "karansingh.thakur89@gmail.com": "karan@example.com",      # Karan Singh Thakur -> Karan
    "satbirsuru@gmail.com": "satbir@example.com",              # Satbir Singh -> Satbir
    "pritam777018@gmail.com": None,                            # No match
    "nareshshkumarsapehia@gmail.com": "nksapeha@example.com",  # N.K. Sapehia -> NK Sapeha
    "Er.tamanna14@gmail.com": "tamanna@example.com",           # Tamanna Chitra -> Tamanna
    "bhupenderkumar@gmail.com": None,                          # No match
    "Dineshsingh744@gmail.com": "dineshmohas@example.com",     # Dinesh Minhas -> Dinesh Mohas
    "adityasaklani@gmail.com": "aditya@example.com",           # Aditya Saklani -> Aditya
    "sanjeevnaryal@gmail.com": "sanjeevkumar@example.com",     # Sanjeev Naryal -> Sanjeev Kumar
    "Ishwardas15051968@gmail.com": None,                       # No match
    "Pawankumar64399@gmail.com": None,                         # Different Pawan? Skip
    "Varinderkumar723@gmail.com": None,                        # No match
    "Shiyambhatia2003@gmail.com": "shivam@example.com",        # Shivam Bhatia -> Shivam
    "Thakurmanish993@gmail.com": "manish@example.com",         # Manish Thakur -> Manish
}

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    merged = 0
    for orphan_email, active_email in MANUAL_MAP.items():
        if not active_email:
            continue

        # Find orphan teacher record
        orphans = sb.table("teachers").select("*").ilike("email", orphan_email).execute().data or []
        if not orphans:
            print(f"SKIP: Orphan not found: {orphan_email}")
            continue
        orphan = orphans[0]

        # Find active teacher record (the @example.com one)
        actives = sb.table("teachers").select("*").ilike("email", active_email).execute().data or []
        if not actives:
            print(f"SKIP: Active not found: {active_email}")
            continue
        active = actives[0]

        print(f"Merging: '{orphan['full_name']}' ({orphan_email}) <- assignments from '{active['full_name']}' ({active_email})")

        # 1. Give the orphan a teacher_code if missing
        if not orphan.get("teacher_code"):
            tc = "TC_" + uuid.uuid4().hex[:6].upper()
            sb.table("teachers").update({"teacher_code": tc}).eq("id", orphan["id"]).execute()

        # 2. Reassign all assignments
        sb.table("teacher_assignments").update({"teacher_id": orphan["id"]}).eq("teacher_id", active["id"]).execute()

        # 3. Delete the @example.com teacher
        sb.table("teachers").delete().eq("id", active["id"]).execute()

        # 4. Delete the @example.com profile and auth user
        example_profiles = sb.table("profiles").select("id").eq("email", active_email).execute().data or []
        for ep in example_profiles:
            try:
                sb.auth.admin.delete_user(ep["id"])
            except Exception:
                pass
            sb.table("profiles").delete().eq("id", ep["id"]).execute()

        merged += 1

    print(f"\nManually merged: {merged}")

    # Final stats
    teachers = sb.table("teachers").select("id").execute().data or []
    assignments = sb.table("teacher_assignments").select("teacher_id").execute().data or []
    ids_with = set(a["teacher_id"] for a in assignments)
    orphans_remaining = [t for t in teachers if t["id"] not in ids_with]
    print(f"After cleanup: {len(teachers)} teachers, {len(orphans_remaining)} orphans remaining")
