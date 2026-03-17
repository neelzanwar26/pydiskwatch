import pypdf

with open('pdr_text.txt', 'w', encoding='utf-8') as f:
    reader = pypdf.PdfReader('PyDiskWatch_PDR.pdf')
    for page in reader.pages:
        f.write(page.extract_text() + '\n\n---PAGE---\n\n')
