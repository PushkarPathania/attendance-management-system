import argparse
import ast
import csv
import os
from pathlib import Path

from supabase import create_client


def _extract_list_from_file(file_path, var_name):
    source = Path(file_path).read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    return ast.literal_eval(node.value)
    raise ValueError(f"Could not find {var_name} in {file_path}")


def _load_teacher_mapping(mapping_path):
    mapping = {}
    path = Path(mapping_path)
    if not path.exists():
        return mapping
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = (row.get("email") or "").strip().lower()
            branch = (row.get("branch") or "").strip()
            semester = (row.get("semester") or "").strip()
            if email and branch and semester:
                mapping[email] = (branch, semester)
    return mapping


def _infer_teacher_targets(department, branch_semesters):
    dept = (department or "").strip().lower()
    mapping = {
        "cs": "Computer Science",
        "computer science": "Computer Science",
        "computer engineering": "Computer Science",
        "ece": "Electronics",
        "electronics": "Electronics",
        "electrical": "Electrical",
        "ee": "Electrical",
        "ie": "Instrumentation",
        "instrumentation": "Instrumentation",
        "me": "Mechanical",
        "mechanical": "Mechanical",
        "ce": "Civil Engineering",
        "civil": "Civil Engineering",
    }

    if dept in mapping:
        branches = [mapping[dept]]
    else:
        # Physics/Chemistry/English/common teachers can map to all active branches
        branches = list(branch_semesters.keys())

    targets = []
    for branch in branches:
        for sem in sorted(branch_semesters.get(branch, set())):
            targets.append((branch, sem))
    return targets


def _safe_auth_password():
    value = os.getenv("SEED_DEFAULT_PASSWORD", "ChangeMe@123")
    return value


def _get_existing_profile_id_by_email(supabase, email):
    res = supabase.table("profiles").select("id").eq("email", email).limit(1).execute()
    rows = res.data or []
    if rows:
        return rows[0]["id"]
    return None


def seed_to_supabase(test_file, mapping_file):
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_role_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required.")

    supabase = create_client(supabase_url, service_role_key)

    teachers_data = _extract_list_from_file(test_file, "teachers_data")
    students_data = _extract_list_from_file(test_file, "students_data")
    teacher_mapping = _load_teacher_mapping(mapping_file)

    classes = {(branch, str(semester)) for _, _, _, branch, semester in students_data}
    for _, (branch, semester) in teacher_mapping.items():
        classes.add((branch, str(semester)))

    branch_semesters = {}
    for branch, semester in classes:
        branch_semesters.setdefault(branch, set()).add(str(semester))

    # email -> auth user id
    auth_ids = {}

    # Seed students (Auth + profiles + students)
    for full_name, email, board_roll_no, branch, semester in students_data:
        email = (email or "").strip().lower()
        if not email:
            continue

        user_id = auth_ids.get(email)
        if not user_id:
            try:
                created = supabase.auth.admin.create_user(
                    {
                        "email": email,
                        "password": _safe_auth_password(),
                        "email_confirm": True,
                        "user_metadata": {"role": "student"},
                    }
                )
                user_id = created.user.id
            except Exception:
                user_id = _get_existing_profile_id_by_email(supabase, email)
                if not user_id:
                    continue
            auth_ids[email] = user_id

        supabase.table("profiles").upsert(
            {
                "id": user_id,
                "full_name": full_name,
                "email": email,
                "role": "student",
                "branch": branch,
                "semester": str(semester),
            }
        ).execute()

        supabase.table("students").upsert(
            {
                "profile_id": user_id,
                "board_roll_no": str(board_roll_no),
                "branch": branch,
                "semester": str(semester),
            },
            on_conflict="profile_id",
        ).execute()

    # Seed teachers (Auth + profiles + teachers)
    for full_name, email, department, subject in teachers_data:
        email = (email or "").strip().lower()
        if not email:
            continue

        if email in teacher_mapping:
            targets = [teacher_mapping[email]]
        else:
            targets = _infer_teacher_targets(department, branch_semesters)

        user_id = auth_ids.get(email)
        if not user_id:
            try:
                created = supabase.auth.admin.create_user(
                    {
                        "email": email,
                        "password": _safe_auth_password(),
                        "email_confirm": True,
                        "user_metadata": {"role": "teacher"},
                    }
                )
                user_id = created.user.id
            except Exception:
                user_id = _get_existing_profile_id_by_email(supabase, email)
                if not user_id:
                    continue
            auth_ids[email] = user_id

        # Keep one profile per teacher; branch/semester from first target
        default_branch, default_sem = targets[0] if targets else ("General", "1")
        supabase.table("profiles").upsert(
            {
                "id": user_id,
                "full_name": full_name,
                "email": email,
                "role": "teacher",
                "branch": default_branch,
                "semester": str(default_sem),
            }
        ).execute()

        # Insert teacher row per target branch+semester
        for branch, semester in targets:
            supabase.table("teachers").upsert(
                {
                    "profile_id": user_id,
                    "branch": branch,
                    "semester": str(semester),
                    "subject": subject,
                    "department": department,
                },
                on_conflict="profile_id,branch,semester",
            ).execute()


def main():
    parser = argparse.ArgumentParser(description="Seed Supabase from teachers_data/students_data python lists.")
    parser.add_argument("--test-file", default=r"C:\Users\HP\Desktop\test.py", help="Python file containing teachers_data and students_data")
    parser.add_argument("--teacher-map", default="data/teacher_assignments.csv", help="CSV columns: email,branch,semester")
    args = parser.parse_args()
    seed_to_supabase(args.test_file, args.teacher_map)


if __name__ == "__main__":
    main()
