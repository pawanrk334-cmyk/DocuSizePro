package com.docusize.pro

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
