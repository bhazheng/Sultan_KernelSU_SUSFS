# Google Tensor (gs201) KernelSU-Next + SuSFS Build System

[![Release](https://img.shields.io/github/v/release/bhazheng/Sultan_KernelSU_SUSFS?color=blue&label=Release)](https://github.com/bhazheng/Sultan_KernelSU_SUSFS/releases)
[![Build Status](https://img.shields.io/github/actions/workflow/status/bhazheng/Sultan_KernelSU_SUSFS/build-kernel-release.yml?branch=main&label=CI%20Build)](https://github.com/bhazheng/Sultan_KernelSU_SUSFS/actions)
[![Device](https://img.shields.io/badge/Device-Pixel%207%20Series%20(gs201)-informational)](https://github.com/sidharthify/android_kernel_google_gs201)
[![Kernel 6.12](https://img.shields.io/badge/Kernel-6.12%20(Android%2016)-brightgreen)](https://github.com/sidharthify/android_kernel_google_gs201/tree/6.12-test)
[![Kernel 6.1](https://img.shields.io/badge/Kernel-6.1%20(Android%2014)-blue)](https://github.com/bhazheng/android_kernel_google_tensynos/tree/android14-6.1.145)

Automated continuous integration and build system for Google Tensor devices (**gs201** / Pixel 7 series: cheetah, panther, lynx), supporting both **Linux 6.12 (Sidharthify / Android 16)** and **Linux 6.1 (Sultan / Android 14)** with **KernelSU-Next**, **SuSFS**, **NoMount**, **BBR/BBRv3**, and performance optimizations.

---

## Disclaimer

```
* Your warranty is now void.
* I am not responsible for bricked devices, dead SD cards, bootloops, or data loss.
* Please do research before flashing custom kernels and rooting your device.
* YOU are choosing to make these modifications at your own risk.
```

---

## Supported Kernel Trees

1. **Sidharthify Kernel 6.12 (Android 16)**:
   - Source: [sidharthify/android_kernel_google_gs201](https://github.com/sidharthify/android_kernel_google_gs201) (branch `6.12-test`).
   - Linux 6.12 LTS baseline with vendor scheduler, BigOcean video codec, in-tree google-modules, TCPM fixes, and Android 16 platform support.
2. **Sultan Kernel 6.1 (Android 14)**:
   - Source: [bhazheng/android_kernel_google_tensynos](https://github.com/bhazheng/android_kernel_google_tensynos) (branch `android14-6.1.145`).
   - Fully integrated monolithic kernel (`CONFIG_INTEGRATE_MODULES=y`) by kerneltoast and bhazheng.

---

## Features

- **KernelSU-Next (pershoot `dev-susfs`)**:
  - Native kernel-space root implementation without loadable module dependency.
  - Native SuSFS inline hooks enabled.
- **SuSFS (simonpunk `gki-android16-6.12` / pershoot `gki-android14-6.1`)**:
  - Advanced root-hiding subsystem integrated into kernel VFS and namespace calls.
  - Tailored patches for zero-reject integration on both 6.12 and 6.1 trees.
- **NoMount (by maxsteeel)**:
  - Transparent in-memory VFS path redirection framework.
  - Intercepts path resolution dynamically without polluting `/proc/mounts`.
  - Universal metamodule (`NoMount.zip`) built from source via Zig `0.13.0`.
- **Networking & BBR / BBRv3**:
  - BBR congestion control set as default with FQ and CAKE queue disciplines.
  - IPSet, WireGuard, and TTL/HL netfilter targets enabled.
- **NTSync**:
  - NT synchronization primitives for high-performance Wine/Windows emulation gaming.
- **Storage & System Optimizations**:
  - Optimized I/O congestion and reduced filesystem write latency.
  - Silenced kernel logspam (system & IRQ CPU logspam).
  - GKID optimization patches applied for Sultan 6.1; Sidharthify 6.12 relies on native in-tree optimizations without GKID patches.

---

## Build Variants & Toolchains

### Variants:
1. **`KernelSU-Next`**:
   - Kernel + KernelSU-Next + SuSFS inline hooks + NoMount + BBR.
2. **`NoRoot`**:
   - Clean kernel with all performance/network patches + NoMount + BBR (no root, no KSU/SuSFS hooks).

### Toolchains:
- **Clang (Neutron Clang 06092026)**: LLVM toolchain with Android GKI standard **ThinLTO** (`CONFIG_LTO_CLANG_THIN`).
- **GCC (GNU Compiler Collection 14.2.0)**: Official AArch64 crosstool from kernel.org.

---

## Releases & Artifacts

Releases are published automatically on the **[Releases](https://github.com/bhazheng/Sultan_KernelSU_SUSFS/releases)** page:

| File | Description |
|---|---|
| `KernelSU-Next-gs201-6.12-Sidharthify-clang.zip` | 6.12 AnyKernel3 flashable kernel (KSU-Next, Neutron Clang) |
| `NoRoot-gs201-6.12-Sidharthify-clang.zip` | 6.12 AnyKernel3 flashable kernel (Clean, Neutron Clang) |
| `KernelSU-Next-gs201-Sultan-clang.zip` | 6.1 AnyKernel3 flashable kernel (KSU-Next, Neutron Clang) |
| `NoRoot-gs201-Sultan-clang.zip` | 6.1 AnyKernel3 flashable kernel (Clean, Neutron Clang) |
| `NoMount.zip` | Universal NoMount metamodule (install via Root Manager) |
| `KernelSU_Next_*.apk` | Official KernelSU-Next companion manager app |
| `upstream-shas-*.json` | Git commit audit manifest for build reproducibility |

---

## Installation Guide

### Prerequisites:
- Unlocked bootloader on Pixel 7 / Pixel 7 Pro / Pixel 7a (**gs201**).
- Matching Android firmware (Android 16 for 6.12 builds, Android 14/15 for 6.1 builds).

### 1. Flashing the Kernel
1. Download the AnyKernel3 ZIP corresponding to your preferred kernel version, variant, and toolchain from [Releases](https://github.com/bhazheng/Sultan_KernelSU_SUSFS/releases).
2. Flash the ZIP using one of the following methods:
   - **[Horizon Kernel Flasher](https://github.com/libxzr/HorizonKernelFlasher)** (Recommended).
   - **Franco Kernel Manager (FKM)** or **EX Kernel Manager**.
   - Custom recovery (TWRP) if available.
3. Reboot your device.

### 2. Setting Up Root & Modules (KernelSU-Next variant only)
1. Install the downloaded `KernelSU_Next_*.apk` manager application.
2. Open the app to verify root access and SuSFS status.
3. Install companion modules:
   - **SuSFS Module**: Download and flash [ksu_module_susfs](https://github.com/sidex15/ksu_module_susfs).
   - **NoMount Metamodule**: Flash `NoMount.zip` directly in the manager app.
4. Reboot your device to activate all protections.

---

## Repository Structure

```
.
├── .github/workflows/
│   ├── build-kernel-release.yml                       # Unified orchestration workflow (6.12 & 6.1)
│   ├── sidharthify-clang.yml                          # Sidharthify 6.12 Neutron Clang build pipeline
│   └── sultan-clang.yml                               # Sultan 6.1 Neutron Clang build pipeline
├── patches/
│   ├── 00_sultan_kernel_fixes.patch                   # Sultan tree linker, weak symbol, setlocalversion fixes
│   ├── 02_ksun_sultan.patch                           # Non-modular patch_memory build hook for KSU
│   ├── 50_add_susfs_in_gki-android16-6.12-sidharthify.patch # SuSFS inline hooks for Sidharthify 6.12
│   ├── 50_add_susfs_in_gki-android14-6.1-sultan.patch # SuSFS inline hooks for Sultan 6.1 tree
│   └── bbrv3.patch                                    # BBRv3 congestion control patch
└── README.md
```

---

## Credits & Acknowledgements

Special thanks to the developers and open-source projects that make this kernel possible:

- **[sidharthify](https://github.com/sidharthify)** - Creator and maintainer of the gs201 Linux 6.12 kernel tree.
- **[kerneltoast (Sultan Alsawaf)](https://github.com/kerneltoast)** - Creator of Sultan Kernel.
- **[bhazheng](https://github.com/bhazheng)** - Maintainer of the gs201 Tensynos kernel tree and Sultan patches.
- **[pershoot (KernelSU-Next dev-susfs)](https://github.com/pershoot/KernelSU-Next/tree/dev-susfs)** - For the `dev-susfs` fork of KernelSU-Next with native SuSFS integration.
- **[tiann](https://github.com/tiann)** & **[rifsxd](https://github.com/KernelSU-Next/KernelSU-Next)** - KernelSU & KernelSU-Next core developers.
- **[simonpunk](https://gitlab.com/simonpunk/susfs4ksu.git)** - Creator of SuSFS.
- **[maxsteeel](https://github.com/maxsteeel/nomount)** - Creator of the NoMount framework.
- **[sidex15](https://github.com/sidex15/ksu_module_susfs)** - Creator of the SuSFS Magisk/KSU module.
- **[Neutron Toolchains](https://github.com/Neutron-Toolchains)** - High-performance LLVM/Clang builds.
- **[TheWildJames](https://github.com/TheWildJames)** & **[WildKernels](https://github.com/WildKernels)** - Base build scripts and CI inspirations.
- **[osm0sis](https://github.com/osm0sis/AnyKernel3)** - AnyKernel3 template and flashing tools.
