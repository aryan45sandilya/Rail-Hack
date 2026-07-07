import os
import random
import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Train, Route, Ticket, WLSnapshot, Prediction

load_dotenv(os.path.join(os.path.dirname(__file__), '..', '..', '.env'))

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///railhack.db")
print(f"Using database: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ─── 50+ Popular Indian Routes ────────────────────────────────────────────────
POPULAR_ROUTES = [
    # Original 20
    ("NDLS", "MMCT", "Delhi - Mumbai Central",         1386.0, 0.78),
    ("NDLS", "HWH",  "Delhi - Howrah",                 1447.0, 0.72),
    ("NDLS", "MAS",  "Delhi - Chennai Central",        2182.0, 0.65),
    ("SBC",  "HYB",  "Bangalore - Hyderabad",           610.0, 0.82),
    ("CSMT", "SBC",  "Mumbai - Bangalore",             1013.0, 0.74),
    ("HWH",  "CSMT", "Howrah - Mumbai CSMT",           1968.0, 0.68),
    ("HWH",  "MAS",  "Howrah - Chennai",               1661.0, 0.70),
    ("NDLS", "SBC",  "Delhi - Bangalore",              2365.0, 0.60),
    ("NDLS", "PNBE", "Delhi - Patna",                   998.0, 0.55),
    ("ADI",  "MMCT", "Ahmedabad - Mumbai Central",      491.0, 0.88),
    ("GKP",  "NDLS", "Gorakhpur - Delhi",               730.0, 0.50),
    ("CSMT", "PNBE", "Mumbai - Patna",                 1700.0, 0.45),
    ("SBC",  "MAS",  "Bangalore - Chennai",             357.0, 0.85),
    ("LKO",  "NDLS", "Lucknow - Delhi",                 512.0, 0.80),
    ("SC",   "HWH",  "Secunderabad - Howrah",          1545.0, 0.72),
    ("PUNE", "CSMT", "Pune - Mumbai CSMT",              192.0, 0.92),
    ("CNB",  "NDLS", "Kanpur - Delhi",                  440.0, 0.83),
    ("NDLS", "JAT",  "Delhi - Jammu Tawi",              577.0, 0.78),
    ("GHY",  "HWH",  "Guwahati - Howrah",               980.0, 0.65),
    ("CSMT", "MAS",  "Mumbai - Chennai",               1279.0, 0.70),
    # Rajasthan routes
    ("NDLS", "JP",   "Delhi - Jaipur",                  303.0, 0.85),
    ("JP",   "NDLS", "Jaipur - Delhi",                  303.0, 0.85),
    ("NDLS", "KOTA", "Delhi - Kota",                    458.0, 0.80),
    ("KOTA", "NDLS", "Kota - Delhi",                    458.0, 0.80),
    ("NDLS", "BKN",  "Delhi - Bikaner",                 458.0, 0.72),
    ("BKN",  "NDLS", "Bikaner - Delhi",                 458.0, 0.72),
    ("JP",   "MMCT", "Jaipur - Mumbai",                1196.0, 0.68),
    ("KOTA", "MMCT", "Kota - Mumbai",                   897.0, 0.74),
    ("JP",   "KOTA", "Jaipur - Kota",                   244.0, 0.88),
    ("UDZ",  "NDLS", "Udaipur - Delhi",                 739.0, 0.70),
    # Bihar / UP routes
    ("CPR",  "NDLS", "Chapra - Delhi",                  986.0, 0.48),
    ("CPR",  "PNBE", "Chapra - Patna",                  100.0, 0.82),
    ("PNBE", "HWH",  "Patna - Howrah",                  530.0, 0.75),
    ("PNBE", "NDLS", "Patna - Delhi",                   998.0, 0.55),
    ("BSB",  "NDLS", "Varanasi - Delhi",                789.0, 0.62),
    ("BSB",  "HWH",  "Varanasi - Howrah",               679.0, 0.68),
    ("ALD",  "NDLS", "Prayagraj - Delhi",               634.0, 0.70),
    ("GKP",  "LKO",  "Gorakhpur - Lucknow",             272.0, 0.78),
    # South India
    ("MAS",  "SBC",  "Chennai - Bangalore",             357.0, 0.85),
    ("MAS",  "HYB",  "Chennai - Hyderabad",             627.0, 0.78),
    ("ERS",  "NDLS", "Ernakulam - Delhi",              2820.0, 0.55),
    ("TVC",  "NDLS", "Thiruvananthapuram - Delhi",     3105.0, 0.50),
    ("CBE",  "MAS",  "Coimbatore - Chennai",            497.0, 0.80),
    ("MDU",  "MAS",  "Madurai - Chennai",               460.0, 0.78),
    # West India
    ("ADI",  "NDLS", "Ahmedabad - Delhi",               935.0, 0.75),
    ("ADI",  "SBC",  "Ahmedabad - Bangalore",          1514.0, 0.62),
    ("PUNE", "SBC",  "Pune - Bangalore",                841.0, 0.72),
    ("PUNE", "HYB",  "Pune - Hyderabad",                559.0, 0.76),
    ("NGP",  "NDLS", "Nagpur - Delhi",                  1094.0, 0.68),
    ("NGP",  "MMCT", "Nagpur - Mumbai",                  836.0, 0.74),
    # North / Central India
    ("BPL",  "NDLS", "Bhopal - Delhi",                  704.0, 0.78),
    ("BPL",  "MMCT", "Bhopal - Mumbai",                 779.0, 0.72),
    ("INDB", "NDLS", "Indore - Delhi",                  877.0, 0.70),
    ("INDB", "MMCT", "Indore - Mumbai",                 591.0, 0.76),
    ("AGC",  "NDLS", "Agra - Delhi",                    200.0, 0.90),
    ("MTJ",  "NDLS", "Mathura - Delhi",                 141.0, 0.92),
    # East / North-East
    ("DBRG", "HWH",  "Dibrugarh - Howrah",             1286.0, 0.58),
    ("GHY",  "NDLS", "Guwahati - Delhi",               1956.0, 0.55),
    ("RNC",  "HWH",  "Ranchi - Howrah",                 423.0, 0.75),
    ("BBS",  "HWH",  "Bhubaneswar - Howrah",            443.0, 0.80),
    ("BBS",  "MAS",  "Bhubaneswar - Chennai",          1047.0, 0.68),
]

# ─── Real Trains per Route ─────────────────────────────────────────────────────
ROUTE_TRAINS = {
    ("NDLS", "MMCT"): [
        ("12951", "Mumbai Rajdhani Express",        "Rajdhani"),
        ("12953", "August Kranti Rajdhani",         "Rajdhani"),
        ("12909", "Garib Rath Express",             "Garib Rath"),
        ("12925", "Paschim Express",                "Superfast Express"),
        ("12903", "Golden Temple Mail",             "Mail Express"),
    ],
    ("NDLS", "HWH"): [
        ("12301", "Howrah Rajdhani Express",        "Rajdhani"),
        ("12305", "Howrah Rajdhani (via Patna)",    "Rajdhani"),
        ("12381", "Poorva Express",                 "Superfast Express"),
        ("12311", "Kalka Mail",                     "Mail Express"),
        ("12259", "Sealdah Duronto Express",        "Duronto"),
    ],
    ("NDLS", "MAS"): [
        ("12615", "Grand Trunk Express",            "Superfast Express"),
        ("12621", "Tamil Nadu Express",             "Superfast Express"),
        ("12433", "Chennai Rajdhani Express",       "Rajdhani"),
        ("12269", "Chennai Duronto Express",        "Duronto"),
        ("12641", "Thirukkural Express",            "Superfast Express"),
    ],
    ("SBC",  "HYB"): [
        ("12785", "Kacheguda Express",              "Superfast Express"),
        ("17603", "Kacheguda-Bangalore Express",    "Express"),
        ("22691", "Rajdhani Express",               "Rajdhani"),
        ("12731", "Tirupati Garib Rath",            "Garib Rath"),
        ("17657", "Hampi Express",                  "Express"),
    ],
    ("CSMT", "SBC"): [
        ("11301", "Udyan Express",                  "Superfast Express"),
        ("16529", "Udyan Express (Daily)",          "Superfast Express"),
        ("11023", "Sahyadri Express",               "Express"),
        ("12779", "Goa Express",                    "Superfast Express"),
        ("16331", "Trivandrum Express",             "Superfast Express"),
    ],
    ("HWH",  "CSMT"): [
        ("12810", "Mumbai Mail",                    "Mail Express"),
        ("12860", "Gitanjali Express",              "Superfast Express"),
        ("22221", "CSMT Rajdhani Express",          "Rajdhani"),
        ("12262", "Howrah-Mumbai Duronto",          "Duronto"),
        ("12102", "Jnaneswari Super Deluxe",        "Superfast Express"),
    ],
    ("HWH",  "MAS"): [
        ("12841", "Coromandel Express",             "Superfast Express"),
        ("12839", "Chennai Mail",                   "Mail Express"),
        ("22807", "Chennai AC Express",             "AC Express"),
        ("12663", "Howrah-Trichy Express",          "Superfast Express"),
        ("12245", "Howrah-Yesvantpur Duronto",      "Duronto"),
    ],
    ("NDLS", "SBC"): [
        ("22691", "Rajdhani Express",               "Rajdhani"),
        ("12627", "Karnataka Express",              "Superfast Express"),
        ("12649", "Sampark Kranti Express",         "Superfast Express"),
        ("12677", "Ernakulam Express",              "Superfast Express"),
        ("16031", "Andaman Express",                "Express"),
    ],
    ("NDLS", "PNBE"): [
        ("12309", "Patna Rajdhani Express",         "Rajdhani"),
        ("12391", "Shramjeevi Express",             "Superfast Express"),
        ("12801", "Poorvottara Sampark Kranti",     "Superfast Express"),
        ("13201", "Rajendra Nagar Express",         "Express"),
        ("12578", "Bagmati Express",                "Superfast Express"),
    ],
    ("ADI",  "MMCT"): [
        ("12009", "Shatabdi Express",               "Shatabdi"),
        ("12901", "Gujarat Mail",                   "Mail Express"),
        ("12931", "Ahmedabad Double Decker",        "Double Decker"),
        ("19011", "Gujarat Express",                "Express"),
        ("12479", "Suryanagari Express",            "Superfast Express"),
    ],
    ("GKP",  "NDLS"): [
        ("12555", "Gorakhdham Express",             "Superfast Express"),
        ("15003", "Chauri Chaura Express",          "Express"),
        ("12591", "Gorakhpur Anand Vihar Express",  "Superfast Express"),
        ("14007", "Sadbhavna Express",              "Express"),
        ("12529", "Lucknow Anand Vihar Express",    "Superfast Express"),
    ],
    ("CSMT", "PNBE"): [
        ("11061", "Darbhanga Express",              "Express"),
        ("12141", "Mumbai-Patna Express",           "Superfast Express"),
        ("15268", "Raxaul Express",                 "Express"),
        ("12167", "Varanasi Express",               "Superfast Express"),
        ("11093", "Mahanagari Express",             "Express"),
    ],
    ("SBC",  "MAS"): [
        ("12007", "Shatabdi Express",               "Shatabdi"),
        ("12027", "Chennai Shatabdi",               "Shatabdi"),
        ("12609", "Intercity Express",              "Intercity"),
        ("12658", "Chennai Mail",                   "Mail Express"),
        ("22625", "Double Decker Express",          "Double Decker"),
    ],
    ("LKO",  "NDLS"): [
        ("12003", "Lucknow Shatabdi Express",       "Shatabdi"),
        ("12419", "Gomti Express",                  "Superfast Express"),
        ("12230", "Lucknow Mail",                   "Mail Express"),
        ("14853", "Marudhar Express",               "Express"),
        ("15107", "Avadh Express",                  "Express"),
    ],
    ("SC",   "HWH"): [
        ("12703", "Falaknuma Express",              "Superfast Express"),
        ("12659", "Gurudev Express",                "Superfast Express"),
        ("17005", "Hyderabad Express",              "Express"),
        ("12777", "Sipat Express",                  "Superfast Express"),
        ("12751", "Cocanada Express",               "Superfast Express"),
    ],
    ("PUNE", "CSMT"): [
        ("12127", "Intercity Express",              "Intercity"),
        ("12123", "Deccan Queen",                   "Superfast Express"),
        ("11007", "Deccan Express",                 "Express"),
        ("12025", "Pune Shatabdi",                  "Shatabdi"),
        ("12289", "Nagpur Duronto",                 "Duronto"),
    ],
    ("CNB",  "NDLS"): [
        ("12033", "Kanpur Shatabdi",                "Shatabdi"),
        ("12418", "Prayagraj Express",              "Superfast Express"),
        ("12275", "Allahabad Duronto",              "Duronto"),
        ("14213", "Kanpur Intercity",               "Intercity"),
        ("12307", "Jodhpur Express",                "Superfast Express"),
    ],
    ("NDLS", "JAT"): [
        ("12031", "Amritsar Shatabdi",              "Shatabdi"),
        ("12445", "Uttar Sampark Kranti",           "Superfast Express"),
        ("14609", "Hemkunt Express",                "Express"),
        ("12413", "Jammu Rajdhani",                 "Rajdhani"),
        ("12473", "Sarvodaya Express",              "Express"),
    ],
    ("GHY",  "HWH"): [
        ("12345", "Saraighat Express",              "Superfast Express"),
        ("12235", "Dibrugarh Rajdhani",             "Rajdhani"),
        ("15959", "Kamrup Express",                 "Express"),
        ("12423", "Dibrugarh Town Rajdhani",        "Rajdhani"),
        ("15645", "Guwahati Express",               "Express"),
    ],
    ("CSMT", "MAS"): [
        ("11041", "Chennai Express",                "Superfast Express"),
        ("12163", "Dadar-Chennai Express",          "Superfast Express"),
        ("22115", "Kochuveli AC Express",           "AC Express"),
        ("16331", "Trivandrum Express",             "Superfast Express"),
        ("12201", "Mumbai-Chennai Garib Rath",      "Garib Rath"),
    ],
    # Rajasthan
    ("NDLS", "JP"): [
        ("12015", "Ajmer Shatabdi Express",         "Shatabdi"),
        ("12957", "Swarna Jayanti Rajdhani",        "Rajdhani"),
        ("12903", "Golden Temple Mail",             "Mail Express"),
        ("12461", "Mandore Express",                "Superfast Express"),
        ("22991", "Jaipur Intercity",               "Intercity"),
    ],
    ("JP",   "NDLS"): [
        ("12016", "Ajmer Shatabdi Express",         "Shatabdi"),
        ("12958", "Swarna Jayanti Rajdhani",        "Rajdhani"),
        ("12462", "Mandore Express",                "Superfast Express"),
        ("12904", "Golden Temple Mail",             "Mail Express"),
        ("12992", "Jaipur Intercity",               "Intercity"),
    ],
    ("NDLS", "KOTA"): [
        ("12059", "Kota Janshatabdi Express",       "Jan Shatabdi"),
        ("12903", "Golden Temple Mail",             "Mail Express"),
        ("12963", "Mewar Express",                  "Superfast Express"),
        ("12465", "Ranthambore Express",            "Superfast Express"),
        ("19665", "Kurj Express",                   "Express"),
    ],
    ("KOTA", "NDLS"): [
        ("12060", "Kota Janshatabdi Express",       "Jan Shatabdi"),
        ("12904", "Golden Temple Mail",             "Mail Express"),
        ("12964", "Mewar Express",                  "Superfast Express"),
        ("12466", "Ranthambore Express",            "Superfast Express"),
        ("12951", "Mumbai Rajdhani Express",        "Rajdhani"),
    ],
    ("NDLS", "BKN"): [
        ("12461", "Mandore Express",                "Superfast Express"),
        ("14659", "Bikaner Express",                "Express"),
        ("12467", "Leelan Express",                 "Superfast Express"),
        ("14791", "Bikaner Dehradun Express",       "Express"),
        ("12915", "Ashram Express",                 "Superfast Express"),
    ],
    ("BKN",  "NDLS"): [
        ("12462", "Mandore Express",                "Superfast Express"),
        ("14660", "Bikaner Express",                "Express"),
        ("12468", "Leelan Express",                 "Superfast Express"),
        ("12916", "Ashram Express",                 "Superfast Express"),
        ("14792", "Bikaner Dehradun Express",       "Express"),
    ],
    ("JP",   "MMCT"): [
        ("12955", "Mumbai Superfast Express",       "Superfast Express"),
        ("22951", "DEE-BDTS Superfast",             "Superfast Express"),
        ("12991", "Jaipur-Udaipur Express",         "Superfast Express"),
        ("12997", "Ajmer-Bangalore Express",        "Superfast Express"),
        ("14701", "Sriganganagar Express",          "Express"),
    ],
    ("KOTA", "MMCT"): [
        ("12903", "Golden Temple Mail",             "Mail Express"),
        ("12963", "Mewar Express",                  "Superfast Express"),
        ("11059", "Chhattisgarh Express",           "Express"),
        ("12951", "Mumbai Rajdhani Express",        "Rajdhani"),
        ("19023", "Firozpur Janta Express",         "Express"),
    ],
    ("JP",   "KOTA"): [
        ("12059", "Kota Janshatabdi Express",       "Jan Shatabdi"),
        ("12963", "Mewar Express",                  "Superfast Express"),
        ("12465", "Ranthambore Express",            "Superfast Express"),
        ("12903", "Golden Temple Mail",             "Mail Express"),
        ("22991", "Jaipur Intercity",               "Intercity"),
    ],
    ("UDZ",  "NDLS"): [
        ("12963", "Mewar Express",                  "Superfast Express"),
        ("12991", "Udaipur City Express",           "Superfast Express"),
        ("19601", "Udaipur-Ahmedabad Express",      "Express"),
        ("12951", "Mumbai Rajdhani Express",        "Rajdhani"),
        ("12961", "Avantika Express",               "Superfast Express"),
    ],
    # Bihar / UP
    ("CPR",  "NDLS"): [
        ("13049", "Amritsar Express",               "Express"),
        ("12553", "Vaishali Express",               "Superfast Express"),
        ("15027", "Maurya Express",                 "Express"),
        ("12557", "Sapt Kranti Express",            "Superfast Express"),
        ("14005", "Lichchhavi Express",             "Express"),
    ],
    ("CPR",  "PNBE"): [
        ("15028", "Maurya Express",                 "Express"),
        ("15204", "LJN-PNBE Express",               "Express"),
        ("13201", "Rajendra Nagar Express",         "Express"),
        ("12557", "Sapt Kranti Express",            "Superfast Express"),
        ("15024", "Gorakhpur-Patna Express",        "Express"),
    ],
    ("PNBE", "HWH"): [
        ("12302", "New Delhi Rajdhani",             "Rajdhani"),
        ("12306", "Howrah Rajdhani",                "Rajdhani"),
        ("12382", "Poorva Express",                 "Superfast Express"),
        ("13150", "Kavi Guru Express",              "Express"),
        ("12340", "Coalfield Express",              "Superfast Express"),
    ],
    ("PNBE", "NDLS"): [
        ("12309", "Patna Rajdhani Express",         "Rajdhani"),
        ("12391", "Shramjeevi Express",             "Superfast Express"),
        ("12578", "Bagmati Express",                "Superfast Express"),
        ("13201", "Rajendra Nagar Express",         "Express"),
        ("12801", "Poorvottara Sampark Kranti",     "Superfast Express"),
    ],
    ("BSB",  "NDLS"): [
        ("12559", "Shiv Ganga Express",             "Superfast Express"),
        ("12583", "Lucknow Anand Vihar Express",    "Superfast Express"),
        ("15127", "Kashi Vishwanath Express",       "Express"),
        ("14257", "Kashi Express",                  "Express"),
        ("12817", "Jharkhand Sampark Kranti",       "Superfast Express"),
    ],
    ("BSB",  "HWH"): [
        ("13022", "Mithila Express",                "Express"),
        ("12818", "Jharkhand Sampark Kranti",       "Superfast Express"),
        ("12394", "Sampoorna Kranti Express",       "Superfast Express"),
        ("12876", "Neelachal Express",              "Superfast Express"),
        ("15024", "Gorakhpur-Patna Express",        "Express"),
    ],
    ("ALD",  "NDLS"): [
        ("12275", "Allahabad Duronto",              "Duronto"),
        ("12418", "Prayagraj Express",              "Superfast Express"),
        ("12417", "Prayagraj Express",              "Superfast Express"),
        ("14115", "Allahabad Express",              "Express"),
        ("12307", "Jodhpur Express",                "Superfast Express"),
    ],
    ("GKP",  "LKO"): [
        ("12592", "Gorakhpur LJN Express",          "Superfast Express"),
        ("15009", "Douriaganj Express",             "Express"),
        ("55020", "GKP LJN Passenger",              "Passenger"),
        ("12530", "Lucknow Express",                "Superfast Express"),
        ("15003", "Chauri Chaura Express",          "Express"),
    ],
    # South
    ("MAS",  "SBC"): [
        ("12008", "Shatabdi Express",               "Shatabdi"),
        ("12028", "Chennai Shatabdi",               "Shatabdi"),
        ("12610", "Intercity Express",              "Intercity"),
        ("12659", "Gurudev Express",                "Superfast Express"),
        ("22626", "Double Decker Express",          "Double Decker"),
    ],
    ("MAS",  "HYB"): [
        ("12759", "Charminar Express",              "Superfast Express"),
        ("12604", "Chennai Hyderabad Express",      "Superfast Express"),
        ("12794", "Rayalaseema Express",            "Superfast Express"),
        ("17057", "Devagiri Express",               "Express"),
        ("22693", "Rajdhani Express",               "Rajdhani"),
    ],
    ("ERS",  "NDLS"): [
        ("12625", "Kerala Express",                 "Superfast Express"),
        ("22641", "Swaraj Express",                 "Superfast Express"),
        ("16317", "Himsagar Express",               "Express"),
        ("12677", "Ernakulam Express",              "Superfast Express"),
        ("22113", "Kochuveli Rajdhani",             "Rajdhani"),
    ],
    ("TVC",  "NDLS"): [
        ("12625", "Kerala Express",                 "Superfast Express"),
        ("16317", "Himsagar Express",               "Express"),
        ("22113", "Kochuveli Rajdhani",             "Rajdhani"),
        ("16327", "Trivandrum Express",             "Express"),
        ("12431", "Trivandrum Rajdhani",            "Rajdhani"),
    ],
    ("CBE",  "MAS"): [
        ("12671", "Nilgiri Express",                "Superfast Express"),
        ("12243", "Coimbatore Shatabdi",            "Shatabdi"),
        ("12680", "Coimbatore Intercity",           "Intercity"),
        ("12696", "Kovai Express",                  "Superfast Express"),
        ("11013", "Mumbai-Coimbatore Express",      "Express"),
    ],
    ("MDU",  "MAS"): [
        ("12637", "Pandian Express",                "Superfast Express"),
        ("12175", "Chambal Express",                "Express"),
        ("12082", "Jan Shatabdi Express",           "Jan Shatabdi"),
        ("16101", "Boat Mail Express",              "Express"),
        ("22661", "NagerCoil Express",              "Superfast Express"),
    ],
    # West
    ("ADI",  "NDLS"): [
        ("12957", "Swarna Jayanti Rajdhani",        "Rajdhani"),
        ("12915", "Ashram Express",                 "Superfast Express"),
        ("12217", "Sampark Kranti Express",         "Superfast Express"),
        ("12995", "Ajmer Express",                  "Superfast Express"),
        ("12479", "Suryanagari Express",            "Superfast Express"),
    ],
    ("ADI",  "SBC"): [
        ("12997", "Ajmer-Bangalore Express",        "Superfast Express"),
        ("12295", "Sanghamitra Express",            "Superfast Express"),
        ("16209", "Ajmer-Mysore Express",           "Express"),
        ("12479", "Suryanagari Express",            "Superfast Express"),
        ("17017", "Rajkot-Hyderabad Express",       "Express"),
    ],
    ("PUNE", "SBC"): [
        ("11013", "Mumbai-Coimbatore Express",      "Express"),
        ("12779", "Goa Express",                    "Superfast Express"),
        ("16529", "Udyan Express",                  "Superfast Express"),
        ("12296", "Sanghamitra Express",            "Superfast Express"),
        ("12163", "Dadar-Chennai Express",          "Superfast Express"),
    ],
    ("PUNE", "HYB"): [
        ("12701", "Hussainsagar Express",           "Superfast Express"),
        ("17031", "Mumbai-Hyderabad Express",       "Express"),
        ("11401", "Nandigram Express",              "Express"),
        ("12289", "Nagpur Duronto",                 "Duronto"),
        ("12025", "Pune Shatabdi",                  "Shatabdi"),
    ],
    ("NGP",  "NDLS"): [
        ("12810", "Mumbai Mail",                    "Mail Express"),
        ("12419", "Gomti Express",                  "Superfast Express"),
        ("12293", "Allahabad Duronto",              "Duronto"),
        ("12841", "Coromandel Express",             "Superfast Express"),
        ("12001", "Bhopal Shatabdi",                "Shatabdi"),
    ],
    ("NGP",  "MMCT"): [
        ("11061", "Darbhanga Express",              "Express"),
        ("12809", "Mumbai Mail",                    "Mail Express"),
        ("12140", "Sewagram Express",               "Superfast Express"),
        ("12294", "Allahabad Duronto",              "Duronto"),
        ("12849", "Bilaspur Rajdhani",              "Rajdhani"),
    ],
    # Central
    ("BPL",  "NDLS"): [
        ("12001", "Bhopal Shatabdi Express",        "Shatabdi"),
        ("12137", "Punjab Mail",                    "Mail Express"),
        ("12627", "Karnataka Express",              "Superfast Express"),
        ("12615", "Grand Trunk Express",            "Superfast Express"),
        ("12293", "Allahabad Duronto",              "Duronto"),
    ],
    ("BPL",  "MMCT"): [
        ("11059", "Chhattisgarh Express",           "Express"),
        ("12138", "Punjab Mail",                    "Mail Express"),
        ("12140", "Sewagram Express",               "Superfast Express"),
        ("12294", "Allahabad Duronto",              "Duronto"),
        ("12233", "Itarsi Express",                 "Superfast Express"),
    ],
    ("INDB", "NDLS"): [
        ("12919", "Malwa Express",                  "Superfast Express"),
        ("12961", "Avantika Express",               "Superfast Express"),
        ("12415", "Indore Rajdhani",                "Rajdhani"),
        ("12965", "Rani Kamlapati Express",         "Superfast Express"),
        ("12921", "Flying Ranee",                   "Superfast Express"),
    ],
    ("INDB", "MMCT"): [
        ("12961", "Avantika Express",               "Superfast Express"),
        ("12918", "Gujarat Express",                "Superfast Express"),
        ("19307", "Chandigarh Express",             "Express"),
        ("12920", "Malwa Express",                  "Superfast Express"),
        ("12244", "Indore-Mumbai Duronto",          "Duronto"),
    ],
    ("AGC",  "NDLS"): [
        ("12280", "Taj Express",                    "Superfast Express"),
        ("12002", "Bhopal Shatabdi",                "Shatabdi"),
        ("12137", "Punjab Mail",                    "Mail Express"),
        ("12627", "Karnataka Express",              "Superfast Express"),
        ("12903", "Golden Temple Mail",             "Mail Express"),
    ],
    ("MTJ",  "NDLS"): [
        ("12280", "Taj Express",                    "Superfast Express"),
        ("12903", "Golden Temple Mail",             "Mail Express"),
        ("12627", "Karnataka Express",              "Superfast Express"),
        ("14553", "Himachal Express",               "Express"),
        ("12137", "Punjab Mail",                    "Mail Express"),
    ],
    # East / North-East
    ("DBRG", "HWH"): [
        ("12235", "Dibrugarh Rajdhani",             "Rajdhani"),
        ("12423", "Dibrugarh Town Rajdhani",        "Rajdhani"),
        ("15959", "Kamrup Express",                 "Express"),
        ("12345", "Saraighat Express",              "Superfast Express"),
        ("15910", "Avadh Assam Express",            "Express"),
    ],
    ("GHY",  "NDLS"): [
        ("12235", "Dibrugarh Rajdhani",             "Rajdhani"),
        ("12423", "Dibrugarh Town Rajdhani",        "Rajdhani"),
        ("12507", "Guwahati-Trivandrum Express",    "Superfast Express"),
        ("15910", "Avadh Assam Express",            "Express"),
        ("12345", "Saraighat Express",              "Superfast Express"),
    ],
    ("RNC",  "HWH"): [
        ("12817", "Jharkhand Sampark Kranti",       "Superfast Express"),
        ("12020", "Shatabdi Express",               "Shatabdi"),
        ("18615", "Kriya Yoga Express",             "Express"),
        ("12896", "Howrah-Puri Express",            "Superfast Express"),
        ("18609", "Ranchi-Patna Express",           "Express"),
    ],
    ("BBS",  "HWH"): [
        ("12841", "Coromandel Express",             "Superfast Express"),
        ("12877", "Neelachal Express",              "Superfast Express"),
        ("22811", "Bhubaneswar Rajdhani",           "Rajdhani"),
        ("12821", "Dhauli Express",                 "Superfast Express"),
        ("18410", "Sri Jagannath Express",          "Express"),
    ],
    ("BBS",  "MAS"): [
        ("12841", "Coromandel Express",             "Superfast Express"),
        ("12839", "Chennai Mail",                   "Mail Express"),
        ("12863", "Howrah-Yesvantpur Express",      "Superfast Express"),
        ("22807", "Chennai AC Express",             "AC Express"),
        ("18495", "Bhubaneswar-Bikaner Express",    "Express"),
    ],
}

random.seed(42)

def generate_trains_and_routes(db):
    routes_db = []
    for src, dst, name, dist, rate in POPULAR_ROUTES:
        route = Route(source_station=src, dest_station=dst, distance_km=dist, avg_confirm_rate=rate)
        db.add(route)
        routes_db.append((route, src, dst))
    db.commit()

    train_map = {}
    trains_db = []
    for route_obj, src, dst in routes_db:
        for num, name, ttype in ROUTE_TRAINS.get((src, dst), []):
            if num not in train_map:
                t = Train(train_number=num, train_name=name, train_type=ttype)
                db.add(t)
                train_map[num] = t
        db.commit()
        for num, _, _ in ROUTE_TRAINS.get((src, dst), []):
            trains_db.append((train_map[num], route_obj))

    print(f"Seeded {len(routes_db)} routes and {len(train_map)} unique trains.")
    return routes_db, trains_db


def generate_historical_tickets(db, routes_db, trains_db):
    quotas        = ["GN", "TQ", "LD", "SS"]
    quota_weights = [0.70, 0.15, 0.08, 0.07]
    classes       = ["SL", "3A", "2A", "1A"]
    class_weights = [0.45, 0.35, 0.15, 0.05]
    tickets_count = 8000
    base_date     = datetime.date(2026, 7, 10)

    route_train_map = {}
    for train_obj, route_obj in trains_db:
        route_train_map.setdefault(route_obj.id, []).append(train_obj)

    routes_list = [r for r, _, _ in routes_db]
    ticket_instances = []

    for _ in range(tickets_count):
        route       = random.choice(routes_list)
        avail       = route_train_map.get(route.id, [t for t, _ in trains_db])
        train       = random.choice(avail)
        quota       = random.choices(quotas, weights=quota_weights)[0]
        coach_class = random.choices(classes, weights=class_weights)[0]

        days_offset  = random.randint(-90, 30)
        journey_date = base_date + datetime.timedelta(days=days_offset)
        days_before  = random.randint(15, 45)
        booked_at    = datetime.datetime.combine(
            journey_date - datetime.timedelta(days=days_before),
            datetime.time(random.randint(6, 22), random.randint(0, 59))
        )

        wl_mult    = {"SL": 1.5, "3A": 1.0, "2A": 0.7, "1A": 0.4}.get(coach_class, 1.0)
        initial_wl = int(random.randint(5, 100) * wl_mult)

        prob  = route.avg_confirm_rate
        prob += {"GN": 0.0, "TQ": -0.15, "LD": 0.02, "SS": 0.05}.get(quota, 0)
        prob += {"SL": -0.05, "3A": 0.08, "2A": 0.12, "1A": 0.18}.get(coach_class, 0)
        prob *= max(0.1, 1.0 - (initial_wl / (80.0 * wl_mult)))
        if journey_date.month in [10, 11, 12]: prob -= 0.15
        if days_before > 30: prob += 0.05
        prob = max(0.05, min(0.95, prob))

        confirmed = random.random() < prob
        final_wl  = None if confirmed else max(1, int(initial_wl * random.uniform(0.1, 0.7)))

        ticket = Ticket(
            train_id=train.id, route_id=route.id,
            quota=quota, coach_class=coach_class,
            initial_wl=initial_wl, final_wl=final_wl,
            confirmed=confirmed, journey_date=journey_date, booked_at=booked_at,
        )
        db.add(ticket)
        ticket_instances.append((ticket, initial_wl, final_wl or 0, confirmed, journey_date))

    db.commit()
    print(f"Seeded {tickets_count} ticket records.")

    snap_count = 0
    dc = {72: 0.80, 48: 0.55, 24: 0.30, 12: 0.12, 2: 0}
    du = {72: 0.90, 48: 0.80, 24: 0.65, 12: 0.55, 2: 0.45}
    for ticket, init_wl, fin_wl, conf, j_date in ticket_instances:
        for hrs in [72, 48, 24, 12, 2]:
            wl_val = int(init_wl * dc[hrs]) if conf else int(fin_wl + (init_wl - fin_wl) * du[hrs])
            wl_val = max(0 if (conf and hrs == 2) else 1, wl_val)
            db.add(WLSnapshot(
                ticket_id=ticket.id, wl_number=wl_val,
                hours_to_departure=hrs,
                recorded_at=datetime.datetime.combine(j_date, datetime.time(10, 0)) - datetime.timedelta(hours=hrs),
            ))
            snap_count += 1
    db.commit()
    print(f"Seeded {snap_count} waitlist snapshots.")


def main():
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(Route).count() > 0:
            print("Database already contains data. Skipping seed.")
            return
        routes_db, trains_db = generate_trains_and_routes(db)
        generate_historical_tickets(db, routes_db, trains_db)
        print("Database seeding completed successfully!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
