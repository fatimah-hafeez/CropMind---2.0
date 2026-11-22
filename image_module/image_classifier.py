"""Loads the trained model and returns the raw probabilities of one crop.

This file decides nothing. It reads the photo exactly as the training code did
(tf.io.decode_image, tf.image.resize to 224 x 224, tf.round, uint8), runs the
27-class model and returns the 9 raw probabilities of the selected crop, in the
order of results/class_labels.py. They are NOT re-normalised: a photo of the
wrong crop keeps its probability on the other crop's classes, which is what
makes the thresholds reject it.

The model is loaded once, on first use. Technical details go to the log
(terminal). A DiagnosisError message is short, plain and safe to show to a
farmer: no paths, no codes.
"""

import logging
import os
import threading

import numpy as np

from results.class_labels import ALL_LABELS, CROPS, LABELS_BY_CROP
from results.errors import DiagnosisError

logger = logging.getLogger(__name__)

IMAGE_SIZE = 224
LABELS_PER_CROP = 9

READ_ERROR = "The photo could not be read. Please try another photo."
CHECK_ERROR = "The photo could not be checked. Please try again."
UNAVAILABLE_ERROR = "The photo check is not available right now. Please try again later."


def check_labels():
    """The model outputs follow the alphabetical class list. Fail loudly if the list is wrong."""
    if len(ALL_LABELS) != len(CROPS) * LABELS_PER_CROP:
        raise RuntimeError(f"Expected 27 class labels, found {len(ALL_LABELS)}")
    if list(ALL_LABELS) != sorted(ALL_LABELS):
        raise RuntimeError("The class labels are not in alphabetical order")
    for crop in CROPS:
        if len(LABELS_BY_CROP[crop]) != LABELS_PER_CROP:
            raise RuntimeError(f"{crop} must have {LABELS_PER_CROP} labels")


class ImageClassifier:
    def __init__(self, model_path):
        check_labels()
        self._model_path = os.fspath(model_path)
        self._tf = None
        self._model = None
        self._lock = threading.Lock()

    def load(self):
        """Load the model once. Raises DiagnosisError if it is missing or broken."""
        with self._lock:
            if self._model is not None:
                return
            if not os.path.isfile(self._model_path):
                logger.error("Model file not found: %s", self._model_path)
                raise DiagnosisError(UNAVAILABLE_ERROR)
            try:
                import keras
                import tensorflow as tf

                model = keras.models.load_model(self._model_path)
                if model.output_shape[-1] != len(ALL_LABELS):
                    raise ValueError(f"The model has {model.output_shape[-1]} outputs, expected 27")
                # One warm-up call so that the first real photo is not slow.
                model.predict(np.zeros((1, IMAGE_SIZE, IMAGE_SIZE, 3), dtype="uint8"), verbose=0)
            except Exception:
                logger.exception("Could not load the model")
                raise DiagnosisError(UNAVAILABLE_ERROR)
            self._tf = tf
            self._model = model

    def _decode(self, data):
        return self._tf.io.decode_image(data, channels=3, expand_animations=False)

    def _to_tensor(self, image):
        """Photo in, uint8 tensor of 224 x 224 x 3 out, as in training."""
        tf = self._tf
        try:
            if isinstance(image, (str, os.PathLike)):
                pixels = self._decode(tf.io.read_file(os.fspath(image)))
            elif isinstance(image, (bytes, bytearray)):
                pixels = self._decode(bytes(image))
            elif hasattr(image, "getvalue"):  # a Streamlit upload or BytesIO
                pixels = self._decode(image.getvalue())
            elif hasattr(image, "read"):  # another file-like object
                if hasattr(image, "seek"):
                    image.seek(0)
                pixels = self._decode(image.read())
            elif hasattr(image, "convert"):  # a PIL image
                pixels = tf.convert_to_tensor(np.asarray(image.convert("RGB")), dtype=tf.uint8)
            else:
                raise TypeError(f"Unsupported image type: {type(image).__name__}")
            pixels.set_shape([None, None, 3])
            resized = tf.image.resize(pixels, (IMAGE_SIZE, IMAGE_SIZE))
            return tf.cast(tf.round(resized), tf.uint8)
        except Exception:
            logger.exception("Could not read the photo")
            raise DiagnosisError(READ_ERROR)

    def crop_probabilities(self, image, crop):
        """The 9 raw probabilities of the selected crop as (label, probability) pairs.

        The pairs are in the order of the class list, not sorted.
        """
        if crop not in CROPS:
            raise ValueError(f"Unknown crop: {crop}")
        self.load()
        pixels = self._to_tensor(image)
        try:
            with self._lock:
                probs = self._model.predict(pixels[None], verbose=0, batch_size=1)[0]
            start = CROPS.index(crop) * LABELS_PER_CROP
            block = np.asarray(probs[start : start + LABELS_PER_CROP], dtype="float64")
            if block.shape != (LABELS_PER_CROP,) or not np.all(np.isfinite(block)):
                raise ValueError(f"Invalid probabilities: {block}")
        except Exception:
            logger.exception("The model could not check the photo")
            raise DiagnosisError(CHECK_ERROR)
        return tuple(zip(LABELS_BY_CROP[crop], (float(p) for p in block)))
