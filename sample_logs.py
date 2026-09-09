"""
Step 1: Log/error input
------------------------
A handful of synthetic deployment logs so the demo doesn't depend on
finding real logs on the spot. Feel free to add more before your demo.
"""

SAMPLE_LOGS = {
    "Kubernetes CrashLoopBackOff": """
2026-09-09T10:12:01Z INFO  Starting deployment rollout for service=payments-api
2026-09-09T10:12:04Z INFO  Pod payments-api-7d9f8c-abc12 scheduled on node worker-3
2026-09-09T10:12:07Z ERROR Readiness probe failed: HTTP probe failed with statuscode: 503
2026-09-09T10:12:10Z ERROR Liveness probe failed: HTTP probe failed with statuscode: 503
2026-09-09T10:12:11Z WARN  Back-off restarting failed container
2026-09-09T10:12:11Z ERROR Pod payments-api-7d9f8c-abc12 status=CrashLoopBackOff restartCount=4
""",

    "Out of Memory (OOMKilled)": """
2026-09-09T11:02:15Z INFO  Container inventory-worker started
2026-09-09T11:04:44Z WARN  Memory usage at 92% of limit (950Mi/1024Mi)
2026-09-09T11:04:59Z ERROR Container inventory-worker killed: OOMKilled
2026-09-09T11:05:00Z ERROR Exit code: 137
2026-09-09T11:05:01Z INFO  Restarting container inventory-worker (attempt 3)
""",

    "Missing Environment Variable": """
2026-09-09T09:41:02Z INFO  Booting service auth-service v2.3.1
2026-09-09T09:41:02Z ERROR Traceback (most recent call last):
2026-09-09T09:41:02Z ERROR   File "app/config.py", line 22, in load_config
2026-09-09T09:41:02Z ERROR     secret = os.environ["JWT_SECRET_KEY"]
2026-09-09T09:41:02Z ERROR KeyError: 'JWT_SECRET_KEY'
2026-09-09T09:41:03Z ERROR Application startup failed, exit code 1
""",

    "Permission Denied on Deploy": """
2026-09-09T14:20:11Z INFO  Deploying build #482 to prod-cluster
2026-09-09T14:20:13Z ERROR rpc error: code = PermissionDenied desc = service account
    deploy-bot@project.iam.gserviceaccount.com does not have
    permission to access namespace 'prod'
2026-09-09T14:20:13Z ERROR Deployment aborted
""",

    "Database Connection Timeout": """
2026-09-09T16:05:00Z INFO  orders-service connecting to db host=db-primary.internal
2026-09-09T16:05:30Z ERROR could not connect to server: Connection timed out
2026-09-09T16:05:30Z ERROR   Is the server running on host "db-primary.internal" and accepting
    TCP/IP connections on port 5432?
2026-09-09T16:05:31Z ERROR Retrying (1/3)...
2026-09-09T16:06:01Z ERROR Retrying (2/3)...
2026-09-09T16:06:31Z ERROR Max retries exceeded. Service health check failing.
""",
}
