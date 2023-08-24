import pdfplumber

pdf = pdfplumber.open("data/支付宝交易明细.pdf")
for page in (pdf.pages[0],pdf.pages[-2],pdf.pages[-1]):
    table = page.extract_table()
    text = page.extract_text()
    page.page_obj