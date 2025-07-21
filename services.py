from googletrans import Translator
from models import SessionLocal, TranslationLog

def translate_text(text: str, target_lang: str) -> str:
    try:
        translator = Translator()
        result = translator.translate(text, dest=target_lang)

        
        db = SessionLocal()
        log = TranslationLog(
            original_text=text,
            translated_text=result.text,
            target_language=target_lang
        )
        db.add(log)
        db.commit()
        db.close()

        return result.text
    except Exception as e:
        return f"Translation failed: {str(e)}"
