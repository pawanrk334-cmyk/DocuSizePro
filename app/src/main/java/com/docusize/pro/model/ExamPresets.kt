package com.docusize.pro.model

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
