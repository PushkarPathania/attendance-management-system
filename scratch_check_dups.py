from supabase_app import create_app
from supabase_app.supabase_client import get_supabase_admin
import pandas as pd

app = create_app()
with app.app_context():
    sb = get_supabase_admin()
    teachers = sb.table("teachers").select("*").execute().data
    
    df = pd.DataFrame(teachers)
    print("Teachers by name count:")
    print(df['full_name'].value_counts()[df['full_name'].value_counts() > 1])

    print("\nTeacher Full View counts (what admin sees):")
    tfv = sb.table("teacher_full_view").select("full_name").execute().data
    df2 = pd.DataFrame(tfv)
    print(df2['full_name'].value_counts()[df2['full_name'].value_counts() > 1])
