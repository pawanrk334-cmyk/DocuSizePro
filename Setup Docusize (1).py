import os
import zipfile

BASE_DIR = "."
OUT_ZIP = "artifacts/file_generation/ttl=63d/output/DocuSizePro_Android.zip"

files = {
    "settings.gradle.kts": """pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "DocuSizePro"
include(":app")
""",

    "build.gradle.kts": """plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "1.9.24" apply false
}
""",

    "gradle.properties": """org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true
""",

    "app/build.gradle.kts": """plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.docusize.pro"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.docusize.pro"
        minSdk = 24
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
        vectorDrawables { useSupportLibrary = true }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
    }
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.14"
    }
    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.4")
    implementation("androidx.activity:activity-compose:1.9.1")
    implementation(platform("androidx.compose:compose-bom:2024.06.00"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")
    implementation("androidx.exifinterface:exifinterface:1.3.7")
}
""",

    "app/proguard-rules.pro": """-keep class com.docusize.pro.** { *; }
""",

    "app/src/main/AndroidManifest.xml": """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" android:maxSdkVersion="32" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />

    <application
        android:allowBackup="true"
        android:icon="@android:drawable/ic_menu_gallery"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.DocuSizePro">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.DocuSizePro">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>
    </application>

</manifest>
""",

    "app/src/main/res/xml/file_paths.xml": """<?xml version="1.0" encoding="utf-8"?>
<paths>
    <cache-path name="cache" path="." />
    <files-path name="files" path="." />
</paths>
""",

    "app/src/main/res/values/strings.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">DocuSize Pro</string>
</resources>
""",

    "app/src/main/res/values/themes.xml": """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.DocuSizePro" parent="android:Theme.Material.Light.NoActionBar" />
</resources>
""",

    "app/src/main/java/com/docusize/pro/model/ExamPresets.kt": """package com.docusize.pro.model

data class DocSpec(
    val targetKb: Int,
    val widthPx: Int,
    val heightPx: Int,
    val label: String
)

data class ExamPreset(
    val id: String,
    val name: String,
    val photo: DocSpec,
    val sign: DocSpec,
    val thumb: DocSpec
)

object ExamPresets {
    val all = listOf(
        ExamPreset(
            id = "ssc",
            name = "SSC (CGL / CHSL / GD / MTS)",
            photo = DocSpec(45, 350, 450, "20-50 KB (3.5x4.5cm)"),
            sign = DocSpec(18, 400, 200, "10-20 KB (4x2cm)"),
            thumb = DocSpec(40, 300, 300, "20-50 KB")
        ),
        ExamPreset(
            id = "upsc",
            name = "UPSC (IAS / NDA / CDS)",
            photo = DocSpec(150, 500, 500, "20-300 KB (500x500px)"),
            sign = DocSpec(100, 500, 300, "20-300 KB"),
            thumb = DocSpec(100, 400, 400, "20-300 KB")
        ),
        ExamPreset(
            id = "ibps",
            name = "IBPS / SBI Bank PO",
            photo = DocSpec(45, 200, 230, "20-50 KB (200x230px)"),
            sign = DocSpec(18, 140, 60, "10-20 KB (140x60px)"),
            thumb = DocSpec(40, 240, 240, "20-50 KB (240x240px)")
        ),
        ExamPreset(
            id = "pancard",
            name = "PAN Card (NSDL / UTIITSL)",
            photo = DocSpec(45, 213, 213, "<= 50 KB (200 DPI)"),
            sign = DocSpec(40, 400, 200, "<= 50 KB (200 DPI)"),
            thumb = DocSpec(40, 300, 300, "<= 50 KB")
        ),
        ExamPreset(
            id = "passport",
            name = "Indian Passport",
            photo = DocSpec(90, 413, 531, "<= 100 KB (35x45mm)"),
            sign = DocSpec(30, 350, 150, "<= 50 KB"),
            thumb = DocSpec(30, 300, 300, "<= 50 KB")
        )
    )
}
""",

    "app/src/main/java/com/docusize/pro/engine/ImageEngine.kt": """package com.docusize.pro.engine

import android.content.ContentValues
import android.content.Context
import android.graphics.*
import android.graphics.pdf.PdfDocument
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.provider.MediaStore
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream
import kotlin.math.max
import kotlin.math.min
import kotlin.math.roundToInt

data class ProcessedResult(
    val bytes: ByteArray,
    val bitmap: Bitmap,
    val quality: Int
)

object ImageEngine {

    fun loadBitmap(context: Context, uri: Uri): Bitmap? {
        return context.contentResolver.openInputStream(uri)?.use { stream ->
            BitmapFactory.decodeStream(stream)
        }
    }

    fun transformBitmap(
        source: Bitmap,
        targetW: Int,
        targetH: Int,
        rotationDeg: Float = 0f,
        flipH: Boolean = false,
        addNameDop: Boolean = false,
        candidateName: String = "",
        photoDate: String = ""
    ): Bitmap {
        val matrix = Matrix().apply {
            if (rotationDeg != 0f) postRotate(rotationDeg)
            if (flipH) postScale(-1f, 1f)
        }
        val oriented = if (rotationDeg != 0f || flipH) {
            Bitmap.createBitmap(source, 0, 0, source.width, source.height, matrix, true)
        } else {
            source
        }

        val w = max(50, targetW)
        val h = max(50, targetH)
        val scaled = Bitmap.createScaledBitmap(oriented, w, h, true)

        if (!addNameDop || (candidateName.isBlank() && photoDate.isBlank())) {
            return scaled
        }

        val out = scaled.copy(Bitmap.Config.ARGB_8888, true)
        val canvas = Canvas(out)
        val bannerH = max(34f, h * 0.16f)
        val topY = h - bannerH

        val bgPaint = Paint().apply { color = Color.WHITE; style = Paint.Style.FILL }
        canvas.drawRect(0f, topY, w.toFloat(), h.toFloat(), bgPaint)

        val linePaint = Paint().apply { color = Color.BLACK; strokeWidth = 2f }
        canvas.drawLine(0f, topY, w.toFloat(), topY, linePaint)

        val textPaint = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = Color.BLACK
            textAlign = Paint.Align.CENTER
            typeface = Typeface.create(Typeface.DEFAULT, Typeface.BOLD)
            textSize = max(12f, bannerH * 0.28f)
        }

        val cleanName = candidateName.trim().uppercase()
        val cleanDate = photoDate.trim()
        if (cleanName.isNotEmpty() && cleanDate.isNotEmpty()) {
            canvas.drawText(cleanName, w / 2f, topY + bannerH * 0.38f, textPaint)
            textPaint.textSize = textPaint.textSize * 0.88f
            canvas.drawText("DOP: $cleanDate", w / 2f, topY + bannerH * 0.78f, textPaint)
        } else {
            val single = cleanName.ifEmpty { "DOP: $cleanDate" }
            canvas.drawText(single, w / 2f, topY + bannerH * 0.60f, textPaint)
        }
        return out
    }

    /**
     * Hard-ceiling binary search compression: output is strictly <= targetKb * 1024 bytes.
     */
    fun compressToCeiling(
        bitmap: Bitmap,
        targetKb: Int,
        format: Bitmap.CompressFormat = Bitmap.CompressFormat.JPEG,
        strictCeiling: Boolean = true
    ): ProcessedResult {
        val rawTarget = targetKb * 1024L
        val targetBytes = if (strictCeiling) (rawTarget * 0.985).toLong() else rawTarget

        if (format == Bitmap.CompressFormat.PNG) {
            var cur = bitmap
            var bytes = encode(cur, format, 100)
            var scale = 1.0f
            var iter = 0
            while (bytes.size > targetBytes && iter < 8) {
                scale *= 0.85f
                val nw = max(50, (bitmap.width * scale).roundToInt())
                val nh = max(50, (bitmap.height * scale).roundToInt())
                cur = Bitmap.createScaledBitmap(bitmap, nw, nh, true)
                bytes = encode(cur, format, 100)
                iter++
            }
            return ProcessedResult(bytes, cur, 100)
        }

        var minQ = 5
        var maxQ = 98
        var bestBytes: ByteArray? = null
        var bestQ = minQ

        repeat(7) {
            val midQ = (minQ + maxQ) / 2
            val bytes = encode(bitmap, format, midQ)
            if (bytes.size <= targetBytes) {
                bestBytes = bytes
                bestQ = midQ
                minQ = midQ + 1
            } else {
                maxQ = midQ - 1
            }
        }

        var cur = bitmap
        if (bestBytes == null) {
            var scale = 0.85f
            for (i in 0 until 6) {
                val nw = max(50, (bitmap.width * scale).roundToInt())
                val nh = max(50, (bitmap.height * scale).roundToInt())
                val tmp = Bitmap.createScaledBitmap(bitmap, nw, nh, true)
                val bytes = encode(tmp, format, 40)
                if (bytes.size <= targetBytes) {
                    bestBytes = bytes
                    bestQ = 40
                    cur = tmp
                    break
                }
                scale *= 0.8f
            }
        }

        val finalBytes = bestBytes ?: encode(cur, format, 10)
        return ProcessedResult(finalBytes, cur, bestQ)
    }

    /**
     * Increase file size to >= minKb without ruining aspect ratio.
     */
    fun increaseToFloor(
        bitmap: Bitmap,
        minKb: Int,
        format: Bitmap.CompressFormat = Bitmap.CompressFormat.JPEG
    ): ProcessedResult {
        val targetBytes = minKb * 1024
        var cur = bitmap
        var bytes = encode(cur, format, 98)
        var scale = 1.0f
        var iter = 0
        while (bytes.size < targetBytes && iter < 4) {
            scale *= 1.35f
            val nw = min(4000, (bitmap.width * scale).roundToInt())
            val nh = min(4000, (bitmap.height * scale).roundToInt())
            cur = Bitmap.createScaledBitmap(bitmap, nw, nh, true)
            bytes = encode(cur, format, 98)
            iter++
        }
        if (bytes.size < targetBytes) {
            val padded = ByteArray(targetBytes)
            System.arraycopy(bytes, 0, padded, 0, bytes.size)
            bytes = padded
        }
        return ProcessedResult(bytes, cur, 98)
    }

    private fun encode(bmp: Bitmap, fmt: Bitmap.CompressFormat, quality: Int): ByteArray {
        val out = ByteArrayOutputStream()
        bmp.compress(fmt, quality, out)
        return out.toByteArray()
    }

    fun generateTargetSizePdf(
        context: Context,
        images: List<Bitmap>,
        targetKb: Int,
        fileName: String
    ): File {
        val perPageKb = max(25, ((targetKb * 0.88) / max(1, images.size)).roundToInt())
        val pdfDoc = PdfDocument()
        val a4W = 595
        val a4H = 842

        images.forEachIndexed { idx, raw ->
            val scale = min(1240f / raw.width, 1240f / raw.height).coerceAtMost(1f)
            val cw = max(100, (raw.width * scale).roundToInt())
            val ch = max(100, (raw.height * scale).roundToInt())
            val resized = Bitmap.createScaledBitmap(raw, cw, ch, true)
            val compressed = compressToCeiling(resized, perPageKb, Bitmap.CompressFormat.JPEG, true)
            val pageBmp = BitmapFactory.decodeByteArray(compressed.bytes, 0, compressed.bytes.size)

            val pageInfo = PdfDocument.PageInfo.Builder(a4W, a4H, idx + 1).create()
            val page = pdfDoc.startPage(pageInfo)
            val fitScale = min((a4W - 40f) / pageBmp.width, (a4H - 40f) / pageBmp.height)
            val dw = pageBmp.width * fitScale
            val dh = pageBmp.height * fitScale
            val left = (a4W - dw) / 2f
            val top = (a4H - dh) / 2f
            page.canvas.drawBitmap(pageBmp, null, RectF(left, top, left + dw, top + dh), null)
            pdfDoc.finishPage(page)
        }

        val outFile = File(context.cacheDir, fileName)
        FileOutputStream(outFile).use { pdfDoc.writeTo(it) }
        pdfDoc.close()
        return outFile
    }

    fun createZipPackage(context: Context, entries: Map<String, ByteArray>, zipName: String): File {
        val outFile = File(context.cacheDir, zipName)
        ZipOutputStream(FileOutputStream(outFile)).use { zos ->
            entries.forEach { (name, data) ->
                zos.putNextEntry(ZipEntry(name))
                zos.write(data)
                zos.closeEntry()
            }
        }
        return outFile
    }

    fun saveBytesToDownloads(context: Context, bytes: ByteArray, fileName: String, mimeType: String): Uri? {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val values = ContentValues().apply {
                put(MediaStore.Downloads.DISPLAY_NAME, fileName)
                put(MediaStore.Downloads.MIME_TYPE, mimeType)
                put(MediaStore.Downloads.RELATIVE_PATH, Environment.DIRECTORY_DOWNLOADS + "/DocuSizePro")
            }
            val uri = context.contentResolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, values)
            uri?.let {
                context.contentResolver.openOutputStream(it)?.use { os -> os.write(bytes) }
            }
            uri
        } else {
            val dir = File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "DocuSizePro")
            if (!dir.exists()) dir.mkdirs()
            val f = File(dir, fileName)
            FileOutputStream(f).use { it.write(bytes) }
            Uri.fromFile(f)
        }
    }
}
""",

    "app/src/main/java/com/docusize/pro/MainActivity.kt": """package com.docusize.pro

import android.content.Intent
import android.graphics.Bitmap
import android.net.Uri
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.core.content.FileProvider
import com.docusize.pro.engine.ImageEngine
import com.docusize.pro.model.ExamPresets
import java.io.File
import java.io.FileOutputStream

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            var darkTheme by remember { mutableStateOf(false) }
            MaterialTheme(
                colorScheme = if (darkTheme) darkColorScheme() else lightColorScheme()
            ) {
                DocuSizeApp(darkTheme = darkTheme, onToggleTheme = { darkTheme = !darkTheme })
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DocuSizeApp(darkTheme: Boolean, onToggleTheme: () -> Unit) {
    var selectedTab by remember { mutableIntStateOf(0) }
    val tabs = listOf("Resizer", "3-in-1 Bundle", "Img to PDF", "Sign & Blur")

    Scaffold(
        topBar = {
            TopAppBar(
                title = {
                    Column {
                        Text("DocuSize Pro", fontWeight = FontWeight.Bold, fontSize = 18.sp)
                        Text("100% Offline • Govt Exam & PDF Studio", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    }
                },
                actions = {
                    IconButton(onClick = onToggleTheme) {
                        Icon(if (darkTheme) Icons.Default.LightMode else Icons.Default.DarkMode, contentDescription = "Theme")
                    }
                }
            )
        },
        bottomBar = {
            NavigationBar {
                val icons = listOf(Icons.Default.PhotoSizeSelectLarge, Icons.Default.FolderZip, Icons.Default.PictureAsPdf, Icons.Default.Draw)
                tabs.forEachIndexed { idx, title ->
                    NavigationBarItem(
                        selected = selectedTab == idx,
                        onClick = { selectedTab = idx },
                        icon = { Icon(icons[idx], contentDescription = title) },
                        label = { Text(title, fontSize = 11.sp) }
                    )
                }
            }
        }
    ) { padding ->
        Box(modifier = Modifier.padding(padding).fillMaxSize()) {
            when (selectedTab) {
                0 -> ResizerScreen()
                1 -> BundleScreen()
                2 -> PdfScreen()
                3 -> SignAndBlurScreen()
            }
        }
    }
}

@Composable
fun ResizerScreen() {
    val context = LocalContext.current
    var sourceBmp by remember { mutableStateOf<Bitmap?>(null) }
    var resultBmp by remember { mutableStateOf<Bitmap?>(null) }
    var resultBytes by remember { mutableStateOf<ByteArray?>(null) }

    var isReduceMode by remember { mutableStateOf(true) }
    var strictCeiling by remember { mutableStateOf(true) }
    var targetKbText by remember { mutableStateOf("50") }
    var widthText by remember { mutableStateOf("350") }
    var heightText by remember { mutableStateOf("450") }
    var rotation by remember { mutableFloatStateOf(0f) }
    var addNameDop by remember { mutableStateOf(false) }
    var candidateName by remember { mutableStateOf("") }
    var photoDate by remember { mutableStateOf("29/10/2026") }

    val picker = rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri: Uri? ->
        uri?.let {
            val bmp = ImageEngine.loadBitmap(context, it)
            if (bmp != null) {
                sourceBmp = bmp
                widthText = bmp.width.toString()
                heightText = bmp.height.toString()
                resultBmp = null
                resultBytes = null
            }
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Button(
            onClick = { picker.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)) },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp)
        ) {
            Icon(Icons.Default.AddPhotoAlternate, contentDescription = null)
            Spacer(Modifier.width(8.dp))
            Text(if (sourceBmp == null) "Select Photo from Gallery" else "Change Photo")
        }

        if (sourceBmp != null) {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                FilterChip(selected = isReduceMode, onClick = { isReduceMode = true }, label = { Text("Reduce (<= KB)") }, modifier = Modifier.weight(1f))
                FilterChip(selected = !isReduceMode, onClick = { isReduceMode = false }, label = { Text("Increase (>= KB)") }, modifier = Modifier.weight(1f))
            }

            OutlinedTextField(
                value = targetKbText,
                onValueChange = { targetKbText = it },
                label = { Text("Target Size (KB)") },
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                modifier = Modifier.fillMaxWidth()
            )

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(
                    value = widthText, onValueChange = { widthText = it },
                    label = { Text("Width (px)") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f)
                )
                OutlinedTextField(
                    value = heightText, onValueChange = { heightText = it },
                    label = { Text("Height (px)") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                    modifier = Modifier.weight(1f)
                )
            }

            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Checkbox(checked = strictCeiling, onCheckedChange = { strictCeiling = it })
                    Text("Hard Ceiling Limit", fontSize = 13.sp)
                }
                OutlinedButton(onClick = { rotation = (rotation + 90f) % 360f }) {
                    Text("Rotate 90°")
                }
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                Switch(checked = addNameDop, onCheckedChange = { addNameDop = it })
                Spacer(Modifier.width(8.dp))
                Text("Add Name & Date of Photo (Govt Form)", fontSize = 13.sp)
            }

            if (addNameDop) {
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(value = candidateName, onValueChange = { candidateName = it }, label = { Text("Full Name") }, modifier = Modifier.weight(1f))
                    OutlinedTextField(value = photoDate, onValueChange = { photoDate = it }, label = { Text("DOP") }, modifier = Modifier.weight(1f))
                }
            }

            Button(
                onClick = {
                    val bmp = sourceBmp ?: return@Button
                    val kb = targetKbText.toIntOrNull() ?: 50
                    val w = widthText.toIntOrNull() ?: bmp.width
                    val h = heightText.toIntOrNull() ?: bmp.height
                    val transformed = ImageEngine.transformBitmap(bmp, w, h, rotation, false, addNameDop, candidateName, photoDate)
                    val res = if (isReduceMode) {
                        ImageEngine.compressToCeiling(transformed, kb, Bitmap.CompressFormat.JPEG, strictCeiling)
                    } else {
                        ImageEngine.increaseToFloor(transformed, kb, Bitmap.CompressFormat.JPEG)
                    }
                    resultBmp = res.bitmap
                    resultBytes = res.bytes
                    Toast.makeText(context, "Processed: ${res.bytes.size / 1024} KB", Toast.LENGTH_SHORT).show()
                },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp)
            ) {
                Text("Process Image")
            }

            resultBmp?.let { outBmp ->
                val sizeKb = (resultBytes?.size ?: 0) / 1024f
                Card(modifier = Modifier.fillMaxWidth()) {
                    Column(modifier = Modifier.padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                        Text("Output: %.1f KB (%dx%d px)".format(sizeKb, outBmp.width, outBmp.height), fontWeight = FontWeight.Bold)
                        Spacer(Modifier.height(8.dp))
                        Image(bitmap = outBmp.asImageBitmap(), contentDescription = "Result", modifier = Modifier.height(220.dp))
                        Spacer(Modifier.height(8.dp))
                        Button(onClick = {
                            resultBytes?.let { bytes ->
                                val name = "DocuSize_${sizeKb.toInt()}kb_${System.currentTimeMillis()}.jpg"
                                ImageEngine.saveBytesToDownloads(context, bytes, name, "image/jpeg")
                                Toast.makeText(context, "Saved to Downloads/DocuSizePro/$name", Toast.LENGTH_LONG).show()
                            }
                        }) {
                            Text("Save to Downloads")
                        }
                    }
                }
            }
        }
    }
}

@Composable
fun BundleScreen() {
    val context = LocalContext.current
    var selectedPresetIdx by remember { mutableIntStateOf(0) }
    var photoBmp by remember { mutableStateOf<Bitmap?>(null) }
    var signBmp by remember { mutableStateOf<Bitmap?>(null) }
    var thumbBmp by remember { mutableStateOf<Bitmap?>(null) }
    var candidateName by remember { mutableStateOf("") }
    var photoDate by remember { mutableStateOf("29/10/2026") }

    val pickPhoto = rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri -> uri?.let { photoBmp = ImageEngine.loadBitmap(context, it) } }
    val pickSign = rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri -> uri?.let { signBmp = ImageEngine.loadBitmap(context, it) } }
    val pickThumb = rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri -> uri?.let { thumbBmp = ImageEngine.loadBitmap(context, it) } }

    val preset = ExamPresets.all[selectedPresetIdx]

    Column(modifier = Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("3-in-1 Govt Exam Bundle (ZIP)", fontWeight = FontWeight.Bold, fontSize = 16.sp)
        ExamPresets.all.forEachIndexed { idx, p ->
            Row(verticalAlignment = Alignment.CenterVertically) {
                RadioButton(selected = selectedPresetIdx == idx, onClick = { selectedPresetIdx = idx })
                Text(p.name, fontSize = 13.sp)
            }
        }

        OutlinedTextField(value = candidateName, onValueChange = { candidateName = it }, label = { Text("Name on Photo (Optional)") }, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(value = photoDate, onValueChange = { photoDate = it }, label = { Text("Date of Photo (Optional)") }, modifier = Modifier.fillMaxWidth())

        OutlinedButton(onClick = { pickPhoto.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)) }, modifier = Modifier.fillMaxWidth()) {
            Text(if (photoBmp == null) "1. Upload Photo (${preset.photo.label})" else "1. Photo Selected ✓")
        }
        OutlinedButton(onClick = { pickSign.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)) }, modifier = Modifier.fillMaxWidth()) {
            Text(if (signBmp == null) "2. Upload Signature (${preset.sign.label})" else "2. Signature Selected ✓")
        }
        OutlinedButton(onClick = { pickThumb.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)) }, modifier = Modifier.fillMaxWidth()) {
            Text(if (thumbBmp == null) "3. Upload Thumb (Optional)" else "3. Thumb Selected ✓")
        }

        Button(
            onClick = {
                val map = mutableMapOf<String, ByteArray>()
                photoBmp?.let {
                    val t = ImageEngine.transformBitmap(it, preset.photo.widthPx, preset.photo.heightPx, 0f, false, candidateName.isNotBlank(), candidateName, photoDate)
                    map["1_photo.jpg"] = ImageEngine.compressToCeiling(t, preset.photo.targetKb).bytes
                }
                signBmp?.let {
                    val t = ImageEngine.transformBitmap(it, preset.sign.widthPx, preset.sign.heightPx)
                    map["2_signature.jpg"] = ImageEngine.compressToCeiling(t, preset.sign.targetKb).bytes
                }
                thumbBmp?.let {
                    val t = ImageEngine.transformBitmap(it, preset.thumb.widthPx, preset.thumb.heightPx)
                    map["3_thumb.jpg"] = ImageEngine.compressToCeiling(t, preset.thumb.targetKb).bytes
                }
                if (map.isEmpty()) {
                    Toast.makeText(context, "Select at least 1 image", Toast.LENGTH_SHORT).show()
                    return@Button
                }
                val zipFile = ImageEngine.createZipPackage(context, map, "Exam_${preset.id}_Bundle.zip")
                ImageEngine.saveBytesToDownloads(context, zipFile.readBytes(), zipFile.name, "application/zip")
                Toast.makeText(context, "Saved ZIP to Downloads/DocuSizePro/${zipFile.name}", Toast.LENGTH_LONG).show()
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Generate & Save ZIP Bundle")
        }
    }
}

@Composable
fun PdfScreen() {
    val context = LocalContext.current
    var images by remember { mutableStateOf<List<Bitmap>>(emptyList()) }
    var targetKbText by remember { mutableStateOf("200") }

    val pickMultiple = rememberLauncherForActivityResult(ActivityResultContracts.PickMultipleVisualMedia(10)) { uris ->
        images = uris.mapNotNull { ImageEngine.loadBitmap(context, it) }
    }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("Image to PDF (Target Size Under KB)", fontWeight = FontWeight.Bold, fontSize = 16.sp)
        OutlinedTextField(
            value = targetKbText, onValueChange = { targetKbText = it },
            label = { Text("Max PDF Size (KB)") }, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
            modifier = Modifier.fillMaxWidth()
        )
        Button(onClick = { pickMultiple.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)) }, modifier = Modifier.fillMaxWidth()) {
            Text("Select Images (${images.size} selected)")
        }
        Button(
            enabled = images.isNotEmpty(),
            onClick = {
                val kb = targetKbText.toIntOrNull() ?: 200
                val file = ImageEngine.generateTargetSizePdf(context, images, kb, "DocuSize_${kb}kb_${System.currentTimeMillis()}.pdf")
                ImageEngine.saveBytesToDownloads(context, file.readBytes(), file.name, "application/pdf")
                Toast.makeText(context, "PDF Saved (${file.length() / 1024} KB) in Downloads/DocuSizePro/", Toast.LENGTH_LONG).show()
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("Create & Save PDF")
        }
    }
}

@Composable
fun SignAndBlurScreen() {
    val context = LocalContext.current
    val paths = remember { mutableStateListOf<List<Offset>>() }
    var currentPath by remember { mutableStateOf<List<Offset>>(emptyList()) }

    Column(modifier = Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("Digital Signature Pad", fontWeight = FontWeight.Bold, fontSize = 16.sp)
        Box(
            modifier = Modifier.fillMaxWidth().height(240.dp).background(Color.White, RoundedCornerShape(12.dp))
                .pointerInput(Unit) {
                    detectDragGestures(
                        onDragStart = { offset -> currentPath = listOf(offset) },
                        onDrag = { change, _ -> currentPath = currentPath + change.position },
                        onDragEnd = { paths.add(currentPath); currentPath = emptyList() }
                    )
                }
        ) {
            Canvas(modifier = Modifier.fillMaxSize()) {
                (paths + listOf(currentPath)).forEach { pts ->
                    if (pts.size > 1) {
                        val p = Path().apply {
                            moveTo(pts.first().x, pts.first().y)
                            pts.drop(1).forEach { lineTo(it.x, it.y) }
                        }
                        drawPath(p, color = Color.Black, style = Stroke(width = 6f))
                    }
                }
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            OutlinedButton(onClick = { paths.clear(); currentPath = emptyList() }, modifier = Modifier.weight(1f)) {
                Text("Clear")
            }
            Button(
                onClick = {
                    val bmp = Bitmap.createBitmap(400, 200, Bitmap.Config.ARGB_8888)
                    val canvas = android.graphics.Canvas(bmp)
                    canvas.drawColor(android.graphics.Color.WHITE)
                    val paint = android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG).apply {
                        color = android.graphics.Color.BLACK
                        strokeWidth = 5f
                        style = android.graphics.Paint.Style.STROKE
                    }
                    paths.forEach { pts ->
                        if (pts.size > 1) {
                            val gp = android.graphics.Path()
                            gp.moveTo(pts.first().x * 0.4f, pts.first().y * 0.4f)
                            pts.drop(1).forEach { gp.lineTo(it.x * 0.4f, it.y * 0.4f) }
                            canvas.drawPath(gp, paint)
                        }
                    }
                    val res = ImageEngine.compressToCeiling(bmp, 18, Bitmap.CompressFormat.JPEG, true)
                    val name = "signature_${res.bytes.size / 1024}kb.jpg"
                    ImageEngine.saveBytesToDownloads(context, res.bytes, name, "image/jpeg")
                    Toast.makeText(context, "Signature Saved to Downloads/DocuSizePro/$name", Toast.LENGTH_LONG).show()
                },
                modifier = Modifier.weight(1f)
            ) {
                Text("Save Sign (<=18KB)")
            }
        }
    }
}
""",

    ".github/workflows/build_apk.yml": """name: Build Android Debug APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3
        with:
          gradle-version: '8.7'

      - name: Build Debug APK
        run: gradle assembleDebug

      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: DocuSizePro-Debug-APK
          path: app/build/outputs/apk/debug/app-debug.apk
""",

    "README.md": """# DocuSize Pro — Native Android App (Kotlin + Jetpack Compose)

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
"""
}

os.makedirs(os.path.dirname(OUT_ZIP), exist_ok=True)
for rel_path, content in files.items():
    full_path = os.path.join(BASE_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)


print("SUCCESS: All Android project files created in current folder!")