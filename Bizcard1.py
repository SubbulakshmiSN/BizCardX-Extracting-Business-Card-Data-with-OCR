# Importing all necessary libraries
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import re
import numpy as np
import io
import psycopg2


# Connecting to the database
b_db= psycopg2.connect(host="localhost",
                        user="postgres",
                        password="1234",
                        database="bizcard",
                        port="5432")
cur= b_db.cursor()

# option menu
with st.sidebar:
    selected = option_menu(
        menu_title="BizcardX-OCR",
        options=["About","Image Process"],
        icons=["at","image"],
        default_index=0,
        orientation="vertical"
    )

# Table creation query
cur.execute('''
    CREATE TABLE IF NOT EXISTS BUSINESS_CARD (
        NAME VARCHAR(50),
        DESIGNATION VARCHAR(100),
        COMPANY_NAME VARCHAR(100),
        CONTACT VARCHAR(35),
        EMAIL VARCHAR(100),
        WEBSITE VARCHAR(100),
        ADDRESS TEXT,
        PINCODE VARCHAR(100))
        ''')
b_db.commit()

# extract the data
def extracted_text(picture):
    ext_dic = {'Name': [], 'Designation': [], 'Company name': [], 'Contact': [], 'Email': [], 'Website': [],
               'Address': [], 'Pincode': []}

    ext_dic['Name'].append(result[0])
    ext_dic['Designation'].append(result[1])

    for m in range(2, len(result)):
        if result[m].startswith('+') or (result[m].replace('-', '').isdigit() and '-' in result[m]):
            ext_dic['Contact'].append(result[m])

        elif '@' in result[m] and '.com' in result[m]:
            email = result[m].lower()
            ext_dic['Email'].append(email)

        elif 'www' in result[m] or 'WWW' in result[m] or 'wwW' in result[m]:
            website = result[m].lower()
            ext_dic['Website'].append(website)

        elif 'TamilNadu' in result[m] or 'Tamil Nadu' in result[m] or result[m].isdigit():
            ext_dic['Pincode'].append(result[m])

        elif re.match(r'^[A-Za-z]', result[m]):
            ext_dic['Company name'].append(result[m])

        else:
            removed_colon = re.sub(r'[,;]', '', result[m])
            ext_dic['Address'].append(removed_colon)

    for key, value in ext_dic.items():
        if len(value) > 0:
            concatenated_string = ' '.join(value)
            ext_dic[key] = [concatenated_string]  #for multiple value making it a single string
        else:
            value = 'NA'
            ext_dic[key] = [value]

    return ext_dic



if selected == "Image Process":
    st.header(":red[Extracting Business Card Data with OCR] ")
    image = st.file_uploader(label="Upload the image", type=['png', 'jpg', 'jpeg'], label_visibility="hidden")


    
    def load_image():
        reader = easyocr.Reader(['en'], model_storage_directory=".")
        return reader

    reader_1 = load_image()
    
    if image is not None:
        input_image = Image.open(image)
        
        # Displaying uploaded image
        st.image(input_image, width=550, caption='Uploaded Image')
        
        #performing OCR
        result = reader_1.readtext(np.array(input_image), detail=0)
        
        # creating dataframe
        ext_text = extracted_text(result)
        df = pd.DataFrame(ext_text)  #dataframe contains all extracted information
        st.dataframe(df)

        # Converting image into bytes
        image_bytes = io.BytesIO()
        
        #saving image in bytes
        input_image.save(image_bytes, format='PNG')
        
        #extracting byte data
        image_data = image_bytes.getvalue()

        # Creating dictionary
        data = {"Image": [image_data]}
        df_1 = pd.DataFrame(data)  #dataframe contains image bytes information
        
        #synchronizing both dataframes
        concat_df = pd.concat([df, df_1], axis=1)

        # Database
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
        
            selected =option_menu(
                menu_title=None,
                options=["Preview", "Delete"],
                icons=['file-earmark', 'trash'],
                default_index=0,
                orientation="horizontal"
                
            )

        ext_text = extracted_text(result)
        df = pd.DataFrame(ext_text)
        
        
        if selected == "Preview":
            col_1, col_2 = st.columns([4, 4])
            with col_1:
                modified_n = st.text_input('Name', ext_text["Name"][0])
                modified_d = st.text_input('Designation', ext_text["Designation"][0])
                modified_c = st.text_input('Company name', ext_text["Company name"][0])
                modified_con = st.text_input('Mobile', ext_text["Contact"][0])
                concat_df["Name"], concat_df["Designation"], concat_df["Company name"], concat_df[
                    "Contact"] = modified_n, modified_d, modified_c, modified_con
            with col_2:
                modified_m = st.text_input('Email', ext_text["Email"][0])
                modified_w = st.text_input('Website', ext_text["Website"][0])
                modified_a = st.text_input('Address', ext_text["Address"][0][1])
                modified_p = st.text_input('Pincode', ext_text["Pincode"][0])
                concat_df["Email"], concat_df["Website"], concat_df["Address"], concat_df[
                    "Pincode"] = modified_m, modified_w, modified_a, modified_p

            
            with col_1:
                Preview = st.button("Preview modified text")
                Upload = st.button("Upload")
            if Preview:
                filtered_df = concat_df[
                    ['Name', 'Designation', 'Company name', 'Contact', 'Email', 'Website', 'Address', 'Pincode']]
                st.dataframe(filtered_df)
            else:
                pass

            
            if Upload:
                with st.spinner("In progress"):
                    insert_query = '''INSERT INTO BUSINESS_CARD(NAME, DESIGNATION, COMPANY_NAME, CONTACT, EMAIL, WEBSITE, ADDRESS,  
                        PINCODE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
                    for index, i in concat_df.iterrows():
                        result_table = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
                        cur.execute(insert_query, result_table)
                        b_db.commit()
                        st.success('SUCCESSFULLY UPLOADED', icon="✅")
        
        else:
            col1, col2 = st.columns([4, 4])
            
            #card details dataframe from database
            st.subheader(":red[Card Details]")
            cur.execute("SELECT * FROM BUSINESS_CARD")
            all_card_details = cur.fetchall()
            if all_card_details:
                columns = [name[0] for name in cur.description]
                all_card_df = pd.DataFrame(all_card_details, columns=columns)
                st.dataframe(all_card_df)
            else:
                st.write("No card details found in the database.")
            
            with col1:
                cur.execute("SELECT NAME FROM BUSINESS_CARD")
                n = cur.fetchall()
                names = ["Select"]
                for i in n:
                    names.append(i[0])
                name_selected = st.selectbox("Select the name to delete", options=names)
               
            with col2:
                cur.execute(f"SELECT DESIGNATION FROM BUSINESS_CARD WHERE NAME = '{name_selected}'")
                d = cur.fetchall()
                designation = ["Select"]
                for j in d:
                    designation.append(j[0])
                designation_selected = st.selectbox("Select the designation of the chosen name", options=designation)

            st.markdown(" ")

            col_a, col_b, col_c = st.columns([5, 3, 3])
            with col_b:
                remove = st.button("Clik here to delete")
            if name_selected and designation_selected and remove:
                cur.execute(f"DELETE FROM BUSINESS_CARD WHERE NAME = '{name_selected}' AND DESIGNATION = '{designation_selected}'")
                b_db.commit()
                if remove:
                    st.warning('SUCCESSFULLY DELETED', icon="⚠️")

    else:
        st.write("Upload an image")
if selected == "About":
    col1, col2 = st.columns(2)
    with col2:
        st.title(':red[BizCardX- Extracting Business Card Data with OCR]')
        st.write(
            "BizCardX is to automate and simplify the process of capturing and managing contact information from business cards, saving users time and effort. It is particularly useful for professionals who frequently attend networking events, conferences, and meetings where they receive numerous business cards that need to be converted into digital contacts.")
        st.write("---")
        st.write(":red[**Technologies Used :**] Python,easy OCR, Streamlit, SQL, Pandas")
        st.write(":red[**Overview :**] In this streamlit web app you can upload an image of a business card and extract relevant information from it using easyOCR. You can view, modify or delete the extracted data in this app. This app would also allow users to save the extracted information into a database along with the uploaded business card image. The database would be able to store multiple entries, each with its own business card image and extracted information.")
   



     