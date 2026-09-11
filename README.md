# Sultan KernelSU + SUSFS for Google Tensor (gs201)

[![Release](https://img.shields.io/github/v/release/bhazheng/Sultan_KernelSU_SUSFS?color=blue&label=Release)](https://github.com/bhazheng/Sultan_KernelSU_SUSFS/releases)
[![Build Status](https://img.shields.io/github/actions/workflow/status/bhazheng/Sultan_KernelSU_SUSFS/build-kernel-release.yml?branch=main&label=CI%20Build)](https://github.com/bhazheng/Sultan_KernelSU_SUSFS/actions)
[![Device](https://img.shields.io/badge/Device-Pixel%207%20Series%20(gs201)-informational)](https://github.com/bhazheng/android_kernel_google_tensynos)
[![Kernel](https://img.shields.io/badge/Kernel-6.1%20(Android%2014)-brightgreen)](https://github.com/bhazheng/android_kernel_google_tensynos/tree/android14-6.1.145)

Automated continuous integration and build system for **Sultan Kernel** on Google Tensor devices (**gs201** / Pixel 7 series), featuring **KernelSU-Next**, **SuSFS**, **NoMount**, **BBRv3**, and performance optimizations.

---

## Disclaimer

```
* Your warranty is now void.
* I am not responsible for bricked devices, dead SD cards, bootloops, or data loss.
* Please do research before flashing custom kernels and rooting your device.
* YOU are choosing to make these modifications at your own risk.
```

---

## Features

- **Sultan Kernel (by kerneltoast / bhazheng)**:
  - Fully integrated monolithic kernel (`CONFIG_INTEGRATE_MODULES=y`) for maximum responsiveness, security, and battery efficiency.
- **KernelSU-Next (pershoot `dev-susfs`)**:
  - Native kernel-space root implementation without relying on loadable modules or KPROBES.
  - Native SuSFS inline hooks enabled.
- **SuSFS (pershoot `gki-android14-6.1`)**:
  - Advanced root-hiding subsystem integrated into kernel VFS and namespace calls.
- **NoMount (by maxsteeel)**:
  - Transparent in-memory VFS path redirection framework.
  - Intercepts path resolution dynamically without polluting `/proc/mounts`.
  - Universal metamodule (`NoMount.zip`) built from source via Zig `0.13.0`.
- **Networking & BBR / BBRv3**:
  - BBR congestion control set as default with BBRv3 available.
  - FQ & CAKE queue disciplines enabled.
  - IPSet, WireGuard, and TTL/HL targets enabled.
- **NTSync**:
  - NT synchronization primitives for high-performance Wine/Windows emulation gaming.
- **Storage & System Optimizations**:
  - Reduced F2FS write congestion and optimized min fsync blocks.
  - Silenced kernel logspam (system & IRQ CPU logspam).

---

## Build Variants & Toolchains

The repository supports multiple build configurations:

### Variants:
1. **`KernelSU-Next`**:
   - Sultan kernel + KernelSU-Next + SuSFS inline hooks + NoMount + BBRv3.
2. **`NoRoot`**:
   - Clean Sultan kernel with all performance/network patches + NoMount + BBRv3 (no root, no KSU/SuSFS hooks).

### Toolchains:
- **GCC (GNU Compiler Collection 14.2.0)**: Official AArch64 crosstool from kernel.org.
- **Clang (Neutron Clang 06092026)**: LLVM toolchain with Android GKI standard **ThinLTO** (`CONFIG_LTO_CLANG_THIN`).

---

## Releases & Artifacts

Releases are published automatically on the **[Releases](https://github.com/bhazheng/Sultan_KernelSU_SUSFS/releases)** page as a rolling `latest` release:

| File | Description |
|---|---|
| `KernelSU-Next-gs201-Sultan-gcc.zip` | AnyKernel3 flashable kernel (KSU-Next, GCC 14) |
| `KernelSU-Next-gs201-Sultan-clang.zip` | AnyKernel3 flashable kernel (KSU-Next, Neutron Clang) |
| `NoRoot-gs201-Sultan-gcc.zip` | AnyKernel3 flashable kernel (Clean, GCC 14) |
| `NoRoot-gs201-Sultan-clang.zip` | AnyKernel3 flashable kernel (Clean, Neutron Clang) |
| `NoMount.zip` | Universal NoMount metamodule (install via Root Manager) |
| `KernelSU_Next_*.apk` | Official KernelSU-Next companion manager app |
| `upstream-shas-*.json` | Git commit audit manifest for build reproducibility |

---

## Installation Guide

### Prerequisites:
- Unlocked bootloader on Pixel 7 / Pixel 7 Pro (**gs201**).
- Stock or custom AOSP ROM based on Android 14.

### 1. Flashing the Kernel
1. Download the AnyKernel3 ZIP corresponding to your preferred variant and toolchain from [Releases](https://github.com/bhazheng/Sultan_KernelSU_SUSFS/releases).
2. Flash the ZIP using one of the following methods:
   - **[Horizon Kernel Flasher](https://github.com/libxzr/HorizonKernelFlasher)** (Recommended).
   - **Franco Kernel Manager (FKM)** or **EX Kernel Manager**.
   - Custom recovery (TWRP) if available.
3. Reboot your device.

### 2. Setting Up Root & Modules (KernelSU-Next variant only)
1. Install the downloaded `KernelSU_Next_*.apk` manager application.
2. Open the app to verify root access and SuSFS status.
3. Install the companion modules:
   - **SuSFS Module**: Download and flash [ksu_module_susfs](https://github.com/sidex15/ksu_module_susfs).
   - **NoMount Metamodule**: Flash `NoMount.zip` directly in the manager app.
4. Reboot your device to activate all protections.

---

## Repository Structure

```
.
├── .github/workflows/
│   ├── build-kernel-release.yml   # Main orchestration workflow (triggers build & release)
│   ├── sultan-gcc.yml             # GCC 14 build pipeline
│   └── sultan-clang.yml           # Neutron Clang (ThinLTO) build pipeline
├── patches/
│   ├── 00_sultan_kernel_fixes.patch               # Linker, weak symbol, and setlocalversion fixes
│   ├── 02_ksun_sultan.patch                       # Non-modular patch_memory build hook for KSU
│   ├── 50_add_susfs_in_gki-android14-6.1-sultan.patch # SuSFS inline hooks for Sultan tree
│   └── deprecated/
│       └── next-susfs-fixup.patch                 # Legacy overlay patch (deprecated)
└── README.md
```

---

## Credits & Acknowledgements

Special thanks to the developers and open-source projects that make this kernel possible:

- **[kerneltoast (Sultan Alsawaf)](https://github.com/kerneltoast)** - Creator of Sultan Kernel.
- **[bhazheng](https://github.com/bhazheng)** - Maintainer of the gs201 Tensynos kernel tree and patches.
- **[pershoot](https://github.com/pershoot)** - For the `dev-susfs` fork of KernelSU-Next and `susfs4ksu`.
- **[tiann](https://github.com/tiann)** & **[rifsxd](https://github.com/KernelSU-Next/KernelSU-Next)** - KernelSU & KernelSU-Next core developers.
- **[simonpunk](https://gitlab.com/simonpunk/susfs4ksu.git)** - Creator of SuSFS.
- **[maxsteeel](https://github.com/maxsteeel/nomount)** - Creator of the NoMount framework.
- **[sidex15](https://github.com/sidex15/ksu_module_susfs)** - Creator of the SuSFS Magisk/KSU module.
- **[Neutron Toolchains](https://github.com/Neutron-Toolchains)** - High-performance LLVM/Clang builds.
- **[TheWildJames](https://github.com/TheWildJames)** & **[WildKernels](https://github.com/WildKernels)** - Base build scripts and CI inspirations.
- **[osm0sis](https://github.com/osm0sis/AnyKernel3)** - AnyKernel3 template and flashing tools.
