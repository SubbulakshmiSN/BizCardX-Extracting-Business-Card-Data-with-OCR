import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import easyocr
from PIL import Image
import cv2
import os
# import matplotlib.pyplot as plt
import re
import numpy as np
import io
import psycopg2



b_db= psycopg2.connect(host="localhost",
                        user="postgres",
                        password="1234",
                        database="bizcard",
                        port="5432")
cur= b_db.cursor()

st.markdown(f""" """, unsafe_allow_html=True)

# st.header("Extracting Business Card Data with OCR ")

#option menu
with st.sidebar:
    selected = option_menu(
        menu_title="BizcardX-OCR",
        options=["Image Process", "Contact"],
        icons=["image", "at"],
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
        PINCODE VARCHAR(100)
    )
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
            small = result[m].lower()
            ext_dic['Email'].append(small)

        elif 'www' in result[m] or 'WWW' in result[m] or 'wwW' in result[m]:
            small = result[m].lower()
            ext_dic['Website'].append(small)

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
            ext_dic[key] = [concatenated_string]
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
        # Setting Image size
        st.image(input_image, width=350, caption='Uploaded Image')
        st.markdown(
            f'',
            unsafe_allow_html=True
        )

        result = reader_1.readtext(np.array(input_image), detail=0)
        # creating dataframe
        ext_text = extracted_text(result)
        df = pd.DataFrame(ext_text)
        st.dataframe(df)

        # Converting image into bytes
        image_bytes = io.BytesIO()
        input_image.save(image_bytes, format='PNG')
        image_data = image_bytes.getvalue()

        # Creating dictionary
        data = {"Image": [image_data]}
        df_1 = pd.DataFrame(data)
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

            col3, col4 = st.columns([4, 4])
            with col3:
                Preview = st.button("Preview modified text")
            with col4:
                Upload = st.button("Upload")
            if Preview:
                filtered_df = concat_df[
                    ['Name', 'Designation', 'Company name', 'Contact', 'Email', 'Website', 'Address', 'Pincode']]
                st.dataframe(filtered_df)
            else:
                pass

            if Upload:
                with st.spinner("In progress"):
                    # cur.execute(
                    #     '''CREATE TABLE IF NOT EXISTS BUSINESS_CARD(NAME VARCHAR(50), DESIGNATION VARCHAR(100), 
                    #     COMPANY_NAME VARCHAR(100), CONTACT VARCHAR(35), EMAIL VARCHAR(100), WEBSITE VARCHAR(
                    #     100), ADDRESS TEXT, PINCODE VARCHAR(100))''')
                    # con.commit()
                    A = '''INSERT INTO BUSINESS_CARD(NAME, DESIGNATION, COMPANY_NAME, CONTACT, EMAIL, WEBSITE, ADDRESS,  
                        PINCODE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'''
                    for index, i in concat_df.iterrows():
                        result_table = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7])
                        cur.execute(A, result_table)
                        b_db.commit()
                        st.success('SUCCESSFULLY UPLOADED', icon="✅")
        else:
            col1, col2 = st.columns([4, 4])
            with col1:
                cur.execute("SELECT NAME FROM BUSINESS_CARD")
                Y = cur.fetchall()
                names = ["Select"]
                for i in Y:
                    names.append(i[0])
                name_selected = st.selectbox("Select the name to delete", options=names)
                # st.write(name_selected)
            with col2:
                cur.execute(f"SELECT DESIGNATION FROM BUSINESS_CARD WHERE NAME = '{name_selected}'")
                Z = cur.fetchall()
                designation = ["Select"]
                for j in Z:
                    designation.append(j[0])
                designation_selected = st.selectbox("Select the designation of the chosen name", options=designation)

            st.markdown(" ")

            col_a, col_b, col_c = st.columns([5, 3, 3])
            with col_b:
                remove = st.button("Clik here to delete")
            if name_selected and designation_selected and remove:
                cur.execute(
                    f"DELETE FROM BUSINESS_CARD WHERE NAME = '{name_selected}' AND DESIGNATION = '{designation_selected}'")
                b_db.commit()
                if remove:
                    st.warning('DELETED', icon="⚠️")

    else:
        st.write("Upload an image")
if selected == "Contact":
    name = "Tamilanban.d"
    mail = (f'{"Mail :"}  {"agastiagathamil2000@gmail.com"}')
    description = "An Aspiring DATA-SCIENTIST..!"
    social_media = {
        "GITHUB": "https://github.com/Tamilanband",
        "LINKEDIN": "https://www.linkedin.com/in/tamilanban-d-8098314369/"}




    col1, col2 = st.columns(2)
    #col3.image(Image.open("/content/dark-background-empty-room-with-plants-floor_41470-1526.avif"), width=250)
    with col2:
        st.title(':red[BizCardX- Extracting Business Card Data with OCR]')
        st.write(
            "BizCardX is to automate and simplify the process of capturing and managing contact information from business cards, saving users time and effort. It is particularly useful for professionals who frequently attend networking events, conferences, and meetings where they receive numerous business cards that need to be converted into digital contacts.")
        st.write("---")
        st.subheader(mail)
    st.write("#")
    cols = st.columns(len(social_media))
    for index, (platform, link) in enumerate(social_media.items()):
        cols[index].write(f"[{platform}]({link})")




     