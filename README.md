# BizCardX - Extracting Business Card Data with OCR

BizCardX is a Streamlit web application designed to automate and simplify the process of capturing and managing contact information from business cards. It utilizes OCR (Optical Character Recognition) technology to extract relevant information from uploaded images of business cards, saving users time and effort.

## Features

- **Image Processing**: Users can upload images of business cards in common formats such as PNG, JPG, and JPEG.
- **OCR Extraction**: The application uses the EasyOCR library to extract text from the uploaded images.
- **Data Presentation**: Extracted information is presented in a user-friendly DataFrame format, allowing users to easily view the extracted data.
- **Database Integration**: Extracted data can be stored in a PostgreSQL database, enabling users to manage and organize their digital contacts.
- **Preview and Modification**: Users can preview extracted information, modify it if necessary, and upload the modified data to the database.
- **Deletion**: Users can delete specific business card entries from the database based on name and designation.

## Technologies Used

- Python
- Streamlit
- EasyOCR
- PostgreSQL
- Pandas

## Getting Started

1. **Install dependencies**:

       pip install -r requirements.txt

2. **Set up PostgreSQL database**:

Install PostgreSQL and create a database named bizcard.
Update the database connection parameters (host, user, password, port) in the app.py file.

3.**Run the application**:
    
       streamlit run app.py

4.Access the application in your web browser at **http://localhost:8501**

## Usage

Upload an image of a business card using the file uploader.
View the extracted information in the DataFrame.
Optionally modify the extracted data and click "Upload" to save it to the database.
Use the "Preview" and "Delete" options to preview or delete existing entries in the database.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with any improvements or bug fixes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

You can place this content in your `README.md` file along with the code snippet provided in the "Getting Started" section. Adjust the paths and details according to your project's structure and requirements.




