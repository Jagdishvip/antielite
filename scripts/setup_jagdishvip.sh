#!/usr/bin/env bash
set -euo pipefail

OWNER="Jagdishvip"
PROJ="/storage/emulated/0/AndroidCSProjects/AntiGem"
STAGE="${HOME}/.cache/jagdishvip_stage"

echo "==> Checking GitHub authentication..."
gh auth status
gh auth setup-git

rm -rf "$STAGE"
mkdir -p "$STAGE"

create_and_push_dir() {
    local repo="$1"
    local src="$2"
    local branch="$3"
    local prep_cmd="${4:-}"
    local work="$STAGE/$repo"

    echo "==> Creating GitHub repo $OWNER/$repo (if missing)..."
    gh repo create "$OWNER/$repo" --public 2>/dev/null || gh repo view "$OWNER/$repo" >/dev/null

    echo "==> Staging $repo..."
    rm -rf "$work"
    mkdir -p "$work"
    cp -rL "$src/." "$work/"
    rm -rf "$work/.git"

    if [ -n "$prep_cmd" ]; then
        (cd "$work" && eval "$prep_cmd")
    fi

    cd "$work"
    git init -b "$branch"
    git config user.name "$OWNER"
    git config user.email "${OWNER}@users.noreply.github.com"
    git add -A
    git commit -m "Initial AntiElite setup for $repo"
    git remote add origin "https://github.com/$OWNER/$repo.git"
    git push -u origin "$branch" --force
}

# 1. Plugins repo
create_and_push_dir "antielite_plugins" "$PROJ/antigem_plugins" "main"

# 2. Mini apps repo (ensure antielite-mini-apps.json exists & matches dist/*.agapp filenames)
create_and_push_dir "antielite_mini_apps" "$PROJ/antigem_mini_apps" "main" \
    'sed "s/com\.antielite\./com.antigem./g" antigem-mini-apps.json > antielite-mini-apps.json'

# 3. Languages repo (mirror upstream files since local antigem_languages/ is empty)
echo "==> Creating & syncing $OWNER/antielite_languages..."
gh repo create "$OWNER/antielite_languages" --public 2>/dev/null || gh repo view "$OWNER/antielite_languages" >/dev/null
rm -rf "$STAGE/antielite_languages"
git clone --depth=1 https://github.com/Santoshkurmi/antigem_languages.git "$STAGE/antielite_languages"
(
    cd "$STAGE/antielite_languages"
    rm -rf .git
    git init -b main
    git config user.name "$OWNER"
    git config user.email "${OWNER}@users.noreply.github.com"
    git add -A
    git commit -m "Initial AntiElite languages"
    git remote add origin "https://github.com/$OWNER/antielite_languages.git"
    git push -u origin main --force
)

# 4. Main app repo (excluding build outputs / caches / nested submodule .git)
echo "==> Creating & staging $OWNER/antielite..."
gh repo create "$OWNER/antielite" --public 2>/dev/null || gh repo view "$OWNER/antielite" >/dev/null
rm -rf "$STAGE/antielite"
mkdir -p "$STAGE/antielite"
tar -C "$PROJ" \
    --exclude-vcs \
    --exclude='build' \
    --exclude='*/build' \
    --exclude='.gradle' \
    --exclude='.kotlin' \
    --exclude='node_modules' \
    --exclude='local.properties' \
    -cf - . | tar -C "$STAGE/antielite" -xf -
(
    cd "$STAGE/antielite"
    git init -b main
    git config user.name "$OWNER"
    git config user.email "${OWNER}@users.noreply.github.com"
    git add -A
    git commit -m "Initial AntiElite source"
    git remote add origin "https://github.com/$OWNER/antielite.git"
    git push -u origin main --force
    git push origin main:standalone --force
)

# 5. Upload pinned release assets (render-v1 and rootfs-v2)
mkdir -p "$STAGE/releases"

echo "==> Uploading render-v1 release..."
curl -fL "https://github.com/Santoshkurmi/antigem/releases/download/render-v1/antigem-render-bundle-v1.zip" \
    -o "$STAGE/releases/antielite-render-bundle-v1.zip"
gh release create render-v1 "$STAGE/releases/antielite-render-bundle-v1.zip" \
    -R "$OWNER/antielite" --title "render-v1" --notes "AntiElite STEM render bundle" 2>/dev/null || \
    gh release upload render-v1 "$STAGE/releases/antielite-render-bundle-v1.zip" -R "$OWNER/antielite" --clobber

echo "==> Uploading rootfs-v2 release (~400 MB)..."
curl -fL "https://github.com/Santoshkurmi/antigem/releases/download/rootfs-v2/bootrapz_2026-11-19.zip" \
    -o "$STAGE/releases/bootrapz_2026-11-19.zip"
gh release create rootfs-v2 "$STAGE/releases/bootrapz_2026-11-19.zip" \
    -R "$OWNER/antielite" --title "rootfs-v2" --notes "AntiElite Linux rootfs" 2>/dev/null || \
    gh release upload rootfs-v2 "$STAGE/releases/bootrapz_2026-11-19.zip" -R "$OWNER/antielite" --clobber

rm -rf "$STAGE"
echo "==> DONE! All repositories and releases pushed to https://github.com/$OWNER"
