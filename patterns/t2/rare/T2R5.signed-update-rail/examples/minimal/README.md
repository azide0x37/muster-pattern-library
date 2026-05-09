# Minimal Signed Update Rail Example

The update rail expects a release manifest with a version, artifact URL, and SHA256:

```json
{
  "version": "0.2.0",
  "artifact_url": "https://example.invalid/releases/example-0.2.0.tar.gz",
  "sha256": "..."
}
```

The artifact is extracted into `/opt/<project>/releases/<version>`, `/opt/<project>/current` is switched, and `current/bin/doctor.sh` decides whether promotion stands.
