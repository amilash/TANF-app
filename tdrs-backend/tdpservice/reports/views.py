"""Check if user is authorized."""
import logging

from rest_framework import mixins, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from ..users.permissions import CanDownloadReport, CanUploadReport

from .models import User, ReportFile
from .serializers import ReportFileSerializer

logger = logging.getLogger()
logger.setLevel(logging.INFO)

class GetYearList(APIView):
    """Get list of years for which there are reports."""

    query_string = False
    pattern_name = "report-list"
    permission_classes = [CanDownloadReport]

    def get(self, request, **kargs):
        """Handle get action for get list of years there are reports."""
        user = request.user
        is_ofa_admin = user.groups.filter(name="OFA Admin").exists()

        stt_id = kargs.get('stt') if (is_ofa_admin) else user.stt.id

        available_years = ReportFile.objects.filter(
            stt=stt_id
        ).values_list('year', flat=True).distinct()
        return Response(list(available_years))


class ReportFileViewSet(
    mixins.CreateModelMixin, viewsets.GenericViewSet,
):
    """Report file views."""

    queryset = User.objects.select_related("stt")

    def get_permissions(self):
        """Get permissions for the viewset."""
        permission_classes = {
            "create": [CanUploadReport],
        }.get(self.action)
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class."""
        return {
            "create": ReportFileSerializer,
        }.get(self.action, ReportFileSerializer)
