# Deployment Runbook

## Environments

| Environment | Branch | URL | Auto-Deploy |
|-------------|--------|-----|-------------|
| Development | feature/* | localhost | Manual |
| Staging | develop | staging.example.com | Yes (on push) |
| Production | main (tags) | example.com | Yes (on tag) |

## Pre-Deployment Checklist

- [ ] All tests passing in CI
- [ ] Code review approved
- [ ] Database migrations tested
- [ ] Environment variables updated
- [ ] Feature flags configured
- [ ] Monitoring alerts configured

## Deployment Steps

### Staging
1. Merge feature branch to `develop`
2. CI/CD pipeline automatically deploys to staging
3. Run smoke tests
4. Verify in staging environment

### Production
1. Create a release tag: `git tag v1.x.x`
2. Push tag: `git push origin v1.x.x`
3. CI/CD pipeline builds and deploys
4. Monitor deployment progress
5. Run production smoke tests
6. Verify health checks pass

## Post-Deployment

1. Monitor error rates for 30 minutes
2. Check application performance metrics
3. Verify all services are healthy
4. Update CHANGELOG.md

## Rollback

If issues are detected post-deployment, see [rollback.md](./rollback.md).
