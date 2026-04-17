-- ============================================================
-- FINAL OFFICIAL TEACHER ASSIGNMENTS (Sem 2, 4, 6)
-- Resolves teacher references by Name
-- ============================================================

-- Create a helper function to safely assign subjects by exact (or partial) name
CREATE OR REPLACE FUNCTION public.assign_subject(
    p_teacher_name text,
    p_branch text,
    p_semester integer,
    p_subject_code text,
    p_subject_name text,
    p_department text
) RETURNS void AS $$
DECLARE
    v_teacher_id uuid;
BEGIN
    -- Only match the first teacher found with that name (just in case)
    SELECT id INTO v_teacher_id FROM public.teachers WHERE full_name ILIKE '%' || p_teacher_name || '%' LIMIT 1;
    
    IF v_teacher_id IS NOT NULL THEN
        INSERT INTO public.teacher_assignments (teacher_id, branch, semester, subject_code, subject_name, department)
        VALUES (v_teacher_id, p_branch, p_semester, p_subject_code, p_subject_name, p_department)
        ON CONFLICT (teacher_id, branch, semester, subject_code) DO NOTHING;
    END IF;
END;
$$ LANGUAGE plpgsql;

DO $$
BEGIN

-- ==========================================================
-- APPLIED SCIENCES & HUMANITIES (All Branches Sem 2 Subjects)
-- ==========================================================
-- Math-II
PERFORM assign_subject('Kamlesh Chand', 'Computer Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities');
PERFORM assign_subject('Kamlesh Chand', 'Electronics & Communication Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities');
PERFORM assign_subject('Reema Choudhary', 'Electrical Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities');
PERFORM assign_subject('Reema Choudhary', 'Instrumentation Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities');
PERFORM assign_subject('Reema Choudhary', 'Mechanical Engineering', 2, 'MATH-II', 'Mathematics-II', 'Applied Sciences & Humanities');

-- Applied Physics-II
PERFORM assign_subject('Saroop Chand', 'Computer Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities');
PERFORM assign_subject('Kumari Indu', 'Electrical Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities');
PERFORM assign_subject('Kumari Indu', 'Instrumentation Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities');
PERFORM assign_subject('Vijay Thakur', 'Electronics & Communication Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities');
PERFORM assign_subject('Vijay Thakur', 'Mechanical Engineering', 2, 'PHY-II', 'Applied Physics-II', 'Applied Sciences & Humanities');

-- EVS
PERFORM assign_subject('Anil Kumar', 'Computer Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities');
PERFORM assign_subject('Anil Kumar', 'Electrical Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities');
PERFORM assign_subject('Anil Kumar', 'Electronics & Communication Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities');
PERFORM assign_subject('Anil Kumar', 'Instrumentation Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities');
PERFORM assign_subject('Anil Kumar', 'Mechanical Engineering', 2, 'EVS', 'Environmental Science', 'Applied Sciences & Humanities');

-- SCA (Sem 2)
PERFORM assign_subject('Saroop Chand', 'Computer Engineering', 2, 'SCA', 'Student Centered Activities', 'Applied Sciences & Humanities');
PERFORM assign_subject('Anil Kumar', 'Electrical Engineering', 2, 'SCA', 'Student Centered Activities', 'Applied Sciences & Humanities');
PERFORM assign_subject('Vijay Thakur', 'Electronics & Communication Engineering', 2, 'SCA', 'Student Centered Activities', 'Applied Sciences & Humanities');
PERFORM assign_subject('Kumari Indu', 'Instrumentation Engineering', 2, 'SCA', 'Student Centered Activities', 'Applied Sciences & Humanities');
PERFORM assign_subject('Reema Choudhary', 'Mechanical Engineering', 2, 'SCA', 'Student Centered Activities', 'Applied Sciences & Humanities');


-- ==========================================================
-- COMPUTER ENGINEERING
-- ==========================================================
-- Sem 2
PERFORM assign_subject('Surbhi Sharma', 'Computer Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering');
PERFORM assign_subject('Varun', 'Computer Engineering', 2, 'FEEE', 'FEEE', 'Instrumentation Engineering');
PERFORM assign_subject('Prag Sharma', 'Computer Engineering', 2, 'EM', 'Engineering Mechanics', 'Mechanical Engineering');

-- Sem 4
PERFORM assign_subject('Rajeev Kumar', 'Computer Engineering', 4, 'DBMS', 'DBMS', 'Computer Engineering');
PERFORM assign_subject('N.K. Sapehia', 'Computer Engineering', 4, 'DSA', 'DSA', 'Computer Engineering');
PERFORM assign_subject('Tamanna Chitra', 'Computer Engineering', 4, 'PE-I', 'Professional Elective-I', 'Computer Engineering');
PERFORM assign_subject('Aashima Sharma', 'Computer Engineering', 4, 'PE-II', 'Professional Elective-II / DM', 'Computer Engineering');
PERFORM assign_subject('Aashima Sharma', 'Computer Engineering', 4, 'EIKT', 'Emerging ICT', 'Computer Engineering');
PERFORM assign_subject('Rajeev Kumar', 'Computer Engineering', 4, 'MINOR', 'Minor Project', 'Computer Engineering');
PERFORM assign_subject('Tamanna Chitra', 'Computer Engineering', 4, 'MINOR', 'Minor Project', 'Computer Engineering');
PERFORM assign_subject('Yashwant Singh', 'Computer Engineering', 4, 'SCA', 'Student Centered Activities', 'Computer Engineering'); -- (Note: Yashwant Singh might not be in DB yet)

-- Sem 6
PERFORM assign_subject('Surbhi Sharma', 'Computer Engineering', 6, 'OE-II', 'Open Elective-II', 'Computer Engineering');
PERFORM assign_subject('Tamanna Chitra', 'Computer Engineering', 6, 'OE-II', 'Open Elective-II', 'Computer Engineering');
PERFORM assign_subject('Talvinder Singh', 'Computer Engineering', 6, 'ESU', 'E&SU', 'Computer Engineering');
PERFORM assign_subject('Hari Singh Thakur', 'Computer Engineering', 6, 'IC', 'Industrial Communication', 'Electronics & Communication Engineering');
PERFORM assign_subject('Avinash Sharma', 'Computer Engineering', 6, 'SL', 'SL Lab', 'Computer Engineering');
PERFORM assign_subject('Avinash Sharma', 'Computer Engineering', 6, 'MAJOR', 'Major Project', 'Computer Engineering');
PERFORM assign_subject('Tamanna Chitra', 'Computer Engineering', 6, 'MAJOR', 'Major Project', 'Computer Engineering');
PERFORM assign_subject('Yashwant Singh', 'Computer Engineering', 6, 'SCA', 'Student Centered Activities', 'Computer Engineering');


-- ==========================================================
-- ELECTRICAL ENGINEERING
-- ==========================================================
-- Sem 2
PERFORM assign_subject('Rajeev Kumar', 'Electrical Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering');
PERFORM assign_subject('Tamanna Chitra', 'Electrical Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering');
PERFORM assign_subject('Aditya Saklani', 'Electrical Engineering', 2, 'FEEE', 'FEEE', 'Electrical Engineering');
PERFORM assign_subject('Pawan Kumar', 'Electrical Engineering', 2, 'EM', 'Engineering Mechanics', 'Workshop');
PERFORM assign_subject('Satbir Singh', 'Electrical Engineering', 2, 'EM', 'Engineering Mechanics', 'Mechanical Engineering');

-- Sem 4
PERFORM assign_subject('Rajesh Sharma', 'Electrical Engineering', 4, 'EPTD', 'EPT&D', 'Electrical Engineering');
PERFORM assign_subject('Sudhir Dhiman', 'Electrical Engineering', 4, 'BMMHPP', 'BM&MHPP', 'Electrical Engineering');
PERFORM assign_subject('Aditya Saklani', 'Electrical Engineering', 4, 'ISSEM', 'IS&SEM', 'Electrical Engineering');
PERFORM assign_subject('Aditya Saklani', 'Electrical Engineering', 4, 'FPE', 'FPE', 'Electrical Engineering');
PERFORM assign_subject('Richa Sharma', 'Electrical Engineering', 4, 'EIKT', 'Emerging ICT', 'Applied Sciences & Humanities');
PERFORM assign_subject('Ina Gupta', 'Electrical Engineering', 4, 'MINOR', 'Minor Project', 'Electrical Engineering');
PERFORM assign_subject('Aditya Saklani', 'Electrical Engineering', 4, 'SCA', 'Student Centered Activities', 'Electrical Engineering');

-- Sem 6
PERFORM assign_subject('Richa Sharma', 'Electrical Engineering', 6, 'IC', 'Industrial Communication', 'Applied Sciences & Humanities');
PERFORM assign_subject('Iela Bharti', 'Electrical Engineering', 6, 'ESU', 'E&SU', 'Electrical Engineering');
PERFORM assign_subject('Sudhir Dhiman', 'Electrical Engineering', 6, 'BE', 'BE', 'Electrical Engineering');
PERFORM assign_subject('Iela Bharti', 'Electrical Engineering', 6, 'ITM', 'IT&M', 'Electrical Engineering');
PERFORM assign_subject('Ina Gupta', 'Electrical Engineering', 6, 'PPC', 'PP&C', 'Electrical Engineering');
PERFORM assign_subject('Sudhir Dhiman', 'Electrical Engineering', 6, 'MAJOR', 'Major Project', 'Electrical Engineering');
PERFORM assign_subject('Rajesh Sharma', 'Electrical Engineering', 6, 'MAJOR', 'Major Project', 'Electrical Engineering');
PERFORM assign_subject('Shivam Bhatia', 'Electrical Engineering', 6, 'SCA', 'Student Centered Activities', 'Workshop');


-- ==========================================================
-- ELECTRONICS & COMMUNICATION ENGINEERING
-- ==========================================================
-- Sem 2
PERFORM assign_subject('Avinash Sharma', 'Electronics & Communication Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering');
PERFORM assign_subject('Talvinder Singh', 'Electronics & Communication Engineering', 2, 'IT', 'Introduction to IT', 'Computer Engineering');
PERFORM assign_subject('Ina Gupta', 'Electronics & Communication Engineering', 2, 'FEEE', 'FEEE', 'Electrical Engineering');
PERFORM assign_subject('Varun', 'Electronics & Communication Engineering', 2, 'EM', 'Engineering Mechanics', 'Instrumentation Engineering');

-- Sem 4
PERFORM assign_subject('Nishant Kaushal', 'Electronics & Communication Engineering', 4, 'MA', 'Microprocessors & Applications', 'Electronics & Communication Engineering');
PERFORM assign_subject('Hari Singh Thakur', 'Electronics & Communication Engineering', 4, 'CE', 'Consumer Electronics', 'Electronics & Communication Engineering');
PERFORM assign_subject('Jagdeep Singh', 'Electronics & Communication Engineering', 4, 'IE', 'Industrial Electronics', 'Electronics & Communication Engineering');
PERFORM assign_subject('Rohit Kumar', 'Electronics & Communication Engineering', 4, 'BMI', 'BMI', 'Electronics & Communication Engineering');
PERFORM assign_subject('Anil Kumar', 'Electronics & Communication Engineering', 4, 'DCS', 'Digital Communication Systems', 'Applied Sciences & Humanities');
PERFORM assign_subject('Rohit Kumar', 'Electronics & Communication Engineering', 4, 'MINOR', 'Minor Project', 'Electronics & Communication Engineering');
PERFORM assign_subject('Anil Kumar', 'Electronics & Communication Engineering', 4, 'MINOR', 'Minor Project', 'Applied Sciences & Humanities');
PERFORM assign_subject('Jaswinder Kumar', 'Electronics & Communication Engineering', 4, 'SCA', 'Student Centered Activities', 'Electronics & Communication Engineering');

-- Sem 6
PERFORM assign_subject('Anil Kumar', 'Electronics & Communication Engineering', 6, 'CNDC', 'CNDC', 'Applied Sciences & Humanities');
PERFORM assign_subject('Rohit Kumar', 'Electronics & Communication Engineering', 6, 'ESU', 'E&SU', 'Electronics & Communication Engineering');
PERFORM assign_subject('Jagdeep Singh', 'Electronics & Communication Engineering', 6, 'OE-II', 'Open Elective-II', 'Electronics & Communication Engineering');
PERFORM assign_subject('Nishant Kaushal', 'Electronics & Communication Engineering', 6, 'OE-II', 'Open Elective-II', 'Electronics & Communication Engineering');
PERFORM assign_subject('Hari Singh Thakur', 'Electronics & Communication Engineering', 6, 'IC', 'Industrial Communication', 'Electronics & Communication Engineering');
PERFORM assign_subject('Nishant Kaushal', 'Electronics & Communication Engineering', 6, 'MAJOR', 'Major Project', 'Electronics & Communication Engineering');
PERFORM assign_subject('Hari Singh Thakur', 'Electronics & Communication Engineering', 6, 'MAJOR', 'Major Project', 'Electronics & Communication Engineering');
PERFORM assign_subject('Sanjeev Naryal', 'Electronics & Communication Engineering', 6, 'SCA', 'Student Centered Activities', 'Electronics & Communication Engineering'); -- Used Sanjeev Naryal as per DB


-- ==========================================================
-- INSTRUMENTATION ENGINEERING
-- ==========================================================
-- Sem 2
PERFORM assign_subject('Iela Bharti', 'Instrumentation Engineering', 2, 'FEEE', 'FEEE', 'Electrical Engineering');
PERFORM assign_subject('Pawan Chandel', 'Instrumentation Engineering', 2, 'EM', 'Engineering Mechanics', 'Instrumentation Engineering');
PERFORM assign_subject('Sanjeev Naryal', 'Instrumentation Engineering', 2, 'EWS', 'Engineering Workshop', 'Electronics & Communication Engineering');
PERFORM assign_subject('Kumari Indu', 'Instrumentation Engineering', 2, 'EWS', 'Engineering Workshop', 'Applied Sciences & Humanities');

-- Sem 4
PERFORM assign_subject('Vikal Sharma', 'Instrumentation Engineering', 4, 'CS', 'Control Systems', 'Instrumentation Engineering');
PERFORM assign_subject('Karan Singh Thakur', 'Instrumentation Engineering', 4, 'PC-I', 'Process Control-I', 'Instrumentation Engineering');
PERFORM assign_subject('Munish Kumar', 'Instrumentation Engineering', 4, 'PE-I', 'Professional Elective-I', 'Instrumentation Engineering');
PERFORM assign_subject('Ritika Sharma', 'Instrumentation Engineering', 4, 'PE-I', 'Professional Elective-I', 'Instrumentation Engineering');
PERFORM assign_subject('Richa Sharma', 'Instrumentation Engineering', 4, 'EIKT', 'Emerging ICT', 'Applied Sciences & Humanities');
PERFORM assign_subject('Ritika Sharma', 'Instrumentation Engineering', 4, 'MINOR', 'Minor Project', 'Instrumentation Engineering');
PERFORM assign_subject('Munish Kumar', 'Instrumentation Engineering', 4, 'MINOR', 'Minor Project', 'Instrumentation Engineering');
PERFORM assign_subject('Vikal Sharma', 'Instrumentation Engineering', 4, 'SCA', 'Student Centered Activities', 'Instrumentation Engineering');

-- Sem 6
PERFORM assign_subject('Pawan Chandel', 'Instrumentation Engineering', 6, 'LCDCS', 'LC&DCS', 'Instrumentation Engineering');
PERFORM assign_subject('Ritika Sharma', 'Instrumentation Engineering', 6, 'OE-II', 'Open Elective-II', 'Instrumentation Engineering');
PERFORM assign_subject('Karan Singh Thakur', 'Instrumentation Engineering', 6, 'AUEA', 'AUEA', 'Instrumentation Engineering');
PERFORM assign_subject('Vikal Sharma', 'Instrumentation Engineering', 6, 'ESU', 'E&SU', 'Instrumentation Engineering');
PERFORM assign_subject('Munish Kumar', 'Instrumentation Engineering', 6, 'DE-II', 'DE-II', 'Instrumentation Engineering');
PERFORM assign_subject('Pawan Chandel', 'Instrumentation Engineering', 6, 'MAJOR', 'Major Project', 'Instrumentation Engineering');
PERFORM assign_subject('Vikal Sharma', 'Instrumentation Engineering', 6, 'MAJOR', 'Major Project', 'Instrumentation Engineering');
PERFORM assign_subject('Ritika Sharma', 'Instrumentation Engineering', 6, 'MAJOR', 'Major Project', 'Instrumentation Engineering');
PERFORM assign_subject('Munish Kumar', 'Instrumentation Engineering', 6, 'SCA', 'Student Centered Activities', 'Instrumentation Engineering');


-- ==========================================================
-- MECHANICAL ENGINEERING
-- ==========================================================
-- Sem 2
PERFORM assign_subject('Ina Gupta', 'Mechanical Engineering', 2, 'FEEE', 'FEEE', 'Electrical Engineering');
PERFORM assign_subject('Jaswinder Kumar', 'Mechanical Engineering', 2, 'FEEE', 'FEEE', 'Electronics & Communication Engineering');
PERFORM assign_subject('Satbir Singh', 'Mechanical Engineering', 2, 'EM', 'Engineering Mechanics', 'Mechanical Engineering');
PERFORM assign_subject('Workshop Staff', 'Mechanical Engineering', 2, 'EWS', 'Engineering Workshop', 'Workshop');

-- Sem 4
PERFORM assign_subject('Satbir Singh', 'Mechanical Engineering', 4, 'PE-II', 'PE-II (PPE)', 'Mechanical Engineering');
PERFORM assign_subject('Santosh Kumar', 'Mechanical Engineering', 4, 'PE-I', 'PE-I (AE)', 'Mechanical Engineering');
PERFORM assign_subject('Prag Sharma', 'Mechanical Engineering', 4, 'SOM', 'Strength of Materials', 'Mechanical Engineering');
PERFORM assign_subject('Subash Chand', 'Mechanical Engineering', 4, 'TE-II', 'Thermal Engineering-II', 'Mechanical Engineering');
PERFORM assign_subject('Prag Sharma', 'Mechanical Engineering', 4, 'CADCAM', 'CAD/CAM Practice', 'Mechanical Engineering');
PERFORM assign_subject('Subash Chand', 'Mechanical Engineering', 4, 'CADCAM', 'CAD/CAM Practice', 'Mechanical Engineering');
PERFORM assign_subject('Onkar Singh', 'Mechanical Engineering', 4, 'MINOR', 'Minor Project', 'Mechanical Engineering');
PERFORM assign_subject('Satbir Singh', 'Mechanical Engineering', 4, 'MINOR', 'Minor Project', 'Mechanical Engineering');
PERFORM assign_subject('N.C. Kaul', 'Mechanical Engineering', 4, 'MINOR', 'Minor Project', 'Mechanical Engineering');
PERFORM assign_subject('N.C. Kaul', 'Mechanical Engineering', 4, 'SCA', 'Student Centered Activities', 'Mechanical Engineering');

-- Sem 6
PERFORM assign_subject('Subash Chand', 'Mechanical Engineering', 6, 'CADCAML', 'CAD/CAM Lab', 'Mechanical Engineering');
PERFORM assign_subject('Vikas Kandoria', 'Mechanical Engineering', 6, 'CADCAML', 'CAD/CAM Lab', 'Workshop');
PERFORM assign_subject('Onkar Singh', 'Mechanical Engineering', 6, 'DoME', 'Design of Machine Elements', 'Mechanical Engineering');
PERFORM assign_subject('Amandeep Sharma', 'Mechanical Engineering', 6, 'WT', 'Welding Technology', 'Mechanical Engineering');
PERFORM assign_subject('Santosh Kumar', 'Mechanical Engineering', 6, 'OE-II', 'Open Elective-II', 'Mechanical Engineering');
PERFORM assign_subject('Prag Sharma', 'Mechanical Engineering', 6, 'ESU', 'E&SU', 'Mechanical Engineering');
PERFORM assign_subject('Richa Sharma', 'Mechanical Engineering', 6, 'IC', 'Industrial Communication', 'Applied Sciences & Humanities');

-- Major Project
PERFORM assign_subject('Amandeep Sharma', 'Mechanical Engineering', 6, 'MAJOR', 'Major Project', 'Mechanical Engineering');
PERFORM assign_subject('Santosh Kumar', 'Mechanical Engineering', 6, 'MAJOR', 'Major Project', 'Mechanical Engineering');
PERFORM assign_subject('Pawan Kumar', 'Mechanical Engineering', 6, 'MAJOR', 'Major Project', 'Workshop');
PERFORM assign_subject('Vikas Kandoria', 'Mechanical Engineering', 6, 'MAJOR', 'Major Project', 'Workshop');
PERFORM assign_subject('Sanjay Kumar', 'Mechanical Engineering', 6, 'MAJOR', 'Major Project', 'Workshop');
PERFORM assign_subject('Manish Thakur', 'Mechanical Engineering', 6, 'MAJOR', 'Major Project', 'Workshop');

PERFORM assign_subject('N.C. Kaul', 'Mechanical Engineering', 6, 'SCA', 'Student Centered Activities', 'Mechanical Engineering');

END $$;
