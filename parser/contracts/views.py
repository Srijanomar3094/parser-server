import threading
import time
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.utils.text import get_valid_filename
from .models import Contract


def _score_and_gaps(contract: Contract) -> None:
    score = 0
    gaps = []
    # Financial completeness (30)
    financial = contract.financial_details or {}
    financial_fields = ["line_items", "total_value", "currency", "taxes"]
    have_financial = sum(1 for f in financial_fields if financial.get(f))
    score += int(30 * (have_financial / len(financial_fields)))
    for f in financial_fields:
        if not financial.get(f):
            gaps.append(f"Missing financial_details.{f}")

    # Party identification (25)
    parties = contract.parties or {}
    party_fields = ["customer", "vendor", "signatories"]
    have_parties = sum(1 for f in party_fields if parties.get(f))
    score += int(25 * (have_parties / len(party_fields)))
    for f in party_fields:
        if not parties.get(f):
            gaps.append(f"Missing parties.{f}")

    # Payment terms (20)
    payment = contract.payment_structure or {}
    payment_fields = ["terms", "schedule", "method", "banking"]
    have_payment = sum(1 for f in payment_fields if payment.get(f))
    score += int(20 * (have_payment / len(payment_fields)))
    for f in payment_fields:
        if not payment.get(f):
            gaps.append(f"Missing payment_structure.{f}")

    # SLA (15)
    sla = contract.sla or {}
    sla_fields = ["metrics", "penalties", "support"]
    have_sla = sum(1 for f in sla_fields if sla.get(f))
    score += int(15 * (have_sla / len(sla_fields)))
    for f in sla_fields:
        if not sla.get(f):
            gaps.append(f"Missing sla.{f}")

    # Contact info (10)
    account = contract.account_info or {}
    contact_fields = ["billing_contact", "technical_contact"]
    have_contact = sum(1 for f in contact_fields if account.get(f))
    score += int(10 * (have_contact / len(contact_fields)))
    for f in contact_fields:
        if not account.get(f):
            gaps.append(f"Missing account_info.{f}")

    contract.score = score
    contract.gaps = gaps


def _background_parse(contract_id: int) -> None:
    contract = Contract.objects.get(pk=contract_id)
    try:
        contract.status = Contract.STATUS_PROCESSING
        contract.progress = 10
        contract.save(update_fields=["status", "progress"])

        # Simulate parsing work
        time.sleep(0.5)
        contract.progress = 40
        contract.save(update_fields=["progress"])

        # Minimal dummy extraction structure
        contract.parties = {"customer": None, "vendor": None, "signatories": None}
        contract.account_info = {"billing_contact": None, "technical_contact": None}
        contract.financial_details = {"line_items": None, "total_value": None, "currency": None, "taxes": None}
        contract.payment_structure = {"terms": None, "schedule": None, "method": None, "banking": None}
        contract.revenue_classification = {"type": None, "billing_cycle": None, "renewal": None}
        contract.sla = {"metrics": None, "penalties": None, "support": None}
        time.sleep(0.5)
        contract.progress = 80
        _score_and_gaps(contract)
        contract.status = Contract.STATUS_COMPLETED
        contract.progress = 100
        contract.save()
    except Exception as exc:
        contract.status = Contract.STATUS_FAILED
        contract.error_message = str(exc)
        contract.save(update_fields=["status", "error_message"])


@csrf_exempt
def contract_upload(request):
    if request.method != "POST":
        return JsonResponse({"detail": "Method not allowed"}, status=405)
    upload = request.FILES.get("file")
    if not upload:
        return JsonResponse({"detail": "No file provided"}, status=400)
    if upload.size > 50 * 1024 * 1024:
        return JsonResponse({"detail": "File too large"}, status=400)
    if not upload.name.lower().endswith(".pdf"):
        return JsonResponse({"detail": "Unsupported file type"}, status=400)

    safe_name = get_valid_filename(upload.name)
    contract = Contract.objects.create(
        file=upload,
        original_filename=safe_name,
        status=Contract.STATUS_PENDING,
        progress=0,
    )

    threading.Thread(target=_background_parse, args=(contract.id,), daemon=True).start()

    return JsonResponse({"contract_id": str(contract.id)})


def contract_status(request, contract_id: int):
    contract = get_object_or_404(Contract, pk=contract_id)
    return JsonResponse(
        {
            "status": contract.status,
            "progress": contract.progress,
            "error": contract.error_message or None,
        }
    )


def contract_detail(request, contract_id: int):
    contract = get_object_or_404(Contract, pk=contract_id)
    if contract.status != Contract.STATUS_COMPLETED:
        return JsonResponse({"detail": "Processing not complete"}, status=409)
    return JsonResponse(
        {
            "id": str(contract.id),
            "file": contract.file.url if contract.file else None,
            "uploaded_at": contract.uploaded_at,
            "status": contract.status,
            "score": contract.score,
            "parties": contract.parties,
            "account_info": contract.account_info,
            "financial_details": contract.financial_details,
            "payment_structure": contract.payment_structure,
            "revenue_classification": contract.revenue_classification,
            "sla": contract.sla,
            "gaps": contract.gaps,
        }
    )


def contract_list(request):
    qs = Contract.objects.all().order_by("-uploaded_at")
    status_param = request.GET.get("status")
    if status_param:
        qs = qs.filter(status=status_param)
    page = int(request.GET.get("page", 1))
    page_size = min(int(request.GET.get("page_size", 10)), 100)
    paginator = Paginator(qs, page_size)
    p = paginator.get_page(page)
    data = [
        {
            "id": str(c.id),
            "original_filename": c.original_filename,
            "status": c.status,
            "progress": c.progress,
            "score": c.score,
            "uploaded_at": c.uploaded_at,
        }
        for c in p.object_list
    ]
    return JsonResponse({"results": data, "page": p.number, "pages": paginator.num_pages, "count": paginator.count})


def contract_download(request, contract_id: int):
    contract = get_object_or_404(Contract, pk=contract_id)
    if not contract.file:
        raise Http404("No file")
    response = HttpResponse(contract.file.open("rb").read(), content_type="application/pdf")
    response["Content-Disposition"] = f"attachment; filename=\"{contract.original_filename}\""
    return response



