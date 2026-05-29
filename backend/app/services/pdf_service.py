"""
Generación de PDFs de resumen de graduación.

Misma estrategia que SmsService: interfaz abstracta + implementación concreta.
Los tests inyectan MockPdfService sin tocar el sistema de archivos.
"""
import asyncio
import uuid
from abc import ABC, abstractmethod
from pathlib import Path


class PdfService(ABC):
    @abstractmethod
    async def generate_graduation_summary(self, data: dict) -> str:
        """Genera el PDF y devuelve la ruta del archivo."""
        raise NotImplementedError


class Fpdf2PdfService(PdfService):
    def __init__(self, output_dir: str = "summaries"):
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(exist_ok=True)

    async def generate_graduation_summary(self, data: dict) -> str:
        return await asyncio.to_thread(self._generate, data)

    def _generate(self, data: dict) -> str:
        from fpdf import FPDF

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        pdf.set_margins(20, 20, 20)

        # Encabezado
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(0, 120, 0)
        pdf.cell(0, 12, "TecnoAmigo", ln=True, align="C")

        pdf.set_font("Helvetica", "", 13)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(0, 8, "Tu recorrido de aprendizaje digital", ln=True, align="C")
        pdf.ln(6)

        pdf.set_draw_color(0, 120, 0)
        pdf.set_line_width(0.5)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(8)

        # Datos personales
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(30, 30, 30)
        name = data.get("full_name") or "Estimada persona"
        pdf.cell(0, 8, name, ln=True)

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(80, 80, 80)
        if data.get("city"):
            pdf.cell(0, 6, data["city"], ln=True)
        pdf.cell(0, 6, f"Comenzó el {data.get('first_visit_date', '')}", ln=True)
        pdf.cell(0, 6, f"Graduada/o el {data.get('graduation_date', '')}", ln=True)
        pdf.ln(6)

        # Logros
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 8, "Lo que aprendiste:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(40, 40, 40)

        area_labels = {
            "comunicacion": "Comunicacion con familia (WhatsApp, videollamadas)",
            "banca":        "Banco por internet",
            "gobierno":     "Tramites digitales y ClaveUnica",
            "seguridad":    "Seguridad digital (estafas, virus, llamadas)",
            "mi_telefono":  "Manejo del telefono (archivos, PDF, descargas)",
        }
        for area in data.get("completed_areas", []):
            label = area_labels.get(area, area)
            pdf.cell(0, 7, f"  + {label}", ln=True)
        pdf.ln(4)

        # Estadísticas
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(0, 100, 0)
        pdf.cell(0, 8, "Tu progreso en números:", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(0, 7, f"  Logros obtenidos: {data.get('achievements_earned', 0)} de {data.get('achievements_total', 0)}", ln=True)
        pdf.cell(0, 7, f"  Lecciones completadas: {data.get('total_lessons_completed', 0)}", ln=True)
        pdf.cell(0, 7, f"  Dias de practica: {data.get('total_active_days', 0)}", ln=True)
        pdf.ln(8)

        # Mensaje de cierre
        pdf.set_draw_color(0, 120, 0)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(8)
        pdf.set_font("Helvetica", "I", 11)
        pdf.set_text_color(60, 60, 60)
        pdf.multi_cell(
            0, 7,
            "Completaste tu camino en TecnoAmigo. "
            "Ahora tienes las herramientas para usar la tecnologia "
            "con confianza y autonomia. "
            "Cuando necesites repasar algo, este resumen te acompana.",
        )

        filename = f"graduacion_{data['user_id']}.pdf"
        path = self._output_dir / filename
        pdf.output(str(path))
        return str(path)


class MockPdfService(PdfService):
    """Para tests — no genera archivos reales."""
    async def generate_graduation_summary(self, data: dict) -> str:
        return f"summaries/mock_graduacion_{data['user_id']}.pdf"


def get_pdf_service() -> PdfService:
    return Fpdf2PdfService()
