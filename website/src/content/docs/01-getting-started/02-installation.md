---
title: Install AntiElite
sidebar: Installation
description: Download the APK from GitHub and install it on your phone. Takes about two minutes.
---

AntiElite isn't on the Play Store. You install it from its GitHub releases page, like many open-source apps. It works on **Android 7.0 and newer**.

## Which file to download

Every release has a few APK files. Most people want the first one.

| File | For |
| :--- | :--- |
| `AntiElite-v2.x.x.apk` | Almost every phone (64-bit ARM). **Start with this one.** |
| `AntiElite-v2.x.x-chroot.apk` | Rooted phones that will use the [Ubuntu chroot](../04-power-features/05-ubuntu-chroot.md). |
| `AntiElite-v2.x.x-x86_64.apk` | Emulators and Intel / AMD Chromebooks. |

## Install it

:::steps
### Open the releases page

On your phone, open [github.com/santoshkurmi/antigem/releases](https://github.com/santoshkurmi/antigem/releases). The newest release is at the top.

### Download the APK

Scroll down to **Assets** and tap `AntiElite-v2.x.x.apk`. Your browser downloads it.

> [!NOTE]
> Releases marked **Pre-release** are betas. They install over the stable app and keep your data.

### Allow installing apps from your browser

When you open the file, Android asks for permission to install apps from your browser. Tap **Settings**, turn on **Allow from this source**, then go back.

### Install and open

Tap **Install**. When it is done, tap **Open**. AntiElite starts with its welcome screen.

![The first screen: choosing your agents](/screens/agent_picker.webp "phone")
:::

## Next step

The app now walks you through permissions, picking agents and installing its Linux environment. See [First launch](./03-first-launch.md).

:::details Android says "App not installed"
This usually means another build of AntiElite with a different signature is installed, or the download was cut short. Download the APK again. If an older test build is installed, uninstall it first (back up your environment before).
:::

:::details Can I install it next to Termux?
Yes. From v2.0.0, AntiElite uses its own package name (`com.elitex`), so it installs next to the real Termux app and next to the old AntiElite.
:::
