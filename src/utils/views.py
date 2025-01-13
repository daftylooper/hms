from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import json

from celery.result import AsyncResult

class TaskView(APIView):
    def get(self, request, task_id):
        try:
            result = AsyncResult(str(task_id))
            if result.ready():
                return Response({"status": "Completed", "result": result.get()})
            elif result.failed():
                return Response({"status": "Failed"})
            else:
                return Response({"status": "In Progress"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)