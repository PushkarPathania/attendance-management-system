import os
import re
from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin
import uuid

raw_data = """
Branch: Computer Engineering
2nd Sem
Subject	Teacher
Mathematics-II	Sh. Kamesh Chand
Applied Physics-II	Sh. Saroop Chand
Intro to IT	Sh. Surbhi Sharma (NWL)
FEEE	Sh. Varun
Engineering Mechanics	Er. Prag Sharma
Environmental Science	Sh. Anil Kumar
IT Lab / EM Lab	Surbhi Sharma / Prag Sharma
SCA	Saroop Chand

4th Sem
Subject	Teacher
DBMS	Er. Rajeev Kumar
DSA	NK Sapeha
PE-I	Er. Tamanna
PE-II	Ashima L-8
EIKT	Er. Ashima Sharma
Minor Project	Er. Rajeev (G1) / Er. Tamanna (G2)
SCA	Yashwant Singh

6th Sem
Subject	Teacher
E&SU	Talvinder L-8
SL	Avinash L-8
OE-III	Er. Tamanna
OE-II	Surbhi L-8
IC	Talvinder L-8
SL Lab (G3)	AVS (As. BS) New Lab
SL DCS	Avinash L-8
Major Project	Er. Surbhi / Er. Talvinder (G2) / Dinesh Mohas (G3)
Seminar	NS(G1) SS(G2) AVS(G3)
SCA	Yashwant Singh

Branch: Electrical Engineering
2nd Sem
Subject	Teacher
Mathematics-II	Smt. Reema Choudhary
Applied Physics-II	Smt. Kumari Indu
Intro to IT	Er. Rajeev / Er. Tamanna
FEEE	Er. Aditya
Engineering Mechanics	Er. Pawan / Er. Sarbei
Environmental Science	Sh. Anil Kumar
EM Lab / IT Lab	Tamanna (As. DM) CC-II / Varun
SCA	Sh. Anil Kumar

4th Sem
Subject	Teacher
IS&SEM	Er. Aditya TC-1
BM&MHPP	Er. Sudhir TC-1
EPT&D	Er. R Sharma TC-1
EIKT	Er. Richa TC-1
FPE	Er. Aditya TC-1
Minor Project (G1 & G2)	Iela Bharti / Ina Gupta
SCA	Er. Aditya

6th Sem
Subject	Teacher
PP&C	Ina Gupta TC-1
BE	Sudhir TC-1
E&SU	Iela Bharti L-4
IT&M	Iela Bharti L-4
IC	Richa TC-1
SEMINAR	Ina Gupta
Major Project (G1 & G2)	Sudhir Dhiman / R Sharma
SCA	Shivam

Branch: ECE
2nd Sem
Subject	Teacher
Mathematics-II	Dr. Kamlesh Chand
Applied Physics-II	Smt. Vijay Thakur
FEEE	Ina L-5
EM	Varun L-5
EVS	Anil L-5
IT Lab (G1) / EM Lab (G2)	Ina Gupta / TS (As. BS) CC-II / Vijay
SCA	Smt. Vijay Thakur

4th Sem
Subject	Teacher
M&A	Dr. Nishant TC-2
CE	HS Thakur TC-2
DCS	Anil TC-2
BMI	Rohit TC-2
IE	Jagdeep TC-2
Minor Project	Anil (Asst. Jaswinder G1) / Rohit (Asst. Sanjeev G2)
SCA	Jaswinder Kumar

6th Sem
Subject	Teacher
CNDC	Anil L-4
E&SU	Rohit L-4
OE-III	Jagdeep TC-2
OE-II	Nishant TC-2
IC	HS Thakur TC-2
Major Project	Nishant Kaushal (As. Sanjeev G1) / HS Thakur (As. JK)
CNDC Lab / CNDC DCS	Anil Kumar
SCA	Sanjeev Kumar

Branch: Instrumentation Engineering
2nd Sem
Subject	Teacher
Mathematics-II	Smt. Reema Choudhary
Applied Physics-II	Smt. Kumari Indu
EWS	Workshop Staff
FEEE	Iela L-2
EM	Pawan L-2
Environmental Science	Sh. Anil Kumar
SCA	Kumari Indu

4th Sem
Subject	Teacher
PC-I	Karan EH
CS	Vikal EH
PE-I	Munish EH
EIKT	Richa EH
Minor Project (PC & MI Lab)	Ritika / Munish
SCA	Er. Vikal Sharma

6th Sem
Subject	Teacher
LC&DCS	Pawan TC-6
OE-II	Ritika TC-6
AULA	Karan TC-6
E&SU	Vikal TC-6
IC	Richa TC-6
SEMINAR	Munish TC-6
Major Project (PC & I Lab)	Pawan / Vikal / Ritika
SCA	Er. Munish Kumar

Branch: Mechanical Engineering
2nd Sem
Subject	Teacher
Mathematics-II	Smt. Reema Choudhary
FEEE	Ina L-3
EVS	Anil L-3
EWS	Workshop Staff
EM	Satbir L-3
Environmental Science	Sh. Anil Kumar
SCA	Smt. Reema Choudhary

4th Sem
Subject	Teacher
PE-II (PPE)	Satbir NDH
PE-I (AE)	Santosh NDH
SOM	Prag NDH
TE-II	Subhash L-3
CADM Practice	Onkar Singh / Subhash Chand
EIKT	Richu NDH
Minor Project	Onkar / Satbir / NC Kaul / AK / VRK / SB
SCA	N.C. Kaul

6th Sem
Subject	Teacher
CAD/CAM Lab	Subhash Chand / Vikas Kandoria
WT	Amandeep NDH
DoME	Onkar NDH
OE-II	Santosh NDH
IC	Richa NDH
E&SU	Prag L-2
SEMINAR	Satbir
Major Project	Amandeep / Santosh / Pawan / Vikas / Sanjay / Manish
SCA	N.C. Kaul
"""

# Map raw branch names from data -> normalized branch names used in students table
BRANCH_MAP = {
    "Computer Engineering": "Computer Science",
    "Electrical Engineering": "Electrical",
    "ECE": "Electronics",
    "Instrumentation Engineering": "Instrumentation",
    "Mechanical Engineering": "Mechanical",
}

def clean_teacher_name(name):
    # Remove titles
    name = re.sub(r'^(Dr\.|Er\.|Sh\.|Smt\.|Mr\.|Mrs\.|Ms\.)\s+', '', name, flags=re.IGNORECASE)
    # Remove things in parentheses
    name = re.sub(r'\(.*?\)', '', name)
    # Remove trailing room/lab numbers like "L-8", "TC-1", "EH", "NDH", "New Lab"
    name = re.sub(r'\b(L-\d+|TC-\d+|EH|NDH|New Lab|CC-II)\b', '', name)
    return name.strip()

def split_teachers(raw_teacher_str):
    teachers = []
    for part in raw_teacher_str.split('/'):
        part = part.strip()
        if not part: continue
        cleaned = clean_teacher_name(part)
        if cleaned:
            teachers.append(cleaned)
    return teachers

def parse_data():
    assignments = []
    current_branch = None
    current_sem = None
    
    for line in raw_data.strip().split('\n'):
        line = line.strip()
        if not line: continue
        
        if line.startswith('Branch:'):
            raw_branch = line.split(':')[1].strip()
            current_branch = BRANCH_MAP.get(raw_branch, raw_branch)
        elif line.endswith('Sem'):
            current_sem = int(line[0])
        elif line.startswith('Subject'):
            continue
        else:
            if '\t' in line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    subject = parts[0].strip()
                    teachers_raw = parts[1].strip()
                    teacher_names = split_teachers(teachers_raw)
                    for t in teacher_names:
                        assignments.append({
                            'branch': current_branch,
                            'semester': current_sem,
                            'subject': subject,
                            'teacher_name': t
                        })
    return assignments

def generate_email(name):
    clean = re.sub(r'[^a-zA-Z0-9]', '', name.lower())
    if not clean:
        clean = "teacher"
    return f"{clean}@example.com"

def run_migration():
    app = create_app()
    with app.app_context():
        sb = get_supabase_admin()
        
        # 1. Fetch current teachers and profiles
        print("Fetching current data...")
        profiles_res = sb.table("profiles").select("*").eq("role", "teacher").execute().data or []
        teachers_res = sb.table("teachers").select("*").execute().data or []
        
        # Build mapping of lowercase name -> profile_id and teacher_id
        # Also clean up duplicates
        
        name_to_profile = {}
        name_to_teacher = {}
        
        # Map profiles by name
        for p in profiles_res:
            name_key = clean_teacher_name(p['full_name']).lower()
            if name_key not in name_to_profile:
                name_to_profile[name_key] = p
            else:
                # It's a duplicate profile, delete it later
                pass
                
        # Map teachers by name
        for t in teachers_res:
            name_key = clean_teacher_name(t['full_name']).lower()
            if name_key not in name_to_teacher:
                name_to_teacher[name_key] = t
            else:
                pass
                
        # Parse new assignments
        new_assignments = parse_data()
        all_new_names = set(a['teacher_name'] for a in new_assignments)
        
        print(f"Found {len(all_new_names)} unique teachers in the new data.")
        
        # 2. Ensure all teachers in new data exist, create if not
        for name in all_new_names:
            name_key = name.lower()
            
            if name_key not in name_to_profile:
                email = generate_email(name)
                # Ensure email uniqueness
                while any(p['email'] == email for p in name_to_profile.values()):
                    email = "1" + email
                    
                print(f"Creating Auth User for: {name} ({email})")
                try:
                    user = sb.auth.admin.create_user({
                        "email": email,
                        "password": "ChangeMe@123",
                        "email_confirm": True,
                        "user_metadata": {"role": "teacher"}
                    })
                    uid = user.user.id
                except Exception as e:
                    print(f"Failed to create auth user {email}: {e}")
                    # Try to fetch existing user
                    continue
                    
                sb.table("profiles").insert({
                    "id": uid,
                    "full_name": name,
                    "email": email,
                    "role": "teacher"
                }).execute()
                
                name_to_profile[name_key] = {
                    "id": uid,
                    "full_name": name,
                    "email": email
                }
                
            if name_key not in name_to_teacher:
                prof = name_to_profile[name_key]
                print(f"Creating Teacher Record for: {name}")
                t_code = "TC_" + uuid.uuid4().hex[:6].upper()
                res = sb.table("teachers").insert({
                    "full_name": name,
                    "email": prof["email"],
                    "department": "General",
                    "teacher_code": t_code
                }).execute()
                name_to_teacher[name_key] = res.data[0]
                
        # 3. Clean up duplicates in database (keep only one per name)
        print("Cleaning up duplicates...")
        # Actually, let's just delete all teacher assignments first
        sb.table("teacher_assignments").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        
        # For duplicates, we delete the ones not in name_to_teacher / name_to_profile
        keep_teacher_ids = [t['id'] for t in name_to_teacher.values()]
        for t in teachers_res:
            if t['id'] not in keep_teacher_ids:
                sb.table("teachers").delete().eq("id", t['id']).execute()
                
        # 4. Insert new assignments
        print("Inserting new assignments...")
        for a in new_assignments:
            name_key = a['teacher_name'].lower()
            if name_key in name_to_teacher:
                t_id = name_to_teacher[name_key]['id']
                sb.table("teacher_assignments").insert({
                    "teacher_id": t_id,
                    "branch": a['branch'],
                    "semester": a['semester'],
                    "subject_name": a['subject'],
                    "subject_code": a['subject'][:20],
                    "department": "General"
                }).execute()
                
        print("Done!")

if __name__ == '__main__':
    run_migration()
