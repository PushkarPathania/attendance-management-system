"""
Cleanup script: Merge orphan teachers (with real emails) into the active teachers (with assignments).
The issue: old teacher records have real gmail emails, new ones have @example.com.
When a teacher logs in with gmail, it finds the OLD record with no assignments.
Fix: reassign the assignments from the @example.com teacher to the real-email teacher,
then delete the @example.com teacher.
"""
from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin
import uuid

def normalize_name(name):
    """Normalize a teacher name for fuzzy matching."""
    import re
    name = name.lower().strip()
    # Remove titles
    name = re.sub(r'^(dr\.|er\.|sh\.|smt\.|mr\.|mrs\.|ms\.)\s+', '', name)
    # Remove extra spaces
    name = re.sub(r'\s+', ' ', name)
    return name

app = create_app()
with app.app_context():
    sb = get_supabase_admin()

    teachers = sb.table("teachers").select("*").execute().data or []
    assignments = sb.table("teacher_assignments").select("*").execute().data or []

    teacher_ids_with_assignments = set(a["teacher_id"] for a in assignments)

    # Split into orphans (no assignments, real emails) and active (have assignments, @example.com)
    orphans = [t for t in teachers if t["id"] not in teacher_ids_with_assignments]
    active = [t for t in teachers if t["id"] in teacher_ids_with_assignments]

    print(f"Orphans: {len(orphans)}, Active (with assignments): {len(active)}")

    # Build name-based mapping for active teachers
    active_by_name = {}
    for t in active:
        key = normalize_name(t["full_name"])
        active_by_name[key] = t

    # For each orphan, try to find a matching active teacher by name
    merged = 0
    unmatched_orphans = []
    
    for orphan in orphans:
        orphan_name_key = normalize_name(orphan["full_name"])
        
        # Try exact name match
        match = active_by_name.get(orphan_name_key)
        
        # Try partial matches (e.g., "Rajesh Sharma" matching "R Sharma")
        if not match:
            # Try last name match
            orphan_parts = orphan_name_key.split()
            if len(orphan_parts) >= 2:
                last_name = orphan_parts[-1]
                first_initial = orphan_parts[0][0] if orphan_parts[0] else ""
                for key, act in active_by_name.items():
                    act_parts = key.split()
                    if len(act_parts) >= 2 and act_parts[-1] == last_name:
                        # Same last name — check first initial
                        if act_parts[0][0] == first_initial:
                            match = act
                            break
                    elif len(act_parts) == 1 and act_parts[0] == last_name:
                        # Active has only last name
                        match = act
                        break
        
        if match:
            old_teacher_id = match["id"]  # the @example.com one
            real_email = orphan["email"]   # the real gmail
            real_teacher_id = orphan["id"]
            
            print(f"\nMerging: '{orphan['full_name']}' ({real_email})")
            print(f"  -> Reassigning {sum(1 for a in assignments if a['teacher_id'] == old_teacher_id)} assignments from {match['email']} to {real_email}")
            
            # 1. Update the orphan teacher record with a unique teacher_code if it's None
            if not orphan.get("teacher_code"):
                tc = "TC_" + uuid.uuid4().hex[:6].upper()
                sb.table("teachers").update({"teacher_code": tc}).eq("id", real_teacher_id).execute()
            
            # 2. Reassign all assignments from the @example.com teacher to the real-email teacher
            for a in assignments:
                if a["teacher_id"] == old_teacher_id:
                    sb.table("teacher_assignments").update({"teacher_id": real_teacher_id}).eq("id", a["id"]).execute()
            
            # 3. Delete the @example.com teacher record
            sb.table("teachers").delete().eq("id", old_teacher_id).execute()
            
            # 4. Delete the @example.com profile and auth user
            example_profiles = sb.table("profiles").select("id").eq("email", match["email"]).execute().data or []
            for ep in example_profiles:
                try:
                    sb.auth.admin.delete_user(ep["id"])
                except Exception:
                    pass
                sb.table("profiles").delete().eq("id", ep["id"]).execute()
            
            merged += 1
        else:
            unmatched_orphans.append(orphan)

    print(f"\n=== SUMMARY ===")
    print(f"Merged: {merged}")
    print(f"Unmatched orphans remaining: {len(unmatched_orphans)}")
    for u in unmatched_orphans:
        print(f"  - {u['full_name']} ({u['email']})")

    # Final check
    teachers_after = sb.table("teachers").select("id").execute().data or []
    assignments_after = sb.table("teacher_assignments").select("teacher_id").execute().data or []
    ids_with = set(a["teacher_id"] for a in assignments_after)
    orphans_after = [t for t in teachers_after if t["id"] not in ids_with]
    print(f"\nAfter cleanup: {len(teachers_after)} teachers, {len(orphans_after)} orphans")
