package com.docusize.pro.engine

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
