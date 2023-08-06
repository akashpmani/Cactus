from io import BytesIO
import uuid
from django.http import HttpResponse
from django.template.loader import get_template
import xhtml2pdf.pisa as pisa
from django.conf import settings

def save_pdf(params:dict):
    template = get_template("products/invoice.html")
    html = template.render(params)
    response = BytesIO()
    pdf =pisa.pisaDocument(BytesIO(html.encode('UTF-8')),response)
    file_name = uuid.uuid4()
    
    if not pdf.err:
        return HttpResponse(response.getvalue(), content_type='application/pdf'),True
    return '',None
    
    # try:
    #     with open(str(settings.BASE_DIR)+f"/media/pdf/{file_name}.pdf",'wb+') as output:
    #         pdf = pisa.pisaDocument(BytesIO(html.encode('UTF-8')),output)
        
    # except Exception as e:
    #     print(e)
    
    # if pdf.err:
    #     return '',False
    # return file_name,True