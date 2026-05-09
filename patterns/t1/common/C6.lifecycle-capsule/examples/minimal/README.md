# Minimal Lifecycle Capsule Example

Run a staged install twice and confirm that local config survives:

```sh
root="$(mktemp -d)"
MUSTER_ROOT="$root" MUSTER_VERSION=0.1.0 scripts/install.sh --apply
printf '\nUSER_SETTING=kept\n' >> "$root/etc/muster-lifecycle-example/muster-lifecycle-example.env"
MUSTER_ROOT="$root" MUSTER_VERSION=0.1.0 scripts/install.sh --apply
```

The active release is `$root/opt/muster-lifecycle-example/current`, and lifecycle facts are recorded under `$root/var/lib/muster/lifecycle/muster-lifecycle-example`.
