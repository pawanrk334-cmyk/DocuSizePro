# DocuSize Pro — Native Android App (Kotlin + Jetpack Compose)

## Included Features
- **KB Resizer & Compressor:** Strict hard-ceiling (`<= KB`) and Increase (`>= KB`) modes, custom dimensions (px), rotation, and Name + Date of Photo (DOP) banner.
- **3-in-1 Govt Exam Bundle:** SSC, UPSC, IBPS, PAN Card, and Passport presets with direct `.zip` export to `Downloads/DocuSizePro/`.
- **Image to PDF (Target KB):** Combine multiple images into an A4 PDF strictly under your target KB limit.
- **Digital Signature Pad:** Draw and export crisp signatures under 18 KB.

## How to Build the `.apk`

### Option 1: GitHub Actions (No Android Studio Required)
1. Create a new repository on GitHub and upload all files from this ZIP.
2. Go to the **Actions** tab on GitHub and click **Build Android Debug APK -> Run workflow**.
3. Once finished, download **DocuSizePro-Debug-APK** and install `app-debug.apk` on your Android phone.

### Option 2: Android Studio (On Laptop)
1. Open this extracted folder in **Android Studio** (Jellyfish or newer).
2. Let Gradle sync complete.
3. Click **Build -> Build Bundle(s) / APK(s) -> Build APK(s)**.
