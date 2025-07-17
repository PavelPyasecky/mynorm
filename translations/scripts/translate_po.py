# ruff: noqa: BLE001
import logging

import polib
from translate import Translator

logging.basicConfig(level=logging.DEBUG)


def translate_po_file(input_file, output_file, target_lang="ru"):
    # Load the .po file
    po = polib.pofile(input_file)

    # Initialize the translator
    translator = Translator(to_lang=target_lang)

    # Translate each entry
    for entry in po:
        if not entry.msgstr:  # Only translate if msgstr is empty
            try:
                translation = translator.translate(entry.msgid)
                entry.msgstr = translation
                logging.debug(
                    "Translated: %s -> %s", entry.msgid, entry.msgstr
                )
            except Exception as e:
                logging.debug("Error translating '%s': %s", entry.msgid, e)

    # Save the translated .po file
    po.save(output_file)
    logging.debug("Translated file saved to %s", output_file)


# Example usage
translate_po_file(
    "translations/locale/ru/LC_MESSAGES/django.po",
    "translations/locale/ru/LC_MESSAGES/django.po",
)
