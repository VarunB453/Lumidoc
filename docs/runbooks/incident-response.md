# Incident Response Runbook

## Severity Levels

| Level | Description | Response Time | Examples |
|-------|-------------|---------------|----------|
| P1 | Critical | 15 min | Service down, data loss |
| P2 | High | 1 hour | Major feature broken |
| P3 | Medium | 4 hours | Minor feature broken |
| P4 | Low | 24 hours | Cosmetic issues |

## Incident Response Steps

### 1. Detection & Alert
- Monitor alerts from Prometheus/Grafana
- Check application logs in Loki
- Review error tracking dashboard

### 2. Triage
- Determine severity level
- Identify affected services
- Notify relevant team members

### 3. Investigation
- Check recent deployments
- Review application logs
- Check infrastructure metrics
- Identify root cause

### 4. Mitigation
- Apply immediate fix or rollback
- Verify service recovery
- Monitor for recurrence

### 5. Post-Incident
- Write post-mortem within 48 hours
- Identify action items
- Update runbooks if needed

## Common Issues

### API Server Not Responding
1. Check pod/container status: `docker ps` or `kubectl get pods`
2. Check logs: `docker logs <container>` or `kubectl logs <pod>`
3. Check database connectivity
4. Check Redis connectivity
5. Restart if needed: `docker restart <container>`

### Database Connection Issues
1. Check PostgreSQL status
2. Verify connection pool settings
3. Check for long-running queries
4. Review connection limits

### High Memory Usage
1. Check for memory leaks in application
2. Review Celery task queue size
3. Check FAISS index size
4. Consider scaling horizontally
