"""AI-powered metric anomaly analyzer using AWS Bedrock."""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from typing import Any

import boto3
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Anomaly Analyzer",
    description="AWS Bedrock-powered anomaly analysis for observability metrics",
    version="1.0.0",
)

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
BEDROCK_MODEL_ID = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0")


def get_bedrock_client():
    """Create a Bedrock Runtime client."""
    return boto3.client("bedrock-runtime", region_name=AWS_REGION)


def invoke_bedrock(prompt: str) -> str:
    """Invoke AWS Bedrock with the given prompt and return the response text."""
    client = get_bedrock_client()
    body = json.dumps(
        {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        }
    )
    try:
        response = client.invoke_model(modelId=BEDROCK_MODEL_ID, body=body)
        result = json.loads(response["body"].read())
        return result["content"][0]["text"]
    except Exception as e:
        logger.error("Bedrock invocation failed: %s", e)
        raise HTTPException(status_code=502, detail=f"Bedrock API error: {e}") from e


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------

class AnalyzeRequest(BaseModel):
    metric_name: str
    values: list[float]
    labels: dict[str, str] | None = None
    threshold: float | None = None


class AnalyzeResponse(BaseModel):
    metric_name: str
    analysis: str
    is_anomaly: bool
    severity: str
    timestamp: str


class AlertPayload(BaseModel):
    status: str
    alerts: list[dict[str, Any]]


class AlertExplanation(BaseModel):
    alert_name: str
    explanation: str
    suggested_remediation: str
    severity: str
    timestamp: str


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_metrics(request: AnalyzeRequest):
    """Analyze a metric time-series for anomalies using AI."""
    prompt = (
        f"You are an SRE expert analyzing monitoring metrics.\n\n"
        f"Metric: {request.metric_name}\n"
        f"Recent values: {request.values[-20:]}\n"
        f"Labels: {json.dumps(request.labels or {})}\n"
        f"Threshold: {request.threshold}\n\n"
        f"Analyze this metric for anomalies. Respond in JSON with keys:\n"
        f'- "is_anomaly": boolean\n'
        f'- "severity": "low" | "medium" | "high" | "critical"\n'
        f'- "analysis": a concise paragraph explaining the pattern, '
        f"whether it is anomalous, and the likely root cause.\n"
        f"Return ONLY valid JSON."
    )

    raw = invoke_bedrock(prompt)

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        parsed = {"is_anomaly": False, "severity": "low", "analysis": raw}

    return AnalyzeResponse(
        metric_name=request.metric_name,
        analysis=parsed.get("analysis", raw),
        is_anomaly=parsed.get("is_anomaly", False),
        severity=parsed.get("severity", "low"),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )


@app.post("/api/explain-alert", response_model=list[AlertExplanation])
async def explain_alert(payload: AlertPayload):
    """Receive an Alertmanager webhook and return AI-powered explanations."""
    explanations: list[AlertExplanation] = []

    for alert in payload.alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        prompt = (
            f"You are an SRE expert. An alert has fired.\n\n"
            f"Alert: {labels.get('alertname', 'unknown')}\n"
            f"Severity: {labels.get('severity', 'unknown')}\n"
            f"Status: {alert.get('status', 'unknown')}\n"
            f"Summary: {annotations.get('summary', 'N/A')}\n"
            f"Description: {annotations.get('description', 'N/A')}\n"
            f"Instance: {labels.get('instance', 'N/A')}\n\n"
            f"Respond in JSON with keys:\n"
            f'- "explanation": a clear explanation of what this alert means '
            f"and its likely root cause\n"
            f'- "suggested_remediation": step-by-step remediation actions\n'
            f"Return ONLY valid JSON."
        )

        raw = invoke_bedrock(prompt)
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            parsed = {
                "explanation": raw,
                "suggested_remediation": "Review the alert details and investigate manually.",
            }

        explanations.append(
            AlertExplanation(
                alert_name=labels.get("alertname", "unknown"),
                explanation=parsed.get("explanation", raw),
                suggested_remediation=parsed.get(
                    "suggested_remediation",
                    "Investigate the issue manually.",
                ),
                severity=labels.get("severity", "unknown"),
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
        )

    return explanations


@app.get("/health")
async def health():
    """Health check endpoint."""
    return JSONResponse(
        content={"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()},
        status_code=200,
    )
