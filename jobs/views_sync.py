from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework import status

from jobs.utils_fetch import (
    fetch_indeed_jobs,
    fetch_jobberman_jobs,
    fetch_google_jobs,
)

class JobSyncView(APIView):
    """
    POST /api/jobs/sync/
    Trigger external job fetching (Indeed, Jobberman, Google Jobs)
    """

    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        results = {
            "indeed": fetch_indeed_jobs(),
            "jobberman": fetch_jobberman_jobs(),
            "google_jobs": fetch_google_jobs(),
        }

        total_added = sum(len(v) for v in results.values())

        return Response(
            {
                "message": "External job sync completed successfully!",
                "details": {
                    "Indeed": len(results["indeed"]),
                    "Jobberman": len(results["jobberman"]),
                    "Google Jobs": len(results["google_jobs"]),
                    "Total Added": total_added,
                },
            },
            status=status.HTTP_200_OK,
        )

