# 🌟 ClassifyEverything-LumoSort — A Universal Visual Classification Tool

<div align="center">
  <p>
    <a href="https://github.com/Jimmi1e/ClassifyEverything-LumoSort/releases">
      <img src="https://img.shields.io/badge/version-1.1.0-blue.svg" alt="version"/>
    </a>
    <a href="LICENSE">
      <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="license"/>
    </a>
    <a href="https://www.python.org/downloads/release/python-3100/">
      <img src="https://img.shields.io/badge/python-3.10-blue.svg" alt="python"/>
    </a>
  </p>
</div>

## 🎬 Background

I'm an amateur photographer and a Master's student in Electrical & Computer Engineering at **Concordia University**. Initially developed for organizing my photo library, LumoSort has evolved into a powerful universal visual classification tool. Thanks to the robust CLIP model, it can classify not just photos, but virtually any visual content into semantic categories. 🎯✨

Whether you're dealing with photographs, artwork, scientific images, or any other visual data, LumoSort can help you organize them intelligently. The system is highly adaptable - simply modify the categories in `labels.py` to suit your specific classification needs!

## 🌈 Versatility - Beyond Photography

### 🔥 Important Note: Multi-Purpose Visual Classification Tool

While LumoSort was initially designed for photography organization, it's actually a versatile visual classification tool that can be adapted for various visual tasks, such as:

- 🌸 Flower species classification
- 🐾 Animal categorization
- 🦜 Fine-grained bird species identification
- 🎨 Art style classification
- 📦 Product categorization
- And many more!

To adapt LumoSort for your specific classification needs, you can simply modify the `labels.py` file to include your desired categories. The powerful CLIP model behind LumoSort can handle a wide range of visual classification tasks with impressive accuracy!

### 🌺 Example: Flower Classification

Here's an example of how you could modify `labels.py` for flower classification:

```python
CLIP_LABELS = [
    "A photo of an iris flower",
    "A photo of a rose flower",
    "A photo of a tulip flower",
    "A photo of a sunflower",
    "A photo of a bluebell flower",
    "A photo of a dahlia flower",
    "A photo of cherry blossoms",
    "A photo of an orchid",
    "A photo of a lily flower",
    "A photo of a chrysanthemum flower",
    "A photo of a lotus flower",
    "A photo of a peony flower",
]

LABEL_DISPLAY = {
    "A photo of an iris flower": "Iris",
    "A photo of a rose flower": "Rose",
    "A photo of a tulip flower": "Tulip",
    "A photo of a sunflower": "Sunflower",
    "A photo of a bluebell flower": "Bluebell",
    "A photo of a dahlia flower": "Dahlia",
    "A photo of cherry blossoms": "Cherry Blossom",
    "A photo of an orchid": "Orchid",
    "A photo of a lily flower": "Lily",
    "A photo of a chrysanthemum flower": "Chrysanthemum",
    "A photo of a lotus flower": "Lotus",
    "A photo of a peony flower": "Peony",
}
```

Each category follows the "A photo of..." format for CLIP labels, with simplified display names. You can follow this pattern to create your own classification categories!

## 🔗 Download (for Windows)

To support users in different regions, here are alternative download mirrors for the `LumoSort.exe` executable :

### 🌍 Google Drive(For Overseas Users)

If you're located overseas, you can use this Google Drive link to download the executable:

- [Google Drive: LumoSort.exe](https://drive.google.com/file/d/13ZbmWGuOfmzuGjPRudxjpWBjcVkYpWOd/view?usp=sharing)

### ☁️ Baidu NetDisk (For Mainland China Users)

If you're based in mainland China, please use the Baidu NetDisk link below:

- [Baidu NetDisk: LumoSort.exe](https://pan.baidu.com/s/1_BsGWZ860G74Asrspy6lkg?pwd=Lumo)  
  提取码：`Lumo`

## 🔗 Download (for Mac OS)
(
ℹ️ Note: The macOS version of LumoSort is currently under development and will be released soon.)
## ✨ Features

**LumoSort** is a desktop application that helps you automatically classify and organize your photo collections into semantic categories such as *Portrait*, *Street*, *Architecture*, *Food*, and more.

Built with **OpenAI CLIP** and **PyQt6**, it features:

- 🎨 Modern animated UI with Light/Dark mode
- 🌐 Multilingual support (10+ languages)
- 🤖 Local image classification
- 📱 Responsive design
- 🖼️ Background processing tools

### 📸 Screenshots

<div align="center">
  <img src="icon/screen1.png" alt="Main Interface" width="800"/>
  <p><em>Main Interface - Dark Mode</em></p>
  
  <img src="icon/screen2.png" alt="Category View" width="800"/>
  <p><em>Category View with Image Classification</em></p>
  
  <img src="icon/screen3.png" alt="Tools Interface" width="800"/>
  <p><em>Tools Interface - Background Processing</em></p>
</div>

---

## 📊 How It Works

LumoSort uses OpenAI's [CLIP](https://github.com/openai/CLIP) model to classify images by comparing them with a list of text prompts describing various categories. The model computes similarity scores between image and text embeddings and selects the most likely label.

### Key Features

* 🧠 Uses `ViT-B/32`, a Vision Transformer-based CLIP model
* 📂 Includes 20+ categories like `Portrait`, `Food`, `Street`, `Library`, `Nature`, etc.
* 🔄 Automatically groups and copies images into corresponding folders
* 💻 Modern PyQt6 GUI with:
  * 🌓 Light/Dark mode support
  * ⏳ Real-time progress tracking
  * 🎯 Grid-based album view
  * 🔍 Individual preview mode
  * 🌍 Multilingual interface

---

## 📦 Manual Model Downloads

Due to GitHub file size restrictions, two required files must be downloaded manually:

### 1. CLIP Model Weights: `ViT-B-32.pt`

* 🔗 [Download ViT-B-32.pt](https://openaipublic.blob.core.windows.net/clip/models/ViT-B-32.pt)
* 📁 Place in: `models/ViT-B-32.pt`

### 2. Tokenizer Vocabulary: `bpe_simple_vocab_16e6.txt.gz`

* 🔗 [Download bpe_simple_vocab_16e6.txt.gz](https://openaipublic.blob.core.windows.net/clip/bpe_simple_vocab_16e6.txt.gz)
* 📁 Place in: `clip/bpe_simple_vocab_16e6.txt.gz`
* (See `clip/download_Vocabulary.txt` for the link)

---

## 📁 Directory Structure

```bash
LumoSort/
├── main.py               # Application entry point
├── gui_qt.py            # Main GUI implementation
├── Classifierpy.py      # CLIP classifier logic
├── labels.py            # Category definitions
├── icon/
│   └── logo.ico         # Application icon
├── models/
│   └── ViT-B-32.pt     # <- manual download
├── clip/
│   └── bpe_simple_vocab_16e6.txt.gz  # <- manual download
├── requirements.txt     # Dependencies
└── ...
```

---

## 🚀 Getting Started

```bash
# Create a virtual environment
conda create -n lumosort python=3.10
conda activate lumosort

# Install dependencies
pip install -r requirements.txt

# Run the main program
python main.py
```

### Pre-built Executable

The pre-built Windows executable (`LumoSort.exe`) is available on the [Releases](https://github.com/your-repo/releases) page.  
**Note:** You still need to manually download `bpe_simple_vocab_16e6.txt.gz` and place it in the `clip` folder.

---

## 🔧 Building Executable (Windows)

```bash
pyinstaller main.py --onefile \
  --icon=icon/logo.ico \
  --add-data "models/ViT-B-32.pt;models" \
  --add-data "clip/bpe_simple_vocab_16e6.txt.gz;clip"
```

Ensure `sys._MEIPASS` is handled properly when accessing resources inside your code (e.g., tokenizer path).

---

## 👤 Author

Created by Jiaxi Yang

## 🙏 Acknowledgments

Special thanks to:
- [Photo_background](https://github.com/waterkingest/Photo_background) by @waterkingest for providing inspiration for the background processing features
- The open-source community for their invaluable tools and libraries

## 📄 License & Attribution

This project is released under the MIT License.

If you use LumoSort or its components (UI, classifier design, or visuals) as part of a derivative work, **please include a visible attribution** such as:

> "Based on [LumoSort](https://github.com/Jimmi1e/LumoSort) by @Jimmi1e"

This helps support the original author and gives proper credit. Thank you!

# Make sure clip/bpe_simple_vocab_16e6.txt.gz exists
pyinstaller main.spec --clean --noconfirm

