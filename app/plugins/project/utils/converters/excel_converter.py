class ExcelConverter(object):
    @staticmethod
    def float_to_excel(val):
        return str(val).replace('.', ',')

    @staticmethod
    def excel_to_float(val):
        return str(val).replace(',', '.')
