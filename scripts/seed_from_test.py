import argparse
import ast
import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from werkzeug.security import generate_password_hash

from app import (
    DEFAULT_USER_PASSWORD,
    app,
    ensure_class_tables,
    get_class_tables,
    mysql,
    resolve_class_tables,
)


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
            if not email or not branch or not semester:
                continue
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

    branches = []
    if dept in mapping:
        branches = [mapping[dept]]
    else:
        # For AS&H / common subjects (Physics, English, Chemistry, etc), apply to all branches
        branches = list(branch_semesters.keys())

    targets = []
    for branch in branches:
        semesters = branch_semesters.get(branch, set())
        for sem in semesters:
            targets.append((branch, sem))
    return targets


def _wipe_existing_data(cur):
    cur.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = DATABASE()
          AND (
            table_name LIKE 'students\\_%'
            OR table_name LIKE 'teachers\\_%'
            OR table_name LIKE 'attendance\\_%'
            OR table_name IN ('students', 'teachers', 'attendance', 'class_tables')
          )
        """
    )
    tables = [row[0] for row in cur.fetchall()]
    for table in tables:
        cur.execute(f"DROP TABLE IF EXISTS {table}")


def seed(test_file, mapping_file, wipe=False):
    teachers_data = _extract_list_from_file(test_file, "teachers_data")
    students_data = _extract_list_from_file(test_file, "students_data")
    teacher_mapping = _load_teacher_mapping(mapping_file)

    classes = {(branch, str(semester)) for _, _, _, branch, semester in students_data}
    for _, (branch, semester) in teacher_mapping.items():
        classes.add((branch, str(semester)))

    with app.app_context():
        cur = mysql.connection.cursor()
        if wipe:
            _wipe_existing_data(cur)
            mysql.connection.commit()

        for branch, semester in sorted(classes):
            ensure_class_tables(branch, semester)

        # Build branch -> semesters map for fallback teacher placement
        branch_semesters = {}
        for branch, semester in classes:
            branch_semesters.setdefault(branch, set()).add(str(semester))

        default_pwd = generate_password_hash(DEFAULT_USER_PASSWORD)

        # Seed students
        for name, email, roll_num, branch, semester in students_data:
            class_row = resolve_class_tables(branch, semester)
            if not class_row:
                continue
            students_table = class_row["students_table"]
            cur.execute(
                f"SELECT id FROM {students_table} WHERE email = %s OR board_roll_no = %s",
                (email, roll_num),
            )
            if cur.fetchone():
                continue
            cur.execute(
                f"""INSERT INTO {students_table}
                    (full_name, email, board_roll_no, branch, semester, password)
                    VALUES (%s, %s, %s, %s, %s, %s)""",
                (name, email, roll_num, branch, str(semester), default_pwd),
            )

        # Seed teachers
        for name, email, department, subject in teachers_data:
            teacher_email = (email or "").lower()
            targets = []
            mapping = teacher_mapping.get(teacher_email)
            if mapping:
                targets = [mapping]
            else:
                targets = _infer_teacher_targets(department, branch_semesters)

            for branch, semester in targets:
                class_row = resolve_class_tables(branch, semester)
                if not class_row:
                    continue
                teachers_table = class_row["teachers_table"]
                cur.execute(
                    f"SELECT id FROM {teachers_table} WHERE email = %s",
                    (teacher_email,),
                )
                if cur.fetchone():
                    continue
                cur.execute(
                    f"""INSERT INTO {teachers_table}
                        (full_name, email, mobile, teacher_id, branch, semester, subject, designation, gender, dob, password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (name, teacher_email, None, None, branch, str(semester), subject, department, None, None, default_pwd),
                )

        mysql.connection.commit()
        cur.close()


def main():
    parser = argparse.ArgumentParser(description="Seed MySQL tables from test.py data.")
    parser.add_argument("--test-file", default=r"C:\Users\HP\Desktop\test.py", help="Path to test.py")
    parser.add_argument("--teacher-map", default="data/teacher_assignments.csv", help="CSV with columns: email,branch,semester")
    parser.add_argument("--wipe", action="store_true", help="Drop existing per-branch tables before seeding")
    args = parser.parse_args()

    seed(args.test_file, args.teacher_map, wipe=args.wipe)


if __name__ == "__main__":
    main()
