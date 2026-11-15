# CropMind 2.0 class list (Version 1)

Agreed on 14 November 2026 by the group leader. Any change to this list needs the agreement of all three members, because the same names are used by the image module, the text module and the main screen.

## Overview

- 3 crops: Cotton, Sugarcane and Wheat.
- 9 classes per crop (8 disease or pest classes and 1 healthy class), 27 classes in total.
- A result can also be "no match". No match is an outcome, not a class, and it has no label in this list.

## Naming rules

- Every label has the form `Crop_Name`, with words separated by underscores.
- The crop prefix is `Cotton`, `SugarCane` or `Wheat`.
- The healthy class of each crop is always `Crop_Healthy`.
- The display name is what the user reads on the screen. It is made from the label by removing the crop prefix and replacing underscores with spaces. The crop is shown as Cotton, Sugarcane or Wheat.

## The 27 classes

| Index | Crop | Label | Display name |
| --- | --- | --- | --- |
| 0 | Cotton | Cotton_Alternaria_Leaf_Spot | Alternaria Leaf Spot |
| 1 | Cotton | Cotton_Bacterial_Blight | Bacterial Blight |
| 2 | Cotton | Cotton_Curl_Virus | Curl Virus |
| 3 | Cotton | Cotton_Fusarium_Wilt | Fusarium Wilt |
| 4 | Cotton | Cotton_Healthy | Healthy |
| 5 | Cotton | Cotton_Leaf_Hopper_Jassids | Leaf Hopper Jassids |
| 6 | Cotton | Cotton_Leaf_Redding | Leaf Redding |
| 7 | Cotton | Cotton_Leaf_Variegation | Leaf Variegation |
| 8 | Cotton | Cotton_Verticillium_Wilt | Verticillium Wilt |
| 9 | Sugarcane | SugarCane_Brown_Rust | Brown Rust |
| 10 | Sugarcane | SugarCane_Eye_Spot | Eye Spot |
| 11 | Sugarcane | SugarCane_Healthy | Healthy |
| 12 | Sugarcane | SugarCane_Mawa | Mawa |
| 13 | Sugarcane | SugarCane_Mites | Mites |
| 14 | Sugarcane | SugarCane_Red_Rot | Red Rot |
| 15 | Sugarcane | SugarCane_Red_Spot | Red Spot |
| 16 | Sugarcane | SugarCane_Ring_Spot | Ring Spot |
| 17 | Sugarcane | SugarCane_Yellow_Leaf | Yellow Leaf |
| 18 | Wheat | Wheat_Black_Rust | Black Rust |
| 19 | Wheat | Wheat_Blast | Blast |
| 20 | Wheat | Wheat_Brown_Rust | Brown Rust |
| 21 | Wheat | Wheat_Common_Root_Rot | Common Root Rot |
| 22 | Wheat | Wheat_Fusarium_Head_Blight | Fusarium Head Blight |
| 23 | Wheat | Wheat_Healthy | Healthy |
| 24 | Wheat | Wheat_Leaf_Blight | Leaf Blight |
| 25 | Wheat | Wheat_Mildew | Mildew |
| 26 | Wheat | Wheat_Septoria | Septoria |

The index is the position used by the image module. It follows the order above (crop, then label), and it is the same order as in the earlier working files.

## Notes

- **Spelling:** `Leaf_Redding` keeps the spelling used by the dataset authors, so that the report matches the source.
- **Disease or pest:** Cotton Leaf Hopper Jassids (insects) and Sugarcane Mites are pests rather than diseases. The report and the screen say "disease or pest" where they describe the classes.
- **Healthy class:** the healthy class is a normal class. A healthy match is shown as Healthy for the selected crop.

## Renamed from the earlier working labels

| Earlier label | Label in this list |
| --- | --- |
| Cotton_Healthy_Leaf | Cotton_Healthy |
| SugarCane_Healthy_Leaves | SugarCane_Healthy |
| SugarCane_BrownRust | SugarCane_Brown_Rust |
| SugarCane_EyeSpot | SugarCane_Eye_Spot |
| SugarCane_RedRot | SugarCane_Red_Rot |
| SugarCane_RedSpot | SugarCane_Red_Spot |
| SugarCane_RingSpot | SugarCane_Ring_Spot |
| SugarCane_YellowLeaf | SugarCane_Yellow_Leaf |

The other 19 labels did not change.
