"""Class labels of CropMind 2.0 (Version 1), grouped by crop.

The agreed list for people is docs/class_list.md. This file holds the same
labels for the code. If the list ever changes, change both files and tell the
whole group, because the image module, the text module and the screen all read
these names.

Owner: Fatima. The order below is the order of the class list (index 0 to 26).
"""

CROPS = ("Cotton", "SugarCane", "Wheat")

LABELS_BY_CROP = {
    "Cotton": (
        "Cotton_Alternaria_Leaf_Spot",
        "Cotton_Bacterial_Blight",
        "Cotton_Curl_Virus",
        "Cotton_Fusarium_Wilt",
        "Cotton_Healthy",
        "Cotton_Leaf_Hopper_Jassids",
        "Cotton_Leaf_Redding",
        "Cotton_Leaf_Variegation",
        "Cotton_Verticillium_Wilt",
    ),
    "SugarCane": (
        "SugarCane_Brown_Rust",
        "SugarCane_Eye_Spot",
        "SugarCane_Healthy",
        "SugarCane_Mawa",
        "SugarCane_Mites",
        "SugarCane_Red_Rot",
        "SugarCane_Red_Spot",
        "SugarCane_Ring_Spot",
        "SugarCane_Yellow_Leaf",
    ),
    "Wheat": (
        "Wheat_Black_Rust",
        "Wheat_Blast",
        "Wheat_Brown_Rust",
        "Wheat_Fusarium_Head_Blight",
        "Wheat_Healthy",
        "Wheat_Leaf_Blight",
        "Wheat_Mildew",
        "Wheat_Septoria",
        "Wheat_Yellow_Rust",
    ),
}

# All 27 labels in class list order (crop, then label).
ALL_LABELS = tuple(label for crop in CROPS for label in LABELS_BY_CROP[crop])
