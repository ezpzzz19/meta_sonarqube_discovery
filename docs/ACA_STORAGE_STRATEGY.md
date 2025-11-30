# Azure Container Apps Storage Strategy

## Storage Decision Matrix

| Data Type | Current Location | Storage Type | Rationale |
|-----------|------------------|--------------|-----------|
| **PostgreSQL Data** | Azure PostgreSQL | Managed DB | ✅ Persistent, backed up, managed |
| **SonarQube Elasticsearch** | `/opt/sonarqube/data` | **Ephemeral (local SSD)** | ✅ Fast, free, rebuilds from PostgreSQL |
| **SonarQube Extensions** | `/opt/sonarqube/extensions` | **Azure Files (Premium)** | ✅ Persist plugins across restarts |
| **SonarQube Logs** | `/opt/sonarqube/logs` | **Azure Blob** (optional) | ✅ Cheap archival, diagnostics |
| **Backend Code** | Docker image | N/A | ✅ Stateless |
| **Frontend Assets** | Docker image | N/A | ✅ Stateless |

## Why Ephemeral for Elasticsearch?

### SonarQube's Data Flow:
```
1. Scan repo → SonarQube analyzes code
2. Results stored in PostgreSQL ✅ (persistent)
3. Elasticsearch indexes for fast search ⚡ (can be rebuilt)
4. Your backend reads from PostgreSQL ✅ (persistent)
```

**Key Insight**: PostgreSQL is the source of truth, Elasticsearch is just a cache!

### Rebuild Time After Scale-to-Zero:
- Small project (100-500 issues): ~30 seconds
- Medium project (500-2000 issues): ~2 minutes  
- Large project (2000+ issues): ~5 minutes

**For a school project with occasional scans**: Totally acceptable!

## Cost Comparison

### Current ACI Setup (Always Running):
```
PostgreSQL (B_Standard_B2s): $54/month
Storage Account (32GB):      $4/month
Container Instances:         $35/month (estimated)
────────────────────────────────────
Total:                       ~$93/month
```

### ACA with Ephemeral + Scale to Zero:
```
PostgreSQL (B_Standard_B2s):     $54/month
Storage Account (minimal):       $1/month
ACA Environment:                 $0/month (free tier: 180k vCPU-seconds)
Frontend (scale-to-0):           ~$0/month (only runs when accessed)
Backend (1 replica always on):   ~$8/month (0.25 vCPU × 0.5GB)
SonarQube (scale-to-0):          ~$0/month (only runs during scans)
────────────────────────────────────
Total:                           ~$63/month ✅ 32% savings!
```

### ACA with Azure Files Premium (No Scale-to-Zero):
```
PostgreSQL:                  $54/month
Azure Files Premium (32GB):  $6.40/month
ACA - same as above:         $8/month
────────────────────────────────────
Total:                       ~$68/month (still 27% savings)
```

## Recommended: Start with Ephemeral

### Why:
1. **Fastest development iteration**
2. **Lowest cost**
3. **Good enough for school project**
4. **Can always add Azure Files later if needed**

### When to Upgrade to Azure Files:
- ⚠️ If rebuild time becomes annoying (>5 minutes)
- ⚠️ If you have 10,000+ issues indexed
- ⚠️ If you're running in production with SLAs

## Alternative: Azure Files for Everything

If you want persistent Elasticsearch (no rebuilds):

### Pros:
- ✅ Instant startup after scale-to-zero
- ✅ No index rebuild time
- ✅ Better for frequent restarts

### Cons:
- ❌ Slower Elasticsearch performance (network latency)
- ❌ $6-8/month additional cost
- ❌ Need Premium tier for acceptable performance

### Configuration:
```hcl
# In Terraform
resource "azurerm_storage_share" "sonarqube_data" {
  name                 = "sonarqube-data"
  storage_account_name = azurerm_storage_account.storage.name
  quota                = 32
  
  # Premium tier for Elasticsearch
  access_tier = "Premium"
}
```

## My Recommendation for You

### Phase 1: School Project (Now)
```
✅ Stay with ACI for simplicity
✅ Get SonarQube token working
✅ Demo working system
✅ Finish project
```

### Phase 2: Post-Submission Migration (Optional)
```
✅ Migrate to ACA
✅ Use ephemeral storage
✅ Enable scale-to-zero on SonarQube
✅ Keep backend running (for background worker)
✅ Save ~$30/month
```

### Phase 3: Production (If You Productionize)
```
✅ Add Azure Files Premium for SonarQube data
✅ Set up proper monitoring
✅ Configure auto-scaling rules
✅ Add Azure Front Door (global CDN)
```

## Code Storage Analogy

Think of it like this:

**Blob Storage** = Amazon S3
- Great for: Images, videos, backups, logs
- Bad for: Databases, file locking, random access

**Azure Files** = Network Attached Storage (NAS)
- Great for: Shared file systems, legacy apps
- Bad for: High-performance databases

**Ephemeral Storage** = Local SSD
- Great for: Databases, caches, temporary data
- Bad for: Persistent data, shared across containers

**Azure PostgreSQL** = Managed database
- Great for: Persistent structured data
- Perfect for: Your use case (source of truth)

## Questions to Ask Yourself

1. **How often will SonarQube restart?**
   - With ACA scale-to-0: Every time it scales up (after inactivity)
   - If acceptable wait time: Use ephemeral

2. **How big is your codebase?**
   - Small (<1000 issues): Ephemeral is fine
   - Large (>5000 issues): Consider Azure Files

3. **Is this for demo or production?**
   - Demo: Ephemeral (fast, cheap)
   - Production: Azure Files Premium

4. **What's your budget?**
   - Tight: Ephemeral ($0)
   - Comfortable: Azure Files Standard ($0.12/GB)
   - Enterprise: Azure Files Premium ($0.20/GB)

## Final Answer

**For your school project**: 
- Use **ephemeral storage** with ACA
- SonarQube rebuilds indices from PostgreSQL after scale-up
- Save money, get HTTPS for free, modern architecture
- 2-3 minute warmup time is acceptable

**If warmup time becomes annoying**:
- Add Azure Files Premium just for SonarQube data
- ~$6/month extra, instant restarts
