# Minimal Client Requirements for Javya

This document provides guidance on minimum device and browser requirements for running the Javya frontend.

## Technical Requirements Summary

| Metric | Minimum | Recommended |
|--------|---------|-------------|
| **RAM** | 512 MB | 1 GB+ |
| **CPU** | Dual-core (2015+) | Quad-core |
| **Browser** | Chrome 63+, Firefox 54+, Safari 12+ | Latest stable |
| **Network** | 2 Mbps | 5 Mbps+ |
| **Bundle Size** | ~70-100 KB gzipped | - |

## Frontend Stack Overview

- **Framework**: React 19 + Vite + TypeScript
- **Build Target**: ES2022
- **Key Dependencies**: dnd-kit (drag-and-drop), i18next (i18n), React Router
- **CSS**: CSS Grid, Flexbox, Custom Properties
- **No heavy assets**: No images, uses system fonts

---

## Recommended Devices

### Chromebooks

| Device | Status | Notes |
|--------|--------|-------|
| **Any Chromebook (2017+)** | Excellent | Chrome updates automatically; 2GB+ RAM typical |
| **HP Chromebook 11 G5** | Works | 4GB RAM, Intel Celeron |
| **Acer Chromebook Spin 311** | Works | 4GB RAM, MediaTek processor |
| **Samsung Chromebook 4** | Works | Budget option, 4GB RAM |

> **Note:** Any Chromebook still receiving updates (check `chrome://version`) will run Javya smoothly.

### Android Phones

| Device | Release | Status | Notes |
|--------|---------|--------|-------|
| **Google Pixel 6** | 2021 | Excellent | 8GB RAM, Tensor chip |
| **Samsung Galaxy A13** | 2022 | Works well | 4GB RAM, Exynos 850 |
| **Samsung Galaxy A12** | 2020 | Works | 3-4GB RAM, budget chip |
| **Xiaomi Redmi Note 9** | 2020 | Works | 3-4GB RAM |
| **Motorola Moto G Power** | 2020+ | Works | Any generation |
| **Google Pixel 4a** | 2020 | Excellent | 6GB RAM |

> **Minimum Android version:** Android 8.0+ with Chrome 63+ or Firefox 54+

### iPhones / iPads

| Device | Release | Status | Notes |
|--------|---------|--------|-------|
| **iPhone 8/X** | 2017 | Works | iOS 12+ required |
| **iPhone SE (2nd gen)** | 2020 | Works well | 3GB RAM |
| **iPad (6th gen+)** | 2018+ | Excellent | Great for scheduling views |

> **Minimum iOS version:** iOS 12+ (Safari 12+)

### Budget Laptops

| Device | Status | Notes |
|--------|--------|-------|
| **Any laptop with Chrome/Firefox** | Works | 4GB+ RAM, 2015+ |
| **Older MacBooks (2015+)** | Works | macOS 10.13+ required |
| **Windows laptops (Intel Celeron/i3)** | Works | Windows 7+ with modern browser |

---

## Borderline Devices (May Have Issues)

| Device | Issue | Workaround |
|--------|-------|------------|
| **Phones with 2GB RAM** | May lag with large song lists | Keep lists under 100 items |
| **2016 Chromebooks** | May lose Chrome updates | Check if still supported |
| **Android 7.x devices** | Browser may be outdated | Install Chrome from Play Store |

---

## Not Recommended

| Device | Reason |
|--------|--------|
| **iPhone 6s or older** | iOS 11 max, Safari 11 lacks ES2022 support |
| **Android 6.0 or older** | Cannot run Chrome 63+ |
| **Windows XP/Vista** | No modern browser support |
| **Internet Explorer** | No ES2022 support (will not work) |
| **Pre-2015 Chromebooks** | Likely out of update support |

---

## Browser Version Requirements

Based on the ES2022 build target:

| Browser | Minimum Version | Release Year |
|---------|-----------------|--------------|
| Chrome | 63+ | 2017 |
| Firefox | 54+ | 2017 |
| Safari | 12+ | 2018 |
| Edge | 79+ (Chromium) | 2020 |
| Chrome Mobile | 63+ | 2017 |
| Safari iOS | 12+ | 2018 |
| Android Browser | 63+ | 2017 |

**Market Coverage:** ~95% of active users (2024+)

---

## Resource Usage

### Memory

| State | RAM Usage | Notes |
|-------|-----------|-------|
| Idle | 50-75 MB | React runtime + base app |
| Typical | 100-150 MB | 1-2 open pages with data |
| Peak | 200-300 MB | Full calendar + drag-drop + large data |

### CPU

| Activity | CPU Usage |
|----------|-----------|
| Idle | <1% |
| Interactive (forms, navigation) | 5-15% |
| Heavy (calendar rendering, imports) | 20-30% |

---

## Key Features & Device Impact

| Feature | Impact | Notes |
|---------|--------|-------|
| **Drag-and-drop (dnd-kit)** | Low | GPU-accelerated CSS transforms |
| **Calendar views** | Low | 42 elements per month, memoized |
| **Song search/filter** | Low | O(n) client-side filtering |
| **i18n (EN/ES)** | Negligible | Hash map lookups |
| **Large data sets (1000+ songs)** | Medium | Consider pagination if needed |

---

## Bottom Line

- **Pixel 6, Samsung A13**: Excellent choices, far exceed requirements
- **Budget phones (2018+)**: Work fine for typical use
- **Chromebooks**: Any model still receiving updates will work
- **Old laptops**: 2015+ with a modern browser is sufficient

The Javya frontend is lightweight and optimized for modern devices. Any device from 2017+ with a current browser will provide a good experience.
