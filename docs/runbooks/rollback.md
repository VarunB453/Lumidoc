# Rollback Runbook

## When to Rollback
- Critical bugs affecting users
- Performance degradation > 50%
- Data integrity issues
- Security vulnerabilities

## Rollback Procedures

### Docker Compose Deployment
```bash
# List available images
docker images | grep lumidoc

# Rollback to previous version
docker compose -f infrastructure/docker/compose/docker-compose.prod.yml down
VERSION=<previous-version> docker compose -f infrastructure/docker/compose/docker-compose.prod.yml up -d
```

### Kubernetes Deployment
```bash
# Check rollout history
kubectl rollout history deployment/<deployment-name>

# Rollback to previous revision
kubectl rollout undo deployment/<deployment-name>

# Rollback to specific revision
kubectl rollout undo deployment/<deployment-name> --to-revision=<revision>
```

### Database Rollback
```bash
# Rollback last migration
cd apps/server
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>
```

## Post-Rollback
1. Verify service health
2. Notify team of rollback
3. Investigate root cause
4. Create hotfix if needed
5. Document in incident report
