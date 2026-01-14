from pypdf import PdfReader
import os

pdf_path = os.path.join("original_paper", "manuscript.pdf")

try:
    reader = PdfReader(pdf_path)
    print(f"Number of pages: {len(reader.pages)}")
    
    text_content = ""
    for page in reader.pages:
        text_content += page.extract_text() + "\n"
        
    with open("manuscript_text.txt", "w", encoding="utf-8") as f:
        f.write(text_content)
    
    print("Successfully wrote content to manuscript_text.txt")

except Exception as e:
    print(f"Error reading PDF: {e}")
