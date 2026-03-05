import polib
from googletrans import Translator
import time
import os
import re

# Regex patterns for Django placeholders
FORMAT_PATTERN = re.compile(r'%\([a-zA-Z0-9_]+\)[sd]|%[sd]|{[a-zA-Z0-9_]+}')

def protect_placeholders(text):
    placeholders = FORMAT_PATTERN.findall(text)
    protected_text = text
    for i, ph in enumerate(placeholders):
        protected_text = protected_text.replace(ph, f"__PLACEHOLDER_{i}__")
    return protected_text, placeholders

def restore_placeholders(text, placeholders):
    restored_text = text
    for i, ph in enumerate(placeholders):
        restored_text = restored_text.replace(f"__PLACEHOLDER_{i}__", ph)
    return restored_text

def auto_translate(file_path, target_lang):
    if not os.path.exists(file_path):
        print(f"Skipping: {file_path} not found.")
        return

    po = polib.pofile(file_path)
    translator = Translator()
    print(f"\n--- Starting {target_lang.upper()} Translation ---")

    for entry in po:
        if not entry.msgstr and entry.msgid and 'fuzzy' not in entry.flags:
            try:
                protected_text, placeholders = protect_placeholders(entry.msgid)
                translation = translator.translate(protected_text, dest=target_lang)
                translated_text = restore_placeholders(translation.text, placeholders)
                entry.msgstr = translated_text

                print(f"✓ Translated: {entry.msgid[:40]}")
                time.sleep(0.5)

            except Exception as e:
                print(f"✗ Error translating '{entry.msgid[:30]}': {e}")

    po.save()
    print(f"--- SUCCESS: {file_path} is updated ---")


auto_translate('locale/hi/LC_MESSAGES/django.po', 'hi')
auto_translate('locale/te/LC_MESSAGES/django.po', 'te')
