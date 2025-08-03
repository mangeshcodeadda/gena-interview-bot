ScrapedJob.objects.create(
    job_name="Software Development Intern",
    job_type=4, 
    positions="5",
    start_date="2025-07-11", 
    expiry_date="2025-07-18", 
    skills="Python, Django, REST",
    duration="6 Months",
    location="Bangalore",
    min_salary=20000.00,
    max_salary=40000.00,
    source_name="Naukri",
    source_url="https://www.naukri.com/software-development-intern",
    logo=None,
    total_views=120
)

ScrapedJob.objects.create(
    job_name="Data Science Intern",
    job_type=4,
    positions="3",
    start_date="2025-07-11",
    expiry_date="2025-07-18",
    skills="Python, Pandas, Machine Learning",
    duration="3 Months",
    location="Remote",
    min_salary=15000.00,
    max_salary=30000.00,
    source_name="LinkedIn",
    source_url="https://www.linkedin.com/jobs/data-science-intern",
    logo=None,
    total_views=95
)

ScrapedJob.objects.create(
    job_name="Frontend Developer Intern",
    job_type=4,
    positions="2",
    start_date="2025-07-11",
    expiry_date="2025-07-18",
    skills="HTML, CSS, JavaScript, React",
    duration="4 Months",
    location="Hyderabad",
    min_salary=18000.00,
    max_salary=35000.00,
    source_name="Internshala",
    source_url="https://internshala.com/frontend-developer-intern",
    logo=None,
    total_views=80
)