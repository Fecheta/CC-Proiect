from fpdf import FPDF


class PDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 15)
        title_w = self.get_string_width('converted doc') + 6
        doc_w = self.w
        self.set_x((doc_w - title_w) / 2)
        self.cell(title_w, 10, 'converted doc', border=1, ln=1, align='C')
        self.ln(10)


def create_pdf(input):
    # create FBDF obj
    # Layout ('P', 'L')
    # Unit ('mm', 'cm', 'in')
    # format ('A3', 'A4' (default), 'A5', 'Letter', 'Legal', (100,150))
    pdf = PDF('P', 'mm', 'Letter')

    # Add a page
    pdf.add_page()

    # specify font
    # fonts ('times', 'courier', 'helvetica', 'symbol', zpdfdingbats')
    # 'B' (bold), 'U' (underline), 'I' (italics), '' (regular), combination (i.e., ('BU'))
    pdf.set_font('helvetica', '', 11)

    pdf.set_auto_page_break(auto=True, margin=15)
    # Add text
    # w = width
    # h = height
    for list in input:
        if len(list) == 1:
            pdf.cell(0, 10, list[0], ln=True)  # (ln = True) == '\n'
        else:
            for item in list:
                pdf.multi_cell(0, 10, item, ln=True)
    return pdf
