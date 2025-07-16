from django.shortcuts import render, get_object_or_404
from invoice.models import Invoice, InvoiceItem
from inventory.models import Inventory
import io
import base64
from barcode import Code128
from barcode.writer import SVGWriter
from quote.models import QuoteSession
from credits.views import individualDetails
from customers.models import Member

# Create your views here.


def get_print_count(quantity):
    return quantity // 2 if quantity % 2 == 0 else quantity // 2 + 1


# create invoice page
def createInvoice(request, pk):
    template = "report/invoiceA5.html"

    invoice = Invoice.objects.get(id=pk)
    values = InvoiceItem.objects.filter(invoice__id=pk)

    # upi_details = UpiDetails.objects.all().first()
    # shop_details = ShopDetails.objects.all().first()
    context = {"values": values, "details": invoice}

    # if upi_details:
    #     try:
    #         qr_data = f"upi://pay?pa={upi_details.upiId}&pn={shop_details.shopName}&am={invoice.amount}&tn=for bill no {invoice.id}&cu=INR"
    #         qr_code = qrcode.make(qr_data)
    #         image_bytes = io.BytesIO()
    #         qr_code.save(image_bytes, format="PNG")
    #         context["qrcode"] = image_bytes.getvalue()

    #     except BaseException as e:
    #         print(e)

    # context["shop_details"] = shop_details
    return render(request, template, context)


def createBarcode(request, pk):
    template = "report/barcode.html"
    values = Inventory.objects.get(id=pk)
    # shop_details = ShopDetails.objects.all().first()
    code128 = Code128(values.barcode, writer=SVGWriter())
    buffer = io.BytesIO()
    code128.write(buffer, options={"write_text": False})
    buffer.seek(0)
    barcode_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

    # Add the barcode image to the context dictionary
    context = {
        "values": values,
        "print_count": 4,
        "barcode_svg": barcode_image,
        # "shop_details": shop_details,
    }
    return render(request, template, context)


def quotation_a4(request, session_id):
    session = get_object_or_404(QuoteSession, pk=session_id)
    items = session.quote_items_session.filter(quantity__gt=0)
    return render(
        request,
        "report/quotation_a4.html",
        {
            "session": session,
            "items": items,
        },
    )


def individual_credit_report(request, pk):
    member = get_object_or_404(Member, pk=pk)
    transactions, balance = individualDetails(pk)

    val_balance = 0
    total_credit = 0
    total_debit = 0

    for value in transactions:
        if value["paid"] == "Purchased":
            val_balance += value["amount"]
            value["balance"] = val_balance
            total_credit += value["amount"]
        else:
            val_balance -= value["amount"]
            value["balance"] = val_balance
            total_debit += value["amount"]

    context = {
        "member": member,
        "data": transactions,
        "balance": balance,
        "total_credit": total_credit,
        "total_debit": total_debit,
        "user": request.user,
    }
    return render(request, "report/individual_report.html", context)


def member_report(request, pk):
    member = get_object_or_404(Member, pk=pk)
    invoices = Invoice.objects.filter(customer=member)

    return render(
        request, "report/member_report.html", {"data": invoices, "member": member}
    )
