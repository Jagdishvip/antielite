#!/usr/bin/env python3
"""Automate renaming AntiElite app Kotlin package (`com.elitex` -> `com.elitex`)
and branding (`AntiElite` -> `AntiElite`) inside the `app/` module.
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path("/storage/emulated/0/AndroidCSProjects/AntiElite")
APP = ROOT / "app"

OLD_PKG = "com.elitex"
NEW_PKG = "com.elitex"
OLD_PATH = Path("ai/antielite")
NEW_PATH = Path("com/elitex")

CLASS_RENAMES = {
    "AntiEliteApplication": "AntiEliteApplication",
    "AntiEliteDeviceAdminReceiver": "AntiEliteDeviceAdminReceiver",
    "AntiEliteDocumentsProvider": "AntiEliteDocumentsProvider",
    "AntiEliteFileProvider": "AntiEliteFileProvider",
    "AntiEliteLiveDiagnostics": "AntiEliteLiveDiagnostics",
    "AntiEliteService": "AntiEliteService",
}


def replace_in_file(path: Path, replacements: list[tuple[str, str]]) -> bool:
    if not path.exists():
        return False
    orig = path.read_text(encoding="utf-8")
    text = orig
    for old, new in replacements:
        text = text.replace(old, new)
    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def move_package_tree(src_root: Path) -> int:
    old_dir = src_root / OLD_PATH
    new_dir = src_root / NEW_PATH
    if not old_dir.exists():
        return 0
    # Remove temporary TermuxCompat.kt in main/java/com/elitex/app if present
    temp_compat = new_dir / "app" / "TermuxCompat.kt"
    if temp_compat.exists():
        temp_compat.unlink()

    moved = 0
    for src_file in list(old_dir.rglob("*")):
        if not src_file.is_file():
            continue
        rel = src_file.relative_to(old_dir)
        dest_name = rel.name
        for old_cls, new_cls in CLASS_RENAMES.items():
            if dest_name == f"{old_cls}.kt":
                dest_name = f"{new_cls}.kt"
                break
        dest_file = new_dir / rel.parent / dest_name
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_file), str(dest_file))
        moved += 1

    # Clean up empty old directory tree `ai/antielite` and `ai` if empty
    shutil.rmtree(old_dir, ignore_errors=True)
    ai_dir = src_root / "ai"
    if ai_dir.exists() and not any(ai_dir.rglob("*")):
        shutil.rmtree(ai_dir, ignore_errors=True)
    return moved


def main() -> None:
    moved_total = 0
    for sub in ("src/main/java", "src/test/java", "src/androidTest/java"):
        moved_total += move_package_tree(APP / sub)

    # Update all Kotlin files under app/src (main, debug, test, androidTest)
    kt_updated = 0
    kt_replacements: list[tuple[str, str]] = [
        (OLD_PKG, NEW_PKG),
        *CLASS_RENAMES.items(),
    ]
    for kt in list((APP / "src").rglob("*.kt")) + list((APP / "src").rglob("*.java")):
        if replace_in_file(kt, kt_replacements):
            kt_updated += 1

    # Update app/build.gradle.kts
    gradle_updated = replace_in_file(
        APP / "build.gradle.kts",
        [
            ('namespace = "com.elitex"', 'namespace = "com.elitex"'),
            ("package com.elitex.data.changelog", "package com.elitex.data.changelog"),
            ("ai/antielite/data/changelog/GeneratedChangelog.kt", "com/elitex/data/changelog/GeneratedChangelog.kt"),
            ("package com.elitex.i18n", "package com.elitex.i18n"),
            ("ai/antielite/i18n/L.kt", "com/elitex/i18n/L.kt"),
        ],
    )

    # Update ProGuard rules
    proguard_updated = replace_in_file(
        APP / "proguard-rules.pro",
        [(OLD_PKG, NEW_PKG), ("for AntiElite", "for AntiElite")],
    )

    # Update widget XMLs + themes
    xml_updated = 0
    for xml_path in (APP / "src/main/res").rglob("*.xml"):
        if replace_in_file(
            xml_path,
            [
                (OLD_PKG, NEW_PKG),
                ("Theme.AntiElite.", "Theme.AntiElite."),
            ],
        ):
            xml_updated += 1

    # Update en.json class reference for AntiEliteApplication.kt
    replace_in_file(
        APP / "src/main/assets/i18n/en.json",
        [("AntiEliteApplication.kt", "AntiEliteApplication.kt")],
    )

    # Update scripts/i18n helpers if present
    for py_path in (ROOT / "scripts/i18n").glob("*.py"):
        replace_in_file(py_path, [(f"{OLD_PKG}.i18n.L", f"{NEW_PKG}.i18n.L")])

    # Update app/src/main/AndroidManifest.xml cleanly (deduplicating Termux wrapper components)
    manifest_path = APP / "src/main/AndroidManifest.xml"
    m_text = manifest_path.read_text(encoding="utf-8")
    # Remove duplicate com.elitex.app.* blocks added before full package move
    dup_blocks = [
        """        <activity
            android:name="com.elitex.app.TermuxOpenActivity"
            android:exported="true"
            android:permission="${applicationId}.permission.RUN_COMMAND"
            android:theme="@android:style/Theme.Translucent.NoTitleBar">
            <intent-filter>
                <action android:name="${applicationId}.app.TermuxUrlOpenActivity" />
                <action android:name="${applicationId}.app.TermuxOpenActivity" />
                <action android:name="android.intent.action.VIEW" />
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
            </intent-filter>
        </activity>""",
        """        <receiver
            android:name="com.elitex.app.TermuxSystemReceiver"
            android:exported="true"
            android:permission="${applicationId}.permission.RUN_COMMAND">
            <intent-filter>
                <action android:name="${applicationId}.app.request_storage_permissions" />
                <action android:name="${applicationId}.app.reload_style" />
            </intent-filter>
        </receiver>""",
        """        <receiver
            android:name="com.elitex.app.TermuxOpenReceiver"
            android:exported="true"
            android:permission="${applicationId}.permission.RUN_COMMAND">
            <intent-filter>
                <action android:name="${applicationId}.app.TermuxOpenReceiver" />
                <action android:name="android.intent.action.VIEW" />
                <action android:name="android.intent.action.SEND" />
                <category android:name="android.intent.category.DEFAULT" />
            </intent-filter>
        </receiver>""",
        """        <service
            android:name="com.elitex.app.TermuxService"
            android:enabled="true"
            android:exported="true"
            android:permission="${applicationId}.permission.RUN_COMMAND"
            android:foregroundServiceType="specialUse">
            <property
                android:name="android.app.PROPERTY_SPECIAL_USE_FGS_SUBTYPE"
                android:value="Background terminal and AI language server execution" />
            <intent-filter>
                <action android:name="${applicationId}.service_wake_lock" />
                <action android:name="${applicationId}.service_wake_unlock" />
                <action android:name="${applicationId}.service_stop" />
            </intent-filter>
        </service>""",
    ]
    for blk in dup_blocks:
        m_text = m_text.replace("\n\n" + blk, "")
    for old, new in [(OLD_PKG, NEW_PKG), ("Theme.AntiElite.", "Theme.AntiElite."), *CLASS_RENAMES.items()]:
        m_text = m_text.replace(old, new)
    manifest_path.write_text(m_text, encoding="utf-8")

    print(
        f"DONE: moved={moved_total} files, updated_kt={kt_updated}, "
        f"gradle={gradle_updated}, proguard={proguard_updated}, xml={xml_updated}"
    )


if __name__ == "__main__":
    main()
