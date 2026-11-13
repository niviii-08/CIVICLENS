# scripts/append_reps.py
import json
import generate_representatives_data

additional_reps = [
    {
        "id": "REP-021",
        "alias_ids": ["SENGOTTAIYAN", "21"],
        "name": "K. A. Sengottaiyan",
        "name_ta": "கே. ஏ. செங்கோட்டையன்",
        "constituency": "Gobichettipalayam",
        "ac_no": 106,
        "district": "Erode",
        "party": "AIADMK",
        "role": "Senior MLA & Former Minister for School Education",
        "attendance_percentage": 93.0,
        "questions_raised": 70,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.6,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "15th Assembly (2016–2021)", "14th Assembly (2011–2016)", "13th Assembly (2006–2011)", "10th Assembly (1989–1991)"],
        "summary": "Senior nine-time MLA representing Gobichettipalayam (Erode). Championed Bhavani river sub-canal concrete lining, turmeric & banana regulated markets, and high-tech government schools.",
        "key_achievements": [
            "Conducted concrete lining of Bhavani River sub-canals preventing seepage loss for 25,000 farm acres.",
            "Upgraded Gobichettipalayam Taluk Hospital with 100 beds and emergency dialysis wing.",
            "Constructed modern banana and turmeric auction complex at Gobichettipalayam.",
            "Built Model Higher Secondary School with robotics lab and digital auditorium.",
            "Executed piped drinking water supply scheme covering 38 rural panchayats."
        ],
        "works": [
            {
                "id": "WRK-GOB-01",
                "title": "Bhavani River Sub-Canal Concrete Lining & Modernization",
                "title_ta": "பவானி ஆற்று கிளைக் கால்வாய்கள் கான்கிரீட் தளம் மற்றும் புனரமைப்பு",
                "category": "Water & Sanitation",
                "description": "Lined 32 km canal reach ensuring swift water flow to tail-end ayacuts in Gobichettipalayam and Nambiyur.",
                "cost_cr": 42.0,
                "location": "Gobichettipalayam Ayacut",
                "year": "2021-2023",
                "status": "Completed",
                "source": "WRD Government Order G.O. (Ms) 144",
                "source_url": "https://tnrd.tn.gov.in"
            },
            {
                "id": "WRK-GOB-02",
                "title": "Gobichettipalayam Regulated Agricultural Banana & Turmeric Market",
                "title_ta": "கோபிசெட்டிபாளையம் நவீன வாழை மற்றும் மஞ்சள் ஒழுங்குமுறை விற்பனைக் கூடம்",
                "category": "Public Amenities",
                "description": "Constructed covered trading shed, electronic weighbridges, drying yard, and cold warehouse.",
                "cost_cr": 11.0,
                "location": "Gobichettipalayam Town",
                "year": "2022-2023",
                "status": "Inaugurated",
                "source": "Erode District MLACDS Register",
                "source_url": "https://erode.nic.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Starred Q #188",
                "date": "2022-04-08",
                "subject": "Bhavanisagar Dam canal modernization and water release schedule",
                "ministry": "Water Resources Department",
                "summary": "Urged timely water release for second crop paddy cultivation and concrete lining of distributaries.",
                "status": "Answered"
            }
        ],
        "related_records": [
            {
                "id": "AIADMK-2021-015",
                "type": "promise",
                "type_label": "Election Promise",
                "title": "Free laptop computers scheme for higher secondary students",
                "relationship_reason": "Pioneered free digital devices in government schools during minister tenure.",
                "href": "/promises",
                "connection_type": "evidence_relationship",
                "confidence_score": 0.95
            },
            {
                "id": "CIV-ERD-001",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Gobichettipalayam turmeric drying yard expansion and shed maintenance",
                "relationship_reason": "Monitored grievance for agricultural drying yards in Erode district.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.89
            }
        ]
    },
    {
        "id": "REP-022",
        "alias_ids": ["REGUPATHY", "22"],
        "name": "S. Regupathy",
        "name_ta": "எஸ். ரகுபதி",
        "constituency": "Tirumayam",
        "ac_no": 180,
        "district": "Pudukkottai",
        "party": "DMK",
        "role": "Minister for Law, Courts and Prisons & MLA",
        "attendance_percentage": 94.0,
        "questions_raised": 31,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.7,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "15th Assembly (2016–2021)", "13th Assembly (2006–2011)"],
        "summary": "Serving as Minister for Law, Courts and Prisons and MLA for Tirumayam (Pudukkottai). Focused on judicial infrastructure modernization, Tirumayam Fort heritage conservation, and rural piped water.",
        "key_achievements": [
            "Constructed integrated judicial court complex and staff quarters at Tirumayam.",
            "Established Government Model Arts and Science College permanent campus in Tirumayam.",
            "Restored heritage surroundings and tourist facilities around the historic Tirumayam Rock Fort.",
            "Commissioned Cauvery River Piped Drinking Water Project for Tirumayam union habitations.",
            "Constructed 18 Village Knowledge Centers and public e-libraries in rural panchayats."
        ],
        "works": [
            {
                "id": "WRK-TRM-01",
                "title": "Tirumayam Integrated Judicial Court Complex & Bar Chambers",
                "title_ta": "திருமயம் ஒருங்கிணைந்த நீதிமன்ற வளாகம் மற்றும் வழக்கறிஞர் அறை",
                "category": "Infrastructure",
                "description": "Constructed 4-courtroom modern judicial complex with e-filing chambers, video conference witness rooms, and quarters.",
                "cost_cr": 18.0,
                "location": "Tirumayam Town",
                "year": "2022-2024",
                "status": "Inaugurated",
                "source": "Home & Law Dept G.O. (Ms) 198",
                "source_url": "https://tn.gov.in/go_view"
            },
            {
                "id": "WRK-TRM-02",
                "title": "Tirumayam Fort Heritage Conservation & Tourist Plaza",
                "title_ta": "திருமயம் கோட்டை பாரம்பரிய பாதுகாப்பு மற்றும் சுற்றுலா வசதிகள்",
                "category": "Public Amenities",
                "description": "Restored approach pathways, solar pathway illumination, tourist information kiosk, and rainwater storage tanks.",
                "cost_cr": 6.8,
                "location": "Tirumayam Fort, Pudukkottai",
                "year": "2021-2023",
                "status": "Completed",
                "source": "Tourism Dept Project Order 2022",
                "source_url": "https://tamilnadutourism.tn.gov.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Ministerial Demand Reply",
                "date": "2023-04-26",
                "subject": "Law, Courts and Prison Reforms Policy Note",
                "ministry": "Law & Prisons",
                "summary": "Reported establishment of 50 new digital civil courts and modernization of prison skill rehabilitation.",
                "status": "Debated"
            }
        ],
        "related_records": [
            {
                "id": "DMK-2021-078",
                "type": "promise",
                "type_label": "Election Promise",
                "title": "Court infrastructure upgrade and digital e-courts expansion",
                "relationship_reason": "Statutory execution under state law portfolio.",
                "href": "/promises",
                "connection_type": "direct_identifier",
                "confidence_score": 1.0
            },
            {
                "id": "CIV-PUD-002",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Heritage conservation and tourist parking around Tirumayam fort",
                "relationship_reason": "Monitored grievance for archaeological protection in Pudukkottai.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.88
            }
        ]
    },
    {
        "id": "REP-023",
        "alias_ids": ["GEETHAJEEVAN", "23"],
        "name": "Geetha Jeevan",
        "name_ta": "கீதா ஜீவன்",
        "constituency": "Thoothukkudi",
        "ac_no": 216,
        "district": "Thoothukkudi",
        "party": "DMK",
        "role": "Minister for Social Welfare & Women Rights & MLA",
        "attendance_percentage": 93.8,
        "questions_raised": 33,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.75,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "15th Assembly (2016–2021)", "13th Assembly (2006–2011)"],
        "summary": "Serving as Minister for Social Welfare & Women Rights and MLA for Thoothukkudi. Spearheading women's safety, child care institutions, Thoothukudi municipal storm water drainage, and working women's hostels.",
        "key_achievements": [
            "Constructed modern Working Women's Hostels (Thozhi Hostels) and One-Stop Child Welfare Centers.",
            "Built Maternal & Child Health Super Specialty Wing at Thoothukudi Government Medical College.",
            "Executed Comprehensive Storm Water Drainage Phase 1 & 2 for flood-prone Thoothukudi Corporation wards.",
            "Modernized Thoothukudi Old Bus Stand with multi-tier commercial passenger complex.",
            "Installed RO clean drinking water dispensing kiosks across 22 coastal fisherfolk colonies."
        ],
        "works": [
            {
                "id": "WRK-TUT-01",
                "title": "Thoothukudi Corporation Comprehensive Storm Water Drainage Project",
                "title_ta": "தூத்துக்குடி மாநகராட்சி விரிவான மழைநீர் வடிகால் திட்டம்",
                "category": "Infrastructure",
                "description": "Constructed 142 km underground RCC storm water drain network with tidal flaps preventing ocean backwater flooding.",
                "cost_cr": 160.0,
                "location": "Thoothukudi Corporation Wards",
                "year": "2021-2024",
                "status": "Completed",
                "source": "MAWS Dept G.O. (Ms) 142",
                "source_url": "https://tn.gov.in/go_view"
            },
            {
                "id": "WRK-TUT-02",
                "title": "Thozhi Working Women's Hostel & Child Care Center",
                "title_ta": "தோழி பணிபுரியும் மகளிர் விடுதி மற்றும் குழந்தைகள் காப்பகம்",
                "category": "Public Amenities",
                "description": "Constructed 150-occupancy secure residential hostel with biometric access, cafeteria, and day-care crèche.",
                "cost_cr": 14.0,
                "location": "Bryant Nagar, Thoothukudi",
                "year": "2022-2023",
                "status": "Inaugurated",
                "source": "Social Welfare Dept Project Register",
                "source_url": "https://thoothukudi.nic.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Ministerial Demand Speech",
                "date": "2023-04-18",
                "subject": "Social Welfare & Women Rights Policy Note & KMUT Rollout",
                "ministry": "Social Welfare & Women Rights",
                "summary": "Reported direct benefit transfer delivery and grievance redressal for women entitlement schemes.",
                "status": "Debated"
            }
        ],
        "related_records": [
            {
                "id": "SCH-SW-KMUT",
                "type": "scheme",
                "type_label": "Welfare Scheme",
                "title": "Kalaignar Magalir Urimai Thittam",
                "relationship_reason": "Overseeing women empowerment entitlement scheme implementation.",
                "href": "/schemes/SCH-SW-KMUT",
                "connection_type": "direct_identifier",
                "confidence_score": 1.0
            },
            {
                "id": "CIV-TUT-001",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Thoothukudi low-lying areas monsoon inundation and drain clearing",
                "relationship_reason": "Monitored civic grievance addressed by newly built drainage network.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.92
            }
        ]
    },
    {
        "id": "REP-024",
        "alias_ids": ["MANOTHANGARAJ", "24"],
        "name": "T. Mano Thangaraj",
        "name_ta": "மனோ தங்கராஜ்",
        "constituency": "Padmanabhapuram",
        "ac_no": 232,
        "district": "Kanniyakumari",
        "party": "DMK",
        "role": "Minister for Milk and Dairy Development & MLA",
        "attendance_percentage": 93.4,
        "questions_raised": 35,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.68,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "15th Assembly (2016–2021)"],
        "summary": "Serving as Minister for Milk and Dairy Development and MLA for Padmanabhapuram (Kanniyakumari). Led Kothayar river basin check dam construction, modern Aavin dairy expansion, rubber agro-processing, and Palace tourism road widening.",
        "key_achievements": [
            "Constructed check dams and desilted supply channels in Kothayar river basin.",
            "Modernized Padmanabhapuram Government Taluk Hospital with advanced casualty.",
            "Established high-tech Rubber and Honey Processing Center at Thuckalay.",
            "Widened tourism circuit roads connecting Padmanabhapuram Palace, Mathoor Hanging Bridge, and Thiruparappu Falls.",
            "Constructed modern Aavin milk chilling and automated packaging dairy plant."
        ],
        "works": [
            {
                "id": "WRK-PAD-01",
                "title": "Padmanabhapuram Palace Tourism Heritage Road Widening & Lighting",
                "title_ta": "பத்மநாபபுரம் அரண்மனை பாரம்பரிய சுற்றுலா சாலை விரிவாக்கம்",
                "category": "Infrastructure",
                "description": "Widened 8.5 km feeder highway from NH 66 to Palace with heritage street lighting and tourist coach parking.",
                "cost_cr": 12.0,
                "location": "Padmanabhapuram Palace Route",
                "year": "2021-2023",
                "status": "Completed",
                "source": "Highways Dept G.O. (Ms) 68",
                "source_url": "https://tn.gov.in/go_view"
            },
            {
                "id": "WRK-PAD-02",
                "title": "Modern Aavin Milk Chilling & Automated Dairy Plant",
                "title_ta": "நவீன ஆவின் பால் குளிரூட்டும் மற்றும் பதப்படுத்தும் நிலையம்",
                "category": "Public Amenities",
                "description": "50,000-liter capacity automated chilling plant benefiting 12,000 dairy farmers in Kalkulam and Vilavancode taluks.",
                "cost_cr": 22.0,
                "location": "Thuckalay, Padmanabhapuram",
                "year": "2022-2024",
                "status": "Inaugurated",
                "source": "Dairy Development Dept Project Register",
                "source_url": "https://aavin.tn.gov.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Ministerial Demand Speech",
                "date": "2023-04-27",
                "subject": "Dairy Development Policy Note & Farmer Milk Incentives",
                "ministry": "Milk & Dairy Development",
                "summary": "Announced Rs. 3/liter procurement incentive increase for dairy producers and solar chilling units.",
                "status": "Debated"
            }
        ],
        "related_records": [
            {
                "id": "DMK-2021-049",
                "type": "promise",
                "type_label": "Election Promise",
                "title": "High-speed broadband optical fiber connectivity for all village panchayats (BharatNet)",
                "relationship_reason": "Execution of rural connectivity during tenure as IT Minister.",
                "href": "/promises",
                "connection_type": "evidence_relationship",
                "confidence_score": 0.95
            },
            {
                "id": "CIV-KK-001",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Rubber growers fair price mechanism and fungal blight relief in Kanniyakumari",
                "relationship_reason": "Monitored grievance for plantation farmers in Padmanabhapuram.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.9
            }
        ]
    },
    {
        "id": "REP-025",
        "alias_ids": ["PONMUDY", "25"],
        "name": "Dr. K. Ponmudy",
        "name_ta": "முனைவர் க. பொன்முடி",
        "constituency": "Tirukkoyilur",
        "ac_no": 76,
        "district": "Villupuram",
        "party": "DMK",
        "role": "Minister for Forests & MLA",
        "attendance_percentage": 92.4,
        "questions_raised": 28,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.65,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "15th Assembly (2016–2021)", "13th Assembly (2006–2011)", "11th Assembly (1996–2001)", "10th Assembly (1989–1991)"],
        "summary": "Senior Cabinet Minister serving as Minister for Forests and MLA for Tirukkoyilur (Villupuram). Guided Thenpennai river anicut renovation, Tirukkoyilur four-lane river bridge, and arts college permanent campus.",
        "key_achievements": [
            "Constructed four-lane high-level bridge across Thenpennai River at Tirukkoyilur.",
            "Established permanent campus for Government Arts & Science College in Tirukkoyilur.",
            "Renovated Thenpennai River Anicut and irrigation supply channels.",
            "Constructed modern central bus terminus and commercial complex at Tirukkoyilur.",
            "Implemented Green Tamil Nadu afforestation and avenue plantation along Villupuram arterial roads."
        ],
        "works": [
            {
                "id": "WRK-TKL-01",
                "title": "Thenpennai River Four-Lane Bridge at Tirukkoyilur",
                "title_ta": "திருக்கோவிலூர் தென்பெண்ணை ஆற்று நான்கு வழி உயர்மட்ட பாலம்",
                "category": "Infrastructure",
                "description": "Constructed 24-span concrete bridge connecting Tirukkoyilur, Asanur, and Villupuram bypassing narrow vintage bridge.",
                "cost_cr": 32.0,
                "location": "Thenpennai Crossing, Tirukkoyilur",
                "year": "2021-2023",
                "status": "Completed",
                "source": "Highways Dept G.O. (Ms) 82",
                "source_url": "https://tn.gov.in/go_view"
            },
            {
                "id": "WRK-TKL-02",
                "title": "Tirukkoyilur Government Arts and Science College Permanent Campus",
                "title_ta": "திருக்கோவிலூர் அரசு கலை மற்றும் அறிவியல் கல்லூரி நிரந்தர வளாகம்",
                "category": "Education",
                "description": "Constructed modern 3-storey academic block, digital library, and science labs for 1,500 rural students.",
                "cost_cr": 12.5,
                "location": "Tirukkoyilur Town",
                "year": "2022-2023",
                "status": "Inaugurated",
                "source": "Villupuram District MLACDS Register",
                "source_url": "https://viluppuram.nic.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Ministerial Demand Reply",
                "date": "2023-04-19",
                "subject": "Higher Education Policy Note & Pudhumai Penn College Enrolment",
                "ministry": "Higher Education",
                "summary": "Reported 27% surge in female college enrolment following Rs. 1,000 monthly allowance implementation.",
                "status": "Debated"
            }
        ],
        "related_records": [
            {
                "id": "SCH-HE-PUDHUMAI",
                "type": "scheme",
                "type_label": "Welfare Scheme",
                "title": "Moovalur Ramamirtham Ammaiyar Pudhumai Penn Scheme",
                "relationship_reason": "Execution of higher education financial assistance scheme.",
                "href": "/schemes/SCH-HE-PUDHUMAI",
                "connection_type": "direct_identifier",
                "confidence_score": 1.0
            },
            {
                "id": "CIV-VLP-001",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Thenpennai river sand protection and check dam restoration",
                "relationship_reason": "Monitored river conservation grievance in Villupuram district.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.89
            }
        ]
    },
    {
        "id": "REP-026",
        "alias_ids": ["MASTHAN", "26"],
        "name": "Gingee K. S. Masthan",
        "name_ta": "செஞ்சி கே. எஸ். மஸ்தான்",
        "constituency": "Gingee",
        "ac_no": 70,
        "district": "Villupuram",
        "party": "DMK",
        "role": "MLA & Former Minister for Minorities Welfare",
        "attendance_percentage": 93.0,
        "questions_raised": 48,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.7,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "15th Assembly (2016–2021)"],
        "summary": "Serving as MLA for Gingee (Villupuram). Guided Gingee Fort World Heritage nomination works, Taluk Hospital trauma wing expansion, comprehensive rural drinking water, and agricultural grain markets.",
        "key_achievements": [
            "Conducted comprehensive tourism infrastructure and heritage preservation works around Gingee Fort.",
            "Upgraded Gingee Government Taluk Hospital with modern trauma wing and blood storage center.",
            "Commissioned Piped Drinking Water Supply Scheme covering 45 rural village panchayats.",
            "Constructed modern regulated grain and vegetable market at Gingee.",
            "Built 12 community halls and modernized minorities welfare educational hostels."
        ],
        "works": [
            {
                "id": "WRK-GIN-01",
                "title": "Gingee Fort World Heritage Tourism Plaza & Conservation Infrastructure",
                "title_ta": "செஞ்சிக் கோட்டை உலக பாரம்பரிய சுற்றுலா வளாகம் மற்றும் பாதுகாப்பு பணிகள்",
                "category": "Public Amenities",
                "description": "Constructed tourist reception center, battery car pathways, heritage illumination, and landscaped parking area.",
                "cost_cr": 18.0,
                "location": "Gingee Fort, Villupuram",
                "year": "2021-2023",
                "status": "Inaugurated",
                "source": "Tourism Dept G.O. (Ms) 67",
                "source_url": "https://tn.gov.in/go_view"
            },
            {
                "id": "WRK-GIN-02",
                "title": "Gingee Rural 45-Village Comprehensive Piped Drinking Water Project",
                "title_ta": "செஞ்சி ஒன்றிய 45 கிராமங்களுக்கான கூட்டுக் குடிநீர் திட்டம்",
                "category": "Water & Sanitation",
                "description": "Laid 64 km pipeline network supplying treated surface drinking water to dry rainfed habitations.",
                "cost_cr": 28.0,
                "location": "Gingee Union Habitations",
                "year": "2022-2024",
                "status": "Completed",
                "source": "Villupuram District MLACDS Register",
                "source_url": "https://viluppuram.nic.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Starred Q #215",
                "date": "2022-09-06",
                "subject": "UNESCO World Heritage Site nomination for Gingee Rajagiri & Krishnagiri forts",
                "ministry": "Tourism, Culture & Religious Endowments",
                "summary": "Urged fast-tracking of monument dossier submission to Archaeological Survey of India (ASI).",
                "status": "Answered"
            }
        ],
        "related_records": [
            {
                "id": "DMK-2021-084",
                "type": "promise",
                "type_label": "Election Promise",
                "title": "Gingee fort tourism circuit modernization and conservation",
                "relationship_reason": "Execution of heritage tourism development manifesto commitment.",
                "href": "/promises",
                "connection_type": "direct_identifier",
                "confidence_score": 1.0
            },
            {
                "id": "CIV-VLP-002",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Gingee rural bus connectivity in hilly and remote hamlets",
                "relationship_reason": "Monitored passenger transit grievance in Gingee assembly.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.89
            }
        ]
    },
    {
        "id": "REP-027",
        "alias_ids": ["VELMURUGAN", "27"],
        "name": "T. Velmurugan",
        "name_ta": "தி. வேல்முருகன்",
        "constituency": "Panruti",
        "ac_no": 156,
        "district": "Cuddalore",
        "party": "TVK / DMK",
        "role": "MLA & President Tamizhaga Vazhvurimai Katchi (TVK)",
        "attendance_percentage": 91.8,
        "questions_raised": 82,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.5,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "13th Assembly (2006–2011)", "12th Assembly (2001–2006)"],
        "summary": "Serving as TVK President and MLA for Panruti (Cuddalore). A vocal advocate for local youth employment in NLC India, Gadilam river flood embankments, jackfruit agro-processing, and cashew farmer welfare.",
        "key_achievements": [
            "Advocated for priority employment for Tamil Nadu youth and land-surrendered families in NLC India Neyveli.",
            "Constructed Gadilam River flood protection stone embankment at Panruti.",
            "Established modern Jackfruit and Cashew Processing and Packaging Center at Panruti.",
            "Upgraded Panruti Government Taluk Hospital with 60 additional inpatient beds and casualty.",
            "Constructed all-weather bitumen roads connecting 26 agrarian hamlets in Panruti taluk."
        ],
        "works": [
            {
                "id": "WRK-PAN-01",
                "title": "Gadilam River Flood Embankment Strengthening & Retaining Wall",
                "title_ta": "கெடிலம் ஆற்று வெள்ளத் தடுப்புச் சுவர் மற்றும் கரைகள் பலப்படுத்துதல்",
                "category": "Environment & Flood",
                "description": "Constructed 4.2 km concrete retaining wall protecting Panruti market wards from flash monsoon flooding.",
                "cost_cr": 16.0,
                "location": "Gadilam River Bank, Panruti",
                "year": "2021-2023",
                "status": "Completed",
                "source": "WRD Work Order 56/2021",
                "source_url": "https://tnrd.tn.gov.in"
            },
            {
                "id": "WRK-PAN-02",
                "title": "Panruti Cashew & Jackfruit Processing Agro-Industrial Complex",
                "title_ta": "பண்ருட்டி முந்திரி மற்றும் பலாப்பழ பதப்படுத்தும் வேளாண் தொழில் மையம்",
                "category": "Public Amenities",
                "description": "Modern solar drying yards, vacuum packaging facility, and cold warehouse supporting 5,000 horticulture growers.",
                "cost_cr": 14.5,
                "location": "Panruti Agro Market",
                "year": "2022-2024",
                "status": "Inaugurated",
                "source": "Cuddalore District MLACDS Register",
                "source_url": "https://cuddalore.nic.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Calling Attention Motion",
                "date": "2023-03-15",
                "subject": "Local employment reservation and compensation for NLC land acquisition",
                "ministry": "Industries & Labour Welfare",
                "summary": "Urged government to mandate permanent employment for families who surrendered farmlands for NLC mining.",
                "status": "Debated"
            }
        ],
        "related_records": [
            {
                "id": "DMK-2021-063",
                "type": "promise",
                "type_label": "Election Promise",
                "title": "Protection of local jobs and fair compensation in public sector industrial expansions",
                "relationship_reason": "High-profile legislative focus on NLC Neyveli mine expansion.",
                "href": "/promises",
                "connection_type": "evidence_relationship",
                "confidence_score": 0.94
            },
            {
                "id": "CIV-CUD-001",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Panruti cashew and jackfruit growers fair pricing and export logistics",
                "relationship_reason": "Monitored agrarian livelihood grievance in Cuddalore district.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.91
            }
        ]
    },
    {
        "id": "REP-028",
        "alias_ids": ["SARASWATHI", "28"],
        "name": "Dr. C. Saraswathi",
        "name_ta": "டாக்டர் சி. சரஸ்வதி",
        "constituency": "Modakkurichi",
        "ac_no": 105,
        "district": "Erode",
        "party": "BJP",
        "role": "MLA & Medical Practitioner",
        "attendance_percentage": 92.6,
        "questions_raised": 80,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.4,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)"],
        "summary": "Serving as MLA for Modakkurichi (Erode). Championed Kalingarayan canal pollution checks, primary health center emergency infrastructure, clean RO water plants, and handloom weaver welfare.",
        "key_achievements": [
            "Conducted pollution inspections and advocated for Zero Liquid Discharge in Kalingarayan Canal.",
            "Upgraded Modakkurichi Primary Health Centers with round-the-clock emergency delivery care.",
            "Installed RO clean water filtration plants across 16 rural panchayats.",
            "Constructed modern computer lab and digital classrooms at Modakkurichi Govt Higher Secondary School.",
            "Constructed Handloom Weavers Community Centre and direct marketing showroom."
        ],
        "works": [
            {
                "id": "WRK-MOD-01",
                "title": "Kalingarayan Canal Solar Streetlighting & Bund Retaining Walls",
                "title_ta": "காலிங்கராயன் வாய்க்கால் சோலார் விளக்குகள் மற்றும் தடுப்புச் சுவர்",
                "category": "Environment & Flood",
                "description": "Constructed stone pitch revetment along 8 km canal bund and installed 120 solar streetlights preventing night accidents.",
                "cost_cr": 6.5,
                "location": "Kalingarayan Channel, Modakkurichi",
                "year": "2022-2023",
                "status": "Completed",
                "source": "Erode District MLACDS Register",
                "source_url": "https://erode.nic.in"
            },
            {
                "id": "WRK-MOD-02",
                "title": "Modakkurichi Handloom Weavers Community Center & Showroom",
                "title_ta": "மொடக்குறிச்சி கைத்தறி நெசவாளர் சமுதாய கூடம் மற்றும் விற்பனை மையம்",
                "category": "Public Amenities",
                "description": "Constructed yarn storage warehouse, community meeting hall, and modern handloom showroom on main highway.",
                "cost_cr": 3.2,
                "location": "Modakkurichi Town",
                "year": "2023",
                "status": "Completed",
                "source": "Handlooms & Textiles Dept Sanction Order 2022",
                "source_url": "https://erode.nic.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Starred Q #402",
                "date": "2023-04-12",
                "subject": "Industrial effluent monitoring & online sensors in Kalingarayan irrigation canal",
                "ministry": "Environment, Climate Change & Forests",
                "summary": "Urged strict TNPCB action against illegal dyeing unit midnight discharges into the irrigation channel.",
                "status": "Answered"
            }
        ],
        "related_records": [
            {
                "id": "AIADMK-2021-014",
                "type": "promise",
                "type_label": "Election Promise",
                "title": "Free electricity quota of 200 units for handloom weavers",
                "relationship_reason": "Welfare support for weaving households in western Erode cluster.",
                "href": "/promises",
                "connection_type": "evidence_relationship",
                "confidence_score": 0.94
            },
            {
                "id": "CIV-ERD-002",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Kalingarayan canal industrial effluent discharge and canal desilting",
                "relationship_reason": "Constituency water pollution complaint monitored under TNPCB.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.93
            }
        ]
    },
    {
        "id": "REP-029",
        "alias_ids": ["MRKPANNEERSELVAM", "29"],
        "name": "M. R. K. Panneerselvam",
        "name_ta": "எம். ஆர். கே. பன்னீர்செல்வம்",
        "constituency": "Kurinjipadi",
        "ac_no": 158,
        "district": "Cuddalore",
        "party": "DMK",
        "role": "Minister for Agriculture and Farmers Welfare & MLA",
        "attendance_percentage": 94.2,
        "questions_raised": 32,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.8,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "15th Assembly (2016–2021)", "13th Assembly (2006–2011)", "11th Assembly (1996–2001)"],
        "summary": "Serving as Minister for Agriculture and Farmers Welfare and MLA for Kurinjipadi (Cuddalore). Conceived Tamil Nadu's historic Separate Agriculture Budget, free farm electricity connections, Vellar river flood walls, and groundnut agro-markets.",
        "key_achievements": [
            "Introduced Tamil Nadu's dedicated Separate Annual Agriculture Budget in the Legislative Assembly.",
            "Sanctioned 2 lakh free electricity connections for agricultural pump sets statewide.",
            "Constructed Vellar River flood retaining walls and check dam at Kurinjipadi.",
            "Established Government Arts and Science College in Kurinjipadi.",
            "Modernized Kurinjipadi Regulated Groundnut & Paddy Agro-Market with electronic trading."
        ],
        "works": [
            {
                "id": "WRK-KUR-01",
                "title": "Vellar River Flood Retaining Wall & Irrigation Check Dam",
                "title_ta": "வெள்ளாறு வெள்ளத் தடுப்புச் சுவர் மற்றும் பாசன தடுப்பணை",
                "category": "Water & Sanitation",
                "description": "Constructed 5.4 km flood embankment and 2 check dams conserving irrigation water for 12,000 acres in Kurinjipadi union.",
                "cost_cr": 26.0,
                "location": "Vellar River Basin, Kurinjipadi",
                "year": "2021-2023",
                "status": "Completed",
                "source": "WRD G.O. (Ms) No. 96",
                "source_url": "https://tnrd.tn.gov.in"
            },
            {
                "id": "WRK-KUR-02",
                "title": "Kurinjipadi Regulated Groundnut & Paddy Agro-Market Modernization",
                "title_ta": "குறிஞ்சிப்பாடி நிலக்கடலை மற்றும் நெல் ஒழுங்குமுறை விற்பனைக் கூடம்",
                "category": "Public Amenities",
                "description": "Constructed 2,000-tonne godown, covered drying platforms, electronic moisture meters, and direct purchase counters.",
                "cost_cr": 12.0,
                "location": "Kurinjipadi Market Yard",
                "year": "2022-2024",
                "status": "Inaugurated",
                "source": "Agriculture Dept Sanction Order 2022",
                "source_url": "https://agritech.tnau.ac.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Agriculture Budget Presentation",
                "date": "2024-02-20",
                "subject": "Tamil Nadu Agriculture Budget 2024-2025",
                "ministry": "Agriculture & Farmers Welfare",
                "summary": "Presented Rs. 42,282 Cr comprehensive agriculture budget focusing on organic farming, millets, and drip irrigation.",
                "status": "Debated"
            }
        ],
        "related_records": [
            {
                "id": "DMK-2021-009",
                "type": "promise",
                "type_label": "Election Promise",
                "title": "Dedicated annual Agriculture Budget for Tamil Nadu",
                "relationship_reason": "Pioneered and presented the state's separate agriculture budget.",
                "href": "/promises",
                "connection_type": "direct_identifier",
                "confidence_score": 1.0
            },
            {
                "id": "CIV-CUD-002",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Cuddalore coastal monsoon crop flood damage compensation",
                "relationship_reason": "Monitored grievance for agricultural calamity relief in Cuddalore.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.92
            }
        ]
    },
    {
        "id": "REP-030",
        "alias_ids": ["SAKKARAPANI", "30"],
        "name": "R. Sakkarapani",
        "name_ta": "அர. சக்கரபாணி",
        "constituency": "Oddanchatram",
        "ac_no": 128,
        "district": "Dindigul",
        "party": "DMK",
        "role": "Minister for Food and Civil Supplies & MLA",
        "attendance_percentage": 94.6,
        "questions_raised": 36,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.85,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "15th Assembly (2016–2021)", "14th Assembly (2011–2016)", "13th Assembly (2006–2011)", "12th Assembly (2001–2006)", "11th Assembly (1996–2001)"],
        "summary": "Six-time MLA serving as Minister for Food and Civil Supplies, representing Oddanchatram (Dindigul). Guided the Oddanchatram mega vegetable market modern logistics hub, Amaravathi river lift drinking water scheme, and paddy procurement centers.",
        "key_achievements": [
            "Constructed the modern Oddanchatram Mega Vegetable Market Cold Storage and Logistics Terminal.",
            "Executed Amaravathi River Lift Drinking Water Scheme delivering potable water to 52 village panchayats.",
            "Modernized Oddanchatram Government Taluk Hospital with 100-bed trauma surgical wing.",
            "Constructed modern grain storage silos and direct paddy procurement centers across Dindigul.",
            "Constructed Model Government Higher Secondary School complex at Oddanchatram."
        ],
        "works": [
            {
                "id": "WRK-ODD-01",
                "title": "Oddanchatram Mega Vegetable Market Modern Logistics & Cold Chain Terminal",
                "title_ta": "ஒட்டன்சத்திரம் மெகா காய்கறி சந்தை நவீன குளிர்பதன மற்றும் சரக்கு முனையம்",
                "category": "Public Amenities",
                "description": "Constructed 25-acre market complex with 500 wholesale stalls, 1,000-tonne cold storage, truck parking, and bio-gas power generation.",
                "cost_cr": 28.0,
                "location": "Oddanchatram Highway Junction",
                "year": "2021-2023",
                "status": "Inaugurated",
                "source": "Food & Civil Supplies Dept G.O. (Ms) 77",
                "source_url": "https://tn.gov.in/go_view"
            },
            {
                "id": "WRK-ODD-02",
                "title": "Amaravathi River Lift Drinking Water Project for 52 Habitations",
                "title_ta": "அமராவதி ஆற்று நீரேற்று கூட்டு குடிநீர் திட்டம் (52 கிராமங்கள்)",
                "category": "Water & Sanitation",
                "description": "Installed intake well in Amaravathi riverbed and laid 88 km distribution pipeline supplying clean water to rural hamlets.",
                "cost_cr": 45.0,
                "location": "Oddanchatram Union",
                "year": "2022-2024",
                "status": "Completed",
                "source": "TWAD Board Project Register",
                "source_url": "https://twadboard.tn.gov.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Ministerial Demand Speech",
                "date": "2023-04-21",
                "subject": "Food and Civil Supplies Policy Note & PDS Biometric Automation",
                "ministry": "Food & Civil Supplies",
                "summary": "Reported elimination of bogus ration cards via biometric Aadhaar authentication and distribution of fortified rice.",
                "status": "Debated"
            }
        ],
        "related_records": [
            {
                "id": "DMK-2021-014",
                "type": "promise",
                "type_label": "Election Promise",
                "title": "Direct procurement centers in every paddy producing block",
                "relationship_reason": "Overseeing paddy and foodgrain procurement statewide.",
                "href": "/promises",
                "connection_type": "direct_identifier",
                "confidence_score": 1.0
            },
            {
                "id": "CIV-DIN-001",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Oddanchatram vegetable market organic waste composting and truck parking",
                "relationship_reason": "Monitored civic infrastructure grievance in Oddanchatram.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.93
            }
        ]
    },
    {
        "id": "REP-031",
        "alias_ids": ["MUNUSAMY", "31"],
        "name": "K. P. Munusamy",
        "name_ta": "கே. பி. முனுசாமி",
        "constituency": "Veppanahalli",
        "ac_no": 53,
        "district": "Krishnagiri",
        "party": "AIADMK",
        "role": "MLA & Deputy General Secretary AIADMK",
        "attendance_percentage": 91.5,
        "questions_raised": 65,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.45,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "14th Assembly (2011–2016)", "12th Assembly (2001–2006)"],
        "summary": "Serving as AIADMK Deputy General Secretary and MLA for Veppanahalli (Krishnagiri). Championed Kelavarapalli dam surplus water diversion, mango pulp agro-processing, elephant corridor fencing, and border hill roads.",
        "key_achievements": [
            "Advocated for Kelavarapalli Dam surplus water diversion to drought-prone irrigation tanks in Veppanahalli.",
            "Constructed all-weather bitumen roads connecting 32 remote hill-border habitations.",
            "Upgraded Veppanahalli Government Taluk Hospital with modern 50-bed inpatient block.",
            "Established Mango & Tomato Pulp Agro Cold Chain storage facility in Krishnagiri belt.",
            "Four-laned the Veppanahalli-Krishnagiri arterial highway corridor."
        ],
        "works": [
            {
                "id": "WRK-VEP-01",
                "title": "Veppanahalli-Krishnagiri Highway Four-Laning & Overbridges",
                "title_ta": "வேப்பனஹள்ளி-கிருஷ்ணகிரி நெடுஞ்சாலை நான்கு வழி விரிவாக்கம்",
                "category": "Infrastructure",
                "description": "Widened 16 km arterial link road with central lighting, culverts, and bus shelters facilitating agricultural transport.",
                "cost_cr": 38.0,
                "location": "Veppanahalli-Krishnagiri Corridor",
                "year": "2021-2023",
                "status": "Completed",
                "source": "State Highways Dept Project Order 2022",
                "source_url": "https://tnhighways.gov.in"
            },
            {
                "id": "WRK-VEP-02",
                "title": "Mango & Tomato Pulp Processing Agro Cold Storage Facility",
                "title_ta": "மாம்பழம் மற்றும் தக்காளி கூழ் பதப்படுத்தும் குளிர்பதன கிடங்கு",
                "category": "Public Amenities",
                "description": "Constructed 1,500-tonne cold storage facility enabling horticulturists to preserve mango pulp for export.",
                "cost_cr": 12.5,
                "location": "Veppanahalli Agro Center",
                "year": "2022-2024",
                "status": "Inaugurated",
                "source": "Krishnagiri District MLACDS Register",
                "source_url": "https://krishnagiri.nic.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Starred Q #276",
                "date": "2022-10-14",
                "subject": "Elephant corridor fencing & crop loss compensation in Krishnagiri border forests",
                "ministry": "Environment & Forests",
                "summary": "Urged construction of elephant-proof trenches and hanging solar fences along Karnataka border villages.",
                "status": "Answered"
            }
        ],
        "related_records": [
            {
                "id": "AIADMK-2021-013",
                "type": "promise",
                "type_label": "Election Promise",
                "title": "Minimum support price and cold storage network for horticultural crops",
                "relationship_reason": "Agrarian support for mango and vegetable cultivators in Krishnagiri.",
                "href": "/promises",
                "connection_type": "evidence_relationship",
                "confidence_score": 0.93
            },
            {
                "id": "CIV-KRG-001",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Wild elephant crop depredation along Veppanahalli forest boundary",
                "relationship_reason": "Forest border grievance in Veppanahalli constituency.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.92
            }
        ]
    },
    {
        "id": "REP-032",
        "alias_ids": ["NAGAIMAALI", "32"],
        "name": "V. P. Nagaimaali",
        "name_ta": "வி. பி. நாகைமாலி",
        "constituency": "Kilvelur",
        "ac_no": 164,
        "district": "Nagapattinam",
        "party": "CPI(M)",
        "role": "MLA & Floor Leader CPI(M) (TNLA)",
        "attendance_percentage": 94.0,
        "questions_raised": 88,
        "mlacds_allocated": 15.0,
        "mlacds_utilized": 14.6,
        "criminal_cases": 0,
        "active_terms": ["16th Assembly (2021–Present)", "14th Assembly (2011–2016)"],
        "summary": "Serving as CPI(M) Floor Leader in the Assembly and MLA for Kilvelur (Nagapattinam). Championed Cauvery delta tail-end canal desilting, agricultural labor daily wages, multi-purpose cyclone shelters, and salinity protection bunds.",
        "key_achievements": [
            "Conducted desilting and tail-end sluice gate repairs across Cauvery Delta irrigation distributaries in Kilvelur.",
            "Constructed Multi-Purpose Cyclone Evacuation Center and community hall at Thirukuvalai.",
            "Modernized Kilvelur Government Taluk Hospital with round-the-clock emergency casualty.",
            "Constructed all-weather bitumen roads connecting 30 agricultural labor settlements.",
            "Installed RO clean drinking water plants across 18 tail-end delta villages preventing salinity contamination."
        ],
        "works": [
            {
                "id": "WRK-KIL-01",
                "title": "Cauvery Delta Tail-End Irrigation Canal Desilting & Sluice Gate Modernization",
                "title_ta": "காவிரி டெல்டா கடைமடை பாசனக் கால்வாய்கள் தூர்வாருதல் மற்றும் மதகுகள் புனரமைப்பு",
                "category": "Water & Sanitation",
                "description": "Desilted 48 km tail-end irrigation canals ensuring Mettur water reaches agricultural fields without coastal sea backflow.",
                "cost_cr": 18.0,
                "location": "Kilvelur Delta Channels",
                "year": "2021-2023",
                "status": "Completed",
                "source": "WRD Special Delta Package Order 2022",
                "source_url": "https://tnrd.tn.gov.in"
            },
            {
                "id": "WRK-KIL-02",
                "title": "Thirukuvalai Multi-Purpose Cyclone Evacuation Center & Disaster Hub",
                "title_ta": "திருக்குவளை பல்நோக்கு புயல் பாதுகாப்பு மையம்",
                "category": "Public Amenities",
                "description": "Constructed cyclone-resistant 2-storey refuge accommodating 1,000 residents with backup diesel generator and first-aid center.",
                "cost_cr": 4.2,
                "location": "Thirukuvalai, Kilvelur",
                "year": "2022-2023",
                "status": "Inaugurated",
                "source": "Nagapattinam District MLACDS Register",
                "source_url": "https://nagapattinam.nic.in"
            }
        ],
        "assembly_questions": [
            {
                "question_no": "Calling Attention Motion",
                "date": "2023-08-10",
                "subject": "Cauvery delta tail-end irrigation water crisis & kuruvai crop distress",
                "ministry": "Water Resources Department",
                "summary": "Demanded urgent release of Cauvery water from Mettur dam to save standing kuruvai paddy in tail-end Nagapattinam.",
                "status": "Debated"
            }
        ],
        "related_records": [
            {
                "id": "DMK-2021-039",
                "type": "promise",
                "type_label": "Election Promise",
                "title": "Cauvery delta tail-end irrigation canal modernization",
                "relationship_reason": "High-priority agrarian demand for protecting delta paddy crops.",
                "href": "/promises",
                "connection_type": "evidence_relationship",
                "confidence_score": 0.96
            },
            {
                "id": "CIV-NGP-001",
                "type": "civic",
                "type_label": "Civic Grievance",
                "title": "Cauvery delta tail-end coastal salinity ingress and sluice repair",
                "relationship_reason": "Monitored agrarian water grievance in Nagapattinam district.",
                "href": "/civic",
                "connection_type": "inferred_relationship",
                "confidence_score": 0.94
            }
        ]
    }
]

# Append additional reps
generate_representatives_data.REPRESENTATIVES.extend(additional_reps)
print(f"Total representatives after append: {len(generate_representatives_data.REPRESENTATIVES)}")

# Now run build_representatives()
generate_representatives_data.build_representatives()
