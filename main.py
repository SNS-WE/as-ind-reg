import streamlit as st
import sqlite3
import sqlitecloud
import hashlib
import re
import time
import pandas as pd


# Utility Functions
# def hash_password(password):
#     """Hashes the password using SHA-256."""
#     return hashlib.sha256(password.encode()).hexdigest()


def is_valid_email(email):
    """Validates email format."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email)

def isValid(phone):
    if phone is None or phone == 0:
        return False  # Return False if phone is None or zero

    # Convert to string and strip any unwanted spaces
    phone_str = str(phone).strip()

    # Regex pattern for valid mobile numbers (starting with 6-9 and followed by 9 digits)
    pattern = r"^[6-9][0-9]{9}$"
    
    # Use fullmatch to ensure the entire phone number matches the pattern
    return bool(re.fullmatch(pattern, phone_str))


def get_database_connection():
    """Returns a database connection."""
    conn = sqlitecloud.connect(
        "sqlitecloud://cqssetgvhz.sqlite.cloud:8860/industry_registration?apikey=v1hNkVAkbMH6JLN7FSU71ARA3aaEodfbuxJ9Cl9HbVQ"
    )
    conn.execute("PRAGMA foreign_keys = ON;")
      # Explicitly enable foreign keys
    return conn

def create_database_tables():
    """Creates the required database tables if not already present."""
    with get_database_connection() as conn:
        c = conn.cursor()
        # Create tables if they do not exist
        c.execute('''
                    CREATE TABLE IF NOT EXISTS user_as (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        email TEXT UNIQUE,
                        password TEXT
                    )
                ''')
        # Admin table for admin login
        c.execute('''
                    CREATE TABLE IF NOT EXISTS admin_as (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE,
                        password TEXT
                    )
                ''')
        # Industry Table
        c.execute('''
                    CREATE TABLE IF NOT EXISTS industry_as (
                        ind_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER UNIQUE,
                        user_id_ind TEXT UNIQUE,
                        industry_category TEXT,
                        state_ocmms_id TEXT UNIQUE,
                        cpcb_ind_code TEXT UNIQUE,
                        industry_name TEXT,
                        address TEXT,
                        state TEXT,
                        district TEXT,
                        production_capacity TEXT,
                        num_stacks INTEGER,
                        industry_environment_head TEXT,
                        env_phone INTEGER,
                        industry_instrument_head TEXT,
                        inst_phone INTEGER,
                        concerned_person_cems TEXT,
                        cems_phone INTEGER,
                        industry_representative_email TEXT,
                        completed_stacks INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES user_as (id)
                    )
                ''')
        # Stacks Table
        c.execute('''
                    CREATE TABLE IF NOT EXISTS stacks_as (
                        stack_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        user_id_ind TEXT,
                        stack_identity TEXT,
                        process_attached TEXT,
                        apcd_details TEXT,
                        latitude REAL,
                        longitude REAL,
                        stack_condition TEXT,
                        stack_shape TEXT,
                        diameter REAL,
                        length REAL,
                        width REAL,
                        stack_material TEXT,
                        stack_height REAL,
                        platform_height REAL,
                        platform_approachable TEXT,
                        approaching_media TEXT,
                        cems_installed TEXT,
                        stack_params TEXT,
                        duct_params TEXT,
                        follows_formula TEXT,
                        manual_port_installed TEXT,
                        cems_below_manual TEXT,
                        parameters TEXT,
                        number_params INTEGER DEFAULT 0,
                        completed_parameters INTEGER DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES industry_as (ind_id)
                    )
                ''')
        # CEMS Instruments Table
        c.execute('''
                    CREATE TABLE IF NOT EXISTS cems_instruments_as (
                        cems_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        stack_id INTEGER,
                        user_id_ind TEXT,
                        parameter TEXT,
                        make TEXT,
                        model TEXT,
                        serial_number TEXT,
                        emission_limit REAL,
                        measuring_range_low REAL,
                        measuring_range_high REAL,
                        certified TEXT,
                        certification_agency TEXT,
                        communication_protocol TEXT,
                        measurement_method TEXT,
                        technology TEXT,
                        connected_bspcb TEXT,
                        bspcb_url TEXT,
                        cpcb_url TEXT,
                        connected_cpcb TEXT,
                        FOREIGN KEY (stack_id) REFERENCES stacks_as (stack_id)
                    )
                ''')  # Keep the existing table creation code as is
        conn.commit()


category = ["Aluminium", "Cement", "Chlor Alkali", "Copper", "Distillery", "Dye & Dye Intermediates", "Fertilizer",
            "Iron & Steel", "Oil Refinery", "Pesticides", "Petrochemical", "Pharmaceuticals", "Power Plant",
            "Pulp And Paper", "Sugar", "Tannery", "Zinc", "CETP", "STP", "Slaughter House", "Textile",
            "Food, Dairy & Beverages", "Common Hazardous Waste Treatment Facility",
            "Common Biomedical Waste Incinerators"]

state_list = ["Andaman And Nicobar Islands","Andhra Pradesh","Arunachal Pradesh","Gujarat","Assam","Bihar","Chandigarh","Chhattisgarh","Kerala",
              "Delhi","Goa","Haryana","Himachal Pradesh","Jammu And Kashmir","Maharashtra","Jharkhand","Karnataka","Ladakh","Lakshadweep",
              "Madhya Pradesh","Manipur","Meghalaya","Mizoram","Nagaland","Odisha","Puducherry","Punjab","Rajasthan","Sikkim","Tamil Nadu",
              "Telangana","The Dadra And Nagar Haveli And Daman And Diu","Tripura","Uttarakhand","Uttar Pradesh","West Bengal"]

dist_dict = {"Andaman And Nicobar Islands": ["Nicobars","North And Middle Andaman","South Andamans"],
             "Andhra Pradesh": ["Alluri Sitharama Raju","Anakapalli","Ananthapuramu","Annamayya","Bapatla","Chittoor","Dr. B.R. Ambedkar Konaseema",
                              "East Godavari","Eluru","Guntur","Kakinada","Krishna","Kurnool","Nandyal","Ntr","Palnadu","Parvathipuram Manyam",
                              "Prakasam","Srikakulam","Sri Potti Sriramulu Nellore","Sri Sathya Sai","Tirupati","Visakhapatnam","Vizianagaram",
                              "West Godavari","Y.S.R."],
             "Arunachal Pradesh": ["Anjaw","Bichom","Changlang","Dibang Valley","East Kameng","East Siang","Kamle","Keyi Panyor","Kra Daadi",
                                 "Kurung Kumey","Leparada","Lohit","Longding","Lower Dibang Valley","Lower Siang","Lower Subansiri","Namsai",
                                 "Pakke Kessang","Papum Pare","Shi Yomi","Siang","Tawang","Tirap","Upper Siang","Upper Subansiri","West Kameng",
                                 "West Siang"],
             "Gujarat": ["Sabar Kantha","Ahmedabad","Amreli","Anand","Arvalli","Banas Kantha","Bharuch","Bhavnagar","Botad","Chhotaudepur","Dahod",
                       "Dangs","Devbhumi Dwarka","Gandhinagar","Gir Somnath","Jamnagar","Junagadh","Kachchh","Kheda","Mahesana","Mahisagar",
                       "Morbi","Narmada","Navsari","Panch Mahals","Patan","Porbandar","Rajkot","Surat","Surendranagar","Tapi","Vadodara",
                       "Valsad"],
            "Assam": ["Bajali","Baksa","Barpeta","Biswanath","Bongaigaon","Cachar","Charaideo","Chirang","Darrang","Dhemaji","Dhubri","Dibrugarh",
                     "Dima Hasao","Goalpara","Golaghat","Hailakandi","Hojai","Jorhat","Kamrup","Kamrup Metro","Karbi Anglong","Karimganj",
                     "Kokrajhar","Lakhimpur","Majuli","Marigaon","Nagaon","Nalbari","Sivasagar","Sonitpur","South Salmara Mancachar",
                     "Tamulpur","Tinsukia","Udalguri","West Karbi Anglong"],
             "Bihar": ["Araria","Arwal","Aurangabad","Banka","Begusarai","Bhagalpur","Bhojpur","Buxar","Darbhanga","Gaya","Gopalganj","Jamui",
                     "Jehanabad","Kaimur (Bhabua)","Katihar","Khagaria","Kishanganj","Lakhisarai","Madhepura","Madhubani","Munger","Muzaffarpur",
                     "Nalanda","Nawada","Pashchim Champaran","Patna","Purbi Champaran","Purnia","Rohtas","Saharsa","Samastipur","Saran",
                     "Sheikhpura","Sheohar","Sitamarhi","Siwan","Supaul","Vaishali"],
             "Chandigarh": ["Chandigarh"],
             "Chhattisgarh": ["Balod","Balodabazar-Bhatapara","Balrampur-Ramanujganj","Bastar","Bemetara","Bijapur","Bilaspur",
                            "Dakshin Bastar Dantewada","Dhamtari","Durg","Gariyaband","Gaurela-Pendra-Marwahi","Janjgir-Champa","Jashpur",
                            "Kabeerdham","Khairagarh-Chhuikhadan-Gandai","Kondagaon","Korba","Korea","Mahasamund",
                            "Manendragarh-Chirmiri-Bharatpur(M C B)","Mohla-Manpur-Ambagarh Chouki","Mungeli","Narayanpur","Raigarh","Raipur",
                            "Rajnandgaon","Sakti","Sarangarh-Bilaigarh","Sukma","Surajpur","Surguja","Uttar Bastar Kanker"],
             "Kerala": ["Malappuram","Palakkad","Alappuzha","Ernakulam","Idukki","Kannur","Kasaragod","Kollam","Kottayam","Kozhikode",
                      "Pathanamthitta","Thiruvananthapuram","Thrissur","Wayanad"],
             "Delhi": ["Central","East","New Delhi","North","North East","North West","Shahdara","South","South East","South West","West"],
             "Goa": ["North Goa","South Goa"],
             "Haryana": ["Ambala","Bhiwani","Charkhi Dadri","Faridabad","Fatehabad","Gurugram","Hisar","Jhajjar","Jind","Kaithal","Karnal",
                       "Kurukshetra","Mahendragarh","Nuh","Palwal","Panchkula","Panipat","Rewari","Rohtak","Sirsa","Sonipat","Yamunanagar"],
             "Himachal Pradesh": ["Bilaspur","Chamba","Hamirpur","Kangra","Kinnaur","Kullu","Lahaul And Spiti","Mandi","Shimla","Sirmaur","Solan","Una"],
             "Jammu And Kashmir": ["Anantnag","Bandipora","Baramulla","Budgam","Doda","Ganderbal","Jammu","Kathua","Kishtwar","Kulgam","Kupwara",
                                 "Poonch","Pulwama","Rajouri","Ramban","Reasi","Samba","Shopian","Srinagar","Udhampur"],
             "Maharashtra": ["Akola","Ahilyanagar","Amravati","Beed","Bhandara","Buldhana","Chandrapur","Chhatrapati Sambhajinagar","Dharashiv","Dhule",
                           "Gadchiroli","Gondia","Hingoli","Jalgaon","Jalna","Kolhapur","Latur","Mumbai","Mumbai Suburban","Nagpur","Nanded","Nandurbar",
                           "Nashik","Palghar","Parbhani","Pune","Raigad","Ratnagiri","Sangli","Satara","Sindhudurg","Solapur","Thane","Wardha","Washim",
                           "Yavatmal"],
             "Jharkhand": ["Bokaro","Chatra","Deoghar","Dhanbad","Dumka","East Singhbum","Garhwa","Giridih","Godda","Gumla","Hazaribagh","Jamtara",
                         "Khunti","Koderma","Latehar","Lohardaga","Pakur","Palamu","Ramgarh","Ranchi","Sahebganj","Saraikela Kharsawan","Simdega",
                         "West Singhbhum"],
             "Karnataka": ["Bagalkote","Ballari","Belagavi","Bengaluru Rural","Bengaluru Urban","Bidar","Chamarajanagar","Chikkaballapura","Chikkamagaluru"
                         ,"Chitradurga","Dakshina Kannada","Davanagere","Dharwad","Gadag","Hassan","Haveri","Kalaburagi","Kodagu","Kolar","Koppal",
                         "Mandya","Mysuru","Raichur","Ramanagara","Shivamogga","Tumakuru","Udupi","Uttara Kannada","Vijayanagara","Vijayapura","Yadgir"],
             "Ladakh": ["Kargil","Leh Ladakh"],
             "Lakshadweep": ["Lakshadweep District"],
             "Madhya Pradesh": ["Agar-Malwa","Alirajpur","Anuppur","Ashoknagar","Balaghat","Barwani","Betul","Bhind","Bhopal","Burhanpur","Chhatarpur",
                              "Chhindwara","Damoh","Datia","Dewas","Dhar","Dindori","Guna","Gwalior","Harda","Indore","Jabalpur","Jhabua","Katni",
                              "Khandwa (East Nimar)","Khargone (West Nimar)","Maihar","Mandla","Mandsaur","MAUGANJ","Morena","Narmadapuram","Narsimhapur",
                              "Neemuch","Niwari","Pandhurna","Panna","Raisen","Rajgarh","Ratlam","Rewa","Sagar","Satna","Sehore","Seoni","Shahdol",
                              "Shajapur","Sheopur","Shivpuri","Sidhi","Singrauli","Tikamgarh","Ujjain","Umaria","Vidisha"],
             "Manipur": ["Bishnupur","Chandel","Churachandpur","Imphal East","Imphal West","Jiribam","Kakching","Kamjong","Kangpokpi","Noney","Pherzawl",
                        "Senapati","Tamenglong","Tengnoupal","Thoubal","Ukhrul"],
             "Meghalaya": ["Eastern West Khasi Hills","East Garo Hills","East Jaintia Hills","East Khasi Hills","North Garo Hills","Ri Bhoi",
                         "South Garo Hills","South West Garo Hills","South West Khasi Hills","West Garo Hills","West Jaintia Hills","West Khasi Hills"],
             "Mizoram": ["Aizawl","Champhai","Hnahthial","Khawzawl","Kolasib","Lawngtlai","Lunglei","Mamit","Saitual","Serchhip","Siaha"],
             "Nagaland": ["Chumoukedima","Dimapur","Kiphire","Kohima","Longleng","Mokokchung","Mon","Niuland","Noklak","Peren","Phek","Shamator","Tseminyu",
                        "Tuensang","Wokha","Zunheboto"],
             "Odisha": ["Anugul","Balangir","Baleshwar","Bargarh","Bhadrak","Boudh","Cuttack","Deogarh","Dhenkanal","Gajapati","Ganjam","Jagatsinghapur",
                      "Jajapur","Jharsuguda","Kalahandi","Kandhamal","Kendrapara","Kendujhar","Khordha","Koraput","Malkangiri","Mayurbhanj","Nabarangpur",
                      "Nayagarh","Nuapada","Puri","Rayagada","Sambalpur","Sonepur","Sundargarh"],
             "Puducherry": ["Karaikal","Puducherry"],
             "Punjab": ["Amritsar","Barnala","Bathinda","Faridkot","Fatehgarh Sahib","Fazilka","Ferozepur","Gurdaspur","Hoshiarpur","Jalandhar",
                      "Kapurthala","Ludhiana","Malerkotla","Mansa","Moga","Pathankot","Patiala","Rupnagar","Sangrur","S.A.S Nagar",
                      "Shahid Bhagat Singh Nagar","Sri Muktsar Sahib","Tarn Taran"],
             "Rajasthan": ["Ajmer","Alwar","Anupgarh","Balotra","Banswara","Baran","Barmer","Beawar","Bharatpur","Bhilwara","Bikaner","Bundi",
                         "Chittorgarh","Churu","Dausa","Deeg","Dholpur","Didwana-Kuchaman","Dudu","Dungarpur","Ganganagar","Gangapurcity","Hanumangarh",
                         "Jaipur","Jaipur (Gramin)","Jaisalmer","Jalore","Jhalawar","Jhunjhunu","Jodhpur","Jodhpur (Gramin)","Karauli","Kekri",
                         "Khairthal-Tijara","Kota","Kotputli-Behror","Nagaur","Neem Ka Thana","Pali","Phalodi","Pratapgarh","Rajsamand","Salumbar",
                         "Sanchore","Sawai Madhopur","Shahpura","Sikar","Sirohi","Tonk","Udaipur"],
             "Sikkim": ["Gangtok","Gyalshing","Mangan","Namchi","Pakyong","Soreng"],
             "Tamil Nadu": ["Ariyalur","Chengalpattu","Chennai","Coimbatore","Cuddalore","Dharmapuri","Dindigul","Erode","Kallakurichi","Kancheepuram",
                          "Kanniyakumari","Karur","Krishnagiri","Madurai","Mayiladuthurai","Nagapattinam","Namakkal","Perambalur","Pudukkottai",
                          "Ramanathapuram","Ranipet","Salem","Sivaganga","Tenkasi","Thanjavur","Theni","The Nilgiris","Thiruvallur","Thiruvarur",
                          "Thoothukkudi","Tiruchirappalli","Tirunelveli","Tirupathur","Tiruppur","Tiruvannamalai","Vellore","Viluppuram","Virudhunagar"],
             "Telangana": ["Adilabad","Bhadradri Kothagudem","Hanumakonda","Hyderabad","Jagitial","Jangoan","Jayashankar Bhupalapally",
                         "Jogulamba Gadwal","Kamareddy","Karimnagar","Khammam","Kumuram Bheem Asifabad","Mahabubabad","Mahabubnagar",
                         "Mancherial","Medak","Medchal Malkajgiri","Mulugu","Nagarkurnool","Nalgonda","Narayanpet","Nirmal","Nizamabad",
                         "Peddapalli","Rajanna Sircilla","Ranga Reddy","Sangareddy","Siddipet","Suryapet","Vikarabad","Wanaparthy","Warangal",
                         "Yadadri Bhuvanagiri"],
            "The Dadra And Nagar Haveli And Daman And Diu": ["Dadra And Nagar Haveli","Daman","Diu"],
            "Tripura": ["Dhalai","Gomati","Khowai","North Tripura","Sepahijala","South Tripura","Unakoti","West Tripura"],
            "Uttarakhand": ["Almora","Bageshwar","Chamoli","Champawat","Dehradun","Haridwar","Nainital","Pauri Garhwal","Pithoragarh",
                          "Rudra Prayag","Tehri Garhwal","Udam Singh Nagar","Uttar Kashi"],
            "Uttar Pradesh": ["Agra","Aligarh","Ambedkar Nagar","Amethi","Amroha","Auraiya","Ayodhya","Azamgarh","Baghpat","Bahraich","Ballia",
                            "Balrampur","Banda","Bara Banki","Bareilly","Basti","Bhadohi","Bijnor","Budaun","Bulandshahr","Chandauli","Chitrakoot",
                            "Deoria","Etah","Etawah","Farrukhabad","Fatehpur","Firozabad","Gautam Buddha Nagar","Ghaziabad","Ghazipur","Gonda",
                            "Gorakhpur","Hamirpur","Hapur","Hardoi","Hathras","Jalaun","Jaunpur","Jhansi","Kannauj","Kanpur Dehat","Kanpur Nagar",
                            "Kasganj","Kaushambi","Kheri","Kushinagar","Lalitpur","Lucknow","Mahoba","Mahrajganj","Mainpuri","Mathura","Mau","Meerut",
                            "Mirzapur","Moradabad","Muzaffarnagar","Pilibhit","Pratapgarh","Prayagraj","Rae Bareli","Rampur","Saharanpur","Sambhal",
                            "Sant Kabir Nagar","Shahjahanpur","Shamli","Shrawasti","Siddharthnagar","Sitapur","Sonbhadra","Sultanpur","Unnao","Varanasi"],
            "West Bengal": ["Alipurduar","Bankura","Birbhum","Cooch Behar","Dakshin Dinajpur","Darjeeling","Hooghly","Howrah","Jalpaiguri","Jhargram",
                          "Kalimpong","Kolkata","Malda","Murshidabad","Nadia","North 24 Parganas","Paschim Bardhaman","Paschim Medinipur","Purba Bardhaman",
                          "Purba Medinipur","Purulia","South 24 Parganas","Uttar Dinajpur"]}


def refresh_page():
    st.markdown("""
        <meta http-equiv="refresh" content="2">
        """, unsafe_allow_html=True)


st.set_page_config(layout="wide")
                
def sidebar_forms(user_id):
    """Function to render the sidebar after login."""
    st.sidebar.title("Navigation")

    #  # Ensure the correct page loads even if sidebar is not clicked
    # if st.session_state.get("current_page") == "Industry Dashboard":
    #     show_industry_dashboard(user_id)
    #     return  # Prevent sidebar from re-rendering unnecessarily

    # Conditional rendering of sidebar options based on login status
    if st.session_state.get("logged_in", False):
        menu = ["Industry Dashboard", "Stack Details", "CEMS Details", "Logout"] 
        #CEMS Suitability is removed. will be added latter.
    else:
        menu = ["Login", "Register Industry"]

    choice = st.sidebar.selectbox("Select an option", menu)

    # Ensure correct redirection
    if choice == "Industry Dashboard":
        show_industry_dashboard(user_id)
    elif choice == "Stack Details":
        fill_stacks(user_id)
    elif choice == "CEMS Details":
        fill_cems_details(user_id)
    elif choice == "CEMS Suitability":   
        cems_finder()
    elif choice == "Logout":
        logout()
        # st.session_state["logged_in"] = False
        # st.session_state["user_id"] = None
        # st.experimental_rerun() # Rerun to reflect the logged-out state


# Admin login page
def admin_login_page():
    st.subheader("Admin Login")
    username = st.text_input("Username", key="admin_username")
    password = st.text_input("Password", type="password", key="admin_password")
    login_button = st.button("Login as Admin")

    if login_button:
        with get_database_connection() as conn:
            c = conn.cursor()
            c.execute("SELECT password FROM admin_as WHERE username = ?", (username,))
            admin = c.fetchone()
            if admin and hash_password(password) == admin[0]:
                st.success("Admin login successful!")
                st.session_state["admin_logged_in"] = True
                st.rerun()  # Redirect to refresh the session
            else:
                st.error("Invalid admin credentials.")


def admin_dashboard():
    st.markdown(f"<h3 style='text-align: center'>Admin Dashboard</h3>", unsafe_allow_html=True)
    # Add a "Home" button to return to the industry list
    if st.sidebar.button("Return to Dasboard"):
        st.session_state["selected_ind_id"] = None  # Clear the selected industry
        st.rerun()  # Refresh the page to go back to the main list

    # Logout button
    if st.sidebar.button("Logout", key="admin_logout"):
        st.session_state["admin_logged_in"] = False
        st.rerun()  # Redirect back to login

    # Check if an industry has been selected
    if "selected_ind_id" in st.session_state and st.session_state["selected_ind_id"]:
        # Show industry details if an industry is selected
        show_industry_details(st.session_state["selected_ind_id"])
    else:
        # Display the list of all industries
        display_all_details()


def display_all_details():
    """Display all user-filled industry details with buttons in each row using `st.columns`."""
    # st.subheader("All User-Filled Industry Details")  # Display the heading once at the top
    with get_database_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM industry_as")
        industries = c.fetchall()

        if industries:
            # Create a DataFrame for better visualization
            df = pd.DataFrame(industries, columns=[col[0] for col in c.description])
            ind_df = df[['state_ocmms_id', 'industry_name', 'industry_category', 'cpcb_ind_code', 'address', 'district',
                         'production_capacity', 'num_stacks', 'industry_environment_head',
                         'concerned_person_cems', 'industry_representative_email', 'ind_id']]

            # Search functionality
            search_term = st.text_input("Search Industry", "")
            if search_term:
                ind_df = ind_df[ind_df['industry_name'].str.contains(search_term, case=False, na=False)]

            columns = st.columns([1, 1, 1, 1, 1, 1, 1, 1])  # Column widths for Streamlit layout
            labels = ["Industry Name", "Category", "State OCMMS Id", "CPCB Industry Code", "District", "Production Capacity", "No. of Stacks",
                      "Actions"]

            for col, label in zip(columns, labels):
                with col:
                    st.markdown(f"**{label}**")

            for _, row in ind_df.iterrows():
                cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1])  # Adjust column widths as needed
                db_labels = ["industry_name", "industry_category", "state_ocmms_id", "cpcb_ind_code", "district", "production_capacity",
                             "num_stacks"]

                for col, db_labels in zip(cols, db_labels):
                    with col:
                        st.markdown(f"{row[db_labels]}")

                with cols[-1]:  # Last column for the button
                    if st.button("View", key=f"view_{row['ind_id']}"):
                        # Store both the ind_id and state_ocmms_id in session state
                        st.session_state["selected_ind_id"] = row["ind_id"]
                        st.session_state["selected_state_ocmms_id"] = row["state_ocmms_id"]
                        st.rerun()
                st.markdown("<hr>", unsafe_allow_html=True)
        else:
            st.warning("No industry details found.")

def show_industry_details(ind_id):
    """Show detailed information for the selected industry."""

    st.markdown("<h3 style='text-align: center; color: black;'>Industry Details</h3>", unsafe_allow_html=True)

    def fetch_data(query, params=None):
        """Fetch data from the database."""
        with get_database_connection() as conn:
            c = conn.cursor()
            c.execute(query, params or ())
            data = c.fetchall()
            columns = [desc[0] for desc in c.description]  # Extract column names
            return pd.DataFrame(data, columns=columns) if data else None

    # Fetch Industry Details
    industry_query = "SELECT * FROM industry_as WHERE ind_id = ?"
    industry_data = fetch_data(industry_query, (ind_id,))

    # Fetch Stack Details
    stack_query = "SELECT * FROM stacks_as WHERE user_id_ind = ?"
    stack_data = fetch_data(stack_query, (f"ind_{ind_id}",))
    #
    # Fetch CEMS Details
    cems_query = "SELECT * FROM cems_instruments_as WHERE user_id_ind = ?"
    cems_data = fetch_data(cems_query, (f"ind_{ind_id}",))

    # Display Industry Details
    if industry_data is not None:
        # st.markdown("### Industry Details")
        industry = industry_data.iloc[0]  # Assuming one industry per user
        industry_details = {
            "Industry State OCMMS Code": industry['state_ocmms_id'],
            "CPCB Industry Code": industry['cpcb_ind_code'],
            "Industry Category": industry['industry_category'],
            "Industry Name": industry['industry_name'],
            "Address": industry['address'],
            "District": industry['district'],
            "State": industry['state'],
            "Production Capacity": industry['production_capacity'],
            "Number of stacks": industry['num_stacks'],
            "Environment Department Head": industry['industry_environment_head'],
            "Environment Head Phone Number": industry['env_phone'],
            "Instrumentation Department Head": industry['industry_instrument_head'],
            "Instrumentation Head Phone Number": industry['inst_phone'],
            "Concerned Person for CEMS": industry['concerned_person_cems'],
            "Concerned Person for CEMS Phone Number": industry['cems_phone'],
            "Industry Representative Email Id": industry['industry_representative_email'],
        }
        for field, value in industry_details.items():
            with st.container():
                cols = st.columns([1, 3])  # Adjust widths as needed
                cols[0].markdown(f"<p style='font-weight: bold; text-align: left;'>{field}:</p>",
                                 unsafe_allow_html=True)
                cols[1].markdown(f"<p style='text-align: left;'>{value}</p>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.warning("No Industry Details Found.")

    # Display Stack Details with Associated CEMS Parameters Horizontally
    if stack_data is not None:
        st.markdown("### Stack and CEMS Details")
        for i, stack in stack_data.iterrows():
            st.markdown(f"#### Stack {i + 1} Details")
            table_data = {
                # "Stack ID": stack_data["stack_id"],
                "Stack Identity or identification Number": stack_data["stack_identity"],
                "Attached Process": stack_data["process_attached"],
                "APCD": stack_data["apcd_details"],
                "Latitude": stack_data["latitude"],
                "Longitude": stack_data["longitude"],
                "Stack Type": stack_data["stack_shape"],
                "Construction Material": stack_data["stack_material"],
                "Diameter (m)": stack_data["diameter"],
                "Length (m)": stack_data["length"],
                "Width (m)": stack_data["width"],
                "Stack Height (m)": stack_data["stack_height"],
                "Platform located at (m)": stack_data["platform_height"],
                "Platform Approachable": stack_data["platform_approachable"],
                "Approaching Media": stack_data["approaching_media"],
                "CEMS Installed": stack_data["cems_installed"],
                "Stack Params": stack_data["stack_params"],
                "Duct Params": stack_data["duct_params"],
                "Follows Formula": stack_data["follows_formula"],
                "Manual Porthole Provided": stack_data["manual_port_installed"],
                "CEMS Below Manual": stack_data["cems_below_manual"],
                "Parameters": stack_data["parameters"],
            }

            # Convert dictionary to DataFrame
            stck_df = pd.DataFrame(table_data)
            stck_df.index = [f"Stack_{i + 1}" for i in range(len(stck_df))]
            stck_x = stck_df.iloc[i:i + 1]
            stck_x.dropna(axis=1, how='all', inplace=True)
            # Display as a table
            # st.table(stck_x)

            # Convert DataFrame to HTML
            html = stck_x.to_html(index=False)

            # Generate CSS for column widths
            column_count = len(stck_x.columns)
            default_width = 100  # Default width for all columns
            specific_widths = {
                # 2: 50,  # Width for the first column
                # Width for the second column
                # Add more specific widths as needed
            }

            # Create CSS rules
            css_rules = []
            for i in range(1, column_count + 1):
                width = specific_widths.get(i, default_width)  # Use specific width or default
                css_rules.append(f"th:nth-child({i}), td:nth-child({i}) {{ width: {width}px; }}")

            # Combine CSS rules
            custom_css = f"""
            <style>
                table {{
                    width: 100%;  /* Set the table width */
                    border-collapse: collapse;  /* Optional: for better border handling */
                }}
                th, td {{
                    border: 1px solid #ddd;  /* Optional: add borders to cells */
                    padding: 8px;  /* Optional: add padding to cells */
                    text-align: center;  /* Optional: align text to the left */
                }}
                {" ".join(css_rules)}  /* Add all CSS rules */
            </style>
            """

            # Display the table with custom CSS
            st.markdown(custom_css, unsafe_allow_html=True)
            st.markdown(html, unsafe_allow_html=True)

            cems_for_stack = pd.DataFrame()  # default to an empty DF

            # Filter CEMS details for this stack
            if cems_data is not None:
                cems_for_stack = cems_data[cems_data['stack_id'] == stack['stack_id']]
            st.markdown("##### Parameter Details")
            if not cems_for_stack.empty:
                for j, cems in cems_for_stack.iterrows():
                    table_param = {
                        "Parameter": cems['parameter'],
                        "Make": cems['make'],
                        "Model": cems['model'],
                        "Serial Number": cems['serial_number'],
                        "SPCB Approved Emission Limit": cems['emission_limit'],
                        "Measuring Range (Low)": cems['measuring_range_low'],
                        "Measuring Range (High)": cems['measuring_range_high'],
                        "Is Certified?": cems['certified'],
                        "Certification Agency": cems['certification_agency'],
                        "Communication Protocol": cems['communication_protocol'],
                        "Measurement Method": cems['measurement_method'],
                        "Technology": cems['technology'],
                        "Connected to SPCB?": cems['connected_bspcb'],
                        "SPCB URL": cems['bspcb_url'],
                        "Connected to CPCB?": cems['connected_cpcb'],
                        "CPCB URL": cems['cpcb_url'],
                    }

                    # Convert dictionary to DataFrame
                    param_df = pd.DataFrame(table_param, index=[0])  # Create a DataFrame with a single row
                    param_df.dropna(axis=1, how='all', inplace=True)

                    # Convert DataFrame to HTML
                    html = param_df.to_html(index=False)

                    # Generate CSS for column widths
                    column_count = len(param_df.columns)
                    default_width = 100  # Default width for all columns
                    specific_widths = {
                        # 2: 50,  # Width for the first column
                        # Width for the second column
                        # Add more specific widths as needed
                    }

                    # Create CSS rules
                    css_rules = []
                    for i in range(1, column_count + 1):
                        width = specific_widths.get(i, default_width)  # Use specific width or default
                        css_rules.append(f"th:nth-child({i}), td:nth-child({i}) {{ width: {width}px; }}")

                    # Combine CSS rules
                    custom_css = f"""
                                <style>
                                    table {{
                                        width: 100%;  /* Set the table width */
                                        border-collapse: collapse;  /* Optional: for better border handling */
                                    }}
                                    th, td {{
                                        border: 1px solid #ddd;  /* Optional: add borders to cells */
                                        padding: 8px;  /* Optional: add padding to cells */
                                        text-align: center;  /* Optional: align text to the left */
                                    }}
                                    {" ".join(css_rules)}  /* Add all CSS rules */
                                </style>
                                """

                    # Display the table with custom CSS
                    st.markdown(custom_css, unsafe_allow_html=True)
                    st.markdown(html, unsafe_allow_html=True)
            else:
                st.warning(f"No CEMS Details Found for Stack {stack['stack_id']}.")
    else:
        st.warning("No Stack Details Found.")

def logout():
    """Function to log out the user and reset session state."""
    # Reset session state
    st.session_state["logged_in"] = False
    st.session_state["user_id"] = None
    st.session_state["current_page"] = "Login"  # Ensure it redirects to the login page
    refresh_page()
    st.session_state.clear()  # Clear other session variables as well (optional)

    # Display a success message
    st.success("You have successfully logged out.")


def cems_finder():
    st.markdown("## CEMS Finder Tool")
    st.markdown(
        "Use this tool to determine the suitable Continuous Emission Monitoring System (CEMS) based on your industry category and process details.")

    # Dropdown for Industry Category
    industry_category = st.selectbox("Select Industry Category", [
        "Aluminium", "Cement", "Chlor Alkali", "Copper", "Distillery", "Dye & Dye Intermediates", "Fertilizer",
        "Iron & Steel", "Oil Refinery", "Pesticides", "Petrochemical", "Pharmaceuticals", "Power Plant",
        "Pulp And Paper", "Sugar", "Tannery", "Zinc", "CETP", "STP", "Slaughter House", "Textile",
        "Food, Dairy & Beverages", "Common Hazardous Waste Treatment Facility",
        "Common Biomedical Waste Incinerators"
    ], index=None, placeholder="Select Category")

    # Text input for process details
    process_details = st.text_area("Describe the process emitting pollutants")

    # Button to determine CEMS type
    if st.button("Find Suitable CEMS"):
        if not industry_category or not process_details:
            st.warning("Please fill in all fields to get recommendations.")
        else:
            # Basic logic for CEMS recommendation (This can be expanded based on actual requirements)
            cems_recommendation = ""
            if "boiler" in process_details.lower() or "furnace" in process_details.lower():
                cems_recommendation = "Extractive CEMS with Gas Analyzer"
            elif "chemical" in process_details.lower():
                cems_recommendation = "In-situ CEMS with Multi-Gas Detector"
            elif "combustion" in process_details.lower() or "refinery" in industry_category.lower():
                cems_recommendation = "FTIR-based CEMS for hydrocarbons and VOC monitoring"
            else:
                cems_recommendation = "Standard CEMS with Particulate and Gas Monitoring"

            st.success(f"Recommended CEMS Type: {cems_recommendation}")


def show_industry_dashboard(user_id):
    """Function to display the industry dashboard with industry details."""
    # st.subheader("Industry Dashboard")
    st.markdown("<h1 style='text-align: center; color: black;'>Industry Dashboard</h1>", unsafe_allow_html=True)

    def fetch_data(query, params=None):
        """Fetch data from the database."""
        with get_database_connection() as conn:
            c = conn.cursor()
            c.execute(query, params or ())
            data = c.fetchall()
            columns = [desc[0] for desc in c.description]  # Extract column names
            return pd.DataFrame(data, columns=columns) if data else None

    # Fetch Industry Details
    industry_query = "SELECT * FROM industry_as WHERE user_id = ?"
    industry_data = fetch_data(industry_query, (user_id,))

    # Fetch Stack Details
    stack_query = "SELECT * FROM stacks WHERE user_id = ?"
    stack_data = fetch_data(stack_query, (user_id,))
    #
    # Fetch CEMS Details
    cems_query = "SELECT * FROM cems_instruments WHERE user_id_ind = ?"
    cems_data = fetch_data(cems_query, (f"ind_{user_id}",))

    # Display Industry Details
    if industry_data is not None:
        st.markdown("### Industry Details")
        industry = industry_data.iloc[0]  # Assuming one industry per user
        industry_details = {
            "Industry State OCMMS Code": industry['state_ocmms_id'],
            "CPCB Industry Code": industry['cpcb_ind_code'],
            "Industry Category": industry['industry_category'],
            "Industry Name": industry['industry_name'],
            "Address": industry['address'],
            "District": industry['district'],
            "State": industry['state'],
            "Production Capacity": industry['production_capacity'],
            "Number of stacks": industry['num_stacks'],
            "Environment Department Head": industry['industry_environment_head'],
            "Environment Head Phone Number": industry['env_phone'],
            "Instrumentation Department Head": industry['industry_instrument_head'],
            "Instrumentation Head Phone Number": industry['inst_phone'],
            "Concerned Person for CEMS": industry['concerned_person_cems'],
            "Concerned Person for CEMS Phone Number": industry['cems_phone'],
            "Industry Representative Email Id": industry['industry_representative_email'],
        }
        for field, value in industry_details.items():
            with st.container():
                cols = st.columns([1, 3])  # Adjust widths as needed
                cols[0].markdown(f"<p style='font-weight: bold; text-align: left;'>{field}:</p>",
                                 unsafe_allow_html=True)
                cols[1].markdown(f"<p style='text-align: left;'>{value}</p>", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)
    else:
        st.warning("No Industry Details Found.")

    # Display Stack Details with Associated CEMS Parameters Horizontally
    if stack_data is not None:
        st.markdown("### Stack and CEMS Details")
        for i, stack in stack_data.iterrows():
            st.markdown(f"#### Stack {i + 1} Details")
            table_data = {
                # "Stack ID": stack_data["stack_id"],
                "Stack Identity or identification Number": stack_data["stack_identity"],
                "Attached Process": stack_data["process_attached"],
                "APCD": stack_data["apcd_details"],
                "Latitude": stack_data["latitude"],
                "Longitude": stack_data["longitude"],
                "Stack Type": stack_data["stack_shape"],
                "Construction Material": stack_data["stack_material"],
                "Diameter (m)": stack_data["diameter"],
                "Length (m)": stack_data["length"],
                "Width (m)": stack_data["width"],
                "Stack Height (m)": stack_data["stack_height"],
                "Platform located at (m)": stack_data["platform_height"],
                "Platform Approachable": stack_data["platform_approachable"],
                "Approaching Media": stack_data["approaching_media"],
                "CEMS Installed": stack_data["cems_installed"],
                "Stack Params": stack_data["stack_params"],
                "Duct Params": stack_data["duct_params"],
                "Follows Formula": stack_data["follows_formula"],
                "Manual Porthole Provided": stack_data["manual_port_installed"],
                "CEMS Below Manual": stack_data["cems_below_manual"],
                "Parameters": stack_data["parameters"],
            }

            # Convert dictionary to DataFrame
            stck_df = pd.DataFrame(table_data)
            stck_df.index = [f"Stack_{i + 1}" for i in range(len(stck_df))]
            stck_x = stck_df.iloc[i:i + 1]
            stck_x.dropna(axis=1, how='all', inplace=True)
            # Display as a table
            # st.table(stck_x)

            # Convert DataFrame to HTML
            html = stck_x.to_html(index=False)

            # Generate CSS for column widths
            column_count = len(stck_x.columns)
            default_width = 100  # Default width for all columns
            specific_widths = {
                # 2: 50,  # Width for the first column
                # Width for the second column
                # Add more specific widths as needed
            }

            # Create CSS rules
            css_rules = []
            for i in range(1, column_count + 1):
                width = specific_widths.get(i, default_width)  # Use specific width or default
                css_rules.append(f"th:nth-child({i}), td:nth-child({i}) {{ width: {width}px; }}")

            # Combine CSS rules
            custom_css = f"""
            <style>
                table {{
                    width: 100%;  /* Set the table width */
                    border-collapse: collapse;  /* Optional: for better border handling */
                }}
                th, td {{
                    border: 1px solid #ddd;  /* Optional: add borders to cells */
                    padding: 8px;  /* Optional: add padding to cells */
                    text-align: center;  /* Optional: align text to the left */
                }}
                {" ".join(css_rules)}  /* Add all CSS rules */
            </style>
            """

            # Display the table with custom CSS
            st.markdown(custom_css, unsafe_allow_html=True)
            st.markdown(html, unsafe_allow_html=True)

            cems_for_stack = pd.DataFrame()  # default to an empty DF

            # Filter CEMS details for this stack
            if cems_data is not None:
                cems_for_stack = cems_data[cems_data['stack_id'] == stack['stack_id']]
            st.markdown("##### Parameter Details")
            if not cems_for_stack.empty:
                for j, cems in cems_for_stack.iterrows():
                    table_param = {
                        "Parameter": cems['parameter'],
                        "Make": cems['make'],
                        "Model": cems['model'],
                        "Serial Number": cems['serial_number'],
                        "SPCB Approved Emission Limit": cems['emission_limit'],
                        "Measuring Range (Low)": cems['measuring_range_low'],
                        "Measuring Range (High)": cems['measuring_range_high'],
                        "Is Certified?": cems['certified'],
                        "Certification Agency": cems['certification_agency'],
                        "Communication Protocol": cems['communication_protocol'],
                        "Measurement Method": cems['measurement_method'],
                        "Technology": cems['technology'],
                        "Connected to SPCB?": cems['connected_bspcb'],
                        "SPCB URL": cems['bspcb_url'],
                        "Connected to CPCB?": cems['connected_cpcb'],
                        "CPCB URL": cems['cpcb_url'],
                    }

                    # Convert dictionary to DataFrame
                    param_df = pd.DataFrame(table_param, index=[0])  # Create a DataFrame with a single row
                    param_df.dropna(axis=1, how='all', inplace=True)

                    # Convert DataFrame to HTML
                    html = param_df.to_html(index=False)

                    # Generate CSS for column widths
                    column_count = len(param_df.columns)
                    default_width = 100  # Default width for all columns
                    specific_widths = {
                        # 2: 50,  # Width for the first column
                        # Width for the second column
                        # Add more specific widths as needed
                    }

                    # Create CSS rules
                    css_rules = []
                    for i in range(1, column_count + 1):
                        width = specific_widths.get(i, default_width)  # Use specific width or default
                        css_rules.append(f"th:nth-child({i}), td:nth-child({i}) {{ width: {width}px; }}")

                    # Combine CSS rules
                    custom_css = f"""
                                <style>
                                    table {{
                                        width: 100%;  /* Set the table width */
                                        border-collapse: collapse;  /* Optional: for better border handling */
                                    }}
                                    th, td {{
                                        border: 1px solid #ddd;  /* Optional: add borders to cells */
                                        padding: 8px;  /* Optional: add padding to cells */
                                        text-align: center;  /* Optional: align text to the left */
                                    }}
                                    {" ".join(css_rules)}  /* Add all CSS rules */
                                </style>
                                """

                    # Display the table with custom CSS
                    st.markdown(custom_css, unsafe_allow_html=True)
                    st.markdown(html, unsafe_allow_html=True)
            else:
                st.warning(f"No CEMS Details Found for Stack {stack['stack_id']}.")
    else:
        st.warning("No Stack Details Found.")


def fill_stacks(user_id):
    """Form to fill stack details."""
    with get_database_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT num_stacks FROM industry_as WHERE user_id = ?", (user_id,))
        total_stacks = c.fetchone()[0]
        # st.write(total_stacks)
        conn.commit()

        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM stacks_as WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        # st.write(result)
        completed_stacks = result[0] if result else 0  # Default to 0 if no stacks are completed
        conn.commit()

        # c = conn.cursor()
        # c.execute("SELECT completed_stacks FROM industry_as WHERE user_id = ?", (user_id,))
        # completed_stacks = c.fetchone()[0]
        # st.write(completed_stacks)
        # conn.commit()

        if completed_stacks >= total_stacks:
            st.success("All stack details are completed.")
            return

    # Display next stack form if not completed all
    current_stack = completed_stacks + 1
    st.subheader(f"Enter Details for Stack {current_stack} of {total_stacks}")

    if f"stack_{current_stack}" not in st.session_state:
        # Simple input fields (without st.form)
        stack_identity = st.text_input("Stack Identity or identification Number")
        process_attached = st.text_input("Process Attached")
        apcd_details = st.text_input("APCD Details")
        latitude = st.number_input(
            "Latitude", value=None, min_value=24.33611111, max_value=27.52083333, format="%.6f"
        )
        longitude = st.number_input(
            "Longitude", value=None, min_value=83.33055556, max_value=88.29444444, format="%.6f"
        )
        stack_condition = st.selectbox("Stack Condition", ["Wet", "Dry"])
        stack_shape = st.selectbox(
            "Is it a Circular Stack/Rectangular Stack", ["Circular", "Rectangular"]
        )
        if stack_shape == "Circular":
            diameter = st.number_input("Diameter (in meters)", min_value=0.0, format="%.2f")
            length, width = None, None
        else:
            length = st.number_input("Length (in meters)", value=None, min_value=0.0, format="%.2f")
            width = st.number_input("Width (in meters)", value=None, min_value=0.0, format="%.2f")
            diameter = None
        stack_material = st.text_input("Stack Construction Material"
                                       )
        stack_height = st.number_input(
            "Stack Height (in meters)", value=None, min_value=0.0, format="%.2f"
        )
        platform_height = st.number_input(
            "Platform for Manual Monitoring location height from Ground level(in meters)",
            value=None, min_value=0.0, format="%.2f"
        )
        if stack_height is not None and platform_height is not None:
            if platform_height >= stack_height:
                st.error(
                    "Kindly enter valid details. Platform height cannot be greater than or equal to stack height.",
                    icon="🚨"
                )
        platform_approachable = st.selectbox(
            "Is Platform approachable?", ["Yes", "No"]
        )
        if platform_approachable == "Yes":
            approaching_media = st.selectbox(
                "Choose one", ["Ladder", "Lift", "Staircase"]
            )
        else:
            approaching_media = None
            st.error(
                "Platform must be approachable, Follow CPCB Guidelines"
            )
        cems_installed = st.selectbox(
            "Where is CEMS Installed?", ["Stack/Chimney", "Duct", "Both"]
        )
        if cems_installed == "Both":
            stack_params = st.multiselect(
                "Parameters Monitored in Stack",
                ["PM", "SO2", "NOx", "CO", "O2", "NH3", "HCL", "Total Fluoride", "HF", "Hg", "H2S", "CL2"]
            )
            duct_params = st.multiselect(
                "Parameters Monitored in Duct",
                ["PM", "SO2", "NOx", "CO", "O2", "NH3", "HCL", "Total Fluoride", "HF", "Hg", "H2S", "CL2"]
            )
        else:
            stack_params = None  # Ensure it is always a list
            duct_params = None

        # Check if stack_params is not None and is a list
        if stack_params and isinstance(stack_params, list):
            stack_params = ",".join(stack_params)  # Safely join list items into a string
        else:
            stack_params = None  # Fallback in case of no parameters selected or invalid data

        # Check if stack_params is not None and is a list
        if duct_params and isinstance(duct_params, list):
            duct_params = ",".join(duct_params)  # Safely join list items into a string
        else:
            duct_params = None  # Fallback in case of no parameters selected or invalid data

        if stack_shape == "Circular":
            follows_formula = st.selectbox(
                "Does the Installation follows 8D/2D formula?", ["Yes", "No"]
            )
        else:
            follows_formula = st.selectbox(
                "Does the Installation follows (2LW/L+W) criteria (Rectangular)?", ["Yes", "No"]
            )

        if cems_installed in ["Duct"]:
            manual_port_installed = st.selectbox(
                "Has a Manual Monitoring Port been installed in the duct?", ["Yes", "No"]
            )
            if manual_port_installed == "No":
                st.write("Please, Refer CPCB Guidelines")

        elif cems_installed in ["Both"]:
            manual_port_installed = st.selectbox(
                "Has a Manual Monitoring Port been installed in the duct?", ["Yes", "No"]
            )
            if manual_port_installed == "No":
                st.write("Please, Refer CPCB Guidelines")
        else:
            manual_port_installed = None

        cems_below_manual = st.selectbox(
            "Is CEMS Installation point at least 500mm below the Manual monitoring point? ", ["Yes", "No"]
        )
        if cems_below_manual == "No":
            st.write("Please, Refer CPCB Guidelines")

        parameters = st.multiselect(
            "Parameters Monitored",
            ["PM", "SO2", "NOx", "CO", "O2", "NH3", "HCL", "Total Fluoride", "HF", "Hg", "H2S", "CL2", "others"],
        )

        # Submit button
        if st.button("Submit Stack Details"):
            # Collecting all mandatory fields into a list for easy checking
            mandatory_fields = [
                stack_identity, process_attached, apcd_details, latitude, longitude, stack_condition, stack_shape,
                stack_material, stack_height, platform_height, platform_approachable,
                cems_installed, follows_formula, cems_below_manual
            ]

            # Additional conditional fields (check based on shape or type)
            if stack_shape == "Circular":
                mandatory_fields.append(diameter)
            else:
                mandatory_fields.extend([length, width])

            if cems_installed == "Both":
                mandatory_fields.extend([stack_params, duct_params])
            if platform_approachable == "Yes":
                mandatory_fields.append(approaching_media)

            # Check if any mandatory field is empty
            if any(field is None or field == "" or field == [] for field in mandatory_fields):
                st.error("All fields are mandatory. Please fill in all required fields.")
                return

            if not parameters:
                st.error("Please select at least one parameter.")
                return
            else:
                st.success("Stack details submitted successfully!")

            with get_database_connection() as conn:
                c = conn.cursor()
                c.execute(""" 
                    INSERT INTO stacks_as (user_id, user_id_ind, stack_identity, process_attached, apcd_details, latitude,
                     longitude, stack_condition, stack_shape, diameter, length, width, stack_material, stack_height, 
                     platform_height, platform_approachable, approaching_media, cems_installed, stack_params, 
                     duct_params, follows_formula, manual_port_installed, cems_below_manual, parameters)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (
                    user_id, f'ind_{user_id}', stack_identity, process_attached, apcd_details, latitude, longitude,
                    stack_condition, stack_shape, diameter, length, width, stack_material, stack_height, platform_height,
                    platform_approachable, approaching_media, cems_installed, stack_params, duct_params,
                    follows_formula, manual_port_installed, cems_below_manual, ",".join(parameters)
                ))
                stack_id = c.lastrowid
                conn.commit()

                c.execute("""
                        UPDATE stacks_as
                        SET number_params = 
                            CASE 
                                WHEN parameters IS NULL OR parameters = '' THEN 0
                                ELSE (LENGTH(parameters) - LENGTH(REPLACE(parameters, ',', '')) + 1)
                            END
                        WHERE stack_id = ?
                    """, (stack_id,))
                conn.commit()

                # Increment the completed_stacks counter
                c.execute("""
                        UPDATE industry_as
                        SET completed_stacks = completed_stacks + 1
                        WHERE user_id = ?
                    """, (user_id,))
                conn.commit()

            # Save stack state in session
            st.session_state[f"stack_{current_stack}"] = True
            st.session_state["parameters"] = parameters  # Store parameters for CEMS form
            st.success("Stack details saved!")
            st.session_state["current_page"] = f"cems_{current_stack}"  # Move to CEMS details form
            st.rerun()


def fill_cems_details(user_id):
    """Form to fill CEMS details."""
    st.subheader("Enter CEMS Details")

    # Retrieve stack details from the session or database
    with get_database_connection() as conn:
        c = conn.cursor()
        c.execute("SELECT stack_id, process_attached, parameters FROM stacks_as WHERE user_id = ?", (user_id,))
        stack_details = c.fetchall()

        # st.write(stack_details)
        # x = stack_details[0][0]
        # st.write(x)

    if not stack_details:
        st.error("No stack details found. Please fill in stack details first.")
        return

    # Filter stacks that have details filled (stack_id with non-null details)
    filled_stacks = [stack for stack in stack_details if stack[1]]  # Stack details should not be empty
    if not filled_stacks:
        st.error("No filled stack details found. Please fill in stack details first.")
        return

    # Dropdown to select stack based on 'process_attached'
    stack_options = [stack[1] for stack in filled_stacks]  # Using process_attached instead of stack_name
    selected_process = st.selectbox("Select Process", stack_options)

    # Get the stack ID and parameters based on selected process
    selected_stack = next(stack for stack in filled_stacks if stack[1] == selected_process)
    selected_stack_id = selected_stack[0]
    stack_parameters = selected_stack[2]

    if stack_parameters:
        available_parameters = stack_parameters.split(",")  # Assuming comma-separated parameters
    else:
        available_parameters = []

    # Retrieve CEMS parameters already filled for the selected stack
    with get_database_connection() as conn:
        c = conn.cursor()
        c.execute("""
            SELECT DISTINCT parameter FROM cems_instruments_as WHERE stack_id = ?
        """, (selected_stack_id,))
        filled_parameters = c.fetchall()

    filled_parameter_names = [param[0] for param in filled_parameters]  # List of filled parameter names
    available_parameters = [param.strip() for param in available_parameters if
                            param.strip() not in filled_parameter_names]

    if not available_parameters:
        st.warning(f"All parameters for the stack with process '{selected_process}' have already been filled.")
        return

    # Dropdown to select parameter (filter out already filled ones)
    selected_parameter = st.selectbox("Select Parameter", options=available_parameters)

    # Initialize session state to track form reset
    if f"form_reset_{selected_stack_id}" not in st.session_state:
        st.session_state[f"form_reset_{selected_stack_id}"] = False

    # Form for entering CEMS details
    with st.form(f"cems_form_{selected_stack_id}",
                 clear_on_submit=st.session_state[f"form_reset_{selected_stack_id}"]) as form:
        make = st.text_input("Make")
        model = st.text_input("Model")
        serial_number = st.text_input("Serial Number")
        emission_limit = st.number_input("SPCB Approved Emission Limit", min_value=0, value=0)
        measuring_range_low = st.number_input("Measuring Range (Low)", min_value=0, value=0)
        measuring_range_high = st.number_input("Measuring Range (High)", min_value=0, value=0)
        certified = st.selectbox("Is Certified?", ["Yes", "No"])
        if certified == "Yes":
            certification_agency = st.text_input("Certification Agency")
        else:
            certification_agency = None
        communication_protocol = st.selectbox("Communication Protocol", ["4-20 mA", "RS-485", "RS-232"], index=None)
        measurement_method = st.selectbox("Measurement Method", ["In-situ", "Extractive"], index=None)
        technology = st.text_input("Technology")
        connected_bspcb = st.selectbox("Connected to SPCB?", ["Yes", "No"])
        if connected_bspcb == "Yes":
            bspcb_url = st.text_input("SPCB URL")
        else:
            bspcb_url = None
        connected_cpcb = st.selectbox("Connected to CPCB?", ["Yes", "No"])
        if connected_cpcb == "Yes":
            cpcb_url = st.text_input("CPCB URL")
        else:
            cpcb_url = None

        submit_cems = st.form_submit_button("Submit CEMS Details")

    if submit_cems:
        if not all([make, model, serial_number, communication_protocol, measurement_method, technology]):
            st.error("All fields are mandatory. Please fill in all fields.")
            return

        # Check for numeric fields: Handle 0.0 as valid input
        if emission_limit is None or measuring_range_low is None or measuring_range_high is None:
            st.error("Numeric fields must have valid values.")
            return

        if measuring_range_low >= measuring_range_high:
            st.error("Measuring Range (Low) must be less than Measuring Range (High).")
            return

        # Check if certification is required
        if certified == "Yes" and not certification_agency:
            st.error("Kindly fill the Certification Agency name.")
            return

        # Validate URLs if needed
        if connected_bspcb == "Yes" and not bspcb_url:
            st.error("Kindly fill the SPCB URL.")
            return

        if connected_cpcb == "Yes" and not cpcb_url:
            st.error("Kindly fill the CPCB URL.")
            return

        # st.success("CEMS Details submitted successfully!")

        st.write("CEMS Form Submitted:", {
            "user_id": user_id,
            "process_attached": selected_process,
            "parameter": selected_parameter,
            "make": make,
            "model": model,
            "serial_number": serial_number,
            "measuring_range_low": measuring_range_low,
            "measuring_range_high": measuring_range_high,
            "certified": certified,
            "certification_agency": certification_agency,
            "communication_protocol": communication_protocol,
            "measurement_method": measurement_method,
            "technology": technology,
            "connected_bspcb": connected_bspcb,
            "connected_cpcb": connected_cpcb,
        })

        # Save CEMS details to database
        try:
            with get_database_connection() as conn:
                c = conn.cursor()

                # Here, use the stack_id to associate the CEMS data with the correct stack
                c.execute(""" 
                    INSERT INTO cems_instruments_as (stack_id, user_id_ind, parameter, make, model, serial_number, emission_limit, 
                    measuring_range_low, measuring_range_high, certified, certification_agency, communication_protocol, 
                    measurement_method, technology, connected_bspcb, bspcb_url, cpcb_url, connected_cpcb)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    selected_stack_id, f'ind_{user_id}', selected_parameter, make, model, serial_number,
                    measuring_range_low,
                    emission_limit, measuring_range_high, certified, certification_agency, communication_protocol,
                    measurement_method, technology, connected_bspcb, bspcb_url, connected_cpcb, cpcb_url
                ))
                conn.commit()

                c.execute("""
                                        UPDATE stacks_as
                                        SET completed_parameters = completed_parameters + 1
                                        WHERE stack_id = ?
                                    """, (selected_stack_id,))
                conn.commit()

                st.session_state[f"form_reset_{selected_stack_id}"] = True  # Allow form reset

            st.success(f"CEMS details for {selected_parameter} saved!")
            # st.session_state[
            #     f"cems_{selected_stack_id}_{selected_parameter}"] = True  # Mark CEMS form as completed for this parameter
            # st.session_state["current_page"] = "Industry Dashboard"

            st.rerun()

        except Exception as e:
            st.error(f"An error occurred while saving CEMS details: {e}")
            st.session_state[f"form_reset_{selected_stack_id}"] = False  # Prevent reset on error


# Main Function
def main():
    hide_streamlit_style = """
    <style>
        /* Hide the Streamlit header and hamburger menu */
        #MainMenu {visibility: hidden;}
        header {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    # reduce_top_margin_style = """
    # <style>
    #     /* Adjust the margins of the main page */
    #     .block-container {
    #         padding-top: 2rem;
    #         padding-left: 1rem; 
    #         padding-right: 1rem; 
    #     }
    # </style>
    # """
    # st.markdown(reduce_top_margin_style, unsafe_allow_html=True)

    #st.image("banner3.jpg", caption=None, use_container_width=True)
    
    # st.title("Industry Registration Portal")
    st.markdown("<h3 style='text-align: center; color: black;'>Industry Registration Portal</h3>", unsafe_allow_html=True)
    create_database_tables()
    # add_admin_user() # One time run

    if "selected_ind_id" not in st.session_state:
        st.session_state["selected_ind_id"] = None

    # Initialize session state
    if "admin_logged_in" not in st.session_state:
        st.session_state["admin_logged_in"] = False

    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None

    # Show navigation only before login
    if not st.session_state["logged_in"] and not st.session_state["admin_logged_in"]:
        st.sidebar.title("User Login")
        navigation = ["Industry Login/New Industry Registration", "Admin Login"]
        selected_page = st.sidebar.selectbox("Select User Type", navigation)

        

        # Admin Login and Dashboard
        if selected_page == "Admin Login":
            admin_login_page()


        # User Login/Registration
        elif selected_page == "Industry Login/New Industry Registration":

            if not st.session_state["logged_in"]:
                # st.header("Please log in or register to continue.")
                menu = ["Login", "Register Industry"]
                choice = st.sidebar.selectbox("Menu", menu)

                if choice == "Register Industry":
                    st.subheader("Register Industry")
                    # Registration form
                    with st.form("register_form"):
                        industry_category = st.selectbox("Industry Category", options=category,placeholder="Select Category",
                                                         index=None)
                        state_ocmms_id = st.text_input("State OCMMS Id")
                        cpcb_ind_code = st.text_input("CPCB Industry Code")
                        industry_name = st.text_input("Industry Name")
                        address = st.text_input("Address")
                        state = st.selectbox("State", options=state_list, placeholder="Select State", index=None)
                        if 'district_list' not in st.session_state:
                            st.session_state.district_list = []
                        if st.form_submit_button("Show Districts"):
                            st.session_state.district_list = dist_dict.get(state, [])
                        if st.session_state.district_list:
                            district = st.selectbox("Select District", st.session_state.district_list, index=None)
                        production_capacity = st.text_input("Production Capacity")
                        num_stacks = st.number_input("Number of Stacks", min_value=1)
                        industry_environment_head = st.text_input("Environment Department Head")
                        env_phone = st.number_input("Environment Department Head Phone Number", value=None, step=1)
                        industry_instrument_head = st.text_input("Instrumentation Department Head")
                        inst_phone = st.number_input("Instrumentation Department Head Phone Number", value=None, step=1)
                        concerned_person_cems = st.text_input("Concerned Person for CEMS")
                        cems_phone = st.number_input("Concerned Person for CEMS Phone Number", value=None, step=1)

                        # Industry Representative Email Id and Password at the end
                        email = st.text_input("Industry Representative Email Id (used for login)")
                        password = st.text_input("Password", type="password")

                        submit = st.form_submit_button("Register Industry")

                    # Validate mandatory fields
                    if submit:
                        if not (
                                industry_category and state_ocmms_id and industry_name and address and state
                                and district and production_capacity and num_stacks and industry_environment_head
                                and industry_instrument_head and concerned_person_cems and email and password
                                and env_phone and inst_phone and cems_phone):
                            st.error("All fields are mandatory. Please fill in all fields.")
                            return

                        # checked the number is valid  or not
                        if not isValid(env_phone) or not isValid(inst_phone) or not isValid(cems_phone) :
                            st.error("kindly enter valid Head mobile number")
                            return

                        # Validate email format
                        if not is_valid_email(email):
                            st.error("Please enter a valid email address.")
                            return

                        def is_email_and_ocmms_unique(email, state_ocmms_id, cpcb_ind_code):
                            with get_database_connection() as conn:
                                c = conn.cursor()
                                # Check email uniqueness
                                c.execute("SELECT COUNT(*) FROM user_as WHERE email = ?", (email,))
                                if c.fetchone()[0] > 0:
                                    return "Email already exists."
                                c = conn.cursor()
                                # Check state_ocmms_id uniqueness
                                c.execute("SELECT COUNT(*) FROM industry_as WHERE state_ocmms_id = ?", (state_ocmms_id,))
                                if c.fetchone()[0] > 0:
                                    return "State OCMMS ID already exists."
                                c = conn.cursor()
                                # Check state_ocmms_id uniqueness
                                c.execute("SELECT COUNT(*) FROM industry_as WHERE cpcb_ind_code = ?", (cpcb_ind_code,))
                                if c.fetchone()[0] > 0:
                                    return "CPCB Industry code already exists."
                            return None  # Both are unique

                        # Example during registration:
                        error_message = is_email_and_ocmms_unique(email, state_ocmms_id, cpcb_ind_code)
                        if error_message:
                            st.error(error_message)
                        else:
                            # Save data to the database
                            try:
                                conn = get_database_connection()
                                c = conn.cursor()

                                # Insert user (with email used for login)
                                # hashed_password = password
                                c.execute("INSERT INTO user_as (email, password) VALUES (?, ?)", (email, password))
                                user_id = c.lastrowid
                                conn.commit()
                                user_id_str = f"ind_{user_id}"  # Format user_id like 'ind_1', 'ind_2', etc.

                                # Insert industry
                                c.execute('''INSERT INTO industry_as (user_id, user_id_ind, industry_category, 
                                state_ocmms_id, cpcb_ind_code, industry_name, address, state, district, production_capacity, 
                                num_stacks, industry_environment_head, env_phone, industry_instrument_head, inst_phone,
                                 concerned_person_cems, cems_phone, industry_representative_email)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                                          (user_id, user_id_str, industry_category, state_ocmms_id,
                                           cpcb_ind_code, industry_name, address, state, district, production_capacity,
                                           num_stacks, industry_environment_head, env_phone, industry_instrument_head,
                                           inst_phone, concerned_person_cems, cems_phone, email))
                                conn.commit()
                                conn.close()
                                st.success("Industry registered successfully!")
                                refresh_page()
                            except sqlite3.IntegrityError:
                                st.error("This email is already registered. Please use a different email.")
                            except Exception as e:
                                st.write()  # Encapsulate registration logic

                elif choice == "Login":
                    st.subheader("Login")

                    # Login form
                    email = st.text_input("Industry Representative Email Id")
                    password = st.text_input("Password", type="password")
                    login_button = st.button("Login")

                    if login_button:
                        try:
                            conn = get_database_connection()
                            c = conn.cursor()

                            # Verify email and password
                            c.execute("SELECT id, password FROM user_as WHERE email = ?", (email,))
                            user = c.fetchone()

                            if user and password == user[1]:
                                st.success("Login successful!")
                                st.session_state["logged_in"] = True
                                st.session_state["user_id"] = user[0]
                                st.session_state["current_page"] = "Industry Details"
                                st.rerun()
                                st.write(f"User ID in session state: {st.session_state['user_id']}")  # Debugging

                            else:
                                st.error("Invalid email or password.")
                            conn.close()
                        except Exception as e:
                            st.error(f"An error occurred: {e}")

    # Admin Dashboard
    elif st.session_state["admin_logged_in"]:
        admin_dashboard()

    # User-Specific Dashboard
    elif st.session_state["logged_in"]:
        user_id = st.session_state["user_id"]
        sidebar_forms(user_id)
        #  # Ensure correct redirection to the selected page
        # if st.session_state.get("current_page") == "Industry Dashboard":
        #     show_industry_dashboard(user_id)
        # elif st.session_state.get("current_page") == "Stack Details":
        #     fill_stacks(user_id)
        # elif st.session_state.get("current_page") == "CEMS Details":
        #     fill_cems_details(user_id)



        # else:
        #     user_id = st.session_state["user_id"]
        #     sidebar_forms(user_id)


if __name__ == "__main__":
    main()

