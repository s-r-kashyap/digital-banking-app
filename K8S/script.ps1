$REGISTRY_URL    = "ghcr.io"
$IMAGE_NAMESPACE = "your-org"
$SERVICES        = @(
    "frontend-service",
    "auth-service",
    "account-service",
    "beneficiary-service",
    "payment-service",
    "transaction-service"
)

New-Item -ItemType Directory -Force -Path ".\k8s" | Out-Null

@"
apiVersion: v1
kind: Namespace
metadata:
  name: digital-banking
"@ | Set-Content -Path ".\k8s\namespace.yaml" -Encoding utf8

foreach ($svc in $SERVICES) {
    $dir          = Join-Path ".\k8s\services" $svc
    $isFrontend   = ($svc -eq "frontend-service")
    $probePath    = if ($isFrontend) { "/" } else { "/docs" }
    $svcType      = if ($isFrontend) { "NodePort" } else { "ClusterIP" }
    $nodePortLine = if ($isFrontend) { "`n      nodePort: 30080" } else { "" }

    New-Item -ItemType Directory -Force -Path $dir | Out-Null

@"
apiVersion: apps/v1
kind: Deployment
metadata:
  name: $svc
  namespace: digital-banking
  labels:
    app: $svc
spec:
  replicas: 2
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: $svc
  template:
    metadata:
      labels:
        app: $svc
    spec:
      imagePullSecrets:
        - name: registry-creds
      containers:
        - name: $svc
          image: ${REGISTRY_URL}/${IMAGE_NAMESPACE}/${svc}:latest
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
              name: http
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "250m"
              memory: "256Mi"
          readinessProbe:
            httpGet:
              path: $probePath
              port: http
            initialDelaySeconds: 5
            periodSeconds: 10
            failureThreshold: 3
          livenessProbe:
            httpGet:
              path: $probePath
              port: http
            initialDelaySeconds: 15
            periodSeconds: 15
            failureThreshold: 3
"@ | Set-Content -Path (Join-Path $dir "deployment.yaml") -Encoding utf8

@"
apiVersion: v1
kind: Service
metadata:
  name: $svc
  namespace: digital-banking
  labels:
    app: $svc
spec:
  type: $svcType
  selector:
    app: $svc
  ports:
    - name: http
      port: 8000
      targetPort: http$nodePortLine
"@ | Set-Content -Path (Join-Path $dir "service.yaml") -Encoding utf8

@"
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: ${svc}-hpa
  namespace: digital-banking
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: $svc
  minReplicas: 2
  maxReplicas: 5
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 65
"@ | Set-Content -Path (Join-Path $dir "hpa.yaml") -Encoding utf8
}