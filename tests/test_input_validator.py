import io

from PIL import Image

from app.input_validator import InputValidator


def make_file(name, data):
    """Build a fake uploaded file: some bytes with a file name."""
    file = io.BytesIO(data)
    file.name = name
    return file


def make_image_bytes(image_format):
    """Build a tiny real image in the given format (JPEG, PNG or GIF)."""
    buffer = io.BytesIO()
    Image.new("RGB", (10, 10), "green").save(buffer, format=image_format)
    return buffer.getvalue()


# Image checks

def test_no_file_is_rejected():
    assert InputValidator().check_image(None) == InputValidator.MSG_NO_FILE


def test_wrong_file_type_is_rejected():
    file = make_file("leaf.pdf", b"some bytes")
    assert InputValidator().check_image(file) == InputValidator.MSG_WRONG_TYPE


def test_jpg_is_accepted():
    file = make_file("leaf.jpg", make_image_bytes("JPEG"))
    assert InputValidator().check_image(file) is None


def test_jpeg_is_accepted():
    file = make_file("leaf.jpeg", make_image_bytes("JPEG"))
    assert InputValidator().check_image(file) is None


def test_png_is_accepted():
    file = make_file("leaf.png", make_image_bytes("PNG"))
    assert InputValidator().check_image(file) is None


def test_uppercase_extension_is_accepted():
    file = make_file("LEAF.PNG", make_image_bytes("PNG"))
    assert InputValidator().check_image(file) is None


def test_file_over_10mb_is_rejected():
    too_big = b"x" * (InputValidator.MAX_IMAGE_BYTES + 1)
    file = make_file("big.jpg", too_big)
    assert InputValidator().check_image(file) == InputValidator.MSG_TOO_LARGE


def test_file_of_exactly_10mb_is_not_rejected_for_size():
    exact = b"x" * InputValidator.MAX_IMAGE_BYTES
    file = make_file("exact.jpg", exact)
    assert InputValidator().check_image(file) != InputValidator.MSG_TOO_LARGE


def test_text_file_renamed_to_png_is_rejected():
    file = make_file("fake.png", b"this is only text")
    assert InputValidator().check_image(file) == InputValidator.MSG_NOT_AN_IMAGE


def test_gif_renamed_to_png_is_rejected():
    file = make_file("fake.png", make_image_bytes("GIF"))
    assert InputValidator().check_image(file) == InputValidator.MSG_NOT_AN_IMAGE


def test_file_is_rewound_after_a_good_check():
    file = make_file("leaf.png", make_image_bytes("PNG"))
    InputValidator().check_image(file)
    assert file.tell() == 0


def test_file_is_rewound_after_a_bad_check():
    file = make_file("fake.png", b"this is only text")
    InputValidator().check_image(file)
    assert file.tell() == 0


# Text checks

def test_empty_text_is_rejected():
    assert InputValidator().check_text("") == InputValidator.MSG_EMPTY_TEXT


def test_spaces_only_text_is_rejected():
    assert InputValidator().check_text("   ") == InputValidator.MSG_EMPTY_TEXT


def test_missing_text_is_rejected():
    assert InputValidator().check_text(None) == InputValidator.MSG_EMPTY_TEXT


def test_normal_text_is_accepted():
    assert InputValidator().check_text("yellow spots on the leaves") is None