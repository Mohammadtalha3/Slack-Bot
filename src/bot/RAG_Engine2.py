import pdfplumber   

def dataloading(self):

    pdf_path= 'Data/django.pdf'

    with pdfplumber.open(pdf_path) as doc:
        full_text=''
        for pages in doc.pages:
            full_text+=pages.extract_text(x_tolerance=1,y_tolerance=1, layout=True)

            return full_text