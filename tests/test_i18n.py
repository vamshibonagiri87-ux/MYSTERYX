from mysteryx.i18n import language_name, tr


def test_supported_languages_have_native_names():
    assert language_name("te") == "తెలుగు"
    assert language_name("hi") == "हिन्दी"


def test_interface_strings_translate_and_format():
    assert tr("Make my guess", "te") == "?? ????? ????????"
    assert tr("Clues found: {found} of {total}", "hi", found=2, total=5) == "मिले सुराग: 5 में से 2"
