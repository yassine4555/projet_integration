# Jenkins Git SSL Backend Fix

## Problem
Jenkins fails with error: `fatal: Unsupported SSL backend 'openssl'. Supported SSL backends: gnutls`

This occurs because Git in the Jenkins container was compiled with GnuTLS support but is trying to use OpenSSL.

## Solution 1: Rebuild Jenkins Container with Corrected Git (Recommended)

### Step 1: Use the Provided Jenkins Dockerfile

A `Jenkins.Dockerfile` has been created in the project root with Git compiled for OpenSSL support.

### Step 2: Build the Custom Jenkins Image

```powershell
# Navigate to project root
cd "c:\Users\yasso\Desktop\antigravity portel"

# Build the Jenkins image
docker build -f Jenkins.Dockerfile -t jenkins-git-fixed:latest .
```

### Step 3: Stop and Remove Existing Jenkins Container

```powershell
# Stop current Jenkins
docker stop jenkins

# Remove container
docker rm jenkins
```

### Step 4: Run the New Jenkins Container

```powershell
docker run -d `
  --name jenkins `
  -p 8080:8080 `
  -p 50000:50000 `
  -v jenkins_home:/var/jenkins_home `
  -v /var/run/docker.sock:/var/run/docker.sock `
  jenkins-git-fixed:latest
```

### Step 5: Verify

```powershell
# Check logs
docker logs jenkins

# Verify Git
docker exec jenkins git --version
```

## Solution 2: Fix Existing Container (Quick Fix)

If you don't want to rebuild, fix the running container:

```powershell
# Access Jenkins container
docker exec -it jenkins bash

# Inside container, run:
apt-get update
apt-get remove -y git
apt-get install -y git libcurl4-openssl-dev ca-certificates
update-ca-certificates
git --version
exit

# Restart Jenkins
docker restart jenkins
```

## Solution 3: Use SSH Instead of HTTPS

In your Jenkins job configuration:
1. Change repository URL from `https://github.com/yassine4555/projet_integration.git`
2. To: `git@github.com:yassine4555/projet_integration.git`
3. Add SSH credentials in Jenkins (Credentials → Add → SSH Username with private key)

## Verify the Fix

After applying the solution, run your pipeline again. The Git fetch should work without SSL backend errors.

## Troubleshooting

If issues persist:

```powershell
# Check Git SSL support
docker exec jenkins git --version --build-options

# Test Git clone manually
docker exec jenkins git clone https://github.com/yassine4555/projet_integration.git /tmp/test
```
