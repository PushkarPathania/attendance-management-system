-- ============================================================
-- INSERT TEACHERS AND SUBJECT ASSIGNMENTS
-- RUN IN SUPABASE SQL EDITOR
-- Features: Safe inserts (skips existing teachers and subjects automatically)
-- ============================================================

-- -----------------------------------------------------------
-- 1. INSERT TEACHERS (Avoids overriding existing emails)
-- -----------------------------------------------------------
INSERT INTO public.teachers (full_name, email, mobile, designation, qualification, department, is_workshop_staff)
VALUES
  -- A) APPLIED SCIENCES & HUMANITIES
  ('Kamlesh Chand',     'Kchand78@gmail.com',            '9418040815', 'HOD',           'M.Phil.',       'Applied Sciences & Humanities', false),
  ('Saroop Chand',      'Saroop2388@gmail.com',           '7018395980', 'Sr. Lecturer',  'M.Sc.',         'Applied Sciences & Humanities', false),
  ('Richa Sharma',      'Richathakur121@gmail.com',       '9418025600', 'Lecturer',      'M.Phil.',       'Applied Sciences & Humanities', false),
  ('Kumari Indu',       'kumariindu@gmail.com',           null,         'Lecturer',      'M.Sc.',         'Applied Sciences & Humanities', false),
  ('Reema Choudhary',   'reemachoudhary@gmail.com',       null,         'Lecturer',      'M.Sc.',         'Applied Sciences & Humanities', false),
  ('Vijay Thakur',      'Thakurviju454@gmail.com',        '8091742032', 'Lecturer',      'M.Sc. Physics', 'Applied Sciences & Humanities', false),
  ('Anil Kumar',        'prashanil77@gmail.com',          '9459206071', 'Lecturer',      'M.Sc. Chemistry','Applied Sciences & Humanities',false),
  ('Pritam Chand',      'pritam777018@gmail.com',         '7018028051', 'Lecturer',      'M.Sc.',         'Applied Sciences & Humanities', false),
  
  -- B) COMPUTER ENGINEERING
  ('N.K. Sapehia',      'nareshshkumarsapehia@gmail.com', '9418479027', 'HOD',           'MCA',           'Computer Engineering', false),
  ('Talvinder Singh',   'Talvinder.mr@gmail.com',         '9418115042', 'Sr. Lecturer',  'M.Tech.',       'Computer Engineering', false),
  ('Surbhi Sharma',     'Surbhisharma.jmi@gmail.com',     '7380178778', 'Lecturer',      'B.Tech.',       'Computer Engineering', false),
  ('Avinash Sharma',    'Avinash.acet@yahoo.com',         '8091251140', 'Lecturer',      'M.Tech.',       'Computer Engineering', false),
  ('Rajeev Kumar',      'Rajeev.kumar357@gmail.com',      '9298286002', 'Lecturer',      'B.Tech.',       'Computer Engineering', false),
  ('Tamanna Chitra',    'Er.tamanna14@gmail.com',         '8894943678', 'Lecturer',      'B.Tech.',       'Computer Engineering', false),
  ('Aashima Sharma',    'aashimasharma@gmail.com',        null,         'Lecturer',      'B.Tech.',       'Computer Engineering', false),
  ('Bhupender Kumar',   'bhupenderkumar@gmail.com',       null,         'Computer Assistant','Diploma MCA','Computer Engineering', false),
  ('Shweta Dhiman',     'Shweta.neetu@gmail.com',         '9736319180', 'Computer Assistant','Diploma',    'Computer Engineering', false),
  ('Dinesh Minhas',     'Dineshsingh744@gmail.com',       '9531484149', 'Computer Assistant','MCA',        'Computer Engineering', false),

  -- C) ELECTRICAL ENGINEERING
  ('Rajesh Sharma',     'rdshan72@gmail.com',             '9418050231', 'HOD',           'B.Tech.',       'Electrical Engineering', false),
  ('Sudhir Dhiman',     'Sudhir.dhiman85@gmail.com',      '9459055519', 'Sr. Lecturer',  'M.Tech.',       'Electrical Engineering', false),
  ('Ina Gupta',         'Guptaina24@gmail.com',           '9418347063', 'Lecturer',      'M.Tech.',       'Electrical Engineering', false),
  ('Iela Bharti',       'jela.b89@gmail.com',             '9418347063', 'Lecturer',      'M.Tech.',       'Electrical Engineering', false),
  ('Aditya Saklani',    'adityasaklani@gmail.com',        null,         'Lecturer',      'M.Tech.',       'Electrical Engineering', false),

  -- D) ELECTRONICS & COMMUNICATION ENGINEERING
  ('Hari Singh Thakur', 'Hsthakur0928@gmail.com',         '9418360465', 'HOD',           'B.Tech.',       'Electronics & Communication Engineering', false),
  ('Jagdeep Singh',     'jagdeep9900@gmail.com',          '9816068262', 'Sr. Lecturer',  'B.Tech.',       'Electronics & Communication Engineering', false),
  ('Nishant Kaushal',   'nishant125@gmail.com',           '9459125376', 'Lecturer',      'M.Tech.',       'Electronics & Communication Engineering', false),
  ('Sachin Sehota',     'sachin.sehotas@gmail.com',       '7018395980', 'Lecturer',      'B.Tech.',       'Electronics & Communication Engineering', false),
  ('Rohit Kumar',       'Rohit06@gmail.com',              '9110402870', 'Lecturer',      'M.Tech.',       'Electronics & Communication Engineering', false),
  ('Jaswinder Kumar',   'Jaswinder70477@gmail.com',       '8219979429', 'Instructor',    'Diploma',       'Electronics & Communication Engineering', false),
  ('Sanjeev Naryal',    'sanjeevnaryal@gmail.com',        '8219298300', 'Instructor',    'CTI NCVT',      'Electronics & Communication Engineering', false),

  -- E) INSTRUMENTATION ENGINEERING
  ('Pawan Chandel',     'Pawanchandel13@gmail.com',       '9418636497', 'HOD',           'B.Tech. MBA',   'Instrumentation Engineering', false),
  ('Karan Singh Thakur','Karansingh.thakur89@gmail.com',  '9411415029', 'Lecturer',      'M.Tech.',       'Instrumentation Engineering', false),
  ('Vikal Sharma',      'vikal.in@gmail.com',             '9411415029', 'Lecturer',      'B.Tech.',       'Instrumentation Engineering', false),
  ('Varun',             'Varunknr72@gmail.com',           '9459014868', 'Lecturer',      'M.Tech.',       'Instrumentation Engineering', false),
  ('Ritika Sharma',     'Ritika30purohit@gmail.com',      '9736167040', 'Lecturer',      'B.Tech.',       'Instrumentation Engineering', false),
  ('Munish Kumar',      'munishsharma198@gmail.com',      '9882856139', 'Lecturer',      'B.Tech.',       'Instrumentation Engineering', false),

  -- F) MECHANICAL ENGINEERING
  ('Amandeep Sharma',   'amandeepsharma@gmail.com',       null,         'HOD',           'B.Tech.',       'Mechanical Engineering', false),
  ('Onkar Singh',       'onkar.singh26970@gmail.com',     '7018814985', 'Sr. Lecturer',  'M.Tech.',       'Mechanical Engineering', false),
  ('Santosh Kumar',     'Kumarsantosh9606@gmail.com',     '9817128854', 'Lecturer',      'B.Tech.',       'Mechanical Engineering', false),
  ('Satbir Singh',      'satbirguru@gmail.com',           '7018376686', 'Lecturer',      'M.Tech.',       'Mechanical Engineering', false),
  ('Prag Sharma',       'pragsharma@gmail.com',           null,         'Lecturer',      'B.Tech.',       'Mechanical Engineering', false),
  ('Subash Chand',      'swastiksneh@gmail.com',          '9960170687', 'Lecturer',      'B.Tech.',       'Mechanical Engineering', false),
  ('N.C. Kaul',         'Narinderkaul68@gmail.com',       '9418219268', 'Foreman Instructor','Diploma',    'Mechanical Engineering', false),

  -- G) WORKSHOP STAFF
  ('Vikas Kandoria',    'vikash40at1579@gmail.com',       '9418161414', 'WSI Turning',   'Diploma',       'Workshop', true),
  ('Ishwar Dass',       'Ishwardas15051968@gmail.com',    '9418645828', 'WSI Fitting',   'Diploma',       'Workshop', true),
  ('Pawan Kumar',       'Pawankumar64399@gmail.com',      '9418864399', 'WSI Welding',   'JTS Part-II',   'Workshop', true),
  ('Varinder Kumar',    'Varinderkumar723@gmail.com',     '9816873723', 'WSI Smithy',    'NCVT',          'Workshop', true),
  ('Sanjay Kumar',      'Sanjaykapilsanjaykapil1@gmail.com','7018943485','WSI Carpentry','Diploma',       'Workshop', true),
  ('Aneesh Kumar',      'Aneeshmalhotra45@gmail.com',     '9882025448', 'WSI Sheet Metal','NCVT',         'Workshop', true),
  ('Shivam Bhatia',     'Shiyambhatia2003@gmail.com',     '8219175710', 'WSI Electrical','Diploma',       'Workshop', true),
  ('Manish Thakur',     'Thakurmanish993@gmail.com',      '8219339225', 'WSI Machinist', 'B.Tech.',       'Workshop', true),
  ('Workshop Staff',    'workshopstaff@gpkangra.edu.in',  null,         'Workshop Staff','',              'Workshop', true)
ON CONFLICT (email) DO UPDATE SET 
  full_name = EXCLUDED.full_name,
  designation = EXCLUDED.designation,
  qualification = EXCLUDED.qualification,
  department = EXCLUDED.department,
  is_workshop_staff = EXCLUDED.is_workshop_staff;


-- -----------------------------------------------------------
-- 2. INSERT TEACHER ASSIGNMENTS (Dynamically linked by emails)
-- -----------------------------------------------------------
INSERT INTO public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department)
SELECT id, 'Computer Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Kchand78@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Saroop2388@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'Surbhisharma.jmi@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'FEEE', 'Fundamentals of EEE', 'Instrumentation Engineering' FROM public.teachers WHERE email = 'Varunknr72@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'EM', 'Engineering Mechanics', 'Mechanical Engineering' FROM public.teachers WHERE email = 'pragsharma@gmail.com'
UNION ALL SELECT id, 'Computer Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'prashanil77@gmail.com'

UNION ALL SELECT id, 'Electrical Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'reemachoudhary@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'kumariindu@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'Rajeev.kumar357@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'FEEE', 'Fundamentals of EEE', 'Electrical Engineering' FROM public.teachers WHERE email = 'adityasaklani@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'EM', 'Engineering Mechanics', 'Mechanical Engineering' FROM public.teachers WHERE email = 'satbirguru@gmail.com'
UNION ALL SELECT id, 'Electrical Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'prashanil77@gmail.com'

UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Kchand78@gmail.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Thakurviju454@gmail.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering' FROM public.teachers WHERE email = 'Avinash.acet@yahoo.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'FEEE', 'Fundamentals of EEE', 'Electrical Engineering' FROM public.teachers WHERE email = 'Guptaina24@gmail.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'EM', 'Engineering Mechanics', 'Instrumentation Engineering' FROM public.teachers WHERE email = 'Ritika30purohit@gmail.com'
UNION ALL SELECT id, 'Electronics & Communication Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'prashanil77@gmail.com'

UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'reemachoudhary@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'kumariindu@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'FEEE', 'Fundamentals of EEE', 'Electrical Engineering' FROM public.teachers WHERE email = 'jela.b89@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'EWS', 'Engineering Workshop', 'Workshop' FROM public.teachers WHERE email = 'Pawankumar64399@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'EM', 'Engineering Mechanics', 'Instrumentation Engineering' FROM public.teachers WHERE email = 'Pawanchandel13@gmail.com'
UNION ALL SELECT id, 'Instrumentation Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'prashanil77@gmail.com'

UNION ALL SELECT id, 'Mechanical Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'reemachoudhary@gmail.com'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'Thakurviju454@gmail.com'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'FEEE', 'Fundamentals of EEE', 'Electrical Engineering' FROM public.teachers WHERE email = 'Guptaina24@gmail.com'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'EWS', 'Engineering Workshop', 'Workshop' FROM public.teachers WHERE email = 'workshopstaff@gpkangra.edu.in'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'EM', 'Engineering Mechanics', 'Mechanical Engineering' FROM public.teachers WHERE email = 'satbirguru@gmail.com'
UNION ALL SELECT id, 'Mechanical Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities' FROM public.teachers WHERE email = 'prashanil77@gmail.com'
ON CONFLICT (teacher_id, branch, semester, subject_code) DO NOTHING;
